import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

# Dữ liệu mẫu (giả lập, thêm house_type và legal_status)
data = pd.read_csv("./data/Clean_HCM.csv", encoding= "utf-8")

df = pd.DataFrame(data)

# Tạo một Pipeline với One-Hot Encoding cho các cột categorical
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['district', 'ward', 'street', 'house_type', 'legal_status']),
    ],
    remainder='passthrough'
)

# Áp dụng One-Hot Encoding và training model
X_encoded = preprocessor.fit_transform(df[["district", "ward", "street", "house_type", "legal_status", "width", "length", "bedrooms", "bathrooms", "floors"]])

# Train mô hình
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_encoded, df['price'])

# Lưu mô hình và preprocessor
joblib.dump(model, 'data/trained_model.pkl')
joblib.dump(preprocessor, 'data/preprocessor.pkl')
