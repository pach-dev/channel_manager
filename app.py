# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, logout_user
import bcrypt
from datetime import datetime, timezone

# Initialize Flask app
app = Flask(__name__)
app.secret_key ="matohogthanio"

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///channels.db'
db = SQLAlchemy(app)


#Initialize Login Manager Class
login_manager = LoginManager()
login_manager.init_app(app)




# Define User model
class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    comments = db.relationship('Comments', backref='channel', lazy=True)

class Users(db.Model):
    #__table__= 'users'
    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(100), unique=True, nullable=False)
    email=db.Column(db.String(50), nullable=False )
    password=db.Column(db.String(100))
    

#Initialize the Class Users within extension
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    #Function to check the Password
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# Add a comment section on the flask app.
#1 Make a Class or db model for the Comment section
class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)

    # a special method for representing the objects in a class as a string
    def __repr__(self):
        return (f"Comment {self.date_posted}, {self.content}")




# Create database tables
with app.app_context():
    db.create_all()

# Default Route
@app.route('/')
def index():
    #channels = Channel.query.all()
    #return render_template('index.html', channels=channels)
    return render_template('index.html')


# CRUD Routes
#Registration Page handler

@app.route('/register', methods = ['GET', 'POST'])
def register():
    # If the user made a POST request, create a new user
    if request.method =='POST':
        username = request.form['username']
        email=request.form['email']
        password=request.form['password']
        new_user = Users(username=username, email=email, password=password)
        #Add the user to the database
        db.session.add(new_user)
        #Commit the changes made
        db.session.commit()
        #Once user has been created, he/she is redirected to log in
        return redirect('login')
    
    # Renders sign_up template if the user made a GET request.
    return render_template('register.html')

# For Logging in users using user_loader callback function
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

#Log in route for users
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    channels = Channel.query.all()
    # If a post request was made, find the user by 
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']

        user = Users.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['loggedin'] = True
            session['email'] = user.email
            session['username'] = user.username
            return render_template('dashboard.html', channels=channels)

        

        #
        #else:
            #flash("Email or user details incorrect")
            #return redirect('login')
    return render_template('login.html')


        
    

#Dashboard to view Channels if user Logged in
@app.route('/dashboard', methods = ['POST', 'GET'])
def dash():

    #user = Users.query.filter_by(email=session['email']).first()
    channels = Channel.query.all()
    content = Comments.query.order_by(Comments.date_posted.desc()) 

    return render_template('dashboard.html',  channels=channels, content=content)


# Create Channel
@app.route('/add_channel', methods=['GET', 'POST'])
def add_channel():
    if request.method == 'POST':
        name = request.form['name']
        number = request.form['number']
        category = request.form['category']
        new_channel = Channel(name=name, number=number, category=category)
        db.session.add(new_channel)
        db.session.commit()
        flash('Added')
        return redirect ('dashboard')
    return render_template('add_channel.html')



# Update Channel
@app.route('/edit_channel/<int:channel_id>', methods=['GET', 'POST'])
def edit_channel(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    comments = Comments.query.filter_by(channel_id=channel_id).order_by(Comments.date_posted.desc()).all()
    if request.method == 'POST':
        channel.name = request.form['name']
        channel.number = request.form['number']
        channel.category = request.form['category']
        content = request.form['content']
        date_posted = datetime.now(timezone.utc)
        new_comment = Comments(date_posted=date_posted, content=content,channel_id=channel_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Updated')
        return redirect ('dashboard')
    return render_template('edit_channel.html') 

# Delete Channel
@app.route('/delete_channel/<int:channel_id>', methods=['POST'])
def delete_channel(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    db.session.delete(channel)
    db.session.commit()
    flash('Deleted')
    return redirect('dashboard')

#Comment section for the user comments = Comment.query.order_by(Comment.date_posted.desc()).all()

#@app.route('/comment', methods = ['POST','GET'])
#def add_comment():
    #comment = Comments.query.order_by(Comments.date_posted.desc()).all()
    #if request.method == 'POST':
        #username = request.form['username']
       # content = request.form['content']
        #new_comment = Comments (username=username, date_posted = datetime.now(), content=content)
        #db.session.add(new_comment)
        #db.session.commit()
        #return redirect ('dashboard')

            

#Logout the user session

@app.route('/logout')
def logout():
    logout_user()
    session.pop('email', None)
    return redirect('logout.html')


# Run the application
if __name__ == '__main__':
    app.run(debug = True)