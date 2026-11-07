import os
from datetime import datetime
import pytz
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

def resolve_location(client_ip):
    """Dynamically resolves country and timezone via IP geolocation."""
    default_loc = {
        "country_name": "India",
        "country_code": "IN",
        "timezone": "Asia/Kolkata",
        "city": "Local Environment"
    }

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
        print(f"[Warn] IP lookup failed: {err}")

    return default_loc

def get_country_events(country_code, target_date):
    """Dynamically fetches official national holidays for any country and date."""
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
        print(f"[Warn] Nager.Date API error: {err}")

    return today_events, upcoming_events[:4]

def get_dynamic_observances(target_date):
    """
    Dynamically pulls all global observances, awareness days, and their
    encyclopedic descriptions for the current date directly from Wikipedia.
    """
    month = target_date.strftime("%m")
    day = target_date.strftime("%d")
    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/holidays/{month}/{day}"

    headers = {
        "User-Agent": "GlobalHolidayApp/2.0 (Flask-Production-Ready)"
    }

    observances = []

    try:
        resp = requests.get(url, headers=headers, timeout=4)
        if resp.status_code == 200:
            for item in resp.json().get("holidays", []):
                title = item.get("text", "")
                pages = item.get("pages", [])

                # Extract description and category dynamically from the linked article
                info = ""
                tag = "International Observance"

                if pages:
                    primary_page = pages[0]
                    info = primary_page.get("extract", "")
                    tag = primary_page.get("description", tag)

                # Fallback clean text if extract is missing
                if not info:
                    info = f"Commemorated internationally on {target_date.strftime('%B %d')}."

                observances.append({
                    "title": title,
                    "tag": tag,
                    "info": info
                })
    except Exception as err:
        print(f"[Warn] Dynamic Wikipedia feed error: {err}")

    return observances

@app.route("/")
def home():
    # 1. Resolve user's public IP
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if client_ip and "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()

    location = resolve_location(client_ip)

    # 2. Allow country parameter override (?country=US, ?country=DE, etc.)
    country_override = request.args.get("country", "").strip().upper()
    if country_override:
        location["country_code"] = country_override
        location["country_name"] = f"Country ({country_override})"

    # 3. Calculate timezone-aware local time
    try:
        local_tz = pytz.timezone(location["timezone"])
    except pytz.UnknownTimeZoneError:
        local_tz = pytz.UTC

    now_local = datetime.now(local_tz)

    # 4. Fetch national holidays and global observances dynamically
    today_events, upcoming_events = get_country_events(
        location["country_code"],
        now_local.date()
    )
    observances = get_dynamic_observances(now_local.date())

    return render_template(
        "home.html",
        location=location,
        local_date=now_local.strftime("%A, %B %d, %Y"),
        local_time=now_local.strftime("%I:%M:%S %p"),
        timezone=location["timezone"],
        today_events=today_events,
        observances=observances,
        upcoming_events=upcoming_events
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)