#This is a python file which goes through your email, extracts contexts from emails and pushes pins to your timeline. 
#For example: You book a table at OpenTable and you get a confirmation from OpenTable. This script will extract context from the confirmation and push a pin to your timeline reminding you of your restaurant confirmation at the right time. 

# Uses the following 3rd Party APIs.
# 1. imaplib to set up an imap client and extract the latest unseen email.
# 2. Easily Do API to extract context from the email.

import json
import hashlib
import hmac
import time
import requests
import ftplib
import os
import imaplib
import ConfigParser
import time
from random import randint

import urllib2, re, sys

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('mumbledumblebopplemopple@gmail.com', 'WRITE YOUR PASSWORD HERE') #such security much wow
mail.list()

# Out: list of "folders" aka labels in gmail.
mail.select("inbox") # connect to inbox.

result, data = mail.uid('search', None, 'ALL') # search and return uids instead
latest_email_uid = data[0].split()[-1]
result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
raw_email = data[0][1]

import email
email_message = email.message_from_string(raw_email)

target2 = open('email.eml', 'w')

target2.write(str(email_message))
target2.close() #So imap saves the latest email as a file called "email.eml"

url = "https://api.easilydo.com/v1/discovery" 

api_key = 'e3d2476bcaa03adeaafbab8ccf505678'
api_secret = '2c6b52c5794697e8133e28994938f72acc6e3a73'

filename = 'email.eml' #Now Easily Do API uses the stored file to extract info.
eml = open(filename, "r").read().strip()
data = {
  'timestamp': int(time.time()),
  'api_key': api_key,
  'email': eml
}

base_string = 'POST&/v1/discovery'

for k in sorted(data):
  base_string += '&' + k + '=' + str(data[k])

data['signature'] = hmac.new(
  api_secret.encode('utf-8'),
  base_string.encode('utf-8'),
  hashlib.sha1
).hexdigest().decode('utf-8')

response = requests.post(url, data=data)

import datetime
import requests

list1= response.json()['result']
str1 = ''.join(list1)

print str1 #For Demo Debugging

if "restaurant" in str1: #Checks if the word restaurant appears in the string. 
  time = response.json()['result']['restaurant']['startTime']
  timeList = time.split("T")
  print timeList[1] #Extracting the time from the time returned by Easily Do

  pin = {
    "id": str(randint(0,10000)),
    "time": "2015-07-14T" + timeList[1] + "+17:00", #for demo ONLY, Change the date.
    "layout": {
      "type": "genericPin",
      "title": "Event at " + response.json()['result']['restaurant']['reservationFor']['name'],
      "headings": ["Details","Time","Address", "Contact"],
      "paragraphs":["Confirmed Reservation for " + response.json()['result']['restaurant']['reservationFor']['name'],"On " + timeList[0] + " at " + timeList[1],response.json()['result']['restaurant']['reservationFor']['address'], response.json()['result']['restaurant']['reservationFor']['telephone']],
      "body": "Event Confirmed",
      "primaryColor": "#FFFFFF",
      "secondaryColor": "#FFFFFF",
      "backgroundColor": "#0055AA",
      "tinyIcon": "system://images/DINNER_RESERVATION"
    },
    "createNotification": {
      "layout": {
        "type": "genericNotification",
        "title": "Food Reservation",
        "tinyIcon": "system://images/NOTIFICATION_GENERIC",
        "body": "Your dinner reservation has been added to your timeline."
      }
    }
  } # Valid Pin object

  url = "https://timeline-api.getpebble.com/v1/user/pins/%s" % pin["id"]
  resp = requests.put(url, #Henry's User Token
                        headers={"X-User-Token": 'SBb1HlJqYDSJ878GYYlwECelTHFGB2E9',
                                 "Content-Type": "application/json"},
                        data=json.dumps(pin))
  resp2 = requests.put(url, #Manu 
                        headers={"X-User-Token": 'SBVtI1VoG4v8SYJMgAvdh3UdnKLZEhl5',
                                 "Content-Type": "application/json"},
                        data=json.dumps(pin))

  print resp.text
  print resp.status_code
  print resp2.status_code

