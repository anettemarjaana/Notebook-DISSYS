# DISTRIBUTED SYSTEMS | Assignment 2 | Anette Sarivuo | 0544022

import sys # for catching errors
from xmlrpc.client import ServerProxy # for allowing clients to join the XML RCP server
from datetime import datetime # for timestamps

 #### CONNECTING CLIENTS ####    with server through a proxy:
s = ServerProxy("http://localhost:3000")

if __name__ == "__main__":
    instructions = "\n1) Write a new note\n2) Append to a note\n3) Read notes\n0) Exit"
    print("\nWelcome in the Notebook App!"+instructions)
    userInput = "-1" # initialize userInput value
    
    try:
        #### HELPFUL FUNCTIONS ####
        # Function for getting the timestamp (for the notes)
        def getTimeStamp():
            timeNow = datetime.now()
            timestampStr = timeNow.strftime("%d/%m/%Y - %H:%M:%S")
            return timestampStr
        
        def checkIfInteger(inputValue):   
            try:
               inputValue = int(inputValue)
            except ValueError:
                print("Invalid input! Enter an integer next time.")
                inputValue = -1
            return inputValue
        
        def printTopicList():
            print("\n--- Topics in the database ---")
            topicList = s.listTopics()
            print(topicList)
            topicID = input("Select topic (number): ")
            return checkIfInteger(topicID)
        
        def selectAppendMethod():
            print("\nHow do you want to modify the note?")
            print("\n1) I want to add my own content only\n2) Let's get content from Wikipedia\n3) Wanna add a link to a Wiki article")
            methodChoice = input("Select method (number): ")
            return checkIfInteger(methodChoice)
            
    
        #### LOOP THROUGH USER INPUTS ####
        # if the input is 0, client session ends
        
        while (userInput != "0"):
            userInput = input("\nEnter: ")
            
            if (userInput == "1"):
                ##### CREATE A NEW NOTE ####
                print("\n--- Write a new note ---")
                topic = input("Enter new topic: ")
                text = input("Enter text: ")
                timestamp = getTimeStamp()
                # Bring these to the server. Modify the db.xml on server.py
                success = s.writeNewNote(topic, text, timestamp)
                if (success == 1):
                    print("\n>> New note has been added successfully.")
                else:
                    print("\nThis topic is taken already.")
                print(instructions)
                
            elif (userInput == "2"):
                #### APPEND TO AN EXISTING NOTE  ####
                print("\n--- Append to a note ---")             
                topicID = printTopicList() 
                if (topicID != -1):  
                    # LET THE USER SELECT WIKIPEDIA OR NOT
                    methodChoice = selectAppendMethod()
                    if (methodChoice == 1):
                        # User adds their own text snippet
                        text = input("Enter text: ")
                    elif (methodChoice == 2):
                        # Extract from Wiki
                        searchTerm = input("Enter a search term: ")
                        text = s.getWikiExtract(searchTerm)
                    elif (methodChoice == 3):
                        # Link to Wiki article
                        searchTerm = input("Enter a search term: ")
                        text = s.getWikiLink(searchTerm)
                    else:
                        print("Invalid input! Enter an integer between 1 and 3")
                    
                    timestamp = getTimeStamp()
                    success = s.appendToNote(topicID, text, timestamp)
                    if (success == 1):
                        print("\n>> Note has been updated successfully")
                    else:
                        print("\nInvalid input! Select a topic from the list next time.")
                print(instructions)
                
            elif (userInput == "3"):
                #### LIST TOPICS AND SELECT A NOTE TO READ ####
                topicID = printTopicList()
                if (topicID != -1):
                    text = s.readNote(topicID)
                    print(text)
                print(instructions)
                
            elif (userInput == "0"):
                print("Thx bye!")
                
            else:
                print("Invalid input! Enter an integer between 0 and 3")
    
    except KeyboardInterrupt:
        print("\nBye bye client!")
        sys.exit(0)