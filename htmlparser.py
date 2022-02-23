from fileinput import filename
import os
from bs4 import BeautifulSoup
import json
from rake_nltk import Rake
from mysqlDB import insertDoc, getLastInsertID, insertElement, insertTable, insertElementsList
import shutil

hospital_name = "MSE" # "Broomfield"
curr_dir = os.getcwd()
input_dir = curr_dir + os.path.sep +"input-html"+ os.path.sep + hospital_name + os.path.sep
processed_dir = curr_dir + os.path.sep +"processed-html"+ os.path.sep + hospital_name + os.path.sep
ouput_json = curr_dir + os.path.sep +"output-json"+ os.path.sep + hospital_name + os.path.sep
logfile = ''
i = 1

def GetKeywords(text, unique=True):
    r = Rake()
    # Extraction given the text.
    r.extract_keywords_from_text(text)
    keywords = r.get_ranked_phrases()
    if unique:
        return list(dict.fromkeys(keywords))
    else:
        return keywords
     
def textCleaning(text):
    text = text.replace("&#xa0;","").replace("\u2022","").replace("\u00a0"," ").replace("\n","")
    text = text.replace("\u2019","'")
    
    while "  " in text:
        text = text.replace("  ", " ")

    return text

def getMetadata():
    print("Parsing metadata")

def parseTable(html_table):
    Table = {}
    rows = len(html_table.find_all('tr'))
    items = html_table.find_all('td')
    table_items = []
    row_items = []

    for row in rows:
        row_item={}
        cols = row.find_all('td')
        row_item["num_cols"] = len(cols)
        for col in cols:
            row_item["text"] = textCleaning(col.text).strip()
        row_items.append(row_item)
    
    for tag in items:
        table_item = {}
        table_item["text"] = textCleaning(tag.text).strip()
        table_items.append(table_item)

    
    Table["num_rows"] = rows
    # Table["num_cols"] = int(len(items)/rows)
    Table["row_items"] = row_items
    Table["table_items"] = table_items
    return Table

def parseText(pTag):
    Text = {}
    # print("Parsing Text")
    txt = ''
    for tag in pTag.find_all():
        # if tag.name == 'span':
        if len(tag.find_all(text=False)) == 0: # If Leaf Node
            # print(tag)
            try:
                if "font-weight:bold" in tag['style']:
                    Text['is_bold'] = 1
                else:
                    Text['is_bold'] = 0
            except:
                logfile += f"no style tag for node:{0} \n", tag

            txt += tag.text   
    
    Text["text"] = textCleaning(txt)      
    return Text

def parseListItem(pTag, logfile):
    txt = ''
    ListItem = {}
    ListItem['is_heading'] = 0

    for tag in pTag.find_all():
        if len(tag.contents) > 0:
            content = str(tag.contents[0])
            if not content.startswith("<"):
                content = textCleaning(content)
                if content:
                    try:
                        ListItem['prefix'] = float(content)
                    except:
                        txt += content
        
        if len(tag.find_all(text=False)) == 0: # If Leaf Node
            try:
                if "font-weight:bold" in tag['style']:
                    ListItem['is_heading'] = 1
            except:
                logfile += "no style tag for node: {0}\n".format(tag)

    ListItem['text'] = txt.strip()

    return ListItem

