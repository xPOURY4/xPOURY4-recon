"""
Flask web application for xPOURY4 Recon
Author: xPOURY4
"""

import asyncio
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash

from ..core.config_manager import config
from ..core.logger import logger
from ..core.recon_engine import ReconEngine


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = config.get("web_ui.secret_key")
    app.config['DEBUG'] = config.get("web_ui.debug", False)
    
    # Initialize SocketIO for real-time updates
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Initialize ReconEngine
    recon_engine = ReconEngine()
    
    @app.route('/')
    def index():
        """Main dashboard"""
        module_status = recon_engine.get_module_status()
        return render_template('index.html', 
                             module_status=module_status,
                             version="1.0.0",
                             author="xPOURY4")
    
    @app.route('/github')
    def github_recon():
        """GitHub reconnaissance page"""
        return render_template('github_recon.html')
    
    @app.route('/domain')
    def domain_recon():
        """Domain reconnaissance page"""
        return render_template('domain_recon.html')
    
    @app.route('/phone')
    def phone_recon():
        """Phone reconnaissance page"""
        return render_template('phone_recon.html')
    
    @app.route('/linkedin')
    def linkedin_recon():
        """LinkedIn reconnaissance page"""
        return render_template('linkedin_recon.html')
    
    @app.route('/shodan')
    def shodan_recon():
        """Shodan reconnaissance page"""
        return render_template('shodan_recon.html')
    
    @app.route('/comprehensive')
    def comprehensive_recon():
        """Comprehensive reconnaissance page"""
        return render_template('comprehensive_recon.html')
    
    @app.route('/results')
    def results():
        """Results page"""
        return render_template('results.html')
    
    @app.route('/settings')
    def settings():
        """Settings page"""
        current_config = config.config
        return render_template('settings.html', config=current_config)
    
    # API Routes
    @app.route('/api/github/investigate', methods=['POST'])
    def api_github_investigate():
        """API endpoint for GitHub investigation"""
        try:
            data = request.get_json()
            username = data.get('username')
            
            if not username:
                return jsonify({'error': 'Username is required'}), 400
            
            # Run investigation in background
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(recon_engine.run_github_recon(username))
            loop.close()
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"GitHub API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/domain/investigate', methods=['POST'])
    def api_domain_investigate():
        """API endpoint for domain investigation"""
        try:
            data = request.get_json()
            domain = data.get('domain')
            
            if not domain:
                return jsonify({'error': 'Domain is required'}), 400
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(recon_engine.run_domain_recon(domain))
            loop.close()
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Domain API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/phone/investigate', methods=['POST'])
    def api_phone_investigate():
        """API endpoint for phone investigation"""
        try:
            data = request.get_json()
            phone_number = data.get('phone_number')
            
            if not phone_number:
                return jsonify({'error': 'Phone number is required'}), 400
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(recon_engine.run_phone_recon(phone_number))
            loop.close()
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Phone API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/linkedin/investigate', methods=['POST'])
    def api_linkedin_investigate():
        """API endpoint for LinkedIn investigation"""
        try:
            data = request.get_json()
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            company = data.get('company', '')
            location = data.get('location', '')
            keywords = data.get('keywords', [])
            
            if not first_name or not last_name:
                return jsonify({'error': 'First and last name are required'}), 400
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                recon_engine.run_linkedin_recon(
                    first_name, last_name, 
                    company=company, location=location, keywords=keywords
                )
            )
            loop.close()
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"LinkedIn API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/shodan/investigate', methods=['POST'])
    def api_shodan_investigate():
        """API endpoint for Shodan investigation"""
        try:
            data = request.get_json()
            target = data.get('target')
            
            if not target:
                return jsonify({'error': 'Target is required'}), 400
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(recon_engine.run_shodan_recon(target))
            loop.close()
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Shodan API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/comprehensive/investigate', methods=['POST'])
    def api_comprehensive_investigate():
        """API endpoint for comprehensive investigation"""
        try:
            data = request.get_json()
            targets = data.get('targets', {})
            
            if not targets:
                return jsonify({'error': 'At least one target is required'}), 400
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(recon_engine.run_comprehensive_recon(targets))
            loop.close()
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Comprehensive API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/status')
    def api_status():
        """API endpoint for module status"""
        try:
            status = recon_engine.get_module_status()
            return jsonify({
                'status': 'ok',
                'modules': status,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/results')
    def api_results():
        """API endpoint to get current results"""
        try:
            results = recon_engine.get_results()
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/config', methods=['GET', 'POST'])
    def api_config():
        """API endpoint for configuration management"""
        if request.method == 'GET':
            # Return current configuration (without sensitive data)
            current_config = config.config.copy()
            # Remove sensitive information
            if 'api_keys' in current_config:
                for key in current_config['api_keys']:
                    if current_config['api_keys'][key]:
                        current_config['api_keys'][key] = '***CONFIGURED***'
            return jsonify(current_config)
        
        elif request.method == 'POST':
            try:
                new_config = request.get_json()
                config.update_config(new_config)
                return jsonify({'status': 'success', 'message': 'Configuration updated'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    # SocketIO Events
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        logger.info("Client connected to WebSocket")
        emit('status', {'message': 'Connected to xPOURY4 Recon'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        logger.info("Client disconnected from WebSocket")
    
    @socketio.on('start_investigation')
    def handle_investigation(data):
        """Handle investigation request via WebSocket"""
        try:
            investigation_type = data.get('type')
            params = data.get('params', {})
            
            emit('investigation_started', {'type': investigation_type})
            
            # Run investigation based on type
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if investigation_type == 'github':
                result = loop.run_until_complete(
                    recon_engine.run_github_recon(params.get('username'))
                )
            elif investigation_type == 'domain':
                result = loop.run_until_complete(
                    recon_engine.run_domain_recon(params.get('domain'))
                )
            elif investigation_type == 'phone':
                result = loop.run_until_complete(
                    recon_engine.run_phone_recon(params.get('phone_number'))
                )
            elif investigation_type == 'linkedin':
                result = loop.run_until_complete(
                    recon_engine.run_linkedin_recon(
                        params.get('first_name'), params.get('last_name'),
                        **{k: v for k, v in params.items() if k not in ['first_name', 'last_name']}
                    )
                )
            elif investigation_type == 'shodan':
                result = loop.run_until_complete(
                    recon_engine.run_shodan_recon(params.get('target'))
                )
            else:
                result = {'error': 'Unknown investigation type'}
            
            loop.close()
            
            emit('investigation_complete', {
                'type': investigation_type,
                'result': result
            })
            
        except Exception as e:
            emit('investigation_error', {
                'type': investigation_type,
                'error': str(e)
            })
    
    # Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', 
                             error_code=404, 
                             error_message="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', 
                             error_code=500, 
                             error_message="Internal server error"), 500
    
    # Store socketio instance for external access
    app.socketio = socketio
    
    return app 