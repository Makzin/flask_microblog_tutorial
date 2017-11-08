import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_openid import OpenID
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from flask_mail import Mail
from .momentjs import momentjs
from flask_babel import Babel, gettext, lazy_gettext
from flask.json import JSONEncoder

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
app.jinja_env.globals['momentjs'] = momentjs
babel = Babel(app)
mail = Mail()

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = lazy_gettext('Please log in to access this page')
oid = OpenID(app, os.path.join(basedir, 'tmp'))

if not app.debug:
  import logging
  from logging.handlers import SMTPHandler
  credentials = None
  if MAIL_USERNAME or MAIL_PASSWORD:
    credentials = (MAIL_USERNAME, MAIL_PASSWORD)
  mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' +
    MAIL_SERVER, ADMINS, 'microblog failure', credentials)
  mail_handler.setLevel(logging.ERROR)
  app.logger.addHandler(mail_handler)


class CustomJSONEncoder(JSONEncoder):
    """This class adds support for lazy translation texts to Flask's
    JSON encoder. This is necessary when flashing translated texts."""
    def default(self, obj):
        from speaklater import is_lazy_string
        if is_lazy_string(obj):
            try:
                return unicode(obj)  # python 2
            except NameError:
                return str(obj)  # python 3
        return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder

from app import views, models