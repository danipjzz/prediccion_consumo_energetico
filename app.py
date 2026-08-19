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
    data = request.form.to_dict()

    processed_data = {}
    for key, value in data.items():
      # Si la clave es la fecha o el valor tiene el formato de una fecha (ej: YYYY-MM-DD)
      if key.lower() in ["date", "fecha", "fechadia"] or (
          isinstance(value, str) and "-" in value and len(value) == 10
      ):
        processed_data[key] = value
      else:
        # Convertir campos numéricos de forma segura
        if isinstance(value, str):
          value = value.replace(",", ".")
        processed_data[key] = float(value) if value else 0.0

    df = pd.DataFrame([processed_data])

    # Asegúrate de buscar el nombre correcto de la columna de fecha que espera tu modelo
    # (Si en tu HTML el input se llama 'fecha', renómbralo a 'Date' para que coincida con tu ingeniería de características)
    if "fecha" in df.columns and "Date" not in df.columns:
      df["Date"] = df["fecha"]

    # 2. Replicar la ingeniería de características del Colab
    fecha = pd.to_datetime(df["Date"])
    df["Month"] = fecha.dt.month
    df["DayOfWeek"] = fecha.dt.dayofweek
    df["IsWeekend"] = (df["DayOfWeek"] >= 5).astype(int)
    df["IsWinter"] = df["Month"].isin([11, 12, 1, 2, 3]).astype(int)

    # Suma de horas de aparatos
    appliance_cols = [c for c in df.columns if "_hours" in c]
    df["Total_Appliance_Hours"] = df[appliance_cols].sum(axis=1)

    if "ElectricHeater_hours" in df.columns:
      df["Heater_Winter_Interaction"] = (
          df["ElectricHeater_hours"] * df["IsWinter"]
      )

    df = pd.get_dummies(df, columns=["Month", "DayOfWeek"], drop_first=True)

    model_features = model.feature_names_in_
    for col in model_features:
      if col not in df.columns:
        df[col] = 0
    df = df[model_features]

    pred_log = model.predict(df)
    pred_wh = float(np.expm1(pred_log)[0])

    return jsonify({"success": True, "prediction": round(pred_wh, 2)})

  except Exception as e:
    import traceback

    traceback.print_exc()
    return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)