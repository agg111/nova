"""
Web dashboard for Nova system
Provides a web interface to monitor and manage file locks
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
import threading
import time

from ..core.lock_manager import LockManager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('NOVA_SECRET_KEY', 'dev-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Global lock manager instance
lock_manager = None

def init_dashboard(lock_directory: str):
    """Initialize the dashboard with a lock manager"""
    global lock_manager
    lock_manager = LockManager(lock_directory)

@app.route('/')
def index():
    """Main dashboard page"""
    if not lock_manager:
        return "Dashboard not initialized", 500
    
    locks = lock_manager.get_all_locks()
    
    # Calculate basic stats
    total_locks = len(locks)
    users = set(lock.user_name for lock in locks)
    computers = set(lock.computer_name for lock in locks)
    
    stats = {
        'total_locks': total_locks,
        'unique_users': len(users),
        'unique_computers': len(computers),
        'users': list(users),
        'computers': list(computers)
    }
    
    return render_template('dashboard.html', locks=locks, stats=stats)

@app.route('/api/locks')
def get_locks():
    """API endpoint to get all locks"""
    if not lock_manager:
        return jsonify({'error': 'Dashboard not initialized'}), 500
    
    locks = lock_manager.get_all_locks()
    return jsonify([{
        'file_path': lock.file_path,
        'user_name': lock.user_name,
        'computer_name': lock.computer_name,
        'lock_time': lock.lock_time,
        'process_id': lock.process_id,
        'lock_id': lock.lock_id
    } for lock in locks])

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
    
    max_age = request.json.get('max_age_hours', 24)
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

def start_dashboard(host='0.0.0.0', port=5000, debug=False):
    """Start the dashboard server"""
    print(f"Starting Nova dashboard on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug)

if __name__ == '__main__':
    # For testing purposes
    init_dashboard('./locks')
    start_dashboard(debug=True)
