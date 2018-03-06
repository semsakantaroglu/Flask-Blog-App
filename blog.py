from functools import wraps
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = "YBBLOG"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ybblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not "logged_in" in session:
            flash("Lütfen Giriş Yapınız","danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/articles")
def articles(): 
    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles"
    
    result = cursor.execute(sorgu)
    
    articles = cursor.fetchall()

    if result > 0:
        return render_template("articles.html",articles = articles)

    else:
        flash("Hiçbir Makale Bulunamadı.","danger")
        return render_template("articles.html")

@app.route("/article/<string:id>")
def detail(id):

    cursor = mysql.connection.cursor()
    
    sorgu =  "Select * from articles where id  = %s"
    result = cursor.execute(sorgu,(id,))

    article = cursor.fetchone()

    if result > 0:
        return render_template("detail.html",article = article)
    else:
        return render_template("detail.html")
class RegisterForm(Form):
    name = StringField("İsim Soyisim",[validators.Length(min = 4,max = 25)])
    username = StringField("Kullanıcı Adı",[validators.Length(min=5,max=35)])
    email = StringField("Email Adresi",[validators.Length(min = 6,max = 35),validators.Email(message="Lütfen Geçerli Bir Email Adresi Girin")])
    password = PasswordField("Parola:",[
        validators.DataRequired(),
        validators.EqualTo("confirm",message="Parolanız Uyuşmuyor")
        ])
    confirm = PasswordField("Parolayı Doğrula")
class ArticleForm(Form):
    title = StringField("Başlık",[validators.Length(max = 100)])
    body = TextAreaField("İçerik",[validators.Length(min=10)])

@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create Cursor

        cur = mysql.connection.cursor()

        sorgu = "Insert Into users(name,username,email,password) VALUES(%s,%s,%s,%s)"

        cur.execute(sorgu,(name,username,email,password))

        mysql.connection.commit()

        cur.close()
        flash("Başarıyla Kayıt Oldunuz...","success")

        return redirect(url_for("/"))
    return render_template("register.html",form = form)

class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")

@app.route("/login",methods = ["GET","POST"])
def login():
    
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data

        cur = mysql.connection.cursor()

        sorgu = "Select * From users where username = %s"

        result = cur.execute(sorgu,(username,))
        
        if result > 0:
            data = cur.fetchone()

            real_password = data["password"]

            if sha256_crypt.verify(password_entered,real_password):
                session["logged_in"] = True
                session["username"] = username

                flash("Başarıyla Giriş Yaptınız","success")
                return redirect(url_for("dashboard"))


            else:
                flash("Parolanızı Yanlış Girdiniz","danger")
                return redirect(url_for("login"))
                
        else:
            flash("Böyle bir kullanıcı bulunmuyor","danger")
            return redirect(url_for("login"))

    return render_template("login.html",form = form)
@app.route("/logout")
def logout():
    session.clear()
    flash("Başarıyla Çıkış Yaptınız","success")

    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles where author = %s"
    result = cursor.execute(sorgu,(session["username"],))
    
    articles = cursor.fetchall()

    if result > 0:
        return render_template("dashboard.html",articles = articles)
    else:
        flash("Henüz makaleniz bulunmuyor...","warning")
        return render_template("dashboard.html")


@app.route("/addarticle",methods = ["GET","POST"])
@login_required
def addArticle():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        body = form.body.data
        # Create Cursor

        cur = mysql.connection.cursor()

        sorgu = "Insert Into articles(title,author,body) VALUES(%s,%s,%s)"

        cur.execute(sorgu,(title,session["username"],body))
        mysql.connection.commit()
        
        cur.close()
        flash("Makale Başarıyla Eklendi","success")

        return redirect(url_for("dashboard"))
    return render_template("addArticle.html",form = form)
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()

    sorgu = "Delete from articles where id = %s"
    
    cursor.execute(sorgu,(id,))
    
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for("dashboard"))
@app.route("/search")
def search():
    keyword = request.args.get("keyword")

    cursor = mysql.connection.cursor()
    keyword  = keyword.lower()
    sorgu = "Select * from articles where title LIKE '%" + keyword + "%'"

    result = cursor.execute(sorgu)
    articles = cursor.fetchall()

    if result > 0:
        return render_template("articles.html",articles = articles)
    else:
        flash("Aranan Kelimeye Uygun Makale Bulunamadı!","warning")
        return render_template("articles.html")
@app.route("/edit/<string:id>",methods = ["GET","POST"])
@login_required
def editArticle(id):
    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles where id = %s"

    result = cursor.execute(sorgu,(id,))
    article =  cursor.fetchone()
    if result > 0:
        form = ArticleForm()
        
        form.title.data = article["title"]
        form.body.data = article["body"]

        if request.method == "POST" and form.validate():
            
            sorgu2 = "Update articles Set title = %s, body = %s where id = %s"
            form = ArticleForm(request.form)

            app.logger.info(form.title.data)
            cursor.execute(sorgu2,(form.title.data,form.body.data,id))

            mysql.connection.commit()

            cursor.close()
            
            flash("Makale başarıyla güncellendi...","success")
            return redirect(url_for("dashboard"))

        else:
            return render_template("edit.html",form = form)
    else:
        return render_template("edit.html",error = "Böyle bir makale bulunmuyor...")



if __name__ == "__main__":
    app.run(debug = True)
