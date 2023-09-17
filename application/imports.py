from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory, jsonify
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Mail, Message
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps
from application.sql import SQL
import random
import json
import math
import os
import re

def login_required(f):
    #Decorate routes to require login.
    #http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code, route="error"):
    #return render_template("error.html", message=message, code=code, route=route)
    print(message, code, route)
    return render_template(route + ".html", alert=message)

def connect_db():
    db = SQL("sqlite:///application/database.db")
    return db
        
def check_email_format(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if(re.search(regex,email)): return True
    else: return False