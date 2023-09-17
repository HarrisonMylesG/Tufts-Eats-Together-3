from application.imports import (login_required, connect_db, request, session, apology, generate_password_hash, check_password_hash, render_template, redirect)
from application.imports import Mail, Serializer, Message, check_email_format
from application import app
mail = Mail(app)

@app.route("/account", methods=["GET", "POST"]) #if user navigates to account page
@login_required
def account():
    db = connect_db()
    username = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])[0]["username"]
    if request.method == "POST": #if form or ajax submit

        full_name_tuple = ("", "")
        if request.form.get("first_name"):
            db.execute("UPDATE users SET first_name=? WHERE username=?", request.form.get("first_name"), username)
            full_name_tuple[0] = request.form.get("first_name")
        if request.form.get("last_name"):
            db.execute("UPDATE users SET last_name=? WHERE username=?", request.form.get("last_name"), username)
            full_name_tuple[1] = request.form.get("last_name")
        if full_name_tuple != ("", ""):
            user = db.execute("SELECT username, first_name, last_name FROM users WHERE id = :myID", myID=session["user_id"])[0]
            full_name = user["first_name"] + " " + user["last_name"]
            db.execute("UPDATE billboard SET name=? WHERE username=?", full_name, username)

        if request.form.get("email"):
            if not request.form.get("email_conf"):
                return apology("must provide email confirmation", 403, "account")
            if not request.form.get("email") == request.form.get("email_conf"):
                return apology("emails do not match", 403, "account")
            if not check_email_format(request.form.get("email")):
                return apology("invalid email", 403, "account")
            db.execute("UPDATE users SET email=? WHERE username=?", request.form.get("email"), username)

        if request.form.get("username"):
            if not request.form.get("username_conf"):
                return apology("must provide username confirmation", 403, "account")
            if not request.form.get("username") == request.form.get("username_conf"):
                return apology("usernames do not match", 403, "account")
            if len(request.form.get("username")) < 8:
                return apology("username must be at least 8 characters", 403, "account")
            rows = db.execute("SELECT * FROM users WHERE username=?", request.form.get("username").lower())
            if len(rows) == 1:
                return apology("username already in use. please try again", 403, "account")
            db.execute("UPDATE users SET username=? WHERE username=?", request.form.get("username").lower(), username)
            session["user_id"] = request.form.get("username").lower()

        if request.form.get("old_password"):
            rows = db.execute("SELECT * FROM users WHERE username=?", username)
            if not check_password_hash(rows[0]["hash"], request.form.get("old_password")):
                return apology("invalid password", 403, "account")
            if not request.form.get("password"):
                return apology("must provide new password", 403, "account")
            if not request.form.get("password_conf"):
                return apology("must provide new password confirmation", 403, "account")
            if not request.form.get("password") == request.form.get("password_conf"):
                return apology("passwords do not match", 403, "account")
            if len(request.form.get("password")) < 8:
                return apology("new password must be at least 8 characters", 403, "account")
            db.execute("UPDATE users SET hash=? WHERE username=?", generate_password_hash(request.form.get("password")), username)

        if request.get_json(): #if the request is an ajax request
            key = next(iter(request.get_json().keys()))
            data = request.get_json()[key]
            if key == "deactivate_account":
                db.execute("DELETE FROM users WHERE username=?", username)
                return redirect("/logout")

    row = db.execute("SELECT * FROM users WHERE username=?", username)[0]
    return render_template("account.html", first_name=row["first_name"], last_name=row["last_name"], email=row["email"], username=row["username"])

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    db = connect_db()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403, "register")
        if len(request.form.get("username")) < 8:
            return apology("username must be at least 8 characters", 403, "register")
        if not request.form.get("email"):
            return apology("must provide email", 403, "register")
        if not check_email_format(request.form.get("email")):
            return apology("invalid email", 403, "register")
        elif not request.form.get("password"):
            return apology("must provide password", 403, "register")
        elif not request.form.get("password_conf"):
            return apology("must provide password confirmation", 403, "register")
        if request.form.get("password") != request.form.get("password_conf"):
            return apology("passwords do not match", 403, "register")
        if len(request.form.get("password")) < 8:
            return apology("password must be at least 8 characters", 403, "register")
        username = request.form.get("username").lower()
        email = request.form.get("email").lower()
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if len(rows) == 1:
            return apology("user account already created. please log in", 403, "register")

        #add their info to the database:
        db.execute("INSERT INTO users (username, email, hash) VALUES(?, ?, ?)", username, email, generate_password_hash(request.form.get("password")))
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if len(rows) != 1:
            return apology("registration error", 403, "register")

        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    db = connect_db()
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("username missing", 403, "login")
        elif not request.form.get("password"):
            return apology("password missing", 403, "login")

        username = request.form.get("username").lower()
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403, "login")

        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")

