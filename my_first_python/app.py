from flask import Flask, request, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, FileField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length, Regexp
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import uuid as uuid
import os

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1955'
app.config['MYSQL_DB'] = 'blogs'

app.config['SECRET_KEY'] = 'blogpostproj'

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    login = SubmitField("Login")


class SignupForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    signup = SubmitField("Signup")


class BlogForm(FlaskForm):
    content = StringField("Content", validators=[
                          DataRequired(), Length(max=100)], widget=TextArea())
    image = FileField('Image', validators=[
                      DataRequired(), Regexp('/^.*jpg|jpeg$')])
    post = SubmitField("Post blog")


class User(UserMixin):
    def __init__(self, id: str, email: str, password: str):
        self.id = id
        self.email = email
        self.password = password

    @staticmethod
    def get(user_id):

        cursor = mysql.connection.cursor()
        try:
            user_id = int(user_id)
            cursor.execute('''SELECT * FROM users where id = %s''', (user_id,))
            res = cursor.fetchone()
            cursor.close()
            return User(res[0], res[1], res[2])
        except Exception as e:
            print("ERROR", e)

    def __str__(self) -> str:
        return f"<Id: {self.id}, Email: {self.email}>"

    def __repr__(self) -> str:
        return self.__str__()


@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)
    return user


mysql = MySQL(app)


@app.route("/home")
@app.route("/")
@login_required
def home():
    email = current_user.email
    blogs = []
    cursor = mysql.connection.cursor()
    try:
        cursor.execute(
            '''SELECT p.id, p.content, p.image, p.created_on, u.email FROM post AS p INNER JOIN users as u ON p.creator = u.id ORDER BY p.created_on desc''')
        res = cursor.fetchall()

        for blog in res:
            blogs.append(blog)

        cursor.close()
    except:
        pass

    return render_template(
        "home.html",
        blogs=blogs,
        email=email
    )


@app.route("/add-blog", methods=['POST', 'GET'])
@login_required
def add_blog():
    form = BlogForm()
    id = current_user.id

    if request.method == 'POST':
        content = request.form['content']
        image = request.files['image']

        image_name = secure_filename(image.filename)
        image_name = str(uuid.uuid1()) + '_' + image_name

        saver = request.files['image']
        cursor = mysql.connection.cursor()

        try:
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))
            cursor.execute(
                '''INSERT INTO post (content, image, creator) VALUES (%s, %s, %s)''', (content, image_name, id))
            mysql.connection.commit()
            cursor.close()
            flash("Blog uploaded successfully!")
            return redirect(url_for('home'))
        except Exception as e:
            cursor.close()

    return render_template(
        'blog_post.html',
        form=form
    )

@app.route('/delete-blog/<blog_id>', methods=['GET', 'POST'])
@login_required
def delete_blog(blog_id):
    cursor = mysql.connection.cursor()

    try:
        cursor.execute('''DELETE FROM post WHERE id = %s''', (blog_id, ))
        mysql.connection.commit()
        cursor.close()
        flash("Blog deleted successfully!", category='warning')
    except:
        cursor.close()
        flash("Some error occurred, Try again!", category='error')

    return redirect(url_for('home'))



@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!")
    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    email = None
    password = None
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        try:
            cursor.execute(
                '''SELECT * FROM users WHERE email = %s and pass = %s''', (email, password))
            res = cursor.fetchone()
            if res:
                user = User(res[0], res[1], res[2])
                res = login_user(user)
                cursor.close()
                return redirect(url_for('home'))
            else:
                flash("Email or password is wrong!", category='error')
                cursor.close()

        except Exception as e:
            cursor.close()

        form.email.data = ''
        form.password.data = ''

    return render_template(
        'login.html',
        email=email,
        password=password,
        form=form
    )


@app.route("/signup", methods=['GET', 'POST'])
def signup():

    name = None
    email = None
    password = None
    form = SignupForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        form.name.data = ''
        form.email.data = ''
        form.password.data = ''

        cursor = mysql.connection.cursor()
        try:
            cursor.execute(
                ''' INSERT INTO users (full_name, email, pass) VALUES (%s, %s, %s)''', (name, email, password))
            mysql.connection.commit()
            cursor.close()
            flash("User created successfully", category='message')
            return redirect(url_for('login'))

        except:
            cursor.close()
            flash("Email already registered!", category='error')

    return render_template(
        'signup.html',
        name=name,
        email=email,
        password=password,
        form=form
    )


app.run(host='localhost', port=5000, debug=True)
