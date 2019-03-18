"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import ProfileForm
from app.models import UserProfile
from werkzeug.security import check_password_hash
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from .forms import ProfileForm
from app.models import UserProfile
from .data import get_date,format_date
###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/profile',methods = ["GET","POST"])
def profile():
    """Render the website's profile page"""
    form   = ProfileForm()
    us_Id = len(UserProfile.query.all())
    
    if request.method == "POST" and form.validate_on_submit():
        
        first_name = form.first_name.data
        last_name  = form.last_name.data
        gender     = form.gender.data
        location   = form.location.data
        email      = form.email.data
        bio        = form.biography.data
        date       = format_date(get_date())
        image      = form.image.data
        imageName  = first_name + last_name + str(us_Id + 1)
        
        newUser = UserProfile(
                                first_name = first_name,
                                last_name  = last_name,
                                gender     = gender,
                                location   = location,
                                email      = email,
                                biography  = bio,
                                created_on = date,
                                profilePic = imageName)
        db.session.add(newUser)
        db.session.commit()
        
        image.save("app/static/profilepictures/" + imageName + ".png")
        
        flash("New User Profile Created", "success")
        return redirect(url_for("profiles"))
        
    return render_template("profile.html",form=form)

@app.route('/about/')
def about():
 
    return render_template('about.html')


@app.route('/profile/<userid>')
def userProfile(userid):
   
    user = UserProfile.query.filter_by(id = userid).first()
    return render_template('userprofile.html',user = user,date = format_date(user.created_on))


# @app.route('/<file_name>.txt')
# def send_text_file(file_name):
#     """Send your static text file."""
#     file_dot_text = file_name + '.txt'
#     return app.send_static_file(file_dot_text)

@app.route('/profiles')
def profiles():
    """Render the website's list of profiles"""
    users = UserProfile.query.all()
    return render_template("profiles.html",users = users)





# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session

###
# The functions below should be applicable to all Flask apps.
###

@app.route('/secure_page')
@login_required
def secure_page():
    """Render a secure page on our website that only logged in users can access."""
    return render_template('secure_page.html')
    
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'danger')
    return redirect(url_for('home'))


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
