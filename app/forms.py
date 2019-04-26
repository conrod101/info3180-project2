from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, Email
from flask_wtf.file import FileField, FileAllowed, FileRequired


class PostForm(FlaskForm):
    photo=FileField('Photo', validators=[FileRequired('Please input a file'), FileAllowed(['jpg','jpeg', 'png'], 'Images only!')])
    caption=StringField('Caption',validators=[InputRequired(message='Caption is required')])



class RegisterForm(FlaskForm):
    fname=StringField('First Name',validators=[InputRequired(message='First Name is required')])
    lname=StringField('Last Name',validators=[InputRequired(message='Last Name is required')])
    email = StringField('Email', validators=[InputRequired(message='Email is required'), Email(message="Only Emails")])   
    password=PasswordField('Password',validators=[InputRequired(message='Password is required')])
    confirmpassword=PasswordField('Confirm Password',validators=[InputRequired(message='Retype password')])
    username=StringField('User Name',validators=[InputRequired(message='User Name is required')])
    location=StringField('Location',validators=[InputRequired(message='Location is required')])
    biography=TextAreaField('Biography',validators=[InputRequired(message='Biography is required')])
    profile_photo = FileField('Image', validators=[FileRequired('Please input a file'), FileAllowed(['jpg', 'jpeg','png'], 'Images only!')])


class FollowForm(FlaskForm):
    userid=HiddenField("TargetUser")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(message='Username is required')])
    password = PasswordField('Password', validators=[InputRequired(message='Password is required')])
