from datetime import datetime
import pytz
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

def get_client_location(client_ip):
    """
    Finds visitor country and timezone.
    Defaults to India on localhost / private networks.
    """
    if not client_ip or client_ip in ("127.0.0.1", "localhost", "::1", "0.0.0.0"):
        return {
            "country_name": "India",
            "country_code": "IN",
            "timezone": "Asia/Kolkata",
            "city": "Hyderabad (Local)"
        }

    try:
        res = requests.get(f"https://ipapi.co/{client_ip}/json/", timeout=4)
        if res.status_code == 200:
            data = res.json()
            if "country_code" in data:
                return {
                    "country_name": data.get("country_name", "Unknown Country"),
                    "country_code": data.get("country_code", "IN"),
                    "timezone": data.get("timezone", "UTC"),
                    "city": data.get("city", "Unknown City")
                }
    except Exception as e:
        print(f"Location lookup error: {e}")

    return {
        "country_name": "India",
        "country_code": "IN",
        "timezone": "Asia/Kolkata",
        "city": "Unknown"
    }

def fetch_country_holidays(country_code, target_date):
    """Fetches real-time holiday/festival data for the user's country."""
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
                h_date = item.get("date")
                h_info = {
                    "name": item.get("name"),
                    "local_name": item.get("localName"),
                    "date": h_date
                }
                if h_date == date_str:
                    today_holidays.append(h_info)
                elif h_date > date_str:
                    upcoming_holidays.append(h_info)
    except Exception as e:
        print(f"Holiday fetch error: {e}")

    return today_holidays, upcoming_holidays[:4]

@app.route("/")
def home():
    # Detect IP address
    user_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if user_ip and "," in user_ip:
        user_ip = user_ip.split(",")[0].strip()

    location = get_client_location(user_ip)

    # Allow testing other countries via URL: ?country=US or ?country=JP
    override_code = request.args.get("country", "").upper()
    if override_code:
        location["country_code"] = override_code
        location["country_name"] = override_code

    # Calculate current local time
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
    app.run(host="0.0.0.0", port=5000)