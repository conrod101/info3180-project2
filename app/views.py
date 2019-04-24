"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
import os,datetime
from functools import wraps
from app import app,db
from flask import render_template,redirect, url_for,request, flash, jsonify,session,abort
from flask_login import login_user, logout_user, current_user, login_required
from app import models
from .forms import SignUpForm,LoginForm,Upload
from werkzeug.utils import secure_filename
from app.models import User,Post, Follow, Like
from werkzeug.security import generate_password_hash, check_password_hash
from .data import current_date
import jwt



###
# Routing for your application.
###


# Please create all new routes and view functions above this route.
# This route is now our catch all route for our VueJS single page
# application.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    """
    Because we use HTML5 history mode in vue-router we need to configure our
    web server to redirect all routes to index.html. Hence the additional route
    "/<path:path".

    Also we will render the initial webpage and then let VueJS take control.
    """
    return render_template('index.html')



def jwt_token_required(fn):
    """A decorator functions that secures endpoints that require
    the user to be logged in"""
    @wraps(fn)
    def decorated(*args,**kwargs):
        jwt_token = request.headers.get('Authorization')
        if jwt_token == None:
            return jsonify_errors(['ACCESS DENIED: No token provided'])
        else:
            token_parts = jwt_token.split()
            
            if token_parts[0].lower() != 'bearer':
                return jsonify_errors(['Invalid schema for token'])
            elif len(token_parts) == 1:
                return jsonify_errors(['Token not found'])
            elif len(token_parts)>2:
                return jsonify_errors(['Invalid Token'])
            
            jwt_token = token_parts[1]
            
            try:
                user_data    = jwt.decode(jwt_token,app.config['SECRET_KEY'])
                current_user = User.query.filter_by(username = user_data['user']).first()
            except jwt.exceptions.InvalidSignatureError:
                return jsonify_errors(['ACCESS DENIED: Ivalid Token'])
            except jwt.exceptions.DecodeError:
                return jsonify_errors(['ACCESS DENIED: Ivalid Token'])
            return fn(current_user,*args,**kwargs)
    return decorated

@app.route('/api/users/<user_id>',methods = ['GET'])
@jwt_token_required
def get_user_details(current_user,user_id):
    """Returns json object containing the details for the user with
    id <user_id>
    """
    print('here')
    user = User.query.filter_by(id = user_id).first()

    if user == None:
        return jsonify_errors(['User does not exist'])
    
    if request.method == 'GET':
        posts = Post.query.filter_by(userid = user.id)
        number_of_followers = Follow.query.filter_by(userid = user.id).count()
        user_data = dictify(user)
        user_data['joined_on'] = user_data['joined_on'].strftime("%d %B, %Y")
        del user_data['password']
        user_data['number_of_followers'] = number_of_followers
        posts = [post.photo for post in posts]
        return jsonify({'User':user_data,'Posts':posts})
        
#----------API ROUTES--------------API ROUTES-----------API ROUTES------------------#






#------------------Authentication Routes------Authentication Routes--Authentication Routes--------------#





#------------------ Login Route ----------------------#

@app.route('/api/auth/login',methods = ["POST"])
def login():
    loginForm=LoginForm()
    
    if request.method == "POST" and loginForm.validate_on_submit():
        
        username = loginForm.username.data.lower()
        password = loginForm.password.data
        users = User.query.filter_by(username=username).all()
        
        if len(users) == 0:
            return jsonify_errors(['Invalid username or password'])
        #elif not check_password_hash (users[0].password.password):
            return jsonify_errors(['Invalid username or password'])
            
        else :
            user = users[0]
            
            jwt_token = jwt.encode({'user': user.username}, app.config['SECRET_KEY'],algorithm = 'HS256')
            
            response = {'message': 'User successfully logged in', 'jwt_token':jwt_token,'current_user':user.id}
            return jsonify(response)
        return jsonify_errors(form_errors(loginForm))
    
        


#------------------ Logout Route ----------------------#

@app.route('/api/auth/logout', methods= ["GET"])
# @jwt_tokenrequired @login_required
def logout(current_user):
    
    if request.method == "GET":
        logout_user()
        response = {'message': 'Logout Successful'}
        return jsonify(response)
    else:
        error = {'Errors': 'Logout could not be completed'}
        return jsonify(error)






#-------------Users Routes------------Users Routes-----Users Routes--------------------#
#------------------Register Route----------------------#

@app.route('/api/users/register', methods = ['POST','GET'])
def register():
    upForm = SignUpForm()
    
    if request.method == 'POST' and upForm.validate_on_submit():
        
        users_with_username = User.query.filter_by(username = upForm.username.data).all()
        if len(users_with_username) >0:
            return jsonify_errors(['Username unavailable'])
            
        firstname       = upForm.firstname.data
        lastname        = upForm.lastname.data
        username        = upForm.username.data.lower()
        hashed_password = generate_password_hash(upForm.password.data)
        location        = upForm.location.data
        email           = upForm.email.data
        bio             = upForm.biography.data
        
        photo    = request.files['photo']
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        user = User(username = username, password = hashed_password, firstname = firstname,\
        lastname = lastname, email = email, location = location, biography = bio, \
        profile_photo = filename, joined_on = current_date())
        
        db.session.add(user)
        db.session.commit()
        
        response = {'message': 'User successfully registered'}
        return jsonify(response)
        
        
    return jsonify_errors(form_errors(upForm))
    



#---------------------------Posts Routes-----------------------------

@app.route("/api/users/user_id/posts", methods=['POST'])
def addPost(userid):
    
    newPost = Upload()
    
    if request.method == 'POST' and newPost.validate_on_submit():
        photo    = request.files['photo']
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
  
        caption = newPost.caption.data
        
        nPost = Post(userid = userid, photo=filename, caption=caption, created_on=current_date()) 
        
        db.session.add(nPost)
        db.session.commit()
        response = {'message': 'Posting Success! '}
        return jsonify(response)
    
    return jsonify_errors(form_errors(newPost))

@app.route("/api/users/user_id/posts", methods = ['GET'])
def viewPost(userid):
    userpost = Post.query.get(int(userid))
    likes = Like.query.filter(Like.postid == userpost.id).count()
    username = User.query(User.username).filter(User.id == userpost.userid)
    response = {"post_id": userpost.id, "userid": userpost.userid, "username": username, "photo": userpost.photo, "caption": userpost.caption, "created_on": userpost.created_on, "likes": likes}
        
    return jsonify(response)


@app.route("/api/posts", methods=['GET'])
def getAllPosts():
      
    posts = Post.query().all()
    
    response = []
    for p in posts:
        likes = Like.query.filter(Like.postid == p.id).count()
        username = User.query(User.username).filter(User.id == p.userid)
        response.append({"post_id": p.id, "userid": p.userid, "username": username, "photo": p.photo, "caption": p.caption, "created_on": p.created_on, "likes": likes})
        
    return jsonify(posts = response)



    
@app.route("/api/posts/<post_id>/like", methods=['POST'])
def likeAPost(post_id):
    like = Like(userid = user_id, postid = post_id)
    
    db.session.add(like)
    db.session.commit()
    
    likes = Like.query.filter(Like.postid == post_id).count()
     
    response = {'message': 'Post liked!', 'Likes': likes}
    return jsonify(response)





#------------------  ----------------------#
#Post_________________________

@app.route('/api/users/<user_id>/posts',methods = ['GET'])
@jwt_token_required
def view_posts(current_user,user_id):
    """Gets a jsonified list of all the posts made by 
    the user with id <user_id>
    """
    user = User.query.filter_by(id = user_id).first()
    if user == None:
        return jsonify({'error': 'This user does not exist'})
        
    if request.method == 'GET':
        posts         = Post.query.filter_by(userid = user_id).all()
        list_of_posts = [dictify(post) for post in posts]
        for post in list_of_posts:
            post['created_on'] = post['created_on'].strftime('%Y-%m-%d')
            print(post['created_on'])
        return jsonify({'POSTS':list_of_posts})


@app.route('/api/posts',methods = ['GET'])
def get_all_posts():
    """Returns a jsonified list of all posts made by all users"""
    if request.method == 'GET':
        all_posts         = Post.query.all()
        list_of_all_posts = [dictify(post) for post in all_posts]
        
        for post in list_of_all_posts:
            user = User.query.filter_by(id = post['userid']).first()
            post['username'] = user.username
            post['likes'] = Like.query.filter_by(postid = post['id']).count()
            post['created_on'] = post['created_on'].strftime("%d %B, %Y")
            post['user_image'] = user.profile_photo
        return jsonify({'POSTS':list_of_all_posts})
    

#------------------------Follow Routes--------------------------    
@app.route('/api/users/<user_id>/follow',methods = ['POST'])
@jwt_token_required
def follow_user(current_user,user_id):
    """Creates a relationship where the currently logged in 
    user follows the user with id <user_id>
    """
    user = User.query.filter_by(id = user_id).first()
    
    if user == None:
        return jsonify({'error': 'This user does not exist'})
    
    if request.method == 'POST':
        follower_id         = current_user.id
        
        pre_existing_relationship = Follow.query.filter_by(follower_id=follower_id,userid=user_id).first()
        
        if pre_existing_relationship == None:
            follow_relationship = Follow(follower_id=follower_id,userid=user_id)
            print(follow_relationship)
            db.session.add(follow_relationship)
            db.session.commit()
            response = {'message':'You are now following that user','newRelationship':'true'}
            return jsonify(response)
        else:
            response = {'message':'You are already following that user','newRelationship':'false'}
            print(response)
            return jsonify(response)
    

@app.route('/api/users/<user_id>/follow',methods = ['GET'])
@jwt_token_required
def get_number_of_followers(current_user,user_id):
    """Returns a json object with the number of followers for the 
    user with id <user_id>
    """
    user = User.query.filter_by(id = user_id).first()
    
    if user == None:
        return jsonify_errors(['This user does not exist'])
    
    if request.method == 'GET':
        number_of_followers = len(Follow.query.filter_by(userid = user_id).all())
        return jsonify({'followers':number_of_followers})


@app.route('/api/users/<user_id>/following',methods = ['GET'])
@jwt_token_required
def is_following(current_user,user_id):
    """Returns a json object telling whether or not 
    the currently loggd in user is following the user with id
    <user_id>
    """
    user = User.query.filter_by(id = user_id).first()
    
    if user == None:
        return jsonify_errors(['This user does not exist'])
    relationship = Follow.query.filter_by(userid = user_id,follower_id = current_user.id).first()
    
    if relationship == None:
        return jsonify({'following':False})
    else:
        return jsonify({'following':True})
    




###
# The functions below should be applicable to all Flask apps.
###

def jsonify_errors(list_of_errors):
    """Returns a json object containing the errors from the form"""
    errors_list = []
    for error in list_of_errors:
        errors_list.append(dict({'error':error}))
    return jsonify({'Errors':errors_list})
    
def form_errors(form):
    """Collects form errors from a Flask-WTF validation"""
    error_messages = []
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)
    return error_messages
    

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
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
