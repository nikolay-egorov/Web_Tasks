import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from src.model.model import connect_to_db

app = Flask(__name__)
from src.routes import main_route

app.register_blueprint(main_route)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
bcrypt = Bcrypt(app)
connect_to_db(app)

if __name__ == "__main__":

    # app.debug = True -- for screencast
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.jinja_env.undefined = StrictUndefined
    app.jinja_env.auto_reload = True

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0", port=5000)
