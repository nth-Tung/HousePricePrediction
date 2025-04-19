import json
import joblib
import pandas as pd
from tensorflow.keras.models import load_model
from flask import Flask, render_template, request, jsonify
from unidecode import unidecode

app = Flask(__name__)

# Load dữ liệu quận, phường, đường
with open('data/hcm_districts.json', encoding='utf-8') as f:
    hcm_data = json.load(f)

# Load mô hình và preprocessor
model = load_model('model/my_model.h5')
scaler = joblib.load('model/scaler.pkl')
dummy_columns = joblib.load('model/dummy_columns.pkl')

# Danh sách loại nhà và pháp lý
house_types = ["Nhà ngõ, hẻm", "Nhà mặt phố, mặt tiền", "Nhà phố liền kề"]
legal_statuses = ["Đã có sổ", "Không có sổ", "Giấy tờ viết tay", "Sổ chung / công chứng vi bằng", "Đang chờ sổ"]

@app.route('/')
def index():
    districts = list(hcm_data.keys())
    return render_template('index.html', districts=districts, house_types=house_types, legal_statuses=legal_statuses)

@app.route('/get_wards/<district>')
def get_wards(district):
    wards = hcm_data.get(district, {}).get('phường', [])
    return jsonify(wards)

@app.route('/get_streets/<district>')
def get_streets(district):
    streets = hcm_data.get(district, {}).get('đường', [])
    return jsonify(streets)

@app.route('/search_street_in_district', methods=['GET'])
def search_street_in_district():
    district = request.args.get('district')
    query = request.args.get('query', '')
    if not district:
        return jsonify([])

    streets = hcm_data.get(district, {}).get('đường', [])
    query = unidecode(query.lower())
    filtered = [s for s in streets if query in unidecode(s.lower())]
    return jsonify(filtered)


@app.route('/predict', methods=['POST'])
def predict():
    data = request.form
    try:
        # Validate required fields
        required_fields = ['district', 'ward', 'street', 'house_type', 'legal_status', 'length', 'width', 'bedrooms', 'bathrooms', 'floors']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Convert and validate numeric inputs
        district = unidecode(str(data['district']).lower())
        ward = unidecode(str(data['ward']).lower())
        street = unidecode(str(data['street']).lower())
        house_type = unidecode(str(data['house_type']).lower())
        legal_status = unidecode(str(data['legal_status']).lower())
        try:
            length = float(data['length'])
            width = float(data['width'])
            bedrooms = int(data['bedrooms'])
            bathrooms = int(data['bathrooms'])
            floors = int(data['floors'])
        except ValueError:
            return jsonify({'error': 'Numeric fields must be valid numbers'}), 400

        # Additional validation (e.g., positive numbers)
        if length <= 0 or width <= 0 or bedrooms < 0 or bathrooms < 0 or floors <= 0:
            return jsonify({'error': 'Numeric fields must be positive (except bedrooms/bathrooms can be 0)'}), 400

        # Create input DataFrame
        data_test = pd.DataFrame({
            'house_type': [house_type],
            'acreage': [length * width],
            'width': [width],
            'length': [length],
            'bedrooms': [bedrooms],
            'bathrooms': [bathrooms],
            'floors': [floors],
            'legal_status': [legal_status],
            'street': [street],
            'ward': [ward],
            'district': [district]
        })

        # Process and predict
        data_test_encoded = pd.get_dummies(data_test, columns=['house_type', 'legal_status', 'street', 'ward', 'district'])
        for col in dummy_columns:
            if col not in data_test_encoded.columns:
                data_test_encoded[col] = 0
        data_test_encoded = data_test_encoded[dummy_columns]
        X_test_scaled = scaler.transform(data_test_encoded)
        price = model.predict(X_test_scaled)
        return jsonify({'price':str(round(price[0][0],2))})

    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 400


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)