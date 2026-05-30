"""
AURA MEDIX — Error Handlers
Custom error pages with futuristic design
"""
from flask import render_template, jsonify, request


def register_error_handlers(app):

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'error': 'Endpoint not found', 'code': 404}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'error': 'Internal server error', 'code': 500}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        if request.is_json:
            return jsonify({'error': 'Access denied', 'code': 403}), 403
        return render_template('errors/403.html'), 403
