import os
from scholarly import scholarly
from flask import Flask, request, render_template
import tinydb
from tinydb.database import TinyDB
from search import *
from statistics import *
import re
from collections import OrderedDict
#print(next(scholarly.search_author('Suhap Şahin')))
import operator

DATABASE_NAME = "authors6.json"

RELATIVITY_SEARCH = False

app = Flask(__name__)
db = tinydb.TinyDB("publications.json")


@app.route("/getCommand", methods=["POST", "GET"])
def get_command():
    data = request.json
    command = data.get("command")
    try:
        eval(command)
        return "done"
    except Exception as e:
        return f"error -> {str(e)}"


@app.route('/searchAuthor', methods=['GET', 'POST'])
def get_info(na=None):
    if na:
        name = na
    else:
        data = request.json
        name = data["author"]

    try:
        author = scholarly.fill(next(scholarly.search_author(name)))
    except Exception as e:
        return(f"No researcher with the name {name} \n {str(e)}\n------------\n")
    interests = author.get("interests")
    publications = []
    for i in author.get("publications"):
        publication = scholarly.fill(i)
        publications.append({"author_pub_id": publication.get("author_pub_id"), "title": publication.get(
            "bib").get("title"), "abstract": publication.get("bib").get("abstract"), "interests": interests})
        break

    return {"author": name, "interests": interests, "publications": publications}


@app.route("/save_publications", methods=['GET', 'POST'])
def save_publications():
    data = request.json
    author_list = data.get("author_list")
    for i in author_list:
        info = get_info(i)
        if isinstance(info, dict):
            db.insert(get_info(i))
        else:
            print(f"No researcher with the name {i} \n------------\n")
    return "done"


@app.route("/updatePublications")
def update_publications():
    data = request.json
    authors_list = data.get("author_list")
    print(authors_list)
    for name in authors_list:
        author = scholarly.fill(next(scholarly.search_author(name)))
        """
        for pub in author.get("publications"):
            if not pub.get("author_pub_id") in database.get(name).get("publications"):
                publication = scholarly.fill(pub)
                write_object = {"author_pub_id":publication.get("author_pub_id"),"title":publication.get("bib").get("title") , "abstract":publication.get("bib").get("abstract")}
                database.name.publications -> append(scholarly.fill(pub)) #pub is the summary object of the publication the author published.
        """
    return "none"


@app.route('/searchAuthorBasic', methods=['GET', 'POST'])
def get_info_basic():
    data = request.json
    name = data["author"]

    try:
        author = scholarly.fill(next(scholarly.search_author(name)))
        print(author)
    except Exception as e:
        return(f"No researcher with the name {name} \n {str(e)}\n------------\n")
    return author


def relative_topics(keyword):
    topics = []
    topics.append(["neural network", "yapay sinir ağı", "yapay zeka", "ensamble", "bulanık", "classifier",
                  "artificial intelligence", "zeka", "görüntü", "image", "cnn", "data mining", "data science"])
    topics.append(["android", "ios", "mobil", "uygulama",
                  "app", "app development", "flutter", "swift"])
    for i in topics:
        if keyword in i:
            return i
    return []


def search(k):
    keyword = k.lower()
    db = TinyDB(DATABASE_NAME)
    author_scores = {}
    if RELATIVITY_SEARCH:
        keyword_pool = relative_topics(keyword.lower())
        if not keyword_pool:
            keyword_pool = [keyword]

    for author in db:
        interest_score = score_interest(author.get("interests"), keyword)
        author_scores[author.get('author')] = list()
        author_scores[author.get("author")].append(interest_score)
        for pub in author.get("publications"):
            try:
                score = score_publication(publication=pub, k=keyword)
                author_scores[author.get('author')].append(score)
            except Exception as e:
                pass

    for a in author_scores:
        author_scores[a] = mean(author_scores[a])

    return author_scores


def rate_scores(score):
    raw_scores = [score[i] for i in score]
    rated_scores = {}

    for n, i in enumerate(score):
        rated_scores[i] = raw_scores[n]/sum(raw_scores)

    return rated_scores


def home2(keyword):
    scores = search(keyword)

    rs = rate_scores(scores)
    print(sum([rs[i] for i in rs]))
    ordered_rs = {
        k: v
        for k, v in sorted(rs.items(), key=lambda item: item[1], reverse=True)
    }
    list_ors = [(i, ordered_rs[i]) for i in ordered_rs]
    dict_lors = {}

    for i in list_ors:
        dict_lors[i[0]] = i[1]

    int_ors = {}
    for i in ordered_rs:
        int_ors[i] = int(ordered_rs[i]*100)
    return int_ors

"""
@app.route("/dont-open")
def dont_open():
    return render_template("dont-open.html")
"""


@app.route("/home", methods=["GET", "POST"])
def home():
    scores = {}
    if request.method == 'POST':
        keyword = request.form["inputUrl"]
        if keyword:
            try:
                scores = home2(keyword)
            except Exception as e:  # requests.exceptions.MissingSchema as e:
                print(f"Something Went Wrong -> {str(e)}")
                pass

    return render_template("index.html", data=scores)


if __name__ == '__main__':
    debug = True if os.getenv("env") != "prod" else False

    app.run(debug=debug, host="0.0.0.0", )#port=5001)
