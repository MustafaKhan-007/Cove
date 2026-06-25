# COVE Website Rebuild — blueprints/booking/routes.py — appointment wizard page
#
# The booking UI is a vanilla-JS multi-step wizard (static/js/booking.js) that
# POSTs to /api/booking. If the client prefers to keep using their existing
# Shore booking, set SHORE_URL below and the template will redirect instead.

from flask import render_template

import content
from . import booking

# To use Shore instead of the internal wizard, set this to the Shore booking URL.
SHORE_URL = None  # e.g. "https://connect.shore.com/bookings/cove"


@booking.route("/")
def index():
    return render_template(
        "booking/index.html",
        services=content.SERVICES,
        regions=content.LOCATION_REGIONS,
        locations=content.locations(),
        shore_url=SHORE_URL,
    )
