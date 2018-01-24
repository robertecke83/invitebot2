from flask import Flask, request
from ciscosparkapi import CiscoSparkAPI
import json
import requests
import csv

app = Flask(__name__)


BOT_TOKEN = 'NjNiMTI2MDctNzRhMC00NGMyLTgwYWMtY2M1NTY2ZTg3ZGFhM2I2MWM1OTctNGU4'

api = CiscoSparkAPI(access_token=BOT_TOKEN)


@app.route('/')
def hello():
    return 'Hello World!'

# Receive POST from Spark Space
@app.route('/sparkhook', methods=['POST'])
def sparkhook():

    if request.method == 'POST':

        jsonAnswer = json.loads(request.data) # Format data from POST into JSON

        botDetails = api.people.me() # Get details of the bot from its token

        if str(jsonAnswer['data']['personEmail']) != str(botDetails.emails[0]): # If the message is not sent by the bot

            botName = str(botDetails.displayName) # Get bot's display name
            botFirstName = botName.split(None, 1)[0] # Get bot's "first name"

            sparkMessage = api.messages.get(jsonAnswer['data']['id']) # Get message object text from message ID
            sparkMsgText = str(sparkMessage.text) # Get message text
            sparkMsgRoomId = str(sparkMessage.roomId) # Get message roomId
            sparkMsgText = sparkMsgText.split(botFirstName,1)[1] # Remove bot's first name from message

            if "Hello" in sparkMsgText:
                textAnswer = 'Hello <@personEmail:' + str(jsonAnswer['data']['personEmail']) + '>, HELLO!!!!!!'
                botAnswered = api.messages.create(roomId=sparkMsgRoomId, markdown=textAnswer)

            if "Help" in sparkMsgText:
                textAnswer = 'Hello <@personEmail:' + str(jsonAnswer['data']['personEmail']) + '>, I will Help you to Invite People to a Spark Space or Team: /n Help /n Hello'
                botAnswered = api.messages.create(roomId=sparkMsgRoomId, markdown=textAnswer, files=https://developer.ciscospark.com/images/logo_spark_lg.png)

            else:

                if not sparkMessage.files:
                    textAnswer = 'Hello <@personEmail:' + str(jsonAnswer['data']['personEmail']) + '>,you can send me a CSV file including a list of e-mail addresses and I will add them to this space.'
                    botAnswered = api.messages.create(roomId=sparkMsgRoomId, markdown=textAnswer)

                # If the message comes with a file
                else:
                    sparkMsgFileUrl = str(sparkMessage.files[0]) # Get the URL of the first file
                    sparkHeader = {'Authorization': "Bearer " + BOT_TOKEN}
                i = 0 # Index to skip title row in the CSV file

                with requests.Session() as s: # Creating a session to allow several HTTP messages with one TCP connection
                    getResponse = s.get(sparkMsgFileUrl, headers=sparkHeader) # Get file

                    # If the file extension is CSV
                    if str(getResponse.headers['Content-Type']) == 'text/csv':
                        decodedContent = getResponse.content.decode('utf-8')
                        csvFile = csv.reader(decodedContent.splitlines(), delimiter=';')
                        listEmails = list(csvFile)
                        textAnswer = 'Hello <@personEmail:' + str(jsonAnswer['data']['personEmail']) + '>, I will start the Invite now' #Message to Room Invite will start
                        botAnswered = api.messages.create(roomId=sparkMsgRoomId, markdown=textAnswer)
                        for row in listEmails: # Creating one list for each line in the file
                            if i != 0:
                                participantAdded = api.memberships.create(roomId=sparkMsgRoomId, personEmail=str(row[2]), isModerator=False) # Add participant from e-mail field
                                #botAnswered = api.messages.create(roomId=sparkMsgRoomId, text='Invite Started'))
                            i += 1

                    # If the attached file is not a CSV
                    else:
                        textAnswer = 'Sorry, I only understand **CSV** files.'
                        botAnswered = api.messages.create(roomId=sparkMsgRoomId, markdown=textAnswer)


    return 'OK'

if __name__ == '__main__':
    app.run()
