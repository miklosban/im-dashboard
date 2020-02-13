from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
from flask_dance.consumer import OAuth2ConsumerBlueprint
import logging

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key="8210f566-4981-11ea-92d1-f079596e599b"
app.config.from_json('config.json')

loglevel = app.config.get("LOG_LEVEL") if app.config.get("LOG_LEVEL") else "INFO"

numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)

logging.basicConfig(level=numeric_level)

oidc_base_url=app.config['OIDC_BASE_URL']
oidc_token_url=oidc_base_url + '/token'
oidc_refresh_url=oidc_base_url + '/token'
oidc_authorization_url=oidc_base_url + '/authorize'

oidc_blueprint = OAuth2ConsumerBlueprint(
    "oidc", __name__,
    client_id=app.config['OIDC_CLIENT_ID'],
    client_secret=app.config['OIDC_CLIENT_SECRET'],
    scope=app.config['OIDC_SCOPES'],
    base_url=oidc_base_url,
    token_url=oidc_token_url,
    auto_refresh_url=oidc_refresh_url,
    authorization_url=oidc_authorization_url,
    redirect_to='home'
)
app.register_blueprint(oidc_blueprint, url_prefix="/login")

from app import routes, errors

if __name__ == "__main__":
    app.run(host='0.0.0.0')

