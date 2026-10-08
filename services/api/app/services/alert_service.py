from email.message import EmailMessage
import smtplib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import AlertNotification, Candidate, JobAlert
from app.services.recommendation_engine import RankedRecommendation, recommend_jobs


def matching_alert_jobs(db: Session, candidate_id: int) -> tuple[JobAlert | None, list[RankedRecommendation]]:
    alert = db.scalar(
        select(JobAlert)
        .where(JobAlert.candidate_id == candidate_id, JobAlert.enabled.is_(True))
        .order_by(JobAlert.created_at.desc())
    )
    if alert is None:
        return None, []
    matches = [
        item for item in recommend_jobs(db, candidate_id, 50)
        if item.score >= alert.minimum_score
    ]
    return alert, matches


def send_alert_email(
    candidate: Candidate,
    matches: list[RankedRecommendation],
) -> bool:
    if not settings.smtp_host or not settings.smtp_from or not candidate.email or not matches:
        return False

    message = EmailMessage()
    message["Subject"] = f"{len(matches)} strong job match(es) found for you"
    message["From"] = settings.smtp_from
    message["To"] = candidate.email

    lines = ["AI Job Match found new jobs above your alert threshold:", ""]
    for item in matches[:10]:
        lines.append(
            f"- {item.job.title} at {item.job.company} ({item.score:.0f}% match)"
        )
        if item.job.apply_url:
            lines.append(f"  Apply: {item.job.apply_url}")
    message.set_content("\n".join(lines))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)
    return True


def mark_new_notifications(
    db: Session,
    alert: JobAlert,
    matches: list[RankedRecommendation],
) -> list[RankedRecommendation]:
    existing_ids = set(
        db.scalars(
            select(AlertNotification.job_id).where(AlertNotification.alert_id == alert.id)
        ).all()
    )
    return [item for item in matches if item.job.id not in existing_ids]
