flask db init
flask db migrate -m "Initial DB"
flask db upgrade

export FLASK_APP="entrypoint"
export FLASK_ENV="production"
export APP_SETTINGS_MODULE="config.prod"
