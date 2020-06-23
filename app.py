from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Blogs
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

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

#Index
@app.route('/')
def index():
    return render_template('home.html')

#about
@app.route('/about')
def about():
    return render_template('about.html')

#all Blogs
@app.route('/blogs')
def blogs():
    return render_template('blogs.html',blogs = BLOG_DATA)

#Single Blog
@app.route('/blog/<string:id>')
def singleBlog(id):
    return render_template('single_blog.html',id=id)

#Register form class
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

#Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create Cursor
        curr = mysql.connection.cursor()

        #Execute
        curr.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",(name, email, username, password))

        #Commit
        mysql.connection.commit()

        #Close Connection
        curr.close()

        flash('You are now registered, Login Now!','success')

        return redirect(url_for('login'))
        
    return render_template('signup.html', form=form)

#Login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        #get form fields
        username = request.form['username']
        password_candidate = request.form['password'] 

        #cursor
        curr = mysql.connection.cursor()
        #get user by username
        result = curr.execute("SELECT * FROM users WHERE username = %s",[username])
        app.logger.info(result)
        #if any row found
        if result > 0:
            #get hash
            data = curr.fetchone()
            password = data['password']
            #compare pass
            if sha256_crypt.verify(password_candidate,password):
                app.logger.info('PASSWORD MATCHED')
                session['logged_in'] = True
                session['username'] = username
                flash('Logged in successfully', 'success')
                return redirect(url_for('dashboard'))
            else:
                app.logger.info('INavlid Username/Password')
                flash('Invalid Username / Password','danger')
            #Close connection
            curr.close()
        else:
            app.logger.info('NO USER FOUND')
            flash('Invalid Username / Password','danger')
    
    return render_template('login.html')

#check user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorised, Please Login','danger')
            return redirect(url_for('login'))
    return wrap

#Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully !','success')
    return redirect(url_for('login'))


#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.secret_key = 'efew_5%&^8ndF4Q8z\c]/'
    app.run(debug=True)