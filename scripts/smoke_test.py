# COVE Website Rebuild — scripts/smoke_test.py — render every route via test client
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

URLS = [
    "/", "/ueber-uns", "/faq", "/standorte", "/standorte/berlin",
    "/standorte/baden-baden", "/massanzug", "/masshemd", "/hochzeit",
    "/sakko", "/mantel", "/schuhe", "/shop/", "/shop/produkt-kategorie/schuhe",
    "/wiki/", "/wiki/bespoke", "/wiki/harris-tweed", "/termin/",
    "/static/translations/de.json", "/static/translations/en.json",
    "/nonexistent-page",
]

failures = 0
with app.test_client() as c:
    for u in URLS:
        try:
            r = c.get(u)
            flag = "OK " if r.status_code in (200, 302, 404) else "ERR"
            if r.status_code not in (200, 302, 404):
                failures += 1
            print(f"{flag} {r.status_code}  {u}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"EXC      {u}: {type(exc).__name__}: {exc}")

    # booking POST
    payload = {
        "service": "MAßANZUG", "location_id": "berlin", "preferred_date": "2026-07-01",
        "preferred_time": "10:00", "first_name": "Max", "last_name": "Mustermann",
        "email": "max@example.com", "privacy": True, "language": "de",
    }
    r = c.post("/api/booking", json=payload)
    print(f"POST {r.status_code} /api/booking -> {r.get_json()}")
    if r.status_code != 200:
        failures += 1

print(f"\n{'PASSED' if failures == 0 else 'FAILED'} — {failures} failure(s)")
sys.exit(1 if failures else 0)
