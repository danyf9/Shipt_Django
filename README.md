
# Django Shipt Store backend

```diff
- WARNING: all commands must be run from the same location as README.md
```

## 1. Initialization

use the following commands (must have virtualenv installed):
1. python -m venv ./venv
2. WIN: ./venv/Scripts/activate | LINUX: source ./venv/bin/activate
3. pip install -r .\requirements.txt.
4. python ./Shipping_django/initial_run_commands.py

## 2. Activation
### `[A] run on localhost:`
1. python ./Shipping_Django/manage.py runserver
2. click this [link](http://127.0.0.1:8000/)
### `[B] run on server:`
1. pip install gunicorn
2. gunicorn -c .Shipping_django/gunicorn_config.py