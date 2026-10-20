


from flask import Blueprint
from sqlalchemy import Date, cast, func
from app.models import RunningHistory
from app.extensions import db

running_history_bp = Blueprint("running_history", __name__)


@running_history_bp.get("/running_history/distance")
def get_distance_history():
    week_start = cast(
        func.date_trunc("week", RunningHistory.run_date),
        Date,
    ).label("week_start")

    query = (
        db.select(
            week_start,
            func.sum(RunningHistory.run_distance).label("distance"),
        )
        .group_by(week_start)
        .order_by(week_start)
    )

    distance_per_week = db.session.execute(query).all()
    
    return {
        "weeks": [
            {
                "week_start": row.week_start.isoformat(),
                "distance": row.distance,
            }
            for row in distance_per_week
        ]
    }

@running_history_bp.get("/running_history/pace")
def get_pace_history():
    week_start = cast(
        func.date_trunc("week", RunningHistory.run_date),
        Date,
    ).label("week_start")

    query_pace = (
        db.select(
            week_start,
            (
                func.sum(RunningHistory.run_time) / func.nullif(func.sum(RunningHistory.run_distance), 0)
            ).label("avg_pace"),
        )
        .group_by(week_start)
        .order_by(week_start)
    )

    pace_per_week = db.session.execute(query_pace).all()
    
    return {
        "weeks": [
            {
                "week_start": row.week_start.isoformat(),
                "avg_pace": round(row.avg_pace, 2)
                if row.avg_pace is not None
                else None,
            }
            for row in pace_per_week
        ]
    }

@running_history_bp.get("/running_history/bpm")
def get_bpm_history():
    week_start = cast(
        func.date_trunc("week", RunningHistory.run_date),
        Date,
    ).label("week_start")

    query = (
        db.select(
            week_start,
            (
                func.sum(RunningHistory.bpm*RunningHistory.run_time) / func.nullif(func.sum(RunningHistory.run_time), 0)
            ).label("avg_bpm"),
        )
        .group_by(week_start)
        .order_by(week_start)
    )

    bpm_per_week = db.session.execute(query).all()
    
    return {
        "weeks": [
            {
                "week_start": row.week_start.isoformat(),
                "avg_bpm": round(row.avg_bpm)
                if row.avg_bpm is not None
                else None,
            }
            for row in bpm_per_week
        ]
    }