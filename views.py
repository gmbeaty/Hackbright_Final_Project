from flask import Flask, render_template, request, url_for, flash, redirect, g, _app_ctx_stack
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from forms import LoginForm, URL_Submit
import rsslib2 
from sys import argv
import feedparser
from SQL_Alchemy import *

app = Flask(__name__)
app.config.from_object('config')

### Start LoginHandler settings

lm = LoginManager()
lm.init_app(app)
lm.login_view = "/login"

@lm.user_loader
def load_user(user_id):
    return session.query(User).get(user_id)

@app.before_request
def before_request():
    # g = global and makes that user the global current user
    # do I need to reverse this?
    g.user = current_user
   
### End LoginHandler setting

# edit this to have users be retrieved from DB

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user is not None and current_user.is_authenticated():
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user =  session.query(User).\
                filter_by(email=form.email.data, password=form.password.data).\
                first()
                
        if user is not None:
           login_user(user)
           flash("Welcome")

        else:
           flash("[Invalid login]")

        return redirect(url_for('home'))
        
    return render_template('login.html', title='Sign In', form=form)


    #   flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
    #   return redirect('/home')

    # return render_template('login.html',
    #       title = 'Sign In',
    #       form = form,
    #       providers = app.config['OPENID_PROVIDERS'])


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route("/", methods = ['GET'])
@login_required

def display_user_front_page():

    user = g.user
    form = URL_Submit()

    return render_template('index.html', 
            user=user,
            title = 'Home ',
            form=form)

@app.route("/", methods = ['POST'])
@login_required
def display_user_front_page():
    user = g.user
    form = URL_Submit()

    # confirms the data submitted is a url
    if form.validate_on_submit(): 
        url = form.url.data
        feed = Feed.query.filter_by(feed_link=url).first()
        # checks if feed url already exists in db and adds info if not
        if feed is None:

            #need to add functions that associate the inputed feed with the current user

            feed = Feed(feed_link = url)
            feed.populate_metadata()
            feed.get_current_posts()
            session.add(feed)
            session.commit()
            session.refresh(feed)
            
        else:
            flash("[Feed already exists]")

        user_associate = User_Feed(user_id = user.user_id, feed_id = feed.feed_id) 
        session.add(user_associate)
        session.commit()
        return redirect(url_for('home'))

    return render_template('index.html', 
            user=user,
            title = 'Home ',
            form=form)

@app.route("/home")
@login_required
def home():  
    # setting user equal to the global/logged-in current user
    user = g.user

    # getting the user_id of the current_user
    user_key = user.user_id

    # querying for the current user's feed_ids
    user_feeds = User_Feed.query.filter_by(user_id=user_key).all()
    
    # creating an empty list to house all the feed_ids of the current_user 
    feed_id_list = []

    # looping through the list of the User_Feed Objects to access just the feed_ids
    for feed in user_feeds:
        feed_id = feed.feed_id
        feed_id_list.append(feed_id) 
        print "THIS IS A FEED_ID", feed_id

    # retireiving the all the feed objects based on the feed_ids from the current user
    user_feed_objects = Feed.query.filter(Feed.feed_id.in_(feed_id_list)).all()

    # user_post = Post.query.filter(Post.feed_id.in_(feed_id_list))
    # user_post_info = user_post.order_by(Post.timestamp.desc())
    # print input_path
    # encoded = input_path.encode('UTF-8')
    # print encoded
    # feed = rsslib2.rss_url_to_dict(encoded)

    return render_template('home.html', 
            header= 'All zee posts',
            user = user,
            feed_list= user_feed_objects,
            post_list = [])


if __name__ == '__main__':
    app.run(debug=True)
    



