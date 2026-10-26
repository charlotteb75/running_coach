

from flask import Blueprint, abort, request
from sqlalchemy import case, func
from app.models import Job
from app.extensions import db
from app.schemas import PaginationParams

job_bp = Blueprint("job", __name__) 


@job_bp.get("/jobs")
def get_jobs():
    pagination = PaginationParams.model_validate(
        request.args.to_dict()
    )

    query_jobs = (
        db.select(Job)
        .order_by(Job.created_at.desc())
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

    jobs_page = db.paginate(
        query_jobs,
        page=pagination.page,
        per_page=pagination.per_page,
        max_per_page=100,
        error_out=False
    )
    job_stats = db.session.execute(query_stats).all()
    
    return {
        "jobs": [
            {
                "job_type": row.job_type,
                "created_at": row.created_at,
                "status": row.status,
                "job_duration": row.job_duration
            }
            for row in jobs_page.items
        ],
        "pagination": {
            "page": jobs_page.page,
            "per_page": jobs_page.per_page,
            "total": jobs_page.total,
            "pages": jobs_page.pages,
            "has_next": jobs_page.has_next,
        },
        "stats": [
            {
                "job_type": row.job_type,
                "success_rate": row.success_rate,
                "avg_duration": row.avg_duration
            }
            for row in job_stats
        ]
    }