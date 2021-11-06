import requests, csv, datetime
import pandas as pd
from geopy.geocoders import Nominatim

class getLocationWeather:
    def __init__(self, location):
        bearings = self.get_latitude_longitude(location)
        startDate, endDate = self.get_date()
        self.weather_data(bearings, startDate, endDate)

    def get_latitude_longitude(self, location):
        geolocator = Nominatim(user_agent="my_user_agent")
        city, country = location, "Uk"
        loc = geolocator.geocode(city+','+ country)
        return str(loc.latitude)+(", ")+(str(loc.longitude))

    def get_date(self):
        start, end = datetime.date.today() + datetime.timedelta(days=1), datetime.date.today() + datetime.timedelta(days=2) 
        start.strftime("%y-%m-%d")
        end.strftime("%y-%m-%d")
        startDate = str(start) +("T00:00:00Z")
        endDate = str(end) +("T00:00:00Z")
        return startDate, endDate

    
    def weather_data(self, bearings, startDate, endDate):
        try:
            url = "https://api.tomorrow.io/v4/timelines"
            querystring = {
            "location": bearings,
            "fields":["temperature", "temperatureApparent",
                      "cloudCover", "windSpeed",
                      "humidity", "precipitationProbability",
                      "precipitationIntensity"],
            "units":"metric",
            "startTime": startDate,
            "endTime": endDate,
            "timesteps":"1h",
            "apikey":"m5BPieS2MSYpYkAgqjUOApSPd5k7Tyqm"}
            response = requests.request("GET", url, params=querystring)
            results = response.json()["data"]["timelines"][0]["intervals"]
            self.time = 0
            for daily_result in results:
                if self.time >= 6 and self.time <= 19:
                    self.date = daily_result["startTime"][0:10]
                    self.temp = round(daily_result["values"]["temperature"])
                    self.tempApp = round(daily_result["values"]["temperatureApparent"])
                    self.cloudCover = daily_result["values"]["cloudCover"]
                    self.windSpeed = daily_result["values"]["windSpeed"]
                    self.humidity = daily_result["values"]["humidity"]
                    self.precipitationProbability = daily_result["values"]["precipitationProbability"]
                    self.precipitationIntensity = daily_result["values"]["precipitationIntensity"]
                    self.day = (datetime.date.today()+datetime.timedelta(days=1)).strftime('%A')
                    self.save_data()
                if self.time == 23: self.time = 0
                else: self.time += 1
                

        except:
            raise Exception("Please check that your connected to the internet")
        
    def save_data(self):
        try:
            valueForToday = False
            with open("App_Package/saved_data/weatherData.csv", "r", newline="") as csvfile:
                index = -1
                reader = csv.reader(csvfile)
                for i in reader:
                    index += 1
                    if i[0] == self.date and self.time == int(i[2]):
                        valueForToday = True
                        break
            if valueForToday == False:
                with open("App_Package/saved_data/weatherData.csv", "a", newline="") as csvfile:
                    fieldnames = ["Date", "Day", "Time","temperature", "temperatureApparent",
                      "cloudCover", "windSpeed",
                      "humidity", "precipitationProbability",
                      "precipitationIntensity"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({"Date": self.date,
                                     "Day": self.day,
                                     "Time": self.time,
                                     "temperature": self.temp,
                                     "temperatureApparent": self.tempApp,
                                     "cloudCover": self.cloudCover,
                                     "windSpeed": self.windSpeed,
                                     "humidity": self.humidity,
                                     "precipitationProbability": self.precipitationProbability,
                                     "precipitationIntensity": self.precipitationIntensity})

        except:
            with open("App_Package/saved_data/weatherData.csv", "w+", newline="") as csvfile:
                fieldnames = ["Date", "Day","Time","temperature", "temperatureApparent",
                      "cloudCover", "windSpeed",
                      "humidity", "precipitationProbability",
                      "precipitationIntensity"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            self.save_data()

