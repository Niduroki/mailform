#!/bin/bash
export FLASK_APP=mailform.py
export FLASK_ENV=development
env $(cat mail-cred.env | xargs) flask run
