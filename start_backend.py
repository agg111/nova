#!/usr/bin/env python3
"""
Simple launcher script for Nova backend dashboard
"""

from backend.web.dashboard import init_dashboard, start_dashboard

if __name__ == '__main__':
    # Initialize dashboard with locks directory
    init_dashboard('./locks')
    
    # Start dashboard on port 5001 to avoid conflict with macOS Control Center
    print("Starting Nova backend dashboard on http://localhost:5001")
    start_dashboard(host='0.0.0.0', port=5001, debug=True)