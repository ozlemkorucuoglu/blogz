from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz-ozzie@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'u351kGays&zP4B'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(250))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,title,body, owner):
        self.title = title
        self.body = body
        self.owner=owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs=db.relationship('Blog',backref='owner')
       
    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET']) 
def login():    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/new_post')
        if user and user.password != password:
            flash('User password incorrect', 'error')
            return render_template('login.html')
        if not user:
            flash('User does not exist', 'error')
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST']) 
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify=request.form['verify']

        if not username:
            flash('That is not a valid username')
            return redirect('/signup')
        if not password:
            flash('That is not a valid password')
            return redirect('/signup')
        if not verify:
            flash('Passwords do not match')
            return redirect('/signup')

        if len(username)<3:
            flash('Invalid username, username must be at least 3 characters')
            return redirect('/signup')

        if len(password)<3:
            flash('Invalid password, password must be at least 3 characters')
            return redirect('/signup')

        if password != verify:
            flash('Passwords do not match') 
            return redirect('/signup')
        users = User.query.filter_by(username=username).all()
        if users:
            flash("Username already exists!")
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username 
            return redirect('/new_post')
        else:
            flash("Username already exist!")
            return render_template('signup.html')
    else:
        return render_template('signup.html')


@app.route('/logout') 
def logout():  
    del session['username']
    return redirect("/blog")


@app.route('/', methods=['POST', 'GET']) 
def index(): 
    
    
    users = User.query.with_entities(User.username).all()

    name_value = request.args.get('username')
    user_id = User.query.filter_by(username=name_value).first()
    if name_value:
        this_blog = Blog.query.filter_by(owner_id=user_id.id).all()
        return render_template('SingleUser.html', blogs=this_blog)


    return render_template('index.html',users=users)



@app.route('/new_post', methods=['POST', 'GET']) 
def new_post():
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        blog_title = request.form['Title']
        blog_body = request.form['Blog']

        title_error=''
        blog_error=''

        if not blog_title:
            title_error='Please fill in the title' 
        if not blog_body: 
            blog_error='Please fill in the body'

        
        if not title_error and not blog_error:

            new_blog= Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            
            blogs = Blog.query.all()

            id_value = new_blog.id
            this_blog = Blog.query.filter_by(id=id_value).all()
            return redirect("/blog?id={0}".format(id_value)) 
        else:
            return render_template('new_post.html', title_error=title_error, blog_error=blog_error, blog_title=blog_title, blog_body=blog_body)
    else:
        return render_template('new_post.html')


@app.route('/blog', methods=['POST', 'GET']) 
def blog():
    blogs = Blog.query.all()

    
    id_value = request.args.get('id')
    if id_value:
        this_blog = Blog.query.filter_by(id=id_value).all()
        return render_template('blog.html', id=id, blogs=this_blog)

    name_value = request.args.get('username')
    user_id = User.query.filter_by(username=name_value).first()
    if name_value:
        this_blog = Blog.query.filter_by(owner_id=user_id.id).all()
        return render_template('blog.html', blogs=this_blog)


    return render_template('blog.html',blogs=blogs)
   

if __name__ == '__main__':
    app.run()