def processHTML(filename, logfile, is_json=True, debug = False):

    output = {}
    # metadata = {}
    nodes = []
    db_elements = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, "html.parser")
        leaf_count = 1
        name = (os.path.basename(filename)).lower().replace(".html","")
        if debug:
            print("processing "+str(i)+"...", name)
        
        # ------------------------- Inserting Document into DB --------------------------- #
        # Extracting keywords for whole document
        x = soup.text
        xx = textCleaning(x)
        doc_keywords = ','.join(GetKeywords(xx, unique=True))
        # Inserting the document into the Database
        insertDoc(name, hospital_name, doc_keywords)  # , reg_num=None, status=None
        docId = getLastInsertID("documents")
        if debug:
            print("Inserted")
        # ------------------------------------------------------------------------------ #
        
        divs = soup.findAll("div")
        for div in divs:
            for node in div.children:
                if node.name == None:
                    continue
                
                elif node.name == 'table':
                    # print("Table Found with sequence number:",leaf_count )
                    element = {}
                    element["type"] = 'Table'
                    element["sequence_num"] = leaf_count
                    element["data"] = parseTable(node)
                    nodes.append(element)
                    # ------------------------- Inserting Table into DB --------------------------- #
                    keywords = GetKeywords(textCleaning(node.text))
                    table_items = str(json.dumps(element["data"]))
                    
                    # insertElement(element["sequence_num"], "", "", "Table", docId)
                    # elem_id = getLastInsertID("elements")
                    # insertTable(table_items, ','.join(keywords), elem_id)

                    db_item =[element["sequence_num"], ','.join(keywords), table_items, "Table",  docId]
                    db_elements.append(db_item)
                    # ------------------------------------------------------------------------------ #
                    leaf_count += 1
                
                elif node.name == 'p':
                    if textCleaning(node.text).strip() != "": # -------------- Extracting ListItem -----------------
                        # print("Extracting Text "+str(leaf_count)+": "+node.text)
                        element = {}
                        element["data"] = parseListItem(node, logfile)
                        if element["data"]["text"].strip() == '':
                            continue
                        element["type"] = 'ListItem'
                        element["sequence_num"] = leaf_count
                        nodes.append(element)
                        # ------------------------- Inserting Document into DB --------------------------- #
                        keywords = GetKeywords(element["data"]["text"])
                        # insertElement(element["sequence_num"], ','.join(keywords), element["data"]["text"], "Text", docId)

                        db_item =[element["sequence_num"], ','.join(keywords),element["data"]["text"], "Text",  docId]
                        db_elements.append(db_item)

                        # -------------------------------------------------------------------------------- #
                        leaf_count += 1

                    if node.find('img'): # -------------- Extracting Image -----------------
                        # print("Image Found with sequence number:", leaf_count)
                        element = {}
                        Image = {}
                        img = node.find('img')
                        element["type"] = 'image'
                        element["sequence_num"] = leaf_count
                        Image["url"] = img['src']
                        element["data"] = Image
                        nodes.append(element)
                        # -------------------------------- # DB Insert ----------------------------------- #
                        db_item =[element["sequence_num"], "", Image["url"], "Image", docId]
                        db_elements.append(db_item)

                        # insertElement(element["sequence_num"], "", Image["url"], "Image", docId)
                        # -------------------------------------------------------------------------------- #
                        leaf_count += 1
                    else:
                        logfile += "Unknown p tag for {0} \n".format(filename)

                else:
                    logfile += "unknown node: {0} for file: {1}\n".format(node.name, filename)
            
    insertElementsList(db_elements)
    # output["metadata"] = metadata
    
    # ------------------------ Writing file to JSON ----------------------------#
    if is_json:
        output["Hospital_name"] = hospital_name
        output["Filename"] = name
        output["No. of elements"] = len(nodes)
        output["elements"] = nodes
        json_object = json.dumps(output, indent = 4)
        
        # print("Writing file", filename[:-5] + ".json")
        with open(ouput_json + name + ".json", "w") as outfile:
            outfile.write(json_object)
    # ---------------------------------------------------------------------------#

def moveProcessedDir(dir_path):
  shutil.move(dir_path, processed_dir, copy_function = shutil.copytree)

 
if __name__ == "__main__":

    dirs = os.listdir(input_dir)

    for dir in dirs:
        d = os.path.join(input_dir, dir)
        if os.path.isdir(d):
            files = os.listdir(d)
            for file in files:
                if file[-5:] == ".html":
                    filepath = os.path.join(d, file)    
                    
                    # try:
                    #     processHTML(filepath, logfile, False)
                    #     moveProcessedDir(d)
                    #     logfile += "file {0} processed.\n".format( file[:-5])
                    # except Exception as e:
                    #     print(e)
                    #     logfile += "---ERROR---: {0}\n".format( file[:-5])
                    
                    processHTML(filepath, logfile, True, False)
                    moveProcessedDir(d)
                    
                    logfile += "------------------------------\n"
                else:
                    continue
        else:
            continue
        print(i)
        i += 1
        # break
        # if i == 5:
        #     break

    with open("logs.txt", "w") as outfile:
        outfile.write(logfile)

