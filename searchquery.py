from rake_nltk import Rake
# from connDB import MySQLDB
import nltk
nltk.download('stopwords')
nltk.download('punkt')
import json

def GetKeywords(text, unique=True):
    r = Rake()
    # Extraction given the text.
    r.extract_keywords_from_text(text)
    keywords = r.get_ranked_phrases()
    # keywords = r.get_ranked_phrases_with_scores()
    if unique:
        return list(dict.fromkeys(keywords))
    else:
        return keywords

def checkAndUpdate(docs, docsCount, lastID, conn_db):
    newCount, newlastID = conn_db.getDocInfo()

    if newCount == docsCount and newlastID == lastID:
        return [docs, docsCount, lastID]
    else:                       # Data Update
        docs = conn_db.getAllDocs()
        docsCount, lastID = newCount, newlastID
        # print("Doc files updated")
        return [docs, docsCount, lastID]

def searchDocs(query_keys, docs, docsCount, lastID, conn_db, top_x=5):

        results={}
        results["docs"], results["docCount"], results["docLastID"] = checkAndUpdate(docs, docsCount, lastID, conn_db)
        
        score = {}
        
        for doc_row in results["docs"].values():
            doc_name = doc_row[1]           # Doc Name at index 1
            doc = doc_name + ';' + str(doc_row[0])
            # doc_id = str(doc_row[0])      # Doc Id at index 0
            for key in query_keys:
                score[doc] = score.get(doc, 0) + doc_row[3].lower().count(key.lower())

        top_5_docs = dict(sorted(score.items(), key=lambda item: item[1], reverse=True)[:top_x])
        ids = []
        names =[]
        for top_doc in top_5_docs.keys():
            name, id= top_doc.split(';')
            ids.append(id)
            names.append(name.replace(".html",""))
        results["matches"] = [ids, names]


        return results

def searchElements(query_keys, doc_ids, conn_db, n_results=5):
    """searching elements"""
    
    matches = []
    elements = conn_db.getElements(doc_ids)
    conn_db.disconnectDB()
    # SELECT `id`, `keywords`, `content`, `item_type`, `doc_id` --> elements[1] = keywords
    score = {}
    for elem in elements.values():
        elem_keywords = elem[1]
        for key in query_keys:
            freq = elem_keywords.lower().count(key.lower())
            score[elem[0]] = score.get(elem[0], 0) + freq
    
    score = dict(sorted(score.items(), key=lambda item: item[1], reverse=True)[:n_results]) #[:n_results]
    
    for elem_id in score.keys():
        if score[elem_id] > 0:
            row = list(elements[elem_id])
            data ={}
            data["element_id"] = row[0]
            data["element_type"] = row[3]
            data["document_id"] = row[4]
            
            if row[3] == "Table":
                data["content"] = json.loads(row[2])
            else:
                data["content"] = row[2]
            
            # data["keywords"] = row[1]
            matches.append(data)
        else:
            continue
    
    return matches
    




if __name__ == "__main__":
    inp_query = "risk assessment"
    results = searchDocs(inp_query,None, None,None, 3)
    print(results["docCount"])
    print(results["docLastID"])
    print(results["matches"])
    


