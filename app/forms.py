from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField,SelectField,FileField
from wtforms.validators import InputRequired,Email,DataRequired
from flask_wtf.file import FileRequired,FileAllowed
from wtforms.widgets import TextArea
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Required
from wtforms import validators, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired 

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    

class SignUpForm(FlaskForm):
    username  = StringField('Username', [validators.Required("(Required)")])
    password  = PasswordField('Password', validators=[InputRequired()])
    firstname = StringField('Firstname', [validators.Required("(Required)")])
    lastname  = StringField('Lastname', [validators.Required("(Required)")])
    email     = StringField("Email",[validators.Required("(Required)"), validators.Email("(Required)")])
    location  = StringField("Location",[validators.Required("(Required)")])
    biography = TextAreaField('Bio', validators=[InputRequired()])
    photo     = FileField('Profile Picture', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'Images only!'])])
    
class Upload(FlaskForm):
    image   = FileField('Profile Picture', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'Images only!'])])
    caption = TextAreaField('Caption', validators=[InputRequired()])
    

class UploadForm(FlaskForm):
    description = StringField(validators = [InputRequired()],widget = TextArea())
    photo       = FileField(validators   = [FileRequired(),FileAllowed(['jpg','png','jpeg'],'Only Images Allowed')])
    