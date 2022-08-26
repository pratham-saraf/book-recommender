import json
import os
import uuid
import re
import datetime
from flask import Flask, render_template, request, redirect, url_for,flash,session,Response
from model.search import search , search_id
from model.recommender import recommender
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length,ValidationError,EqualTo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from itsdangerous import Serializer, URLSafeTimedSerializer, SignatureExpired
import pymongo

from flask_bcrypt import Bcrypt
appBcrypt = Flask(__name__)
bcrypt = Bcrypt(appBcrypt)


# app configs
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


client = pymongo.MongoClient(os.getenv('MONGO_DB'))
dbs = client['user_data']
db = dbs["users"]
book_db = dbs["user_book_data"]


app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEBUG'] = False
app.config["SESSION_PERMANENT"] = False

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

mail = Mail(app)

class User(UserMixin):

    def __init__(self, username, email, password,confirmed ,registered_on ,_id=None,):

        self.username = username
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id
        self.confirmed = confirmed
        self.registered_on = registered_on

    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self._id

    @classmethod
    def get_by_username(cls, username):
        data =db.find_one({"username": username})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_email(cls, email):
        data = db.find_one({"email": email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = db.find_one({"_id": _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(username, password):
        verify_user = User.get_by_username(username)
        if verify_user is not None:
            return bcrypt.check_password_hash(verify_user.password, password)
        return False

    @classmethod
    def register(cls, username, email, password):
        comfirmed = False
        registered_on = datetime.datetime.now()
        user = cls.get_by_email(email)
        if user is None:
            new_user = cls( username, email, password,comfirmed,registered_on)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        else:
            return False

    def save_to_mongo(self):
        data = {"username": self.username, "email": self.email, "password": self.password, "confirmed": self.confirmed, "_id": self._id, "registered_on": self.registered_on}
        db.insert_one(data)
@login_manager.user_loader
def load_user(user_id):
    temp = User.get_by_id(user_id)
    if temp is not None:
        return User.get_by_id(temp._id)
    else:
        return None


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')
    Submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    password2 = PasswordField(
        'Repeat Password', validators=[InputRequired(), EqualTo('password')])
    Submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.get_by_username(username.data)
        if user is not None:
            raise ValidationError('Please use a different username.')
        exp = "^[A-Za-z][A-Za-z0-9_.]{7,14}$"
        pat = re.compile(exp)
        if not pat.match(username.data):
            raise ValidationError('Username must be alphanumeric(A-Z , 0-9 , _ , .) and between 8 and 15 characters long')
        

    def validate_email(self, email):
        user = User.get_by_email(email.data)
        if user is not None:
            raise ValidationError('Please use a different email address.')


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if form.validate_on_submit() and request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        find_user = db.find_one({"username": username})

        if User.login_valid(username, password):
            loguser = User.get_by_username(username)
            login_user(loguser, remember=form.remember.data)
            return redirect(url_for('dashboard'))   
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))    
    return render_template("login.html", form=form)
        

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if form.validate_on_submit() and request.method == 'POST':
        
        password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')
        find_user = User.get_by_email(request.form["email"])
        find_username = User.get_by_username(request.form["username"])

        if find_user is None:
            if find_username is None:

                User.register(request.form["username"], request.form["email"], password)
                # email = request.form["email"]

                # token = serializer.dumps(email, salt='email-confirm-salt')
                
                # msg = Message('Confirm Email', sender='bookkritic3@gmail.com', recipients=[email])
                # link = url_for('confirm', token=token, _external=True)
                # msg.body = 'Your link is: {}'.format(link)
                # mail.send(msg)
                return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/confirm/<token>')
def confirm(token):
    try:
        email = serializer.loads(token, salt='email-confirm-salt', max_age=3600)
        user = User.get_by_email(email)
        if user.confirmed:
            flash('Account already confirmed. Please login.', 'success')
            return redirect(url_for('indec'))
        else:
            user.confirmed = True
            db.update_one({"_id": user._id}, {"$set": {"confirmed": True}})
            user = User.get_by_email(email)
            flash('You have confirmed your account. Thanks!', 'success')

            return redirect(url_for('login'))

    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
        

@app.route('/dashboard' , methods=['GET', 'POST'])
@login_required
def dashboard():

    user_book_data = book_db.find_one({"_id": current_user._id})
    books_id = set() 
    books = []
    if user_book_data is None:
        book_db.insert_one({"_id": current_user._id, "liked_books": []})
    else:    
        liked_books = user_book_data["liked_books"]
        for book in liked_books:
            books_id.add(book)
        for ids in books_id:
            books.append(search_id(ids))  
    return render_template('dashboard.html', books=books)

@app.route('/like', methods=['POST'])
def like():
    try:
        user_book_data = book_db.find_one({"_id": current_user._id})
        if user_book_data is None:
            book_db.insert_one({"_id": current_user._id, "liked_books": []})
        liked_books = user_book_data["liked_books"]
        if request.method == "POST":
            id = int(request.form["id"])
            if id not in liked_books:
                liked_books.append(id)
                book_db.update_one({"_id": current_user._id}, {"$set": {"liked_books": liked_books}})
                flash("Book added to your list!", "success")
                return  Response(status=200)
            else:
                flash("Book already in your list!", "danger")
                return Response(status=200)
    except:
         return  Response(status=404)

@app.route('/unlike', methods=['POST'])
def unlike():
    try:
        user_book_data = book_db.find_one({"_id": current_user._id})
        if user_book_data is None:
            book_db.insert_one({"_id": current_user._id, "liked_books": []})
        liked_books = user_book_data["liked_books"]
        if request.method == "POST":
            id = int(request.form["id"])
            if id in liked_books:
                liked_books.remove(id)
                book_db.update_one({"_id": current_user._id}, {"$set": {"liked_books": liked_books}})
                flash("Book added to your list!", "success")
                return  Response(status=200)
            else:
                flash("Book not in your list!", "danger")
                return Response(status=404)   
    except:
        return  Response(status=404)   

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/find", methods=["GET", "POST"])
@login_required
def find():
    return render_template("find.html")


@app.route("/search", methods=["POST"])
def search_route():
    term = request.form['q']
    print(term)
    result = search(term)
    return result , 200

@app.route("/recommendation_generator")
def recommendation_generator():
    user_book_data = book_db.find_one({"_id": current_user._id})   
    try:
        recommendations = user_book_data["recommendations"]
    except:
        recommendations = []
        book_db.update_one({"_id": current_user._id}, {"$set": {"recommendations": []}})

    liked_books = user_book_data["liked_books"]
    
    books= book_db.find_one({"_id": current_user._id})["liked_books"]
    if len(books) != 0:
        books_id = set()
        for book in books:
            book = str(book)
            books_id.add(book)
        books = books_id
        books = list(books)
        recommended_books = recommender(books)
        data = json.loads(recommended_books)
        for book in data:
            if int(book["book_id"]) in liked_books:
                data.remove(book)
            
        book_db.update_one({"_id": current_user._id}, {"$set": {"recommendations": data}})
        return recommended_books , 200

@app.route("/recommendation")
@login_required
def recommend_route():

   

    user_book_data = book_db.find_one({"_id": current_user._id})   
    try:
        recommendations = user_book_data["recommendations"]
    except:
        recommendations = []
        book_db.update_one({"_id": current_user._id}, {"$set": {"recommendations": []}})
    if recommendations is None:
        recommendations = []

    liked_books = user_book_data["liked_books"]
    books = []
    for book in recommendations:
        temp = int(book["book_id"])
        if temp in liked_books:
            continue
        books.append(search_id(temp))    
    return render_template("recommend.html", books=books)
        

    