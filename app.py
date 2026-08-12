import os
from typing import Optional, cast

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Request, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from geopy.geocoders import Nominatim
from geopy.location import Location

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class Weather:
    def __init__(self, condition, temp, feels_like):
        self.condition = condition
        self.temp = temp
        self.feels_like = feels_like

    def format(self):
        return {
            "Condition": self.condition,
            "temp": self.temp,
            "feels_like": self.feels_like,
        }


def geo_data(city: str) -> Optional[Location]:
    # Initalizes the Nominatim tool so that we can find the geolocation of a place (lat, long)
    geolocator = Nominatim(user_agent="my_weather_app")

    # Uses the geopy library to get the latitude and longitude of the location the user enterd
    # Casts the return value to Location | None instead of Coroutine. This satisfies type checker.
    return cast(Optional[Location], geolocator.geocode(city))


def get_weather_data(lat, lon):
    load_dotenv(dotenv_path=".env")
    # Calls the weather API using the request library
    return requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=imperial&appid={os.getenv('OPEN_WEATHER_API_KEY')}"
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
    try:
        location: Optional[Location] = geo_data(city)
        if location is None:
            return templates.TemplateResponse(
                request,
                "index.html",
                {
                    "weather": None,
                    "error": f"'{city}' Note Found",
                },
            )

        lat, lon = location.latitude, location.longitude

        weather_data = get_weather_data(lat, lon)

        if weather_data.status_code != 200:
            return templates.TemplateResponse(
                request,
                "index.html",
                {
                    "weather": None,
                    "error": f"API could not find '{city}'",
                },
            )

        condition = weather_data.json()["weather"][0]["main"]
        temp = weather_data.json()["main"]["temp"]
        feels_like = weather_data.json()["main"]["feels_like"]
        error = None

        weather = Weather(condition, temp, feels_like)
        return templates.TemplateResponse(request, "index.html", {"weather": weather.format(), "error": None})

    except ValueError as e:
        print(e)
