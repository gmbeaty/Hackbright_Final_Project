from flask import Flask, render_template, flash, redirect
from forms import LoginForm
from rsslib2 import rss_entry_to_html, rss_to_html
from sys import argv
import feedparser

# filename, input_path = argv

app = Flask(__name__)
app.config.from_object('config')

user = {'nickname' : 'Becca'}


@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
		return redirect('/home')
	return render_template('login.html',
			title = 'Sign In',
			form = form,
			providers = app.config['OPENID_PROVIDERS'])

@app.route("/")

def user_front_page():
	return render_template('index.html', 
			title = 'Home ',
			user = user)

@app.route("/home")

def home():
	# input_path = "http://fortydaysofdating.com/feed/"
	# input_path = "http://blog.hackbrightacademy.com/feed/"
	input_path = "http://terrytao.wordpress.com/feed/"
	# input_path = "http://atlantic-pacific.blogspot.com/feeds/posts/default"
	# input_path = "http://rss.cnn.com/rss/cnn_topstories.rss"
	encoded = input_path.encode('UTF-8')
	feed = rss_to_html(encoded)

	# print type(feed)
	# print type(input_path)
	# encoded = feed.encode('UTF-8')
	# print feed.title
	# print "^^^TITLE^^^"



# def home():
# 	posts = [
# 		{
# 			'author' : {'nickname' : 'Mo'},
# 			'title' : 'Coachella time', 
# 			'body' : 'Bandana Mo in full effect!'
# 		},
# 		{
# 			'author': {'nickname': 'Omar'} ,
# 			'title' : '#FriendLove',
# 			'body' : 'Mejjjooooor!'
# 		}
# 		]

	home_page = render_template('home.html', 
			header= 'All zee posts',
			user=user,
			topics= feed)
	return home_page



