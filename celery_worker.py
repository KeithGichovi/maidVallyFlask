from app import create_app
from app.extensions import make_celery, celery

app = create_app()
app.app_context().push()

celery = make_celery(app)

if __name__ == '__main__':
    celery.start()