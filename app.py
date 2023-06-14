import os
import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import contains_number,getIdAndRatings,convertId,getDetails,getGenres,getFullCredits

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///muize.db")



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/")
def index():
    return render_template("index.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    # Forget any user_id
    session.clear()

    if request.method == "POST":

        #username check
        if not request.form.get("username"):
           return render_template("register.html", error="Empty username field!")
        name = request.form.get("username")

        users = db.execute("SELECT name FROM users")
        for x in range(len(users)):
            if users[x]["name"] == name:
                return render_template("register.html", error="Username taken!")

        #password check
        if not request.form.get("password"):
           return render_template("register.html", error="Empty password field!")
        password = request.form.get("password")

        if len(password) < 8:
            return render_template("register.html", error="Password must be at least 8 character!")

        if not contains_number(password):
            return render_template("register.html", error="Password must contain at least one number!")

        #confirmation check
        if not request.form.get("confirmation"):
           return render_template("register.html", error="Empty confirmation field!")
        confirmation = request.form.get("confirmation")

        if confirmation != password:
            return render_template("register.html", error="Password and confirmation does't match!")

        #adding data to database
        db.execute("INSERT INTO users (name,hash) VALUES (?,?)",name,generate_password_hash(password))

        #loging in the user
        session["user_id"] = db.execute("SELECT id FROM users WHERE name = ?", name)[0]["id"]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    if request.method == "POST":

        #username check
        if not request.form.get("username"):
           return render_template("login.html", error="Empty username field!")
        name = request.form.get("username")

        users = db.execute("SELECT name FROM users")
        exists = False
        for x in range(len(users)):
            if users[x]["name"] == name:
                exists = True
                #brak
        if exists == False:
            return render_template("login.html", error="Wrong username!")

        #password check
        if not request.form.get("password"):
           return render_template("login.html", error="Empty password field!")
        password = request.form.get("password")

        if check_password_hash(db.execute("SELECT hash FROM users WHERE name = ?",name)[0]["hash"], password):
            #loging in the user
            session["user_id"] = db.execute("SELECT id FROM users WHERE name = ?", name)[0]["id"]

            # Redirect user to home page
            return redirect("/")
        else:
            return render_template("login.html", error="Wrong password!")


    else:
        return render_template("login.html")


def answCheck():
    submeted = request.form.get("sumbited")
    goodAnsw = db.execute("SELECT answ FROM users WHERE id = ?",session["user_id"])
    questionCounter = db.execute("SELECT questions FROM users WHERE id = ?",session["user_id"])
    questionCounter = int(questionCounter[0]["questions"]) + 1
    db.execute("UPDATE users SET questions = ? WHERE id = ?",questionCounter, session["user_id"])
    if(submeted == goodAnsw[0]["answ"]):
        goodAnswCounter = db.execute("SELECT gansw FROM users WHERE id = ?",session["user_id"])
        goodAnswCounter = int(goodAnswCounter[0]["gansw"]) + 1
        db.execute("UPDATE users SET gansw = ? WHERE id = ?",goodAnswCounter, session["user_id"])



def questions(film):
        id = convertId(film["id"])
        details = getDetails(id)
        answers = [0] * 4
        goodAnswer = 0
        randnum =  random.randint(0,3)
        if(randnum == 0):
            #q1 What is raiting of filmname
            goodAnswer = film["chartRating"]
            answers[0] = goodAnswer
            db.execute("UPDATE users SET answ = ? WHERE id = ?",str(goodAnswer), session["user_id"])
            print("jo rating:",goodAnswer)
            for i in range(3):
                rnum = round(random.uniform(6, 9), 1)
                while rnum in answers:
                    rnum = round(random.uniform(6, 9), 1)
                answers[i+1]=rnum
            question = "What is the rating of "+ details["title"] + " ?"
        elif(randnum == 1):
            #q2 When did the filmname movie came out
            goodAnswer = details["year"]
            answers[0] = goodAnswer
            db.execute("UPDATE users SET answ = ? WHERE id = ?",str(goodAnswer), session["user_id"])
            for i in range(3):
                rnum = random.randint(1960, 2023)
                while rnum in answers:
                    rnum = random.randint(1960, 2023)
                answers[i+1]=rnum
            question = "When did the "+ details["title"] + " movie came out?"
        elif(randnum == 2):
            #q3 What is the main genre of the filmname?
            genres = ["Action","Adventure","Animation","Biography","Comedy","Crime","Documentary","Drama","Family","Fantasy","Film-Noir","History","Horror","Music","Musical","Mystery","Romance","Sci-Fi","Sport","Thriller","War","Western"]
            genreOfMovie = getGenres(id)
            goodAnswer = genreOfMovie[0]
            answers[0] = goodAnswer
            db.execute("UPDATE users SET answ = ? WHERE id = ?",str(goodAnswer), session["user_id"])
            for i in range(3):
                rgenre = genres[random.randint(0, 21)]
                while rgenre in answers:
                    rgenre = genres[random.randint(0, 21)]
                answers[i+1] = rgenre
            question = "What is the main genre of the " + details["title"] + "?"
        elif(randnum == 3):
            #q4 Who was the main actor or actress of the movie
            fullCredit = getFullCredits(id)
            fullCredit = fullCredit["cast"]
            goodAnswer = fullCredit[0]["name"]
            answers[0] = goodAnswer
            db.execute("UPDATE users SET answ = ? WHERE id = ?",str(goodAnswer), session["user_id"])
            for i in range(3):
                rperson = fullCredit[random.randint(0, len(fullCredit)-1)]["name"]
                while rperson in answers:
                    rperson = genres[random.randint(0, len(fullCredit)-1)]["name"]
                answers[i+1] = rperson
            question = "Who was the main actor or actress of the movie " + details["title"] + "?"

        random.shuffle(answers)
        return answers,question,details["image"]["url"],goodAnswer




@app.route("/quize", methods=["GET", "POST"])

def quize():
    if request.method == "POST":
        idAndRatings = getIdAndRatings()
        submited = request.form.get("sumbited")
        if submited != "Start":
            answCheck()
        film = idAndRatings[random.randint(0,len(idAndRatings)-1)]
        question = questions(film)
        return render_template("quize.html",answers = question[0] , question = question[1] , image = question[2])
    else:
        return render_template("quize.html")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    id = session["user_id"]
    data = db.execute("SELECT name,questions,gansw FROM users WHERE id = ?", id)
    if(data[0]["questions"] == 0):
        accuracy = 0
    else:
        accuracy = round(data[0]["gansw"]/data[0]["questions"]*100,2)
    return render_template("profile.html",name = data[0]["name"],questions = data[0]["questions"],gansw = data[0]["gansw"],accuracy = accuracy)

@app.route("/leaderboard", methods=["GET", "POST"])
def leaderboard():
    lb = db.execute("SELECT name,gansw FROM users ORDER BY gansw DESC")
    print(lb[0]["name"])
    return render_template("leaderboard.html",len = len(lb),data = lb)
