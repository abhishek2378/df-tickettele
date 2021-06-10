# import flask dependencies
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
from datetime import datetime
from bson.json_util import dumps,loads
from bson.objectid import ObjectId
import pymongo
from pymongo import MongoClient
import requests
import os
import json
from requests.auth import HTTPBasicAuth

### mongodb+srv://abhishek:chandan@cluster0.akxed.mongodb.net/testdialog?retryWrites=true&w=majority

# client = MongoClient("mongodb+srv://abhishek:chandan@cluster0.akxed.mongodb.net/testdialog?retryWrites=true&w=majority")
# db = client.testdialog

### API url - This API connects with CRM system of Penguin



# initialize the flask app
app = Flask(__name__)

# create a route for webhook - This Webhook connects with DialogFlow which in turn connects with Telegram App.  
@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():
    req = request.get_json(silent=True, force=True)
#    url = "http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json"
# This is the main Function which gets request in JSON format and checks for intent. Based on intent it responds.     
    res = processRequest(req)
    res = json.dumps(res, indent=4)
#    print(res)
    r=make_response(res)
    r.headers['Conten_type'] = 'application/json' 
    return r

# processing the request from dialogflow - Based on intent different values are  returned 
def processRequest(req):
    sessionID = req.get('responseId')
    url = "http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json"
    result = req.get("queryResult")
    intent = result.get("intent").get('displayName')
    query_text = result.get("queryText")
    parameters = result.get("parameters")

# This takes the phone number and then gets the Name from API.     
    if intent == 'phone_number':
#        collection = db.phonename 
        url = "http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json"
        phone_number = parameters["phone_number"]
# response = requests.post("http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json",headers=headers,auth=("admin","1234"),data={"phone_mobile":phone_number})                 
                     
        headers  = {"apikey":"123456"}
        try:
            response = requests.post("http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json",headers=headers,auth=("admin","1234"),data={"phone_mobile":phone_number})
        except Exception as e:
            print(e)
            if e == "Expecting Value: line 1 column 1 (char 0)":
                print("number doed not exist")        
        try:
            response_Json = response.json()
            message = response_Json["message"]
        except Exception as e:
            print(e)                    


# If customer is not found then it sends back the message that you are not autorized. It asks to share registered number. 

        if message=="Customer Not Found.":
            webhooktext = "you are not authorized with this number." 
            webhooktext1 = "Please share your registered number. " 
            return {
             "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhooktext
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            webhooktext1
                        ]
                    }
                }
            ]
        }

# if Customer is found with that number, it gives quick replies and ask for selecting one of them.         
        elif message == "SUCCESS":
            name=response_Json["Customer Name"]
            webhooktext = "Dear "+ name + " ,please select the option from below"
            return {
            "fulfillmentMessages": [
              {
                "quickReplies": {
                  "title": webhooktext,
                  "quickReplies": [
                    "Raise new Ticket",
                    "Old Ticket status"
                  ]
                },
                "platform": "TELEGRAM"
              },
        ],            
        }
#            webhooktext1 = name              

    


# This is called when new ticket is to be raised.
  
    elif intent == "phone_number - option1 - issuedetail":
        phone = parameters["phone_number"]
        query_text = result.get("queryText")
        parameters = result.get("parameters")
        url = "http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json"
        phone_number = parameters["phone_number"]
        headers  = {"apikey":"123456"}
        try:
            response = requests.post("http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json",headers=headers,auth=("admin","1234"),data={"phone_mobile":phone_number, "description":query_text})
        except Exception as e:
            print(e)
            if e == "Expecting Value: line 1 column 1 (char 0)":
                print("number doed not exist")        
        try:
            response_Json = response.json()
            newcount = response_Json["Ticket ID"]   
        except Exception as e:
            print(e)
        webhooktext = str(newcount) 
        webhooktext1 = "Ticket number is " + webhooktext + ". Please select the options from below. "
        return {
            "fulfillmentMessages": [
              {
                "quickReplies": {
                  "title": webhooktext1,
                  "quickReplies": [
                    "I am Satisfied with the response",
                    "Want to connect with customer care"
                  ]
                },
                "platform": "TELEGRAM"
              },
        ],            
        }     

