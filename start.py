#!/usr/bin/env python3
"""
Railway startup script that properly handles PORT environment variable.
"""
import os
import subprocess
import sys

def main():
    # Get port from environment
    port = os.environ.get('PORT', '8080')

    # Validate port is numeric
    try:
        port_int = int(port)
        if not (1 <= port_int <= 65535):
            raise ValueError("Port out of range")
    except ValueError:
        print(f"Error: '{port}' is not a valid port number.", file=sys.stderr)
        sys.exit(1)

    # Build gunicorn command
    cmd = [
        'gunicorn',
        '--worker-class', 'eventlet',
        '-w', '1',
        '--bind', f'0.0.0.0:{port}',
        '--timeout', '120',
        '--access-logfile', '-',
        '--error-logfile', '-',
        'backend.app:app'
    ]

    print(f"Starting gunicorn on port {port}")
    print(f"Command: {' '.join(cmd)}")

    # Run gunicorn
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Gunicorn failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)

if __name__ == '__main__':
    main()