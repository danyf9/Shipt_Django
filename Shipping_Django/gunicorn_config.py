# remove 'Shipping_Django.' before launch in ubuntu
from Shipping_Django.settings import BASE_DIR
wsgi_app = "Shipping_Django.asgi:application"
bind = "127.0.0.1:8000"
reload = True  # only for development mode
accesslog = errorlog = fr'{str(BASE_DIR).split(r"Shipping_Django")[0]}logs/gunicorn/gunicorn.log'
capture_output = True
daemon = True  # True for running in background
worker_class = "uvicorn.workers.UvicornWorker "
