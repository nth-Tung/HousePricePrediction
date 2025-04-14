from flask import Flask, render_template, request, jsonify
import json
import joblib
import pandas as pd
from unidecode import unidecode

app = Flask(__name__)

# Load dữ liệu quận, phường, đường
with open('data/hcm_districts.json', encoding='utf-8') as f:
    hcm_data = json.load(f)

# Load mô hình và các encoder
model = joblib.load('data/trained_model.pkl')
le_district = joblib.load('data/le_district.pkl')
le_ward = joblib.load('data/le_ward.pkl')
le_street = joblib.load('data/le_street.pkl')
le_house_type = joblib.load('data/le_house_type.pkl')
le_legal_status = joblib.load('data/le_legal_status.pkl')

# Danh sách loại nhà và pháp lý
house_types = ["Nhà ngõ, hẻm", "Nhà mặt phố, mặt tiền", "Nhà phố liền kề", "Nhà biệt thự"]
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

@app.route('/search_street/<query>')
def search_street(query):
    query = unidecode(query.lower())
    results = []
    for district, info in hcm_data.items():
        for street in info.get('đường', []):
            if query in unidecode(street.lower()):
                results.append({'district': district, 'street': street})
    return jsonify(results)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.form
    district = data['district']
    ward = data['ward']
    street = data['street']
    length = float(data['length'])
    width = float(data['width'])
    bedrooms = int(data['bedrooms'])
    bathrooms = int(data['bathrooms'])
    floors = int(data['floors'])
    house_type = data['house_type']
    legal_status = data['legal_status']

    # Mã hóa dữ liệu
    try:
        district_encoded = le_district.transform([district])[0]
        ward_encoded = le_ward.transform([ward])[0]
        street_encoded = le_street.transform([street])[0]
        house_type_encoded = le_house_type.transform([house_type])[0]
        legal_status_encoded = le_legal_status.transform([legal_status])[0]
    except:
        return jsonify({'error': 'Invalid input data'}), 400

    # Tạo dataframe để dự đoán
    input_data = pd.DataFrame({
        'district': [district_encoded],
        'ward': [ward_encoded],
        'street': [street_encoded],
        'length': [length],
        'width': [width],
        'bedrooms': [bedrooms],
        'bathrooms': [bathrooms],
        'floors': [floors],
        'house_type': [house_type_encoded],
        'legal_status': [legal_status_encoded]
    })

    # Dự đoán giá
    price = model.predict(input_data)[0]
    return jsonify({'price': round(price, 2)})

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)