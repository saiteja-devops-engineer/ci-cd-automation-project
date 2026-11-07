from datetime import datetime
import pytz
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

def get_client_location(client_ip):
    """
    Detects country, country code, and timezone via IP geolocation.
    Falls back to a default if run on localhost (127.0.0.1).
    """
    # If testing locally or private network, default to India or any ISO country code of choice
    if not client_ip or client_ip in ("127.0.0.1", "localhost", "::1"):
        return {
            "country_name": "India",
            "country_code": "IN",
            "timezone": "Asia/Kolkata",
            "city": "Default (Localhost)"
        }

    try:
        res = requests.get(f"https://ipapi.co/{client_ip}/json/", timeout=4)
        if res.status_code == 200:
            data = res.json()
            if "country_code" in data:
                return {
                    "country_name": data.get("country_name", "Unknown Country"),
                    "country_code": data.get("country_code", "US"),
                    "timezone": data.get("timezone", "UTC"),
                    "city": data.get("city", "Unknown City")
                }
    except Exception as e:
        print(f"Location lookup error: {e}")

    return {
        "country_name": "United States",
        "country_code": "US",
        "timezone": "America/New_York",
        "city": "Unknown"
    }

def fetch_country_holidays(country_code, target_date):
    """
    Fetches the holiday list from the free open-source Nager.Date API
    for the user's specific country and year.
    """
    year = target_date.year
    date_str = target_date.strftime("%Y-%m-%d")
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"

    today_holidays = []
    upcoming_holidays = []

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            all_holidays = response.json()

            for item in all_holidays:
                holiday_date = item.get("date")
                holiday_data = {
                    "name": item.get("name"),
                    "local_name": item.get("localName"),
                    "date": holiday_date,
                    "types": item.get("types", [])
                }

                if holiday_date == date_str:
                    today_holidays.append(holiday_data)
                elif holiday_date > date_str:
                    upcoming_holidays.append(holiday_data)

    except Exception as e:
        print(f"Holiday API fetch error: {e}")

    return today_holidays, upcoming_holidays[:3]  # Return today's + next 3 upcoming

@app.route("/")
def home():
    # Detect the visitor's real IP address (supporting proxies/load balancers)
    user_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if user_ip and "," in user_ip:
        user_ip = user_ip.split(",")[0].strip()

    # Manual country override via ?country=US or ?country=IN for easy testing
    override_code = request.args.get("country", "").upper()

    location = get_client_location(user_ip)
    if override_code:
        location["country_code"] = override_code
        location["country_name"] = f"Country ({override_code})"

    # Calculate exact local time in the user's timezone
    try:
        user_tz = pytz.timezone(location["timezone"])
    except pytz.UnknownTimeZoneError:
        user_tz = pytz.UTC

    now_local = datetime.now(user_tz)
    today_holidays, upcoming = fetch_country_holidays(location["country_code"], now_local.date())

    return render_template(
        "home.html",
        location=location,
        local_date_str=now_local.strftime("%A, %B %d, %Y"),
        local_time_str=now_local.strftime("%I:%M:%S %p"),
        timezone=location["timezone"],
        today_holidays=today_holidays,
        upcoming_holidays=upcoming
    )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)