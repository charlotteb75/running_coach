

import os
from datetime import date
import requests


def get_access_token():
    response = requests.post(
        url=(
            "https://personal.connectapi.garmin.com/personalapitoken-service/personal-api/personal-api-key/token"
        ),
        headers={
            "Authorization": f"ApiKey {os.environ['GARMIN_API_KEY']}",
        },
        timeout=30,
    )
    response.raise_for_status()

    return response.text.strip()

def fetch_activities(token, start_date, end_date):
    """Return running activities for the period, across all result pages."""
    if start_date > end_date:
        raise ValueError("start_date must not be after end_date")

    activities = []
    start = 0

    while True:
        response = requests.get(
            url=(
                "https://personal.connectapi.garmin.com/activitylist-service/activities/search/activities"
            ),
            headers={"Authorization": f"Bearer {token}"},
            params={
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "activityType": "running",
                "start": start,
                "limit": 20,
            },
            timeout=30,
        )
        response.raise_for_status()
        page = response.json()
        if not isinstance(page, list) or any(not isinstance(item, dict) for item in page):
            raise ValueError("Garmin must return a list of activities")
        if not page:
            return activities

        activities.extend(page)
        start += len(page)
