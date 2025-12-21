import os
from app.models import Application, Job
from app.ml.recommender import recommend_jobs


def get_recommendations_for_user(user_id, limit=5):
    """
    Returns ML job recommendations for a user
    """

    # 🔹 Get latest application with resume
    latest_app = (
        Application.query
        .filter_by(seeker_user_id=user_id)
        .order_by(Application.applied_at.desc())
        .first()
    )

    # ❌ No application or no resume
    if not latest_app or not latest_app.resume_file_path:
        return []

    # ❌ Resume file missing on disk
    if not os.path.exists(latest_app.resume_file_path):
        print("Resume file NOT FOUND:", latest_app.resume_file_path)
        return []

    # 🔹 Get all jobs
    jobs = Job.query.all()
    if not jobs:
        return []

    # 🔹 ML Recommendation
    recommendations = recommend_jobs(
        latest_app.resume_file_path,
        jobs,
        top_n=limit
    )

    return recommendations
