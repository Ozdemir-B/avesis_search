from scholarly import scholarly
from flask import Flask,request,render_template
import tinydb
from tinydb.database import TinyDB
from search import *
from statistics import *
import re
from collections import OrderedDict
#print(next(scholarly.search_author('Suhap Şahin')))
import operator

DATABASE_NAME="authors6.json"

RELATIVITY_SEARCH = False

app = Flask(__name__)
db = tinydb.TinyDB("publications.json")
@app.route("/deneme",methods=["POST","GET"])
def deneme():
    data = request.json
    return data

@app.route("/getCommand",methods = ["POST","GET"])
def get_command():
    data = request.json
    command = data.get("command")
    try:
        eval(command)
        return "done"
    except Exception as e:
        return f"error -> {str(e)}"


@app.route('/searchAuthor',methods=['GET','POST'])
def get_info(na=None):
    if na:
        name = na
    else:
        data = request.json
        name = data["author"]

    try:
        author = scholarly.fill(next(scholarly.search_author(name)))
        #to get a summary of every publication of an author, advanced search will be needed. scholarly.fill does the job here.
        #with summary object of a publication, we will be able to fetch the full info of a publication which also contains the summary of the publication.
    except Exception as e:
        return(f"No researcher with the name {name} \n {str(e)}\n------------\n")
    interests = author.get("interests")
    #print(interests)
    publications = []
    #return {"author":name, "interests":interests}
    for i in author.get("publications"):
        publication = scholarly.fill(i)
        publications.append({"author_pub_id":publication.get("author_pub_id"),"title":publication.get("bib").get("title") , "abstract":publication.get("bib").get("abstract"), "interests":interests})
        break
        
    return {"author":name, "interests":interests , "publications":publications}

@app.route("/save_publications",methods=['GET','POST'])
def save_publications():
    data = request.json
    author_list = data.get("author_list")
    for i in author_list:
        info = get_info(i)
        if isinstance(info,dict):
            db.insert(get_info(i))
        else:
            print(f"No researcher with the name {i} \n------------\n")
    return "done"
    
@app.route("/updatePublications")
def update_publications():
    data = request.json
    authors_list= data.get("author_list")
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


@app.route('/searchAuthorBasic',methods=['GET','POST'])
def get_info_basic():
    data = request.json
    name = data["author"]

    try:
        author = scholarly.fill(next(scholarly.search_author(name)))
        print(author)
    except Exception as e:
        return(f"No researcher with the name {name} \n {str(e)}\n------------\n")
    return author
    """interests = author.get("interests")
    print(interests)
    publications = []
    for i in author.get("publications"):
        publication = scholarly.fill(i)
        publications.append({"title":publication.get("bib").get("title") , "abstract":publication.get("bib").get("abstract")})
        
    return {"interests":interests , "publications":publications}"""


def relative_topics(keyword):
    topics=[]
    # topics should be stored in a txt or something to be fetched on runtime
    topics.append(["neural network","yapay sinir ağı","yapay zeka","ensamble","bulanık","classifier","artificial intelligence","zeka","görüntü","image","cnn","data mining","data science"])
    topics.append(["android","ios","mobil","uygulama","app","app development","flutter","swift"])
    for i in topics:
        if keyword in i:
            return i
    return []

#@app.route("/search")
"""def search2(k):

    keyword = k #neural networks
    db = TinyDB(DATABASE_NAME)
    author_scores={}
    
    for author in db:
        interest_score = score_interest(author.get("interests"),keyword) # havent decide how to use correctly
	    
        author_scores[author.get('name')] = list()
        author_scores[author.get("name")].append(interest_score)
	    
        for pub in author.get("publications"):

            score = score_publication(publication = pub, keyword = k)
            #print(score)
            print("asdasdsdsadsd")
            author_scores[author.get('name')].append(score)

        for a in author_scores:
            author_scores[a] = sum(author_scores[a])

        # author_scıres={"suhap şahin":20,"adnan kavak":28}

    return author_scores"""


def search(k):

    keyword = k.lower() #neural networks
    db = TinyDB(DATABASE_NAME)
    author_scores={}
    if RELATIVITY_SEARCH:
        keyword_pool = relative_topics(keyword.lower())
        if not keyword_pool:
            keyword_pool = [keyword]
    #print(keyword_pool)
    #if keyword_pool: # if relative topics have been found at the pool, use them as well else just use the keyword given
    #    keyword = keyword_pool

    for author in db:
        #print(author.get("author"))
        interest_score = score_interest(author.get("interests"),keyword) # havent decide how to use correctly
        #print(author.get("author"))
        author_scores[author.get('author')] = list()
        author_scores[author.get("author")].append(interest_score)
        for pub in author.get("publications"):

            try:
                #print(keyword)
                score = score_publication(publication = pub, k = keyword)
                author_scores[author.get('author')].append(score)
                #print(score)
            except Exception as e:
                pass#print("probably abstract is empty")
                
        
    for a in author_scores:
        author_scores[a] = mean(author_scores[a])

    return author_scores

def  rate_scores(score):
    raw_scores = [score[i] for i in score]
    rated_scores = {}

    for n,i in enumerate(score):
        rated_scores[i] = raw_scores[n]/sum(raw_scores)

    return rated_scores




#@app.route("/home2",methods=["GET","POST"])
def home2(keyword):
    """data = request.json
    keyword = data.get("keyword")"""
    #print(keyword)
    scores = search(keyword)

    #print(scores)
    rs = rate_scores(scores)
    print(sum([rs[i] for i in rs]) )
    ordered_rs = {k: v for k, v in sorted(rs.items(), key=lambda item: item[1],reverse=True) }#OrderedDict(sorted(rs.items()))
    list_ors = [ (i,ordered_rs[i]) for i in ordered_rs ]
    dict_lors = {}
    
    #print(list_ors)
    for i in list_ors:
        dict_lors[i[0]] = i[1]

    print(ordered_rs)
    int_ors = {}
    for i in ordered_rs:
        int_ors[i] = int(ordered_rs[i]*100)
    return int_ors


        
@app.route("/",methods=["GET","POST"])
def home():
    head = "Avesis Search"
    name = "Kocaeli Üniversitesi"
    scores = {}
    if request.method == 'POST':
        keyword = request.form["inputUrl"]
        if keyword:
            try:
                scores = home2(keyword)
            except Exception as e:#requests.exceptions.MissingSchema as e:
                print(f"Something Went Wrong -> {str(e)}")
                pass
                #name = "wrong url"

    return render_template("index.html",head=head,name=name,data=scores)









if __name__ == '__main__':
    app.run(debug = False,host="0.0.0.0")
