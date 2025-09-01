"""
Web dashboard for Nova system
Provides a web interface to monitor and manage file locks
"""

import os
import json
from datetime import datetime
from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time

from ..core.lock_manager import LockManager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('NOVA_SECRET_KEY', 'dev-secret-key')

# Enable CORS for all routes
CORS(app, 
     origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
     methods=["GET", "POST", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "Accept"],
     supports_credentials=True)

socketio = SocketIO(app, cors_allowed_origins="*")

# Global lock manager instance
lock_manager = None

def init_dashboard(lock_directory: str):
    """Initialize the dashboard with a lock manager"""
    global lock_manager
    lock_manager = LockManager(lock_directory)

# Auto-initialize when module is imported
if lock_manager is None:
    # Use a default directory if none specified
    default_lock_dir = os.getenv('NOVA_LOCKS_DIR', './locks')
    init_dashboard(default_lock_dir)

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return '', 204  # No content, but successful response

@app.route('/')
def index():
    """Main dashboard page - redirects to React frontend"""
    return jsonify({
        'message': 'Nova API Server',
        'status': 'running',
        'frontend_url': 'http://localhost:3000',
        'api_docs': {
            'locks': '/api/locks',
            'stats': '/api/stats',
            'cleanup': '/api/cleanup',
            'remove_lock': '/api/locks/<file_path>'
        }
    })

@app.route('/api/locks', methods=['GET', 'POST'])
def locks_endpoint():
    """API endpoint to get all locks or create a new lock"""
    print(f"🔍 API request: {request.method} /api/locks from {request.remote_addr}")
    print(f"🔍 Headers: {dict(request.headers)}")
    
    if not lock_manager:
        return jsonify({'error': 'Dashboard not initialized'}), 500
    
    if request.method == 'GET':
        # Get all locks
        locks = lock_manager.get_all_locks()
        return jsonify([{
            'file_path': lock.file_path,
            'user_name': lock.user_name,
            'computer_name': lock.computer_name,
            'lock_time': lock.lock_time,
            'process_id': lock.process_id,
            'lock_id': lock.lock_id
        } for lock in locks])
    
    elif request.method == 'POST':
        # Create a new lock
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        try:
            data = request.get_json()
            if data is None:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            file_path = data.get('file_path')
            user_name = data.get('user_name')
            computer_name = data.get('computer_name')
            process_id = data.get('process_id', 0)
            
            if not all([file_path, user_name, computer_name]):
                return jsonify({'error': 'Missing required fields: file_path, user_name, computer_name'}), 400
            
            # Create the lock
            success, message = lock_manager.create_lock(file_path, user_name, computer_name, process_id)
            
            if success:
                # Emit socket event for real-time updates
                socketio.emit('lock_created', {'file_path': file_path, 'user_name': user_name})
                return jsonify({'message': message, 'success': True}), 201
            else:
                return jsonify({'error': message, 'success': False}), 400
                
        except Exception as e:
            return jsonify({'error': f'Invalid JSON format: {str(e)}'}), 400

@app.route('/api/locks/<path:file_path>')
def get_lock(file_path):
    """API endpoint to get lock for a specific file"""
    if not lock_manager:
        return jsonify({'error': 'Dashboard not initialized'}), 500
    
    lock = lock_manager.check_lock(file_path)
    if lock:
        return jsonify({
            'file_path': lock.file_path,
            'user_name': lock.user_name,
            'computer_name': lock.computer_name,
            'lock_time': lock.lock_time,
            'process_id': lock.process_id,
            'lock_id': lock.lock_id
        })
    else:
        return jsonify({'error': 'File not locked'}), 404

@app.route('/api/locks/<path:file_path>', methods=['DELETE'])
def remove_lock(file_path):
    """API endpoint to remove a lock"""
    if not lock_manager:
        return jsonify({'error': 'Dashboard not initialized'}), 500
    
    user_name = request.args.get('user_name', 'admin')
    success, message = lock_manager.remove_lock(file_path, user_name)
    
    if success:
        # Emit socket event for real-time updates
        socketio.emit('lock_removed', {'file_path': file_path})
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 400

@app.route('/api/cleanup', methods=['POST'])
def cleanup_locks():
    """API endpoint to cleanup stale locks"""
    if not lock_manager:
        return jsonify({'error': 'Dashboard not initialized'}), 500
    
    # Validate JSON input
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        max_age = data.get('max_age_hours', 24)
        if not isinstance(max_age, (int, float)) or max_age < 0:
            return jsonify({'error': 'max_age_hours must be a positive number'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Invalid JSON format: {str(e)}'}), 400
    removed_count = lock_manager.cleanup_stale_locks(max_age)
    
    # Emit socket event for real-time updates
    socketio.emit('locks_cleaned', {'removed_count': removed_count})
    
    return jsonify({
        'message': f'Cleaned up {removed_count} stale locks',
        'removed_count': removed_count
    })

@app.route('/api/stats')
def get_stats():
    """API endpoint to get lock statistics"""
    print(f"🔍 API request: {request.method} /api/stats from {request.remote_addr}")
    print(f"🔍 Headers: {dict(request.headers)}")
    
    if not lock_manager:
        return jsonify({'error': 'Dashboard not initialized'}), 500
    
    locks = lock_manager.get_all_locks()
    
    # Calculate statistics
    total_locks = len(locks)
    users = set(lock.user_name for lock in locks)
    computers = set(lock.computer_name for lock in locks)
    
    # Group by file extension
    extensions = {}
    for lock in locks:
        ext = os.path.splitext(lock.file_path)[1].lower()
        extensions[ext] = extensions.get(ext, 0) + 1
    
    return jsonify({
        'total_locks': total_locks,
        'unique_users': len(users),
        'unique_computers': len(computers),
        'extensions': extensions,
        'users': list(users),
        'computers': list(computers)
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to Nova dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

def start_dashboard(host='0.0.0.0', port=5050, debug=False):
    """Start the dashboard server"""
    print(f"Starting Nova dashboard on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, use_reloader=False)

if __name__ == '__main__':
    # For testing purposes
    init_dashboard('./locks')
    start_dashboard(debug=True)
