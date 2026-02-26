# Gunicorn configuration file
import multiprocessing

# Bind to localhost, nginx will proxy
bind = "127.0.0.1:8000"

# Workers = 2 * CPU cores + 1 (for small EC2, use 2-4)
workers = 2

# Worker class
worker_class = "sync"

# Timeout for requests
timeout = 120

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = "fitness_tracker"

# Daemon mode (handled by systemd, keep False)
daemon = False
