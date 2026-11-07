import os
import re
from datetime import datetime
import pytz
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

GLOBAL_KEYWORDS = [
    "world", "international", "global", "universal", "earth",
    "united nations", "un ", "worldwide"
]

def resolve_location(client_ip):
    """Dynamically resolves country and timezone via IP geolocation."""
    default_loc = {
        "country_name": "India",
        "country_code": "IN",
        "timezone": "Asia/Kolkata",
        "city": "Hyderabad (Local)"
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
    """Dynamically fetches official national holidays for the user's country."""
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

def get_dynamic_observances(target_date, user_country_name):
    """
    Pulls observances from Wikipedia and categorizes them:
    - Retains: User country days & International days
    - Excludes: Other specific countries' holidays
    """
    month = target_date.strftime("%m")
    day = target_date.strftime("%d")
    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/holidays/{month}/{day}"
    headers = {"User-Agent": "GlobalHolidayApp/2.0 (Flask-Production-Ready)"}

    country_days = []
    international_days = []
    user_country_lower = user_country_name.lower()

    try:
        resp = requests.get(url, headers=headers, timeout=4)
        if resp.status_code == 200:
            for item in resp.json().get("holidays", []):
                title = item.get("text", "")
                pages = item.get("pages", [])

                info = ""
                tag = "International Observance"

                if pages:
                    primary_page = pages[0]
                    info = primary_page.get("extract", "")
                    tag = primary_page.get("description", tag)

                if not info:
                    info = f"Observed on {target_date.strftime('%B %d')}."

                search_corpus = f"{title} {tag} {info}".lower()

                # 1. User country match
                if user_country_lower in search_corpus:
                    country_days.append({
                        "title": title,
                        "tag": f"{user_country_name} Observance",
                        "info": info,
                        "is_local": True
                    })
                    continue

                # 2. International match
                is_global = any(k in search_corpus for k in GLOBAL_KEYWORDS)
                is_foreign_country = bool(re.search(
                    r"\b(in|of|for)\s+(the\s+)?(united states|us|uk|canada|australia|germany|france|japan|china|cambodia|el salvador|brazil|mexico|italy|russia|poland|finland|sweden|norway)\b",
                    search_corpus
                ))

                if is_global and not is_foreign_country:
                    international_days.append({
                        "title": title,
                        "tag": "International Day",
                        "info": info,
                        "is_local": False
                    })
    except Exception as err:
        print(f"[Warn] Dynamic Wikipedia feed error: {err}")

    # Prioritize user's country first, then international days
    return country_days + international_days

@app.route("/")
def home():
    # 1. Resolve user's public IP
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if client_ip and "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()

    location = resolve_location(client_ip)

    # 2. Country query override (?country=US, ?country=IN, etc.)
    country_override = request.args.get("country", "").strip().upper()
    country_names = {
        "IN": "India", "US": "United States", "GB": "United Kingdom",
        "JP": "Japan", "DE": "Germany", "FR": "France", "CA": "Canada"
    }
    if country_override:
        location["country_code"] = country_override
        location["country_name"] = country_names.get(country_override, f"Country ({country_override})")

    # 3. Calculate timezone-aware local time
    try:
        local_tz = pytz.timezone(location["timezone"])
    except pytz.UnknownTimeZoneError:
        local_tz = pytz.UTC

    now_local = datetime.now(local_tz)

    # 4. Fetch national holidays and filtered observances
    today_events, upcoming_events = get_country_events(
        location["country_code"],
        now_local.date()
    )

    filtered_observances = get_dynamic_observances(
        now_local.date(),
        location["country_name"]
    )

    return render_template(
        "home.html",
        location=location,
        local_date=now_local.strftime("%A, %B %d, %Y"),
        local_time=now_local.strftime("%I:%M:%S %p"),
        timezone=location["timezone"],
        today_events=today_events,
        observances=filtered_observances,
        upcoming_events=upcoming_events
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)