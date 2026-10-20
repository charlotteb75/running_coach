

from flask import Blueprint, request
from app.extensions import db
from app.models import Milestone
from app.schemas import MilestoneCreate, MilestoneUpdate

milestone_bp = Blueprint("milestone", __name__)


@milestone_bp.get("/milestone/<int:id_milestone>")
def get_milestone(id_milestone):
    milestone = db.get_or_404(Milestone, id_milestone)
    response = {
        "milestone_type" : milestone.milestone_type,
        "milestone_distance" : milestone.milestone_distance,
        "milestone_speed": milestone.milestone_speed,
        "date_estimated": milestone.date_estimated,
        "achieved": milestone.achieved,
        "date_achieved": milestone.date_achieved
    }
    return {
        "message": "success",
        "milestone": response
        }

@milestone_bp.post("/milestone")
def create_milestone():
    milestone_data = MilestoneCreate.model_validate(request.get_json())
    milestone_obj = Milestone(**milestone_data.model_dump())
    db.session.add(milestone_obj)
    db.session.commit()
    return {
        "message": "success",
        "milestone": {
            "id_milestone": milestone_obj.id_milestone,
            "milestone_type": milestone_obj.milestone_type,
            "date_estimated": milestone_obj.date_estimated
        },
    }, 201

@milestone_bp.patch("/milestone/<int:id_milestone>")
def update_milestone(id_milestone):
    data = MilestoneUpdate.model_validate(request.get_json())
    milestone = db.get_or_404(Milestone, id_milestone)
    
    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(milestone, field, value)

    db.session.commit()
    return {
        "message": "Milestone updated"
        }, 200