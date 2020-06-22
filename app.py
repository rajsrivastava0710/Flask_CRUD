from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Blogs
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

BLOG_DATA = Blogs(); 

# MySQL COnfiguration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'raj'
app.config['MYSQL_DB'] = 'blog_app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#Initialize MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    return render_template('login.html')



@app.route('/blogs')
def blogs():
    return render_template('blogs.html',blogs = BLOG_DATA)

@app.route('/blog/<string:id>')
def singleBlog(id):
    return render_template('single_blog.html',id=id)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=5, max=20),validators.DataRequired(),])
    email = StringField('Email', [validators.Length(min=6, max=50),validators.DataRequired(),])
    password = PasswordField('Password',[
        validators.Length(min=1, max=50),
        validators.DataRequired(),
        validators.Length(min=5, max=30)
    ])
    confirm = PasswordField('Confirm Password',[
        validators.DataRequired(),
        validators.EqualTo('password', message= 'Passwords do not match')])

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        
        return
    return render_template('signup.html', form=form)

if __name__ == ' __main__':
    app.run()