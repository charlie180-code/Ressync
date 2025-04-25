from flask import render_template
from . import main

@main.route("/")
def home():
    return render_template("main/index.html")

@main.route("/about")
def about():
    return render_template("main/about.html")

@main.route("/pricing")
def pricing():
    return render_template("main/pricing.html")

@main.route("/contact")
def contact():
    return render_template("main/contact.html")

@main.route("/cgu")
def cgu():
    return render_template('main/cgu.html')