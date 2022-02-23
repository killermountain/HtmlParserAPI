from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import os
import uvicorn
from searchquery import searchDocs, searchElements, GetKeywords
from connDB import MySQLDB

# pip install python-multipart

api = FastAPI()
cwd = os.getcwd()
# hospital_name = "Broomfield"
# ouput_json = cwd + os.path.sep + "output-json"+ os.path.sep + hospital_name + os.path.sep
ouput_all_json = cwd + os.path.sep + "output-json"+ os.path.sep

documents = None
last_doc_id = None
docs_count = None

@api.get("/")
def welcome():
    return {"msg": "Welcome to HTML to Database API"}

@api.get("/getfilnames/")
def getAlljsons():
    
    # output={}
    hospitals = []
    hospital_names = os.listdir(ouput_all_json)
    # output["Hospital names"]= hospital_names
    
    for hosp_name in hospital_names:
        json_files = []
        folder_path = os.path.join(ouput_all_json, hosp_name)
        json_names = os.listdir(folder_path)
        
        for json_file in json_names:
            if json_file[-5:].lower() == ".json":
                json_files.append(json_file[:-5])
        hospital = {"hospital_name":hosp_name, "No of Files": len(json_files), "Filenames":json_files}
        hospitals.append(hospital)

    # output["data"] =hospitals
    return hospitals

@api.get("/getjson/{filename}")
def getjson(filename: str):
    hospital_names = os.listdir(ouput_all_json)
    filename = filename + ".json"
    for name in hospital_names:
        folder_path = os.path.join(ouput_all_json, name)
        filepath =  os.path.join(folder_path, filename)
        if os.path.exists(filepath):
            return FileResponse(filepath, media_type="application/json")
    return {"Oops":"No JSON found with the name --> "+ filename[:-5]}

@api.get("/search/{query}")
def getjson(query: str):
    global documents, docs_count, last_doc_id
    
    conn_db = MySQLDB()
    query_keys = GetKeywords(query)
    results = searchDocs(query_keys, documents, docs_count, last_doc_id, conn_db, top_x=5)
    
    if len(results["matches"]) < 1:
        return {"Oops!":"No document found."}
    
    documents = results["docs"]
    docs_count = results["docCount"]
    last_doc_id = results["docLastID"]
    
    # return results["matches"]
    search_results = {}
    # print (query_keys)
    search_results["docs"] = results["matches"][1]
    # print(results["matches"][0])
    elements = searchElements(query_keys, results["matches"][0], conn_db)
    if len(elements) < 1:
        return {"Not Found":"No Element found with the given keyword(s)."}
    
    search_results["Elements"] = elements
    return search_results
    
    return {"number of matches":len(elements), "data":elements}

@api.post("/uploadfile/")
async def create_upload_file(uploaded_file: UploadFile = File(...)):
    
    pdfs_recieved = cwd + os.path.sep + "received-pdfs"
    file_location = f"received-pdfs/{uploaded_file.filename}"
    
    with open(file_location, "wb+") as file_object:
        file_object.write(uploaded_file.file.read())
    return {"info": f"file '{uploaded_file.filename}' saved at '{file_location}'"}


def initialize():
    global documents, docs_count, last_doc_id
    conn_db = MySQLDB()
    docs_count, last_doc_id = conn_db.getDocInfo()
    documents = conn_db.getAllDocs()
    conn_db.disconnectDB()

initialize()

if __name__ == "__main__":
    uvicorn.run("FastApi:api", host="127.0.0.1", port=5000, reload=True, log_level="info")

