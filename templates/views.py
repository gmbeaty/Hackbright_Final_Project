from flask import Flask, render_template, flash
from forms import LoginForm

app = Flask(__name__)
app.config.from_object('config')

user = { 'nickname' : 'Becca'}

@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	return render_template('login.html',
			title = 'Sign In',
			form = form)

@app.route("/")

def user_front_page():
	return render_template('index.html', 
			title = 'Home ',
			user = user)

@app.route("/home")

def home():
	posts = [
		{
			'author' : {'nickname' : 'Mo'},
			'title' : 'Coachella time', 
			'body' : 'Bandana Mo in full effect!'
		},
		{
			'author': {'nickname': 'Omar'} ,
			'title' : '#FriendLove',
			'body' : 'Mejjjooooor!'
		}
		]

	return render_template('home.html',
			title= 'All zee posts ',
			user=user,
			posts=posts)




