from influxdb_client import InfluxDBClient
import pandas as pd
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_ORG = "khalil"
INFLUXDB_BUCKET = "khalil"
FROM_EMAIL = "bensassiahmedkhalil@gmail.com"
TO_EMAILS = [
    "frajj2751@gmail.com",
    "bensassiahmedkhalilpro@gmail.com"
]

client = InfluxDBClient(url=INFLUXDB_URL, token="YOUR_INFLUXDB_TOKEN", org=INFLUXDB_ORG)
query_api = client.query_api()

query = f'''
from(bucket: "{INFLUXDB_BUCKET}")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "SmartWeather")
  |> filter(fn: (r) => r["_field"] == "altitude" or r["_field"] == "humidity" or r["_field"] == "pressure" or r["_field"] == "temperature")
'''

try:
    result = query_api.query(query)
    raw_data = {'time': [], 'temperature': [], 'humidity': [], 'pressure': [], 'altitude': []}

    for table in result:
        field_name = table.records[0].get_field()
        for record in table.records:
            time_val = record.get_time()
            value = record.get_value()
            if field_name == 'temperature':
                raw_data['time'].append(time_val)
            if field_name in raw_data:
                raw_data[field_name].append(value)

    df = pd.DataFrame(raw_data)
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')
    df.set_index('time', inplace=True)
    hourly_avg = df.resample('1H').mean().dropna()
    latest_avg = hourly_avg.iloc[-1]
    last_raw_value = df.iloc[-1]

    weights = {
        'humidity': 0.4,
        'pressure_change': 0.3,
        'temperature': 0.1,
        'humidity_change': 0.2,
        'altitude': 0.1
    }

    baseline_pressure = 1013.0
    hourly_avg['pressure_calibrated'] = hourly_avg['pressure'] - baseline_pressure
    pressure_change = hourly_avg['pressure_calibrated'].diff().iloc[-1] / 100
    altitude_effect = max(latest_avg['altitude'], 0) / 1000
    humidity_change = hourly_avg['humidity'].diff().iloc[-1]

    rain_score = (
        weights['humidity'] * latest_avg['humidity'] +
        weights['pressure_change'] * pressure_change +
        weights['temperature'] * (30 - latest_avg['temperature']) +
        weights['humidity_change'] * humidity_change +
        weights['altitude'] * altitude_effect
    )

    if rain_score > 50:
        rain_prediction = "HIGH CHANCE OF RAIN! 🌧️"
    elif rain_score > 30:
        rain_prediction = "Moderate chance of rain. 🌦️"
    else:
        rain_prediction = "Low chance of rain. ☀️"

    email_subject = f"🌧️ Rain Prediction: {rain_prediction}"
    email_content = f"""
    <html>
    <body>
        <h2>Rain Prediction: {rain_prediction}</h2>
        <p>Here's your daily weather update:</p>
        <h3>Last Raw Value in Dataset:</h3>
        <ul>
            <li><strong>Temperature:</strong> {last_raw_value['temperature']}°C</li>
            <li><strong>Humidity:</strong> {last_raw_value['humidity']}%</li>
            <li><strong>Pressure:</strong> {last_raw_value['pressure']} hPa</li>
            <li><strong>Altitude:</strong> {last_raw_value['altitude']} m</li>
        </ul>
        <h3>Rain Score Calculation:</h3>
        <ul>
            <li><strong>Humidity Contribution:</strong> {weights['humidity']} * {latest_avg['humidity']:.2f} = {weights['humidity'] * latest_avg['humidity']:.2f}</li>
            <li><strong>Pressure Change Contribution:</strong> {weights['pressure_change']} * {pressure_change:.2f} = {weights['pressure_change'] * pressure_change:.2f}</li>
            <li><strong>Temperature Contribution:</strong> {weights['temperature']} * (30 - {latest_avg['temperature']:.2f}) = {weights['temperature'] * (30 - latest_avg['temperature']):.2f}</li>
            <li><strong>Humidity Change Contribution:</strong> {weights['humidity_change']} * {humidity_change:.2f} = {weights['humidity_change'] * humidity_change:.2f}</li>
            <li><strong>Altitude Contribution:</strong> {weights['altitude']} * ({max(latest_avg['altitude'], 0):.2f} / 1000) = {weights['altitude'] * altitude_effect:.2f}</li>
        </ul>
        <p><strong>Total Rain Score:</strong> {rain_score:.2f}</p>
        <p>Stay prepared and have a great day!</p>
    </body>
    </html>
    """

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAILS,
        subject=email_subject,
        html_content=email_content
    )

    sg = SendGridAPIClient("YOUR_SENDGRID_API_KEY")
    response = sg.send(message)
    print(f"Email sent! Status code: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")

finally:
    client.close()
