from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Load the model and scaler
with open('rf_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# Feature names after preprocessing
feature_names = [
    'network_packet_size', 'login_attempts', 'session_duration', 'ip_reputation_score',
    'failed_logins', 'unusual_time_access', 'protocol_type_TCP', 'protocol_type_UDP',
    'encryption_used_DES', 'browser_type_Edge', 'browser_type_Firefox', 'browser_type_Safari', 'browser_type_Unknown'
]

# Categorical mappings (based on drop_first=True)
protocol_types = ['TCP', 'UDP']  # Assuming first is dropped, e.g., 'ICMP'
encryption_useds = ['DES']  # Assuming first is dropped, e.g., 'AES'
browser_types = ['Edge', 'Firefox', 'Safari', 'Unknown']  # Assuming first is dropped, e.g., 'Chrome'

def preprocess_input(data):
    # Convert to DataFrame
    df = pd.DataFrame([data])
    
    # Fill missing in encryption_used with mode (assuming 'AES' as mode, but from code it's mode of column)
    # For simplicity, fill with 'AES' if missing, but actually need to compute mode from training data
    # Since we don't have it, assume 'AES' is the mode
    df['encryption_used'] = df['encryption_used'].fillna('AES')
    
    # One-hot encode
    df = pd.get_dummies(df, columns=['protocol_type', 'encryption_used', 'browser_type'], drop_first=True)
    
    # Ensure all dummy columns are present
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0
    
    # Reorder columns to match feature_names
    df = df[feature_names]
    
    # Scale
    scaled = scaler.transform(df)
    
    return scaled

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        processed = preprocess_input(data)
        prediction = model.predict(processed)[0]
        probability = model.predict_proba(processed)[0].tolist()
        return jsonify({'prediction': int(prediction), 'probability': probability})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
