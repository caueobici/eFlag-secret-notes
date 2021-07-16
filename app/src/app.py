from flask import Flask, render_template, request, url_for, redirect, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re
import requests
import mysql.connector
import hashlib

# Configuration
app = Flask(__name__, static_url_path='/static', static_folder='static')

app.config['SECRET_KEY'] = "1b5021c6a073f04fd23d563392c34bb16e81e94620483754"

limiter = Limiter(
    app,
    key_func=get_remote_address
)

# Database connection
db = mysql.connector.connect(user='user', password='455afd90edecf3ef9e3409c4607f3d14', host='127.0.0.1', database='challenge')

# add CSP
@app.after_request
def add_csp(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-eval' cdnjs.cloudflare.com maxcdn.bootstrapcdn.com; style-src maxcdn.bootstrapcdn.com 'self' 'unsafe-inline';"
    return response

1
# authenticated endpoint
@app.route('/', methods=['POST', 'GET'])
def index():
    cursor = db.cursor()
    username = session.get("username")

    if not username:
        return redirect("/login")

    if request.method == 'POST':
        note = request.form['note']
        cursor.execute("UPDATE challenge.users SET note=%s WHERE username=%s", (note, username))
        db.commit()

    cursor.execute("SELECT note FROM challenge.users WHERE username=%s", (username,))
    result = cursor.fetchone()
    cursor.close()

    if not result:
        return redirect("/login")

    note = result[0] or ""

    return render_template('index.html', note=note)


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        cursor = db.cursor()
        username = request.form["username"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        cursor.execute("SELECT username FROM challenge.users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()

        if result:
            session['username'] = result[0]
            return redirect("/")
            
        else:
            return redirect("/login?info=Usuario+ou+senha+incorretos")

        cursor.close()
    else:
        return render_template("login.html")

@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        cursor = db.cursor()
        username = request.form["username"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        try:
            cursor.execute("INSERT INTO challenge.users (username, password) VALUES (%s, %s)", (username, password))

            db.commit()
            cursor.close()
        except mysql.connector.errors.IntegrityError:
            return redirect("/register?info=Esse+nome+de+usuario+ja+esta+sendo+utilizado")
        except:
            return redirect("/register?info=Algum+erro+inesperado+ocorreu")

        return redirect("/login?info=Conta+criada")
    else:
        return render_template("register.html")

@app.route('/admin', methods=['GET', 'POST'])
@limiter.limit('2/5minutes', override_defaults=True, methods=["POST"])
def add_url():
    if request.method == 'POST':
        try:
            url = request.form['url']
            if url == '' or not re.search("^https?://", url):
                return render_template("admin.html", info="url invalida: ^https?://")
            
            requests.post('http://ademir:3000/add-87ytgvhbjnk', data={'url': url, 'secret': '3de2feb1ba568466471e337ae57acd59'})
        except:
            return render_template("admin.html", info="Algum erro inesperado ocorreu, contate algum admin")

        return render_template("admin.html", info="Link enviado, o admin vai checar ele em breve")
    return render_template('admin.html')

# Exporting server
if __name__ == '__main__':
    app.run(host='0.0.0.0')
