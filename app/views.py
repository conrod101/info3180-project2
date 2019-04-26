"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
from json import JSONEncoder
from app import app, db, filefolder,login_manager,token_key
from flask import render_template, request, url_for ,redirect,flash,jsonify, g, session
from flask_login import login_user, logout_user, current_user, login_required
from .forms import LoginForm, PostForm, RegisterForm
from .models import Users, Posts, Follows, Likes
from werkzeug.utils import secure_filename
import os
import datetime
import jwt
from functools import wraps
postfolder='static/images/'





def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.headers.get('Authorization', None)
    if not auth:
      return jsonify({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'}), 401

    parts = auth.split()

    if parts[0].lower() != 'bearer':
      return jsonify({'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}), 401
    elif len(parts) == 1:
      return jsonify({'code': 'invalid_header', 'description': 'Token not found'}), 401
    elif len(parts) > 2:
      return jsonify({'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}), 401

    token = parts[1]
    try:
         payload = jwt.decode(token, token_key)
         get_user = Users.query.filter_by(id=payload['user_id']).first()

    except jwt.ExpiredSignature:
        return jsonify({'code': 'token_expired', 'description': 'token is expired'}), 401
    except jwt.DecodeError:
        return jsonify({'code': 'token_invalid_signature', 'description': 'Token signature is invalid'}), 401

    g.current_user = user = get_user
    return f(*args, **kwargs)

  return decorated

@app.route('/')
def index():
    """Render website's initial page and let VueJS take over."""
    return render_template('index.html')





@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)

@app.route("/api/users/register",methods=["POST"])
def register():
    form=RegisterForm()
    if request.method=="POST" and form.validate_on_submit():
        if form.password.data!=form.confirmpassword.data:
            return jsonify (errors=[{'error':['Passwords do not match']}])
        usernametest=Users.query.filter_by(username=form.username.data).first()
        emailtest=Users.query.filter_by(email=form.email.data).first()
        if usernametest is not None or emailtest is not None:
            if usernametest is not None:
                return jsonify(errors=[{'error':['Username not available. Please enter a different username']}])
            if emailtest is not None:
                return jsonify(errors=[{'error':['Email not available. Please use a different email address']}])
        else:
            fileupd=form.profile_photo.data
            filename=secure_filename(fileupd.filename)
            created=datetime.datetime.now()
            user=Users(form.fname.data,form.lname.data,form.username.data,form.email.data,form.password.data,form.location.data,form.biography.data,filename,created)
            db.session.add(user)
            db.session.commit()
            fileupd.save(os.path.join(filefolder,filename))
            usertest=Users.query.filter_by(username=form.username.data).first()
            if usertest is not None:
                return jsonify(response=[{'message':'Account created','username':usertest.username}])
                
            else:
                return jsonify(errors=[{'error':['Your account was not added. Please try again']}])
    error=[{'error':form_errors(form)}]
    return jsonify(errors=error)

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

@app.route("/api/auth/login", methods=["POST"])
def login():
    #if session['userid']:
    #    return jsonify(errors=[{'error':['You are already logged in.']}])
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        # change this to actually validate the entire form submission
        # and not just one field
        username=form.username.data
        password=form.password.data
        
        user=Users.query.filter_by(username=username,password=password).first()
            # Get the username and password values from the form.
        if user is not None:
            payload = {'user_id' : user.id}
            token = jwt.encode(payload, token_key).decode('utf-8')
            session['userid'] = user.id;
            return jsonify(response=[{'message':'Log in successful','token': token, 'userid': user.id,'userphoto':postfolder+user.profile_photo}])
            flash('You were successfully logged in')
        else:
            return jsonify(errors=[{'error':['Password and user name does not match our records.']}])
            flash('Password and user name does not match our records')
    return jsonify(errors=[{'error':form_errors(form)}])


@app.route("/api/auth/logout",methods=["GET"])
@requires_auth
def logout():
    g.current_user=None
    if session['userid']:
        session.pop('userid')
    return jsonify(response=[{'message':'User successfully logged out.'}])

    
@app.route("/api/users/<int:user_id>/posts",methods=["GET","POST"])
@requires_auth
def addpost(user_id):
    form=PostForm()
    if request.method=="GET":
        thisuser=''
        if user_id==0 or user_id==session['userid']:
            uid=session['userid']
            thisuser='Yes'
            
        else:
            uid=user_id
            thisuser='No'
        user=Users.query.filter_by(id=uid).first()
        if user is not None:
            userinfo={'id':user.id,'username':user.username,'fname':user.first_name,'lname':user.last_name,'location':user.location,'photo':postfolder+user.profile_photo,'bio':user.biography,'joined':user.joined_on.strftime("%B %Y")}
            posts=Posts.query.filter_by(user_id=uid).all()
            follows=Follows.query.filter_by(user_id=uid).all()
            following=Follows.query.filter_by(follower_id=session['userid'], user_id=uid).first()
            isfollowing=''
            if following is None:
                isfollowing='No'
            else:
                isfollowing='Yes'
            return jsonify(response=[{'posts':[review_post(posts)],'numposts':len(posts),'follows':len(follows),'userinfo':userinfo,'current':thisuser,'following':isfollowing}])
        else:
            return jsonify(error={'error':'User does not exist'});
    if request.method=="POST" and form.validate_on_submit():
        image=form.photo.data
        filename=secure_filename(image.filename)
        created=datetime.datetime.now()
        post=Posts(session['userid'],filename,form.caption.data,created)
        db.session.add(post)
        db.session.commit()
        image.save(os.path.join(filefolder,filename))
        return jsonify(response=[{'message':'Post added successfully'}])
    return jsonify(errors=[{'error':form_errors(form)}])
    
@app.route("/api/users/<int:user_id>/follow",methods=["POST"])
@requires_auth
def follow(user_id):
    if request.method=="POST":
        follow=Follows(user_id,session['userid'])
        db.session.add(follow)
        db.session.commit()
        user=Users.query.filter_by(id=user_id).first()
        return jsonify(response={'message':'You are now following '+user.username})
    
@app.route("/api/posts",methods=["GET"])
@requires_auth
def getpost():
    posts=Posts.query.order_by(Posts.created_on.desc()).all()
    return jsonify(response=[{'posts':review_post(posts)}])
        
@app.route("/api/posts/<int:post_id>/like",methods=["POST"])
@requires_auth
def likepost(post_id):
    if request.method=="POST":
        like=Likes(session['userid'],post_id)
        db.session.add(like)
        db.session.commit()
        count=likes_counter(post_id)
        return jsonify(response=[{'message':'Post Liked'}])
        

def form_errors(form):
    error_messages = []
    """Collects form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)

    return error_messages



@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))



def review_post(posts):
    like_tester='';
    newposts=[]
    for i in range (0,len(posts)):
        user=Users.query.filter_by(id=posts[i].user_id).first();
        username=user.username;
        profilephoto=user.profile_photo;
        likevar=Likes.query.filter_by(post_id=posts[i].id,user_id=session['userid']).first()
        if likevar is None:
            like_tester='No'
        else:
            like_tester='Yes'
        wisdom={
        'id':posts[i].id,
        'user_id':posts[i].user_id,
        'photo':postfolder+posts[i].photo,
        'caption':posts[i].caption,
        'created_on':posts[i].created_on.strftime("%d %b %Y"),
        'likes':likes_counter(posts[i].id),
        'username':username,
        'userphoto':postfolder+profilephoto,
        'likebyuser':like_tester
        }
        newposts.append(wisdom)
    return newposts
        
def likes_counter(post_id):
    count=Likes.query.filter_by(post_id=post_id).all()
    return len(count)
    


@app.after_request
def add_header(response):

    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
