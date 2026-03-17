#!/bin/bash
cd /Users/cathy/python_project/Tesla
pipenv run python manage.py makemigrations suite --name add_environment_and_variables
pipenv run python manage.py migrate suite
