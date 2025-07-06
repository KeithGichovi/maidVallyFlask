from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
main_bp = Blueprint('main', __name__)
clients_bp = Blueprint('clients', __name__, url_prefix='/clients')
jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')

from app.views import auth, main, clients, jobs