from flask import Flask, render_template, request, redirect, make_response,flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_BINDS'] = {'info' : 'sqlite:///info.db'}
app.config['SECRET_KEY'] = 'some random string'
db = SQLAlchemy(app)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(20), nullable=False, default='N/A')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'Blog post ' + str(self.id)

class BlogInfo(db.Model):
    __bind_key__ = 'info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return 'Info ' + str(self.id)

app.app_context().push()

@app.route("/", methods=["GET", "POST"])
def index():
    all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
    if request.method == "POST":
        if request.form.get("log out"):
            response = make_response(render_template("index.html",posts=all_posts))
            response.delete_cookie('name')
            return response
        
        email = request.form.get("Email")
        password = request.form.get("Password")
        print(f"Email: {email}\nPassword: {password}")
        any_posts = []
        any_posts = BlogInfo.query.filter_by(email=email).all()
        if any_posts == []:
            flash("Wrong Email")
            return redirect('/Login')
        elif any_posts[0].password != password:
            flash("Wrong Password")
            return redirect('/Login')
        all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
        response = make_response(render_template("main.html",posts=all_posts, name=any_posts[0].name))
        response.set_cookie('name',any_posts[0].name)
        return response
    
    name = request.cookies.get('name')
    if name is not None:
        return render_template("main.html",posts=all_posts, name=name)
    return render_template("index.html",posts=all_posts)

@app.route("/SignUp", methods=["GET", "POST"])
def signup():
    # if request.method == "POST":
    #     name = request.form.get("Name")
    #     email = request.form.get("Email")
    #     password = request.form.get("Password")
    #     print(f"Name: {name}\nEmail: {email}\nPassword: {password}")
    #     any_posts = []
    #     any_posts = BlogInfo.query.filter_by(email=email).all()
    #     #print(str(any_posts) + "\n\n\n")
    #     if any_posts != []:
    #         flash("This Email has been taken")
    #         return redirect(request.url)

    #     new_info = BlogInfo(name=name, email=email, password=password)
    #     db.session.add(new_info)
    #     db.session.commit()
    #     response = make_response(render_template("login.html"))
    #     # response.set_cookie('name',name)
    #     return response
    name = request.cookies.get('name')
    if name is not None:
        return render_template("welcome.html", name=name)
    return render_template("register.html")

@app.route("/Login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("Name")
        email = request.form.get("Email")
        password = request.form.get("Password")
        print(f"Name: {name}\nEmail: {email}\nPassword: {password}")
        any_posts = []
        any_posts = BlogInfo.query.filter_by(email=email).all()
        #print(str(any_posts) + "\n\n\n")
        if any_posts != []:
            flash("This Email has been taken")
            return redirect('/SignUp')

        new_info = BlogInfo(name=name, email=email, password=password)
        db.session.add(new_info)
        db.session.commit()
        response = make_response(render_template("login.html"))
        # response.set_cookie('name',name)
        return response
    # if request.method == "POST":
    #     email = request.form.get("Email")
    #     password = request.form.get("Password")
    #     print(f"Email: {email}\nPassword: {password}")
    #     any_posts = []
    #     any_posts = BlogInfo.query.filter_by(email=email).all()
    #     if any_posts == []:
    #         flash("Wrong Email")
    #         return redirect(request.url)
    #     elif any_posts[0].password != password:
    #         flash("Wrong Password")
    #         return redirect(request.url)
    #     all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
    #     response = make_response(render_template("main.html",posts=all_posts, name=any_posts[0].name))
    #     response.set_cookie('name',any_posts[0].name)
    #     return response
    name = request.cookies.get('name')
    if name is not None:
        return render_template("welcome.html", name=name)
    return render_template("login.html")

@app.route('/delete/<int:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    
    post = BlogPost.query.get_or_404(id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.author = request.cookies.get('name')
        post.content = request.form['content']
        db.session.commit()
        return redirect('/')
    else:
        return render_template('edit.html', post=post)

@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        post_title = request.form['title']
        post_author = request.cookies.get('name')
        post_content = request.form['content']
        new_post = BlogPost(title=post_title, content=post_content, author=post_author)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('new_post.html')

@app.route('/number', methods=['GET', 'POST'])
def number():
    req = request.get_json()
    print(req)
    num = len(BlogInfo.query.all())
    return jsonify({"num":num})

if __name__ == "__main__":
    app.run(debug=True)
