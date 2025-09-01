#!/usr/bin/env python3
"""
Simple launcher script for Nova backend dashboard
"""

import argparse
import os
from backend.web.dashboard import init_dashboard, start_dashboard

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start Nova backend dashboard')
    parser.add_argument('--port', type=int, default=5050, help='Port to run on (default: 5050)')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    # Use locks directory from environment or default
    locks_dir = os.environ.get('NOVA_LOCKS_DIR', './locks')
    
    # Initialize dashboard with locks directory
    init_dashboard(locks_dir)
    
    # Start dashboard
    print(f"Starting Nova backend dashboard on http://{args.host}:{args.port}")
    start_dashboard(host=args.host, port=args.port, debug=args.debug)