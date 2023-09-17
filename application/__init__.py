from application.imports import Flask, Session, Mail, mkdtemp, os, HTTPException, InternalServerError, default_exceptions, apology

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
app.config["SECRET_KEY"] = os.urandom(24) #make a new secret key every time the server starts

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
# app.config['MAIL_SERVER'] = 'smtp.flockmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
# app.config['MAIL_USERNAME'] = "goodshop.hg@gmail.com" #better to keep in env file, but ok
# app.config['MAIL_PASSWORD'] = "goodshop@pythonanywhere.com"
# mail = Mail(app) #make a mail app instance

Session(app)

from application.routes import index, account #connect the route files, each having code for a specific range of pages

def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

