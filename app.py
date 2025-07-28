from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# Simulated dataset and model training
def train_model():
    data = {
        'Day': ['Monday', 'Saturday', 'Sunday', 'Wednesday'],
        'Season': ['Summer', 'Winter', 'Monsoon', 'Summer'],
        'Temperature': [35, 15, 25, 40],
        'Households': [100, 100, 100, 100],
        'ElectricityUsage': [500, 300, 400, 600]
    }
    df = pd.DataFrame(data)

    # Define all possible categories for Day and Season
    all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    all_seasons = ['Summer', 'Winter', 'Monsoon']

    # Initialize LabelEncoders with all possible categories
    day_encoder = LabelEncoder()
    season_encoder = LabelEncoder()
    day_encoder.fit(all_days)  # Train encoder on all days
    season_encoder.fit(all_seasons)  # Train encoder on all seasons

    # Encode the dataset
    df['Day'] = day_encoder.transform(df['Day'])
    df['Season'] = season_encoder.transform(df['Season'])

    # Features and target
    X = df[['Day', 'Season', 'Temperature', 'Households']]
    y = df['ElectricityUsage']

    # Train the model
    model = LinearRegression()
    model.fit(X, y)

    return model, day_encoder, season_encoder

model, day_encoder, season_encoder = train_model()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Log incoming request
        print("Received request:", request.json)

        # Parse input data
        data = request.json
        day = data.get('day')
        season = data.get('season')
        temperature = float(data.get('temperature'))
        households = int(data.get('households'))

        # Input validation
        errors = []
        if day not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            errors.append("Invalid day. Choose from Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, or Sunday.")
        if season not in ['Summer', 'Winter', 'Monsoon']:
            errors.append("Invalid season. Choose from Summer, Winter, or Monsoon.")
        if not (0 <= temperature <= 50):  # Realistic temperature range: 0°C to 50°C
            errors.append("Temperature must be between 0°C and 50°C.")
        if not (1 <= households <= 1000):  # Realistic household range: 1 to 1000
            errors.append("Number of households must be between 1 and 1000.")

        if errors:
            return jsonify({'error': errors}), 400  # Return error with HTTP status 400 (Bad Request)

        print(f"Day: {day}, Season: {season}, Temperature: {temperature}, Households: {households}")

        # Encode inputs using the pre-trained encoders
        day_encoded = day_encoder.transform([day])[0]
        season_encoded = season_encoder.transform([season])[0]

        # Predict electricity usage
        prediction = model.predict([[day_encoded, season_encoded, temperature, households]])[0]
        predicted_usage_kwh = round(prediction, 2)

        # Calculate cost (₹5/kWh or $0.12/kWh)
        electricity_rate = 5  # Example rate in ₹/kWh
        total_cost = round(predicted_usage_kwh * electricity_rate, 2)

        # Appliance usage equivalents
        fan_hours = round(predicted_usage_kwh / 0.075, 1)  # A fan consumes ~75 watts (0.075 kWh)
        bulb_hours = round(predicted_usage_kwh / 0.01, 1)  # A bulb consumes ~10 watts (0.01 kWh)
        fridge_hours = round(predicted_usage_kwh / 0.2, 1)  # A fridge consumes ~200 watts (0.2 kWh)

        # Return result
        return jsonify({
            'predicted_usage_kwh': predicted_usage_kwh,
            'total_cost': total_cost,
            'appliance_usage': {
                'fan_hours': fan_hours,
                'bulb_hours': bulb_hours,
                'fridge_hours': fridge_hours
            }
        })

    except Exception as e:
        # Log and return errors
        print("Error:", str(e))
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    import sys
    app.run(debug=True)
    sys.exit(0)