# This is called when status has to be shared with the customer for a specific ticket number. 

    elif intent == "phone_number - option2 - next ticket - ticketid":
        phone_number = parameters["phone_number"]
        ticket_number=int(parameters["number"])
        url = "http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json"
        headers  = {"apikey":"123456"}
        try:
            response = requests.post("http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json",headers=headers,auth=("admin","1234"),data={"ticket_id":ticket_number,"phone_mobile":phone_number})
        except Exception as e:
            print(e)
            if e == "Expecting Value: line 1 column 1 (char 0)":
                print("number doed not exist")                        
        response_Json = response.json()
        message=response_Json["message"]
        status = response_Json["status"]

        if message=="Ticket does not exist":
            webhooktext = "Ticket does not exist." 
            webhooktext1 = "Please share the correct ticket number. " 
            return {
             "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhooktext
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            webhooktext1
                        ]
                    }
                }
            ]
        }
        elif message== "SUCCESS":
            webhooktext = "Status is as mentioned below"
            webhooktext1 = status
            webhooktext2 = "Status is: " + webhooktext1
        
            return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhooktext2
                        ]

                    }
                },        
              {
                "quickReplies": {
                  "title": webhooktext2,
                  "quickReplies": [
                    "I am Satisfied with the response",
                    "I want to connect with customer care"
                  ]
                },
                "platform": "TELEGRAM"
              },
        ],            
        }      
    
# This is called from option - when issue detail is entered and time for customer support is to be shared with CRM. 

    elif intent == "phone_number - option1 - issuedetail - customer_support":
        phone = parameters["phone_number"]
        webhooktext1 = "Please select the right option, at which customer executive will contact you."
        return {
            "fulfillmentMessages": [
              {
                "quickReplies": {
                  "title": webhooktext1,
                  "quickReplies": [
                    "9am - 12pm",
                    "12pm - 3pm",    
                    "3pm - 6pm"
                  ]
                },
                "platform": "TELEGRAM"
              },
        ],     
        }

# This is from the option1 where we will be sharing the customer support time with the CRM and inform the customer around it. 

    elif intent=="phone_number - option1 - issuedetail - customer_support - time":
        query_text = result.get("queryText")
        url = "http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json"
        phone_number = parameters["phone_number"]
        headers  = {"apikey":"123456"}
        try:
            response = requests.post("http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json",headers=headers,auth=("admin","1234"),data={"phone_mobile":phone_number, "followup_time":query_text})
        except Exception as e:
            print(e)
        webhooktext = "Thank you for the response. We will pass on your details to customer executive"
        webhooktext1 = "They will contact you at your preferred time. This session is closed now. Have a good day."
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhooktext
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            webhooktext1
                        ]

                    }
                }
            ]
        }

# This is for the option 2 (related to issue status), where we will be asking the preferred time for connect. 
    elif intent=="phone_number - custom-option2 - custom - customer_support":
        phone = parameters["phone_number"]
        webhooktext1 = "Please select the right option, at which customer executive will contact you."
        return {
            "fulfillmentMessages": [
              {
                "quickReplies": {
                  "title": webhooktext1,
                  "quickReplies": [
                    "9am - 12pm",
                    "12pm - 3pm",
                    "3pm - 6pm"
                  ]
                },
                "platform": "TELEGRAM"
              },
        ],     
        }
