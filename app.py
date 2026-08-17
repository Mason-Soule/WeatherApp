import os
from typing import Optional, cast

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class Weather:
    def __init__(self, weather_data, city):
        self.favorites = []
        self.weather = weather_data
        self.city = city
        self.condition = weather_data.json()["weather"][0]["main"]
        self.temp = weather_data.json()["main"]["temp"]
        self.feels_like = weather_data.json()["main"]["feels_like"]
        self.humidity = weather_data.json()["main"]["humidity"]

    def format(self):
        return {
            "city": self.city,
            "condition": self.condition,
            "temp": self.temp,
            "feels_like": self.feels_like,
            "humidity": self.humidity,
        }

    def favorite(self, city):
        self.favorites.append(city)


def get_weather_data(city):

    load_dotenv(dotenv_path=".env")
    # Calls the weather API using the request library
    return requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid={os.getenv('OPEN_WEATHER_API_KEY')}"
    )


# Gets the initial state of the page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"weather": None, "error": None},
    )


@app.post("/get-weather", response_class=HTMLResponse)
def get_weather(request: Request, city: str = Form(...)):
    # Using the dotenv library I can create the path to my file so that I can access my API key
    # When I need it
    weather_data = get_weather_data(city)

    if weather_data.status_code != 200:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "weather": None,
                "error": f"API could not find '{city}'",
            },
        )

    weather = Weather(weather_data, city)
    return templates.TemplateResponse(
        request, "index.html", {"weather": weather.format(), "error": None}
    )