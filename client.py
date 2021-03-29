import sys
from xmlrpc.client import ServerProxy
from datetime import datetime

s = ServerProxy("http://localhost:3000")

if __name__ == "__main__":
    # BUILD A SIMPLE USER INTERFACE
    instructions = "\n1) Write a new note\n2) Append to a note\n3) Read notes\n0) Exit"
    print("\nWelcome in the Notebook App!"+instructions)
    userInput = "-1" # initialize userInput value
    
    try:
        # Function for getting the timestamp (for the notes)
        def getTimeStamp():
            timeNow = datetime.now()
            timestampStr = timeNow.strftime("%d/%m/%Y - %H:%M:%S")
            return timestampStr
        
        def printTopicList():
            print("\n--- Topics in the database ---")
            topicList = s.listTopics()
            print(topicList)
            topicID = input("Select topic (number): ")
            try:
               topicID = int(topicID)
            except ValueError:
                print("Invalid input! Enter an integer next time.")
                topicID = -1
            return topicID
    
        # LOOP THROUGH USER INPUTS: if the input is 0, client session ends
        while (userInput != "0"):
            userInput = input("\nEnter: ")
            
            if (userInput == "1"):
                # CREATE A NEW NOTE
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
                # APPEND TO AN EXISTING NOTE               
                topicID = printTopicList() 
                if (topicID != -1):
                    text = input("Enter text: ")
                    timestamp = getTimeStamp()
                    success = s.appendToNote(topicID, text, timestamp)
                    if (success == 1):
                        print("\n>> Note has been updated successfully")
                    else:
                        print("\nInvalid input! Select a topic from the list next time.")
                print(instructions)
                
            elif (userInput == "3"):
                # LIST TOPICS AND SELECT A NOTE TO READ
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