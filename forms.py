from flask.ext.wtf import Form, validators
from flask.ext.wtf import TextAreaField, FloatField, PasswordField, IntegerField, DateField, BooleanField, SelectField, RadioField, SelectMultipleField
from wtforms import TextField

class LoginForm(Form):
    email = TextField('Email Address',
                      [validators.Email(message= (u'Invalid email address.'))])
    password = PasswordField('Password', [validators.Required(),
                             validators.length(min=6, max=25)], default='http://')
    remember_me = BooleanField('remember_me', default = False)


class URL_Submit(Form):
	url = TextField('URL', [validators.URL(require_tld=True, message= (u'[Not a valid URL]'))])

### Creating a new user
class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Email(message= (u'Invalid email address.'))])
    password = PasswordField('New Password', [validators.Required(), validators.EqualTo('confirm', message='Passwords must match'), validators.length(min=6, max=25)])
    confirm = PasswordField('Repeat Password')

### END Creating a new user
