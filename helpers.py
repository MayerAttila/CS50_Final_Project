import requests

from Key import Key

def contains_number(string):
    return any(char.isdigit() for char in string)




headers = {
    "X-RapidAPI-Key": Key(),
    "X-RapidAPI-Host": "imdb8.p.rapidapi.com"
}

def getIdAndRatings():
    url = "https://imdb8.p.rapidapi.com/title/get-top-rated-movies"
    response = requests.request("GET", url, headers=headers).json()
    return(response)

def convertId(id):
    return id[7:-1]

def getDetails(ttid):
    url = "https://imdb8.p.rapidapi.com/title/get-details"
    querystring = {"tconst":ttid}
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    return(response)

def getGenres(ttid):
    url = "https://imdb8.p.rapidapi.com/title/get-genres"
    querystring = {"tconst":ttid}
    response = requests.get(url, headers=headers, params=querystring).json()
    return(response)

def getFullCredits(ttid):
    url = "https://imdb8.p.rapidapi.com/title/get-full-credits"
    querystring = {"tconst":ttid}
    response = requests.get(url, headers=headers, params=querystring).json()
    return(response)


