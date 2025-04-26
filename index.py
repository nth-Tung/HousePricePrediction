import json
import joblib
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from flask import Flask, render_template, request, jsonify
from unidecode import unidecode
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import utils

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'hcm_districts.json')

with open(DATA_PATH, encoding='utf-8') as f:
    hcm_data = json.load(f)
huy =0

# Load mô hình và preprocessor
MODEL_PATH = os.path.join(BASE_DIR,'model','my_model.h5')
SCALER_PATH = os.path.join(BASE_DIR,'model','scaler.pkl')
DUMMY_PATH = os.path.join(BASE_DIR,'model','dummy_columns.pkl')
ENCODER_PATH = os.path.join(BASE_DIR,'model','encoder_label.pkl')
model = load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
dummy_columns = joblib.load(DUMMY_PATH)
encoder_label = joblib.load(ENCODER_PATH)

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
    global str
    data = request.form
    try:
        required_fields = ['district', 'ward', 'street', 'house_type', 'legal_status', 'length', 'width', 'bedrooms', 'bathrooms', 'floors']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

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

        if length <= 0 or width <= 0 or bedrooms < 0 or bathrooms < 0 or floors <= 0:
            return jsonify({'error': 'Numeric fields must be positive (except bedrooms/bathrooms can be 0)'}), 400

        acreage = length * width
        import pandas as pd
        columns = ['house_type', 'acreage', 'width', 'length', 'bedrooms', 'bathrooms', 'floors','legal_status', 'street', 'ward', 'district']

        data_test = pd.DataFrame([[house_type, acreage, width, length, bedrooms, bathrooms, floors,legal_status, street, ward, district]],columns=columns)

        data_test_encoded = pd.get_dummies(data_test, columns=['house_type', 'legal_status','street', 'ward', 'district'])

        for col in dummy_columns:
            if col not in data_test_encoded.columns:
                data_test_encoded[col] = 0

        data_test_encoded = data_test_encoded[dummy_columns]

        X_test_scaled = scaler.transform(data_test_encoded)

        prediction = model.predict(X_test_scaled)
        y_pred = np.argmax(prediction, axis=1)
        y_pred_labels = encoder_label.inverse_transform(y_pred)

        df = pd.read_csv("data/Clean_HCM.csv")
        df1 = df[(df['district'] == district) & (df['price level'] == y_pred_labels[0])]


        x_LN = df1.iloc[:, 1:12]
        Y_LN = df1.iloc[:, 0:1]
        # y_LN = np.array(Y_LN)
        data_encoded_LN = pd.get_dummies(x_LN, columns=['house_type', 'legal_status', 'street', 'ward','district'])
        scaler_LN = StandardScaler()
        X_scaled_LN = scaler_LN.fit_transform(data_encoded_LN)
        # Xu ly trong tap label

        X_train, X_test, y_train, y_test = train_test_split(X_scaled_LN, Y_LN, test_size=0.2, random_state=42)
        model_LN = LinearRegression()
        model_LN.fit(X_train, y_train)


        columns = ['house_type', 'acreage', 'width', 'length', 'bedrooms', 'bathrooms', 'floors','legal_status', 'street', 'ward', 'district']
        data_test_LN = pd.DataFrame([[house_type, acreage, width, length, bedrooms, bathrooms, floors,legal_status, street, ward, district]],columns=columns)
        dummy_columns_LN = data_encoded_LN.columns.tolist()
        data_test_encoded_LN = pd.get_dummies(data_test_LN, columns=['house_type', 'legal_status','street', 'ward', 'district'])
        for col in dummy_columns_LN:
            if col not in data_test_encoded_LN.columns:
                data_test_encoded_LN[col] = 0

        data_test_encoded_LN = data_test_encoded_LN[dummy_columns_LN]
        # print(data_test_encoded_LN)

        X_test_scaled_LN = scaler_LN.transform(data_test_encoded_LN)

        prediction = model_LN.predict(X_test_scaled_LN)
        price_range = utils.price_range(district,y_pred_labels[0])
        price_label = utils.vietnamese_label(y_pred_labels[0])

        return jsonify({'price':str(round(prediction[0][0],2)),
                        'price_level':price_label,
                        'price_range':price_range})

    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 400


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True,port=5001)