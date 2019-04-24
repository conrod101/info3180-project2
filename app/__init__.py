from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
UPLOAD_FOLDER = "./app/static/profilepics"


app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = "df33af2f53254210aa5d28d527983920"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://photogram:password101@localhost/photogram" # changed to reflect the correct user, password and database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # added just to suppress a warning
# app.config['Uploads'] = Uploads

db = SQLAlchemy(app)

# Flask-Login login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config.from_object(__name__)
from app import views
