

from flask import Blueprint
from sqlalchemy import case, func
from app.models import Job
from app.extensions import db

job_bp = Blueprint("job", __name__) 


@job_bp.get("/job/all")
def get_jobs():
    query_jobs = (
        db.select(
            Job.job_type,
            Job.job_duration,
            Job.status,
            Job.created_at,
            Job.updated_at
        )
        .order_by(Job.created_at)
    )

    query_stats = (
        db.select(
            Job.job_type,
            (
                func.avg(
                    case(
                        (Job.status == "succeeded", 1),
                        else_=0,
                    )
                )*100
            ).label("success_rate"),
            func.avg(Job.job_duration).label("avg_duration")
        )
        .where(Job.status.in_(["succeeded", "failed"]))
        .group_by(Job.job_type)
    )

    jobs = db.session.execute(query_jobs).all()
    job_stats = db.session.execute(query_stats).all()
    
    return {
        "jobs": [
            {
                "job_type": row.job_type,
                "created_at": row.created_at,
                "status": row.status,
                "job_duration": row.job_duration
            }
            for row in jobs
        ],
        "stats": [
            {
                "job_type": row.job_type,
                "success_rate": row.success_rate,
                "avg_duration": row.avg_duration
            }
            for row in job_stats
        ]
    }