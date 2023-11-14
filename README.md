
# Django Shipt Store backend

```diff
- WARNING: all commands must be run from the same location as README.md (unless specified otherwise)
```

## 1. Settings
add the following variables to your system environment:
* DJANGO_KEY - the django secret key
* ACCESS_KEY & SECRET_ACCESS_KEY - the s3 keys generated for a IAM user
* S3_URL - s3 url given by AWS
* POSTGRES_KEY - postgres password
* HOST - the public ip of the computer
* DB - the postgres endpoint given by AWS

make sure you can access these environment variables before proceeding


## 2. Initialization
use the following commands (must have virtualenv installed):
1. python -m venv ./venv
2. WIN: ./venv/Scripts/activate | LINUX: source ./venv/bin/activate
3. pip install -r ./requirements.txt.
4. python initial_run_commands.py

## 3. Activation
### `[A] run on localhost:`
1. python ./Shipping_Django/manage.py runserver
2. click this [link](http://127.0.0.1:8000/)
### `[B] run on server:`
1. pip install gunicorn
2. cd <location-of-gunicorn_config.py>
3. gunicorn -c gunicorn_config.py


