# COVE Website Rebuild — app.py — Flask application factory
import os

from flask import Flask, render_template

from config import config
from extensions import db, mail, HAS_MAIL


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    if config_name not in config:
        config_name = "default"

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    if HAS_MAIL and mail is not None:
        mail.init_app(app)

    # Models must be imported before create_all so tables are registered.
    from models import Appointment  # noqa: F401

    from blueprints.main import main as main_bp
    from blueprints.shop import shop as shop_bp
    from blueprints.wiki import wiki as wiki_bp
    from blueprints.booking import booking as booking_bp
    from blueprints.api import api as api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(shop_bp, url_prefix="/shop")
    app.register_blueprint(wiki_bp, url_prefix="/wiki")
    app.register_blueprint(booking_bp, url_prefix="/termin")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("404.html"), 404

    @app.context_processor
    def inject_globals():
        import content
        return {
            "PHONE": content.PHONE,
            "GOOGLE_REVIEWS_LINK": content.GOOGLE_REVIEWS_LINK,
            "SERVICES": content.SERVICES,
        }

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
