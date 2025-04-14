import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib

# Dữ liệu mẫu (giả lập, thêm house_type và legal_status)
data = pd.read_csv("./data/6_quan.csv", encoding= "utf-8")

df = pd.DataFrame(data)

# Mã hóa các cột categorical
le_district = LabelEncoder()
le_ward = LabelEncoder()
le_street = LabelEncoder()
le_house_type = LabelEncoder()
le_legal_status = LabelEncoder()

df['district'] = le_district.fit_transform(df['district'])
df['ward'] = le_ward.fit_transform(df['ward'])
df['street'] = le_street.fit_transform(df['street'])
df['house_type'] = le_house_type.fit_transform(df['house_type'])
df['legal_status'] = le_legal_status.fit_transform(df['legal_status'])

# Chuẩn bị dữ liệu train
X = df[["house_type","width", "length", "bedrooms", "bathrooms", "floors", "legal_status", "street", "ward", "district"]]
y = df['price']

# Train mô hình
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Lưu mô hình và các encoder
joblib.dump(model, 'data/trained_model.pkl')
joblib.dump(le_district, 'data/le_district.pkl')
joblib.dump(le_ward, 'data/le_ward.pkl')
joblib.dump(le_street, 'data/le_street.pkl')
joblib.dump(le_house_type, 'data/le_house_type.pkl')
joblib.dump(le_legal_status, 'data/le_legal_status.pkl')