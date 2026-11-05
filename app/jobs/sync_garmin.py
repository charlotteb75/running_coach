

from app.schemas.database_schemas import RunningHistoryImport
from app.services.garmin import fetch_activities, get_access_token


def normalize_activity(activity):
    normalized_activity = {
        "run_date": activity["startTimeLocal"],
        "run_distance": activity["distance"],
        "run_time": activity["duration"],
        "bpm": activity["averageHR"],
        "elevation": activity["elevationGain"]
    }
    return normalized_activity

def sync_garmin_job():
    token = get_access_token()
    activities = fetch_activities(token, start_date, end_date)

    for activity in activities:
        run_data = normalize_activity(activity)

        validated_run = RunningHistoryImport.model_validate(run_data)
        values = validated_run.model_dump()