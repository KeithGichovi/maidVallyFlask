from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_mail import Mail
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from celery import Celery
from flask_bootstrap import Bootstrap5

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cors = CORS()
mail = Mail()
# talisman = Talisman()
csrf = CSRFProtect()
bootstrap = Bootstrap5()

def make_celery(app):
    """
    Create a Celery instance configured with the given Flask app.

    This function creates a new Celery instance with the given Flask app's name,
    and updates the Celery configuration with the app's configuration. It also
    creates a custom task class that sets up the Flask app context before
    running the task.

    Args:
        app: The Flask app to use for Celery configuration.

    Returns:
        The newly created Celery instance.
    """
    celery = Celery(app.import_name)
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)


    celery.Task = ContextTask
    return celery