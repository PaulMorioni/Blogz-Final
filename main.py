from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://new-blog:1234@localhost:8889/new-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(400))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id =db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True)
    password = db.Column(db.String(12))
    blogs = db.relationship('Blog', backref='owner')
        
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'home', 'index' '']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods = ['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template("index.html", title="Users", users=users)


@app.route('/home', methods=['POST','GET'])
def home():

    posts = Blog.query.all()
    return render_template("home.html", title="Home", blogs=posts)

@app.route('/new_entry', methods = ['POST','GET'])
def new_entry():
    
    owner = User.query.filter_by(username=session['username']).first()
    post_body=''
    post_name=''

    if request.method == 'POST':
        post_name = request.form.get('blog_title')
        post_body = request.form.get('blog_body')

        if post_name:

            if post_body:
                new_post = Blog(post_name, post_body, owner)
                db.session.add(new_post)
                db.session.commit()
                post_id = new_post.id
                post_id_str=str(post_id)
                url = '/post?id=' + post_id_str
                return redirect(url)
            else:
                flash('Body Required', 'error')
        else:
            flash('Title Required', 'error')
    
    return render_template("add_post.html", title="New Post", post_body = post_body, post_name = post_name)

@app.route('/post', methods=['POST','GET'])   
def post_page():
    post_id = request.args.get("id")
    post = Blog.query.get(post_id)
    user_id = post.owner_id
    user = User.query.filter_by(id=user_id).first()
    username = user.username
    return render_template("post_page.html", user=user, blog=post, owner=username)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/new_entry')
        if user and not user.password == password:
            flash('Password Incorrect', 'error')
            return render_template('login.html', username = username)
        if not user:
            flash('User does not exist', 'error')
            return render_template('login.html')
        else:
            flash('Unknown Error', 'error')
        
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if not username or not password or not verify:
            flash('One or more fields left blank', 'error')
        else:    
            if len(password) < 3 or len(password) > 12 or len(username) < 3 or len(username) > 12:
                flash("Username and Password must be between 3 and 12 characters", 'error')
            else:
                if password == verify:
                    existing_user = User.query.filter_by(username=username).first()
                    if not existing_user:
                        new_user = User(username, password)
                        db.session.add(new_user)
                        db.session.commit()
                        session['username'] = username
                        flash('Thank you for creating an account')
                        return redirect('/home')
                    else:
                        flash('Duplicate User', 'error')
                else:
                    flash('Passwords do not match', 'error')

    return render_template('register.html')

@app.route('/user', methods=['POST', 'GET'])
def user_page():
    user_id = request.args.get("user_id")
    user = User.query.filter_by(id=user_id).first()
    blogs = user.blogs
    return render_template('singleUser.html', user=user, blogs=blogs)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')

if __name__ == '__main__':
    app.run()