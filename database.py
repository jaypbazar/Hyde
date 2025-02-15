from flask_sqlalchemy import SQLAlchemy
import bcrypt

# Create a SQLAlchemy instance without binding it to a Flask app
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Function to hash a password
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

# Function to verify a password
def verify_password(hashed_password, input_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)

# Function to add a new user to the database
def add_user(username, password):
    hashed_password = hash_password(password)
    new_user = User(username=username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return new_user

# Function to find a user by username
def find_user(username):
    return User.query.filter_by(username=username).first()

# Function to initialize the database
def init_db(app):
    db.init_app(app)  # Bind the SQLAlchemy instance to the Flask app
    with app.app_context():
        db.create_all()  # Create all database tables