# This is for the option 2 (related to issue status), where we will be sharing customer connect time with CRM through API.

    elif intent=="phone_number - custom-option2 - custom - customer_support - time":
        query_text = result.get("queryText")
        phone = parameters["phone_number"]
        webhooktext = "Thank you for the response. we will pass on your details to customer executive"
        webhooktext1 = "They will contact you at your preferred time. This session is closed now. Have a good day."
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhooktext
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            webhooktext1
                        ]

                    }
                }
            ]
        }

    elif intent == "phone_number - custom-option2 - not needed":
        phone_number = parameters["phone_number"]
        webhooktext1 = "Please select the right option from below."

        return {
            "fulfillmentMessages": [
              {
                "quickReplies": {
                  "title": webhooktext1,
                  "quickReplies": [
                    "I am Satisfied with the response",
                    "Want to connect with customer care"
                  ]
                },
                "platform": "TELEGRAM"
              },
        ],            
        }                 



    elif intent == "phone_number - custom-option2":
        url = "http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json"
        phone_number = parameters["phone_number"]
        headers  = {"apikey":"123456"}
        try:
            response = requests.post("http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json",headers=headers,auth=("admin","1234"),data={"phone_mobile":phone_number})
        except Exception as e:
            print(e)
            if e == "Expecting Value: line 1 column 1 (char 0)":
                print("number doed not exist")        
        try:
            response_Json = response.json()
            ticketid = response_Json["Ticket ID"]
            status = response_Json["status"]
        except Exception as e:
            print(e)                    
        webhooktext = str(ticketid) 
        webhooktext1 = "Status of your ticketid "  + webhooktext + " is: "+ status +" - Please check the option from below"
        return {
            "fulfillmentMessages": [
              {
                "quickReplies": {
                  "title": webhooktext1,
                  "quickReplies": [
                    "Check status of another ticket",
                    "No other query"
                  ]
                },
                "platform": "TELEGRAM"
              },
        ],            
        }   

    elif intent == "phone_number - custom-option2 - not needed - customercare":
        phone = parameters["phone_number"]
        webhooktext1 = "Please select the right option, at which customer executive will contact you."
        return {
            "fulfillmentMessages": [
              {
                "quickReplies": {
                  "title": webhooktext1,
                  "quickReplies": [
                    "9am - 12pm",
                    "12pm - 3pm",
                    "3pm - 6pm"
                  ]
                },
                "platform": "TELEGRAM"
              },
        ],     
        }        
    elif intent == "phone_number - ticket status - not needed - customercare - time":
        query_text = result.get("queryText")
        url = "http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json"
        phone_number = parameters["phone_number"]
        headers  = {"apikey":"123456"}
        try:
            response = requests.post("http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json",headers=headers,auth=("admin","1234"),data={"phone_mobile":phone_number, "followup_time":query_text})
        except Exception as e:
            print(e)
        webhooktext = "Thank you for the response. we will pass on your details to customer executive"
        webhooktext1 = "They will contact you at your preferred time. This session is closed now. Have a good day."
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhooktext
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            webhooktext1
                        ]

                    }
                }
            ]
        }

    elif intent == "phone_number - option2 - next ticket - ticketid - connect customer care":
        phone = parameters["phone_number"]
        webhooktext1 = "Please select the right option, at which customer executive will contact you."
        return {
            "fulfillmentMessages": [
              {
                "quickReplies": {
                  "title": webhooktext1,
                  "quickReplies": [
                    "9am - 12pm",
                    "12pm - 3pm",
                    "3pm - 6pm"
                  ]
                },
                "platform": "TELEGRAM"
              },
        ],     
        }        

    elif intent == "phone_number-next ticket - ticketid - customer care - timeconfirm":
        query_text = result.get("queryText")
        url = "http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json"
        phone_number = parameters["phone_number"]
        headers  = {"apikey":"123456"}
        try:
            response = requests.post("http://cloudpenguincrm.com/poncloud_services/api/v1?module=Generate_tickets&format=json",headers=headers,auth=("admin","1234"),data={"phone_mobile":phone_number, "followup_time":query_text})
        except Exception as e:
            print(e)
        webhooktext = "Thank you for the response. we will pass on your details to customer executive"
        webhooktext1 = "They will contact you at your preferred time. This session is closed now. Have a good day."
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhooktext
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            webhooktext1
                        ]

                    }
                }
            ]
        }

if __name__ == '__main__':
   port=int(os.getenv('PORT',5000))
   print(f"starting on port {port}")
   app.run(debug=False,port=port,host='0.0.0.0')