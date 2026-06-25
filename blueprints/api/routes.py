# COVE Website Rebuild — blueprints/api/routes.py — booking + utility JSON endpoints
import re
import secrets
from datetime import datetime

from flask import request, jsonify, current_app

import content
from extensions import db, mail, HAS_MAIL
from models import Appointment
from . import api

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
REQUIRED = ("service", "location_id", "preferred_date", "preferred_time",
            "first_name", "last_name", "email")


@api.route("/booking", methods=["POST"])
def create_booking():
    data = request.get_json(silent=True) or {}

    # --- validation -------------------------------------------------------
    missing = [f for f in REQUIRED if not str(data.get(f, "")).strip()]
    if missing:
        return jsonify({"success": False,
                        "error": "missing_fields",
                        "fields": missing,
                        "message": "Bitte füllen Sie alle Pflichtfelder aus."}), 400

    if not EMAIL_RE.match(data["email"].strip()):
        return jsonify({"success": False, "error": "invalid_email",
                        "message": "Bitte geben Sie eine gültige E-Mail-Adresse an."}), 400

    if not data.get("privacy"):
        return jsonify({"success": False, "error": "privacy_required",
                        "message": "Bitte stimmen Sie der Datenschutzerklärung zu."}), 400

    try:
        pref_date = datetime.strptime(data["preferred_date"], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "invalid_date",
                        "message": "Ungültiges Datum."}), 400

    # --- persist ----------------------------------------------------------
    loc = content.location(data["location_id"])
    token = secrets.token_urlsafe(32)

    appt = Appointment(
        service=_clean(data["service"], 100),
        location_id=_clean(data["location_id"], 50),
        location_name=(loc.get("city") if loc else data.get("location_name", "")),
        preferred_date=pref_date,
        preferred_time=_clean(data["preferred_time"], 10),
        salutation=_clean(data.get("salutation", ""), 20),
        first_name=_clean(data["first_name"], 100),
        last_name=_clean(data["last_name"], 100),
        email=_clean(data["email"], 200),
        phone=_clean(data.get("phone", ""), 50),
        message=(data.get("message") or "")[:2000],
        language=_clean(data.get("language", "de"), 5),
        status="pending",
        confirmation_token=token,
    )
    db.session.add(appt)
    db.session.commit()

    _send_confirmation(appt)

    msg = ("Vielen Dank! Ihre Terminanfrage ist eingegangen. "
           "Wir bestätigen Ihren Termin in Kürze per E-Mail."
           if appt.language == "de" else
           "Thank you! Your appointment request has been received. "
           "We will confirm your appointment by email shortly.")

    return jsonify({"success": True, "token": token, "message": msg})


def _clean(value, maxlen):
    return re.sub(r"\s+", " ", str(value or "")).strip()[:maxlen]


def _send_confirmation(appt):
    """Send a confirmation email if Flask-Mail is configured; otherwise log."""
    subject = "Ihre Terminanfrage bei cove"
    body = (
        f"Hallo {appt.first_name} {appt.last_name},\n\n"
        f"vielen Dank für Ihre Terminanfrage bei cove.\n\n"
        f"Service: {appt.service}\n"
        f"Standort: {appt.location_name}\n"
        f"Datum: {appt.preferred_date} um {appt.preferred_time} Uhr\n\n"
        f"Wir melden uns in Kürze zur Bestätigung.\n\n"
        f"Ihr cove Team"
    )
    if HAS_MAIL and current_app.config.get("MAIL_SERVER"):
        try:
            from flask_mail import Message
            mail.send(Message(subject=subject, recipients=[appt.email], body=body))
            return
        except Exception as exc:  # noqa: BLE001
            current_app.logger.warning("Mail send failed: %s", exc)
    current_app.logger.info("[booking] confirmation (token=%s) -> %s\n%s",
                            appt.confirmation_token, appt.email, body)


@api.route("/locations", methods=["GET"])
def list_locations():
    return jsonify(content.locations())
