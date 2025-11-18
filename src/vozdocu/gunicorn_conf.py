chdir = "/src"

# Gunicorn Configuration for Nginx
bind = "0.0.0.0:8000"
#bind = "127.0.0.1:8000"  # Ensure it matches the Nginx proxy_pass setting
#forwarded_allow_ips = "*"  # Allow requests from Nginx
#proxy_protocol = True  # Enable proxy support

# Worker Settings
import multiprocessing
workers = 2 * multiprocessing.cpu_count() + 1  # Dynamically determine the optimal workers
#worker_class = 'eventlet'
#worker_connections = 2000

loglevel = "info"
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log errors to stdout
#errorlog = "/srv/logs/gunicorn.log"
#accesslog = "/srv/logs/access.log
loglevel = "info"

# Timeout Settings
timeout = 30  # Automatically restart workers if they take too long
graceful_timeout = 30  # Graceful shutdown for workers

# Keep-Alive Settings
keepalive = 2  # Keep connections alive for 2s

# Worker Restart Settings
max_requests = 1000  # Restart workers after processing 1000 requests
max_requests_jitter = 50  # Add randomness to avoid mass restarts
