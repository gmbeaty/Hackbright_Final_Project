from flask.ext.wtf import Form, validators
from flask.ext.wtf import TextAreaField, FloatField, PasswordField, IntegerField, DateField, BooleanField, SelectField, RadioField, SelectMultipleField
import SQL_Alchemy
from wtforms import TextField

class LoginForm(Form):
    email = TextField('Email Address',
                      [validators.Email(message= (u'Invalid email address.'))])
    password = PasswordField('Password', [validators.Required(), 
                             validators.length(min=6, max=25)])
    remember_me = BooleanField('remember_me', default = False)


class URL_Submit(Form):
	url = TextField('URL', [validators.URL(require_tld=True, message= (u'[Not a valid URL]'))])

### Creating a new user
class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Email(message= (u'Invalid email address.'))])
    password = PasswordField('New Password', [validators.Required(), validators.EqualTo('confirm', message='Passwords must match')])  
    confirm = PasswordField('Repeat Password')

### END Creating a new user

### CASSES HTML/JINJA




#END CASSIE JINJA

### Form helper file

#  This goes in a html file called _formhelper.html    
# {% macro render_field(field)%}
#   <dd>{{ field(**kwargs)|safe }}
#   {% if field.errors %}
#     <ul class=errors>
#     {% for error in field.errors %}
#       {{error}}
#     {% endfor %}
#     </ul>
#   {% endif %}
#   </dd>
# {% endmacro %}

### end formhelper

### Laureli Jinja/HTML

# <form action= "{{url_for('read_cookies')}}" method=post>

# <div id ='login_info'>
#     <p><label for="user_name"> 
#                     Username: </label>
#                     <input type='text' name="user_name"/>
#                 </p>
#                 <p><label for="password"> 
#                     Password: </label>
#                     <input type='password' name="password"/>
#                 </p>
#                     <input type="submit">
#                 </p>
#             </div>
#         </form> 

### End Laureli code