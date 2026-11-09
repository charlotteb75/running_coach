

from datetime import datetime

from app.models import RunningHistory
from app.extensions import db
from app.schemas.database_schemas import RunningHistoryImport
from app.services.garmin import fetch_activities, get_access_token


def normalize_activity(activity):
    normalized_activity = {
        "id_garmin_activity": activity["activityId"],
        "run_date": datetime.fromisoformat(activity["startTimeLocal"]).date(),
        "run_distance": activity["distance"],
        "run_time": activity["duration"],
        "bpm": activity["averageHR"],
        "elevation": activity["elevationGain"]
    }
    return normalized_activity

def sync_garmin_job(start_date, end_date):
    token = get_access_token()
    activities = fetch_activities(token, start_date, end_date)
    validated_activities = []

    for activity in activities:
        run_data = normalize_activity(activity) 

        validated_run = RunningHistoryImport.model_validate(run_data)
        validated_activities.append(validated_run)

    try:
        for activity in validated_activities:
            existing_run = db.session.scalar(
                db.select(RunningHistory).where(
                    RunningHistory.id_garmin_activity
                    == activity.id_garmin_activity
                )
            )
            if existing_run is None:
                running_history_obj = RunningHistory(**activity.model_dump())
                db.session.add(running_history_obj)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
