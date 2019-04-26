from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


UPLOAD_FOLDER = './app/static/images'
TOKEN_SECRET = 'ransnsn'

app = Flask(__name__)
app.config['SECRET_KEY'] = "randa"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://photogram:password101@localhost/photogram'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # added just to suppress a warning
csrf = CSRFProtect(app)
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config.from_object(__name__)
filefolder = app.config['UPLOAD_FOLDER']
token_key = app.config['TOKEN_SECRET']
app.debug= True
from app import views