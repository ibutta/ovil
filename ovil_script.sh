#!/bin/bash
# Sets Flask's environment variables for the Objects and Verbs Issue Logger (OVIL) project and starts Flask

export FLASK_APP=ovil
export FLASK_ENV=development
echo "FLASK_APP set to $FLASK_APP"
echo "FLASK_ENV set to $FLASK_ENV"
flask run
