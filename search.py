import re
#this file is just for searching text(couple of words) in a dictionary that full of texts.

KEYWORD_MAP = []

def findall_list(lst,text): return [re.findall(l,text) for l in lst]

def score_interest(interest,keyword_pool):
    #interests is a list of strings
    
    return 0

def score_publication(publication,k):
    
    title = publication.get("title")
    abstract = publication.get("abstract")
    
    if not abstract:
         abstract = ""
    if title:
        pass
    else:
        title="" #return 1
    title=title.lower()

    abstract = abstract.lower()
    #print(type(k))
    #print(k)
    #print("-------------------------------------------")
    if isinstance(k,list):
        #print(k)
        #print("->->_>__>->")
        title_count_pool = [re.findall(l,title) for l in k]#from_list(k,title)
        abstract_count_pool = [re.findall(l,abstract) for l in k]#from_list(k,abstract)
        #print(title_count_pool)
        
        title_score = sum([len(i) for i in title_count_pool])
        abstract_score = sum([len(i) for i in abstract_count_pool])
        #print(abstract_score)
        
        """title_score = 0
        abstract_score = 0
        for i in title_count_pool:
            title_score += sum(len(i))
        for i in abstract_count_pool:
            abstract_score += sum(len(i))"""
        
        result = title_score*5 + abstract_score
        
        #print(title_score)
            
        return title_score*5 + abstract_score
        
    else:
        #print("not a list mf* *** * * * *")
        title_count = re.findall(k,title)
        abstract_count = re.findall(k,title)
        
        title_score = len(title_count) * 5
        abstract_score = len(abstract_count)

        return title_score + abstract_score


if __name__ == "__main__":
    pass
