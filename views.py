from flask import Flask, render_template, request, url_for, flash, redirect, g, _app_ctx_stack, send_from_directory
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from forms import LoginForm, URL_Submit, RegistrationForm
import os
from sys import argv
import feedparser
from lxml import etree, html
import urllib2
from SQL_Alchemy_LXML import *
from operator import itemgetter, attrgetter
from jinja2 import Environment, PackageLoader
from time import strptime, strftime, mktime, gmtime, struct_time
from datetime import datetime
import pytz
import calendar
from dateutil import parser as du_parser

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
    g.user = current_user

### End LoginHandler setting

@app.route('/favicon.ico')
def favicon():
   return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

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

        else:
           flash("[Invalid login]")

        return redirect(url_for('home'))

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

#make a new user in the DB
@app.route("/new_user_registration", methods=['GET', 'POST'])
def make_user():

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
        user_name = form.username.data,
        email = form.email.data,
        password = form.password.data)

        new_user = User.query.filter_by(email=form.email.data).first()

        if new_user is None:
            session.add(user)
            session.commit()
            flash('Thanks for registering')

        else:
            flash("[User already exists]")

        return redirect(url_for('login'))

    return render_template('new_user.html', title='Sign Up for R2S2', form=form)

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
        read_url = urllib2.urlopen(url).read()
        submitted_url = html.fromstring(read_url)
        feed_url = submitted_url.xpath("//link[@rel='alternate']/@href")[0]

        feed = Feed.query.filter_by(feed_link=feed_url).first()

        # checks if feed url already exists in db and adds info if not
        if feed is None:

            feed = Feed(feed_link = feed_url)
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

    # retireiving the all the feed objects based on the feed_ids from the current user
    user_feed_objects = Feed.query.filter(Feed.feed_id.in_(feed_id_list)).all()

    #sort the posts in python then pass into template to be rendered
    user_feed_posts = Post.query.filter(Post.feed_id.in_(feed_id_list)).all()

    user_post_info = sorted(user_feed_posts, key=attrgetter('timestamp'), reverse=False)

    return render_template('home.html',
            header= 'All zee posts',
            user = user,
            feed_list= user_feed_objects,
            post_list = user_post_info)

@app.route("/show_me_da_feeds")
@login_required
def all_da_feeds_seperated():
    user = g.user

    this_user = user.user_id

    user_info = User_Feed.query.filter_by(user_id=this_user).all()

    # creating an empty list to house all the feed_ids of the current_user
    feed_list = []

    # looping through the list of the User_Feed Objects to access just the feed_ids
    for feed in user_info:
        feed_id = feed.feed_id
        feed_list.append(feed_id)

    # retireiving the all the feed objects based on the feed_ids from the current user
    user_feed_objects = Feed.query.filter(Feed.feed_id.in_(feed_list)).all()

    return render_template('feed_titles.html', feed_list=user_feed_objects, user=user)

@app.route('/feed/<feed_id>')
@login_required
def show_post(feed_id=None):
    user = g.user
    this_user = user.user_id

    user_post_info = Post.query.filter_by(feed_id=feed_id).all()
    print "<<POST INFO>>", user_post_info

    return render_template('feed_posts.html', feed_id=feed_id, user=user, all_post_info=user_post_info)


@app.route("/remove_feed/<feed_id>")
@login_required
def remove_feed(feed_id=None):
    user = g.user
    this_user = user.user_id

    feed_delete = User_Feed.query.filter_by(feed_id=feed_id, user_id=this_user).all()

    feed_list = []
    for feed_d in feed_delete:
        feed_list.append(feed_d)

    final_id_list = []
    for user_feed_item in feed_list:
        user_feed_ID = user_feed_item.user_feed_id
        final_id_list.append(user_feed_ID)

    # import pdb; pdb.set_trace()

    user_feed_num = User_Feed.query.filter(User_Feed.user_feed_id.in_(final_id_list)).all()

    for num in user_feed_num:
        session.delete(num)
        session.commit()

    flash("[Removed the feed!]")

    return redirect(url_for('home'))

    return render_template('remove_feed.html', feed_id=feed_id, user=user)

if __name__ == '__main__':
    app.run(debug=True)
