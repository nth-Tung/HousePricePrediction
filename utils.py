import pandas as pd

df = pd.read_csv("data/q1q2.csv")
def filter(district):
    q1 = None
    q2 = None
    for index, row in df.iterrows():
        if district.strip().lower() == row['Quan'].strip().lower():
            q1 = row['Q1']
            q2 = row['Q2']
            break
    return q1, q2

def price_range(district, price_level):
    q1,q2 = filter(district)
    if price_level == 'thap':
        return f"Dưới {q1} tỷ VND"
    elif price_level == 'trung binh':
        return  f"Trong khoảng {q1} - {q2} tỷ VND"
    else:
        return  f"Trên {q2} tỷ VND"

def vietnamese_label(price_level):
    if price_level == 'thap':
        return "Thấp"
    elif price_level == 'trung binh':
        return "Trung bình"
    else:
        return "Cao"