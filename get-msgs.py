from slackclient import SlackClient

import pprint
pp = pprint.PrettyPrinter(indent=4)

from gtts import gTTS

import sys

import time

import datetime

import os

# function to wait and display waiting time
def sleep_countdown(seconds = 60):
	for i in range(seconds, 0 , -1):
		sys.stdout.write("Waiting {} seconds\r".format(i))
		sys.stdout.flush()
		time.sleep(1)


# set up slack client
slack_token = 'SLACK TOKEN GOES HERE'
sc = SlackClient(slack_token)

# set channel ID to get msgs from
randomChannel = 'C9CFE1J8J' # get all channels with sc.api_call("channels.list")


# play notification sound
os.system("aplay notify.wav")

# first say the last message, we gotta start somewhere..
latestMsg = sc.api_call("channels.history",channel=randomChannel,count=1)
prevTimestamp = latestMsg['messages'][0]['ts']
latestMsgText = latestMsg['messages'][0]['text']

userId = latestMsg['messages'][0]['user']
user = sc.api_call("users.info",user=userId)
pp.pprint(user)
firstName = user['user']['profile']['first_name']

print(firstName+' says '+latestMsgText)

tts = gTTS(text=firstName+' says '+latestMsgText, lang='en-uk') # en-us is another option
tts.save("temp.mp3")
os.system('cvlc --play-and-exit ' + "temp.mp3")
os.remove("temp.mp3")


while True:
	
	# get all msgs that are after the timestamp of the last seen msg
	newMsgs = sc.api_call("channels.history",channel=randomChannel,oldest=prevTimestamp)
	
	#pp.pprint(newMsgs)
	
	if newMsgs['messages']:
		# play notification sound
		os.system("aplay notify.wav")

		#for each message, print and say the msg
		for msg in newMsgs['messages'][::-1]: # reverse order the msgs so they are in chronological order
		
			msgText = msg['text']
			
			userId = msg['user']
			user = sc.api_call("users.info",user=userId)
			firstName = user['user']['profile']['first_name']
			
			print(firstName+' says '+msgText)
			
			tts = gTTS(text=firstName+' says '+latestMsgText, lang='en')
			tts.save("temp.mp3")
			os.system('cvlc --play-and-exit ' + "temp.mp3")
			os.remove("temp.mp3")
			
			prevTimestamp = msg['ts']
	else:
		now = datetime.datetime.now()
		print ("No new messages at {}".format(now.strftime("%Y-%m-%d %H:%M:%S")))
		
	# wait a bit till we recheck the channel, in seconds	
	sleep_countdown(2)
	
	
	
	
	
	
	
	
	
	
	
	
