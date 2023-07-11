####################################
    Django Shipt Store backend
####################################


! WARNING: all commands must be run from same location as README

1. Initialization
    use the following commands (must have virtualenv installed):
        - python -m venv ./venv
        - WIN: ./venv/Scripts/activate | LINUX: source ./venv/bin/activate
        - pip install -r .\requirements.txt
        - python ./Shipping_django/initial_run_commands.py

2. Activation
    run on local:
        - python ./Shipping_Django/manage.py runserver
        - http://127.0.0.1:8000/ on a web browser
    run on server:
        - pip install gunicorn
        - gunicorn -c .Shipping_django/gunicorn_config.py