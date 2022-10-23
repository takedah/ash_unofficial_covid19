def when_ready(server):
    open("/tmp/app-initialized", "w").close()


bind = "unix:///var/gunicorn/nginx.socket"
