from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json

url = "http://localhost:8086"
token = "Ms0Kij_URidvjZKgrYkLQHplYNAj1Ty70g7s7L7hXx1uFZusC1p-oaYff6w3HQ2XEbIrE6s0L5fIMx0X7jgvqA=="
org = "khalil"
bucket = "khalil"

with open("log.txt", "r") as file:
    line = file.readline().strip()
    if "frmPayload" in line and not line.startswith("{"):
        line = "{" + line.replace("frmPayload", "\"frmPayload\"") + "}"
        with open("log.txt", "w") as f:
            f.write(line)
    print("Formatted JSON:", line)
    data = json.loads(line)

values = data["frmPayload"].split(",")
temperature, pressure, altitude, humidity = map(int, values)

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

point = Point("sensor_data")
point.field("temperature", temperature)
point.field("pressure", pressure)
point.field("altitude", altitude)
point.field("humidity", humidity)

write_api.write(bucket=bucket, org=org, record=point)
client.close()