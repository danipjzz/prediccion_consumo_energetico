import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request
import os

app = Flask(__name__)

# Cargar el modelo entrenado al iniciar el servidor
model = joblib.load("modelo_rf_consumo.pkl")


@app.route("/")
def home():
  # Renderiza tu formulario HTML ubicado en la carpeta 'templates'
  return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
  try:
    # 1. Obtener los datos enviados desde el formulario
    data = request.form.to_dict()

    # Convertir los valores numéricos a float/int según corresponda
    processed_data = {}
    for key, value in data.items():
      if key == "Date":
        processed_data[key] = value
      else:
        processed_data[key] = float(value) if value else 0.0

    df = pd.DataFrame([processed_data])

    # 2. Replicar la ingeniería de características del Colab
    fecha = pd.to_datetime(df["Date"])
    df["Month"] = fecha.dt.month
    df["DayOfWeek"] = fecha.dt.dayofweek
    df["IsWeekend"] = (df["DayOfWeek"] >= 5).astype(int)
    df["IsWinter"] = df["Month"].isin([11, 12, 1, 2, 3]).astype(int)

    # Suma de horas de aparatos (columnas que terminan o contienen '_hours')
    appliance_cols = [c for c in df.columns if "_hours" in c]
    df["Total_Appliance_Hours"] = df[appliance_cols].sum(axis=1)

    if "ElectricHeater_hours" in df.columns:
      df["Heater_Winter_Interaction"] = (
          df["ElectricHeater_hours"] * df["IsWinter"]
      )

    # One-hot encoding para Month y DayOfWeek
    df = pd.get_dummies(df, columns=["Month", "DayOfWeek"], drop_first=True)

    # Asegurar que las columnas coincidan exactamente con las que usó el modelo
    # (Si el modelo espera columnas específicas que faltan por el one-hot, se rellenan con 0)
    model_features = model.feature_names_in_
    for col in model_features:
      if col not in df.columns:
        df[col] = 0
    df = df[model_features]

    # 3. Predecir (aplicando expm1 para revertir el log1p del entrenamiento)
    pred_log = model.predict(df)
    pred_wh = float(np.expm1(pred_log)[0])

    return jsonify({"success": True, "prediction": round(pred_wh, 2)})

  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)