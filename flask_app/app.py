import os
from datetime import datetime
import pytz
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

def resolve_location(client_ip):
    """Detects visitor country code and timezone via IP geolocation."""
    default_loc = {
        "country_name": "India",
        "country_code": "IN",
        "timezone": "Asia/Kolkata",
        "city": "Hyderabad (Local)"
    }

    # When testing locally, IP is 127.0.0.1 or localhost; skip external API
    if not client_ip or client_ip in ("127.0.0.1", "localhost", "::1"):
        return default_loc

    try:
        res = requests.get(f"https://ipapi.co/{client_ip}/json/", timeout=3)
        if res.status_code == 200:
            data = res.json()
            if data.get("country_code"):
                return {
                    "country_name": data.get("country_name", "Unknown Country"),
                    "country_code": data.get("country_code", "IN"),
                    "timezone": data.get("timezone", "UTC"),
                    "city": data.get("city", "Unknown City")
                }
    except Exception as err:
        print(f"[Warn] IP geolocation failed: {err}")

    return default_loc

def get_country_events(country_code, target_date):
    """Fetches real-time holiday/observance data from public API."""
    year = target_date.year
    formatted_date = target_date.strftime("%Y-%m-%d")
    api_url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"

    today_events = []
    upcoming_events = []

    try:
        resp = requests.get(api_url, timeout=4)
        if resp.status_code == 200:
            for ev in resp.json():
                ev_date = ev.get("date")
                event_obj = {
                    "name": ev.get("name"),
                    "local_name": ev.get("localName"),
                    "date": ev_date
                }
                if ev_date == formatted_date:
                    today_events.append(event_obj)
                elif ev_date > formatted_date:
                    upcoming_events.append(event_obj)
    except Exception as err:
        print(f"[Warn] Holiday API lookup failed: {err}")

    return today_events, upcoming_events[:4]

@app.route("/")
def home():
    # 1. Determine user's real public IP
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if client_ip and "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()

    location = resolve_location(client_ip)

    # 2. Support optional manual query string override: /?country=US
    country_override = request.args.get("country", "").strip().upper()
    if country_override:
        location["country_code"] = country_override
        location["country_name"] = f"Country ({country_override})"

    # 3. Calculate timezone-aware local date and time
    try:
        local_tz = pytz.timezone(location["timezone"])
    except pytz.UnknownTimeZoneError:
        local_tz = pytz.UTC

    now_local = datetime.now(local_tz)
    today_events, upcoming_events = get_country_events(
        location["country_code"],
        now_local.date()
    )

    return render_template(
        "home.html",
        location=location,
        local_date=now_local.strftime("%A, %B %d, %Y"),
        local_time=now_local.strftime("%I:%M:%S %p"),
        timezone=location["timezone"],
        today_events=today_events,
        upcoming_events=upcoming_events
    )

if __name__ == "__main__":
    # Host 0.0.0.0 is mandatory for Docker port forwarding to work
    app.run(host="0.0.0.0", port=5000, debug=False)