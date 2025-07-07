from app.views import http_bp
from flask import render_template

@http_bp.errorhandler(404)
def page_not_found(e):
    return render_template('http/404.html'), 404


@http_bp.errorhandler(500)
def internal_server_error(e):
    return render_template('http/500.html'), 500


@http_bp.errorhandler(403)
def forbidden(e):
    return render_template('http/403.html'), 403


@http_bp.errorhandler(502)
def bad_gateway(e):
    return render_template('http/502.html'), 502