def get_reset_token(username, expires_sec=1800): #get a token for user to reset password
    secret_key = app.config.get("SECRET_KEY") #get secret key from env file
    s = Serializer(secret_key, expires_sec) #make a new serializer object
    return s.dumps({'username': username}).decode('utf-8') #return token in plaintext

def verify_reset_token(token): #check to see if token is valid, and find the user it belongs to
    secret_key = app.config.get("SECRET_KEY")
    s = Serializer(secret_key)
    try:
        username = s.loads(token)['username']
    except:
        return None
    return username

def send_password_reset_email(username, email):
    token = get_reset_token(username)
    msg = Message('HGordon Mail -- reset your password', sender='goodshop.hg@gmail.com', recipients=[email])
    #msg.body = (f"Hi {username}, \n to reset your password, visit this link: {url_for('newpassword', token=token, _external=True)} \n If you do not recognize this activity, please ignore this message. \n\n --Harrison \n developer of goodShop")
    msg.html = render_template("resetemail.html", username=username, token=token) #send the message as one of the html templates
    mail.send(msg)
    return "okay"

@app.route("/reset", methods=["GET", "POST"])
def reset():
    db = connect_db()
    if request.method == "POST":
        if not request.form.get("username"): return apology("must provide username", 403, "reset")
        username = request.form.get("username")
        temp = db.execute("SELECT email FROM users WHERE username=?", username)
        if not len(temp): return apology("account does not exist", 403, "register")
        email = temp[0]["email"]
        if not email:
            # email = "gohmgz@gmail.com"
            return apology("user account not associated with an email address. password reset not possible :(", 403, "reset")
        result = send_password_reset_email(username, email)
        if result != "okay": return apology("something went wrong", 403, "reset")
        else: return apology("password reset email successfully sent", 200, "index")
    else:
        if session: return redirect("/account")
        return render_template("reset.html")

@app.route("/newpassword/<token>", methods=["GET", "POST"])
def new_password(token):
    db = connect_db()
    if request.method == "POST":
        if not request.form.get("password"): return apology("must provide password", 403, "newpassword/" + token)
        if not request.form.get("password_conf"): return apology("must provide password confirmation", 403, "newpassword/" + token)
        password = request.form.get("password")
        password_conf = request.form.get("password_conf")
        if password != password_conf: return apology("passwords do not match", 403, "newpassword/" + token)
        password_hash = generate_password_hash(password)
        username = verify_reset_token(token)
        if not username: return apology("invalid or expired password reset link", 403, "reset")
        db.execute("UPDATE users SET hash=? WHERE username=?", password_hash, username)
        temp = db.execute("SELECT hash FROM users WHERE username=?", username)
        if len(temp) != 1: return apology("error resetting password", 403, "reset")
        if temp[0]["hash"] != password_hash: return apology("error resetting password", 403, "reset")
        #notify of successful password reset
        return apology("your password was reset successfully. you may now log in", 200, "login")

    else:
        if session: return redirect("/account")
        username = verify_reset_token(token)
        if username: return render_template("newpassword.html", username=username, token=token)
        else: apology("invalid or expired link. please request another", 403, "reset")