elif "flight" in str1: #Check if the world "flight" appears in the json.
        
  print response.json()
  time = response.json()['result']['flight']['reservationFor'][0]['departureTime']
  timeList = time.split("T")
  print timeList[1]
  time2 = response.json()['result']['flight']['reservationFor'][0]['arrivalTime']
  timeList2 = time2.split("T")
  
  pin = {
    "id": str(randint(0,10000)),
    "time": "2015-07-14T" + timeList[1] + "+17:00", 
    "layout": {
      "type": "genericPin",
      "title": "Your " + response.json()['result']['flight']['reservationFor'][0]['seller']['name'] + " Flight",
      "headings": ["Flight Number","Status", "Departure Time", "Departure Airport", "Arrival Time", "Arrival Airport", "Leaves In"],
      "paragraphs":[response.json()['result']['flight']['reservationFor'][0]['flightNumber'] + " ", "Reservation Confirmed" , "On" + timeList[0] + " at " + timeList[1],response.json()['result']['flight']['reservationFor'][0]['departureAirport']['name'] + " ", "On " + timeList2[0] + " at " + timeList2[1], response.json()['result']['flight']['reservationFor'][0]['arrivalAirport']['name'] + " ","5 days"],
      "body": "Your flight details are as follows:",
      "primaryColor": "#FFFFFF",
      "secondaryColor": "#FFFFFF",
      "backgroundColor": "#FF0055",
      "tinyIcon": "system://images/SCHEDULED_FLIGHT"
    },
    "createNotification": {
      "layout": {
        "type": "genericNotification",
        "title": "Flight Reservation",
        "tinyIcon": "system://images/NOTIFICATION_GENERIC",
        "body": "Your flight reservation has been added to your timeline."
      }
    }
  } # Valid Pin 
    
  url = "https://timeline-api.getpebble.com/v1/user/pins/%s" % pin["id"]

  resp = requests.put(url, #Henry
                        headers={"X-User-Token": 'SBb1HlJqYDSJ878GYYlwECelTHFGB2E9',
                                 "Content-Type": "application/json"},
                        data=json.dumps(pin))
  resp2 = requests.put(url, #Manu 
                        headers={"X-User-Token": 'SBVtI1VoG4v8SYJMgAvdh3UdnKLZEhl5',
                                 "Content-Type": "application/json"},
                        data=json.dumps(pin))

  print resp.text
  print resp.status_code
  print resp2.status_code
  
else:
 
  strD = str(response.json()['result'])
  if len(strD) > 1024: #Preventing the condition when length > 1024
    strD = strD[0:1023]
  print len(strD)
  print response.json()
  pin = {
    "id": str(randint(0,10000)),
    "time": "2015-07-14T" + "18:00:00" + "+17:00", 
    "layout": {
      "type": "genericPin",
      "title": "Event Extracted From Your Email",
      "body": strD,
      "primaryColor": "#FFFFFF",
      "secondaryColor": "#FFFFFF",
      "backgroundColor": "#AA00FF",
      "tinyIcon": "system://images/GENERIC_PIN"
    },
    "createNotification": {
      "layout": {
        "type": "genericNotification",
        "title": "Event Notification",
        "tinyIcon": "system://images/NOTIFICATION_GENERIC",
        "body": "Your event has been added to your timeline."
      }
    }
  } # Valid Pin 
  
  url = "https://timeline-api.getpebble.com/v1/user/pins/%s" % pin["id"]
  resp = requests.put(url, #Henry
                        headers={"X-User-Token": 'SBb1HlJqYDSJ878GYYlwECelTHFGB2E9',
                                 "Content-Type": "application/json"},
                        data=json.dumps(pin))
  resp2 = requests.put(url, #Manu 
                        headers={"X-User-Token": 'SBVtI1VoG4v8SYJMgAvdh3UdnKLZEhl5',
                                 "Content-Type": "application/json"},
                        data=json.dumps(pin))

  print resp.text
  print resp.status_code
  print resp2.status_code