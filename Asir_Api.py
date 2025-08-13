from flask import Flask, request, jsonify
import pickle
import pandas as pd
from datetime import timedelta

# تحميل النموذج
with open('model_daily.pkl', 'rb') as f:
    model, بلدية_الخريطة = pickle.load(f)

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    البلدية = data.get('البلدية')
    start_date = pd.to_datetime(data.get('start_date'))
    period = data.get('period', 'day')  # day / month / year

    if البلدية not in بلدية_الخريطة:
        return jsonify({"error": "البلدية غير موجودة"}), 400

    البلدية_كود = بلدية_الخريطة[البلدية]

    if period == 'day':
        dates = [start_date]
    elif period == 'month':
        dates = [start_date + timedelta(days=i) for i in range(30)]
    elif period == 'year':
        dates = [start_date + timedelta(days=i) for i in range(365)]
    else:
        return jsonify({"error": "نوع الفترة غير مدعوم"}), 400

    total_prediction = 0
    for d in dates:
        X_new = pd.DataFrame([[البلدية_كود, d.year, d.month, d.day]],
                             columns=['البلدية_كود', 'السنة', 'الشهر', 'اليوم'])
        total_prediction += model.predict(X_new)[0]

    return jsonify({
        "البلدية": البلدية,
        "الفترة": period,
        "بداية_التاريخ": start_date.strftime('%Y-%m-%d'),
        "التوقع": round(total_prediction)
    })

if __name__ == '__main__':
    app.run(debug=True)
