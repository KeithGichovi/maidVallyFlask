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
    celery = Celery(app.import_name)
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)


    celery.Task = ContextTask
    return celery