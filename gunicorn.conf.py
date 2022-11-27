import multiprocessing


def when_ready(server):
    open("/tmp/app-initialized", "w").close()


bind = "unix:///var/gunicorn/nginx.socket"
reload = True
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 1024
backlog = 2048
max_requests = 5120
timeout = 120
accesslog = "./logs/access.log"
errorlog = "./logs/error.log"
