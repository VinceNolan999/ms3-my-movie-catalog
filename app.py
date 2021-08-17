import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_movies")
def get_movies():
    movies = list(mongo.db.movies.find())
    genres = list(mongo.db.genres.find())
    return render_template("movies.html", movies=movies, genres=genres)


# search movies
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    movies = list(mongo.db.movies.find({"$text": {"$search": query}}))
    return render_template("movies.html", movies=movies)


# movie  display by genre
@app.route("/movies_genre_sort/<genre>")
def movie_genre_sort(genre):
    movies = list(mongo.db.movies.find({'genre_name': genre}))
    genres = mongo.db.genres.find()
    return render_template("movies.html", movies=movies, genres=genres)


# user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        # check if user is existing
        if existing_user:
            flash("That user already exists!")
            return redirect(url_for("register"))
        # registers user
        register = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))

        }
        mongo.db.users.insert_one(register)
        # creates 'session'
        session["user"] = request.form.get("username").lower()
        flash("You are now registered!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


# user login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username does not exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


# Profile incudes username
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    email = mongo.db.users.find_one(
        {"username": session["user"]})["email"]
    if session["user"]:
        return render_template("profile.html", username=username, email=email)

    return redirect(url_for("login"))


# remove user session cookie
@app.route("/logout")
def logout():
    flash("You are now logged out")
    session.pop("user")
    return redirect(url_for("get_movies"))


# Add Movie section
@app.route("/add_movie", methods=["GET", "POST"])
def add_movie():
    if request.method == "POST":
        wish_list = "on" if request.form.get("wish_list") else "off"
        movie = {
            "genre_name": request.form.get("genre_name"),
            "movie_name": request.form.get("movie_name"),
            "release_date": request.form.get("release_date"),
            "run_time": request.form.get("run_time"),
            "age_rating": request.form.get("age_rating"),
            "format_type": request.form.get("format_type"),
            "movie_story": request.form.get("movie_story"),
            "wish_list": wish_list,
            "image_url": request.form.get("image_url"),
            "created_by": session["user"]
            }
        mongo.db.movies.insert_one(movie)
        flash("Movie is added")
        return redirect(url_for("get_movies"))

    genres = mongo.db.genres.find().sort("genre_name", 1)
    formats = mongo.db.formats.find()
    ages = mongo.db.ages.find()
    return render_template("add_movie.html",
                           genres=genres,
                           formats=formats,
                           ages=ages)


@app.route("/edit_movie/<movie_id>", methods=["GET", "POST"])
def edit_movie(movie_id):
    if request.method == "POST":
        wish_list = "on" if request.form.get("wish_list") else "off"
        update = {
            "genre_name": request.form.get("genre_name"),
            "movie_name": request.form.get("movie_name"),
            "release_date": request.form.get("release_date"),
            "run_time": request.form.get("run_time"),
            "age_rating": request.form.get("age_rating"),
            "format_type": request.form.get("format_type"),
            "movie_story": request.form.get("movie_story"),
            "wish_list": wish_list,
            "image_url": request.form.get("image_url"),
            "created_by": session["user"]
            }
        mongo.db.movies.update({"_id": ObjectId(movie_id)}, update)
        flash("Movie is updated")

    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)})
    genres = mongo.db.genres.find().sort("genre_name", 1)
    formats = mongo.db.formats.find()
    ages = mongo.db.ages.find()
    return render_template("edit_movie.html",
                           movie=movie,
                           genres=genres,
                           formats=formats,
                           ages=ages)


@app.route("/delete_movie/<movie_id>")
def delete_movie(movie_id):
    mongo.db.movies.remove({"_id": ObjectId(movie_id)})
    flash("Movie Deleted")
    return redirect(url_for("get_movies"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
