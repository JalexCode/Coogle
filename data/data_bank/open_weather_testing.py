import json

with open("open_weather.json", "r", encoding="utf-8") as f:
    weather_json = json.load(f)
    for i in range(len(weather_json["ID"])):
        print(weather_json["ID"][i], end=" | ")
        print(weather_json["Main"][i], end=" | ")
        print(weather_json["Description"][i], end=" | ")
        print(weather_json["Icon"][i])