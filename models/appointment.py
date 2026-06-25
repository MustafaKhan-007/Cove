# COVE Website Rebuild — models/appointment.py — booking appointment model
from datetime import datetime

from extensions import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Step 1 — Service
    service = db.Column(db.String(100), nullable=False)  # e.g. "MAßANZUG"

    # Step 2 — Location
    location_id = db.Column(db.String(50), nullable=False)  # e.g. "berlin"
    location_name = db.Column(db.String(100))

    # Step 3 — Date / Time
    preferred_date = db.Column(db.Date, nullable=False)
    preferred_time = db.Column(db.String(10), nullable=False)  # "10:00"

    # Step 4 — Personal info
    salutation = db.Column(db.String(20))   # "Herr" / "Frau" / "Keine Angabe"
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    message = db.Column(db.Text)
    language = db.Column(db.String(5), default="de")

    # Status
    status = db.Column(db.String(20), default="pending")  # pending/confirmed/cancelled
    confirmation_token = db.Column(db.String(64), unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "service": self.service,
            "location_id": self.location_id,
            "location_name": self.location_name,
            "preferred_date": self.preferred_date.isoformat() if self.preferred_date else None,
            "preferred_time": self.preferred_time,
            "salutation": self.salutation,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "message": self.message,
            "language": self.language,
            "status": self.status,
            "confirmation_token": self.confirmation_token,
        }
