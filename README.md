# **Muize**
# Introduction
 My final project is a website where users can test their movie knowledge. At first, they need to create an account or log in with an existing one, after that they can check their profile where they can see their statistics. There is also a leaderboard where the profiles with the best statistics are placed, and the most complex part is the quiz part there users will get randomized questions about the top 100 movies ranked by [imdb](https://www.imdb.com/) after answering a question the users statistics will change based on the provided answer.based on the provided answer.
# Features
In the procces of creating my project I used:
* [html](https://devdocs.io/html/)
* [css](https://devdocs.io/css/)
* [flask](https://flask.palletsprojects.com/en/2.3.x/)
* [sqlite](https://www.sqlite.org/docs.html)
* [rapidapi](https://rapidapi.com/hub)
# Explaining each part of my project
## Register & Log In
To create an account a user must provide a username that is not used already, the password
length must be at least 8 characters and the password also must contain at least one number. When the username and the password are accepted by the website then it going to be stored in a database where the password is hashed.

## Database
I used one table in my database, callad users.
The users table containing:
- **id** (INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL)
- **name** (TEXT NOT NULL)
- **hash** (TEXT NOT NULL) That going to be storing the hashed password.
- **questions** (INTEGER DEFAULT 0) That stores the count of the answered questions.
- **gansw** (INTEGER DEFAULT 0) That stores the count of the good answeres provided by the user.
- **answ** (varchar(255)) When the website is generating a question the the good answer is going to be stored there.
## Profile
To be able to access your profile you need to be logged in first. On the profile page, you can see your statistics such as:
- Your username
- Answered questions
- Good answers
- Accuracy

## Leaderboard
The leaderboard page shows the top 10 registered users position, name, and the count of their good answers sorted by how many good answers they provided if there is fewer than 10 registered user then the empty spaces of the leaderboard are filled with - character.
## Quize
When someone enters the quiz page at first he or she will see a short description and a start button. When the start button is pressed then the program going to make an API call, from that call we going to be getting a list of the ids and the ratings of the top 100 movies on imdb.

From that list, the program randomly chose one movie id. That id is passed in the questions function.
### questions(film)
In that function is a API call called getdetails(id) when this is called then it will return details about the randomly selected movie id. Then the program randomly selects one of the four question types.
1.  ```python
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
    ```
2. ```python
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
    ```
3. ```python
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
    ```
4. ```python
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
    ```
When the question is generated the answer to that question is stored in our database.
## Answering a question
When the user selects an answer then the answCheck() function is called.
```python
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
```
At first, this function requests the submitted answer, and after that makes an SQL call which returns the good answer from the database. Then increment the question count by 1 And in the end checking if the submitted answer is the same as the good answer if yes then increments the good answer count by 1.
## API call functions
```python
    def getIdAndRatings():
        url = "https://imdb8.p.rapidapi.com/title/get-top-rated-movies"
        response = requests.request("GET", url, headers=headers).json()
        return(response)
```
The getIdAndRatings function returns the top 100 movieid and there rating of all time based on there rating.
```python
    def getDetails(ttid):
        url = "https://imdb8.p.rapidapi.com/title/get-details"
        querystring = {"tconst":ttid}
        response = requests.request("GET", url, headers=headers, params=querystring).json()
        return(response)
```
The getIdAndRatings(ttid) based on the input makes an API call that returns details about the movie.
```python
    def getGenres(ttid):
        url = "https://imdb8.p.rapidapi.com/title/get-genres"
        querystring = {"tconst":ttid}
        response = requests.get(url, headers=headers, params=querystring).json()
        return(response)
```
The getGenres(ttid) funcsion based on the input makes API call that returns the genres of the movie.
```python
    def getFullCredits(ttid):
        url = "https://imdb8.p.rapidapi.com/title/get-full-credits"
        querystring = {"tconst":ttid}
        response = requests.get(url, headers=headers, params=querystring).json()
        return(response)
```
The getFullCredits(ttid) funcsion based on the input makes API call that returns the members of the cast.
#### Video Demo:  <https://www.youtube.com/watch?v=QpwWYUrj4qs&ab_channel=attilamayer>

