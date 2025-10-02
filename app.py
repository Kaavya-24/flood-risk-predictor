from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler, LabelEncoder

app = Flask(__name__)

# -------------------------------
# Load dataset and model
# -------------------------------
df = pd.read_csv("flood_risk_dataset_india.csv")
df.columns = df.columns.str.strip()  # remove extra spaces

# Identify categorical features
categorical_features = ['Land Cover', 'Soil Type']

# Encode categorical features
le_dict = {}
for col in categorical_features:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    le_dict[col] = le

# Define feature columns used by the model (13 features)
feature_columns = [
    'Latitude', 'Longitude', 'Rainfall (mm)', 'Temperature (°C)', 'Humidity (%)',
    'River Discharge (m³/s)', 'Water Level (m)', 'Elevation (m)',
    'Land Cover', 'Soil Type', 'Population Density', 'Infrastructure', 'Historical Floods'
]

# Separate features for scaling
numeric_features = [
    'Latitude', 'Longitude', 'Rainfall (mm)', 'Temperature (°C)', 'Humidity (%)',
    'River Discharge (m³/s)', 'Water Level (m)', 'Elevation (m)',
    'Population Density', 'Infrastructure', 'Historical Floods'
]

scaler = StandardScaler().fit(df[numeric_features])

# Load pre-trained RandomForest model
model = joblib.load("flood_model.joblib")


# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    try:
        input_values = []

        for col in feature_columns:
            if col in categorical_features:
                # Check for valid categorical input
                if data[col] not in le_dict[col].classes_:
                    return jsonify({"error": f"Invalid value '{data[col]}' for {col}"})
                input_values.append(int(le_dict[col].transform([data[col]])[0]))
            else:
                input_values.append(float(data[col]))

        X_new = np.array([input_values])

        # Scale numeric features only
        X_new_scaled = X_new.copy()
        X_new_scaled[:, [df.columns.get_loc(f) for f in numeric_features]] = scaler.transform(
            X_new[:, [df.columns.get_loc(f) for f in numeric_features]]
        )

        prediction = model.predict(X_new_scaled)[0]
        proba = model.predict_proba(X_new_scaled)[0][prediction]

        return jsonify({
            "prediction": "Yes" if prediction == 1 else "No",
            "probability": round(float(proba), 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
