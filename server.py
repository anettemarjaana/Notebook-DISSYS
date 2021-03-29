# DISTRIBUTED SYSTEMS | Assignment 2 | Anette Sarivuo | 0544022

import sys # for catching errors
from xmlrpc.server import SimpleXMLRPCServer # for building the XML RPC server
import xml.etree.ElementTree as ET # for parsing the database (XML-file)
import requests # for HTTP requests (Wikipedia application programming interface)
from datetime import datetime # for timestamps

# GOAL OF THE SERVER: allow clients to write, modify and read notes on an XML database

# DEFINING SERVER
with SimpleXMLRPCServer(('localhost', 3000)) as server:
    server.register_introspection_functions()
    
     #### CONNECT TO THE DATABASE MOCK  ####
    # The xml tables are represented with a tree. Iterate through it with ET.
    tree = ET.parse("db.xml")
    root = tree.getroot() # root.tag = data
    timeNow = datetime.now()
    timestampStr = timeNow.strftime("%d/%M/%Y %H:%M:%S")
    print("Connected to database at " + timestampStr)
    
     #### SET UP REQUESTS FOR WIKIPEDIA OPENSEARCH ####
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"
    
     #### CREATE NECESSARY FUNCTIONS  ####
    
    # Function for counting how many topics there are in the database
    def countTopics():
        counter = 0   
        for topic in root.findall("topic"):
            counter += 1
        return counter
   
    # Function for getting a wikipedia article link with a search term
    def getWikiLink(searchTerm):
        # Let the user define the search term:
        PARAMS = {
            "action": "opensearch",
            "format": "json",
            "namespace": "0",
            "limit": "1",
            "search": searchTerm
        }
        # Make the query in the Wiki API
        dataSet = S.get(url=URL, params=PARAMS).json()
        # get wikiPageUrl out: It's the first item in the last array of dataSet
        wikiPageUrl = dataSet[-1][0]
        return wikiPageUrl
     
    # Function for getting a wikipedia article extract with a search term
    def getWikiExtract(searchTerm):
        # Let the user define the title of the article (search term)
        PARAMS = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "exlimit": "1",
            "exintro": True,
            "explaintext": True,
            "titles": searchTerm
        }
        # Get response R:
        R = requests.get(url=URL, params=PARAMS).json()
        page = next(iter(R["query"]["pages"].values()))
        
        # Return this string:
        return page["extract"]
    
    # Allow client to write a new note
    def writeNewNote(topic, text, timestamp):
        success = 1
        
        # Check that the topic is not taken already
        for t in root.findall("topic"):
            name = t.get("name")
            if (name == topic):
                success = 0
                break
       
        # If topic is not taken, add new note:
        if (success != 0):    
            newTopic = ET.SubElement(root, "topic", attrib={"name": topic})
            newText = ET.SubElement(newTopic, "text")
            newText.text = text
            newTimestamp = ET.SubElement(newTopic, "timestamp")
            newTimestamp.text = timestamp
            tree.write("db.xml")
        
        # If successful, return 1. else 0
        return success
    
    # Allow client to append to an existing note
    def appendToNote(topicID, newText, newTimestamp):
        # When appending, topic stays the same, text gets longer and timestamp
        # is updated with the new one
        
        # First check whether the topicID corresponds to a topic in the db
        success = 0
        counter = countTopics()
        if (topicID > 0 and topicID < counter+1):
            root[topicID-1][0].text += f'\n{newText}'
            root[topicID-1][1].text = f'\n{newTimestamp}'
            tree.write("db.xml")
            success = 1
        return success

    
    # List the topics of the notes
    def listTopics():
        counter = 0
        topiclist = "" # a string which contains all topics in form: "topicID+1) topic.name"
        
        for topic in root.findall("topic"):
            counter += 1
            name = topic.get("name")
            topiclist += f'{counter}) {name}\n'
        
        # Return the string which contains all topics listed
        return topiclist 

    
    # Allow client to read notes
    def readNote(topicID):
        topicID -= 1
        # String output in case of failure:
        noteText = "Invalid input! Select a topic from the list next time."
        # Count how many topics there are to see whether the input integer is usable:
        counter = countTopics()
        
        if (topicID > -1 and topicID < counter):
            # Find topic and get its name, timestamp and text
            noteText = f'\n--- {root[topicID].get("name")} ({root[topicID][1].text}) ---\n {root[topicID][0].text}'
        return noteText
    
    #### REGISTER FUNCTIONS ####
    server.register_function(getWikiLink)
    server.register_function(getWikiExtract)
    server.register_function(writeNewNote)
    server.register_function(appendToNote)
    server.register_function(listTopics)
    server.register_function(readNote)
    

     #### SET THE SERVER TO LISTEN ####
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, exiting.")
        sys.exit(0)