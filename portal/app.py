import os
from flask import Flask, redirect, jsonify, url_for, request
from flask_admin import helpers as admin_helpers
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from models import db
from models.user import User, Role
from controllers import camera_type_api, processing_api, visualize_api, bathymetry_api, ratingcurve_api, project_api
from views import admin
from flask_migrate import Migrate

# Create flask app
app = Flask(__name__, template_folder="templates")
app.register_blueprint(camera_type_api)
app.register_blueprint(processing_api)
app.register_blueprint(visualize_api)
app.register_blueprint(bathymetry_api)
app.register_blueprint(ratingcurve_api)
app.register_blueprint(project_api)

app.debug = True
app.config["SECRET_KEY"] = os.getenv("APP_SECRET_KEY")
app.config["SECURITY_REGISTERABLE"] = (os.getenv("APP_REGISTRATION_ENABLED") != "false")
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECURITY_PASSWORD_SALT")

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db, User, Role)
security = Security(app, user_datastore)
migrate = Migrate(app, db)

# Alternative routes
@app.route("/")
def index():
    """
    Redirect requests on the root path towards the portal directory.

    :return:
    """
    return redirect("/portal", code=302)


# Create admin interface
admin.init_app(app)

@security.context_processor
def security_context_processor():
    """
    Provide necessary vars to flask-admin views.

    :return:
    """
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for,
    )


@app.teardown_appcontext
def shutdown_session(exception=None):
    """
    Resolve database session issues for the combination of Postgres/Sqlalchemy scoped session/Flask-admin.

    :param exception:
    """
    # load all expired attributes for the given instance
    db.expire_all()

@app.teardown_request
def session_clear(exception=None):
    """
    Resolve database session issues for the combination of Postgres/Sqlalchemy to rollback database transactions after an exception is thrown.
    """
    db.remove()
    if exception and db.is_active:
        db.rollback()

@app.before_request
def before_request():
    """
    Redirect all requests to HTTPS if the environment variable for this is configured.
    """
    # NOTE: String check on FORCE_HTTPS since this is loaded from env variables and not an actual boolean.
    if not request.is_secure and os.getenv("FORCE_HTTPS") == "true":
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

if __name__ == "__main__":
    # Start app
    port = int(os.getenv("PORT", 80))
    app.run(host='0.0.0.0', port=port)
