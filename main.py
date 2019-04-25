from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog-ozzie@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(250))

    def __init__(self,title,body):
        self.title = title
        self.body = body


@app.route('/', methods=['POST', 'GET']) 
def index():
    if request.method == 'POST':
        blog_title = request.form['Title']
        blog_body = request.form['Blog']

    blogs = Blog.query.all()
    return render_template('blog.html',title="Build a Blog", blogs=blogs)

@app.route('/new_post', methods=['POST', 'GET']) 
def new_post():
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

            new_blog= Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            
            blogs = Blog.query.all()

            id_value = new_blog.id
            this_blog = Blog.query.filter_by(id=id_value).all()
            #return render_template("/blog?id='{0}'".format(id_value), id=id, blogs=this_blog)
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

    return render_template('blog.html',title="Build a Blog", blogs=blogs)

if __name__ == '__main__':
    app.run()

