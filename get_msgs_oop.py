from slackclient import SlackClient

import pprint
pp = pprint.PrettyPrinter(indent=4)

from gtts import gTTS

import sys

import time

import datetime

import os

# --- HARD CODED PARAMS ---
# set up slack client
SLACK_TOKEN = 'xoxp-308787255059-309011836258-342347989826-30d8fe1e7a852c8e4578341783511c4f'

# set channel ID to get msgs from
CHANNEL = 'C9CFE1J8J' # get all channels with sc.api_call("channels.list")
#/ --- HARD CODED PARAMS ---


class SlackMessageCaller(object):
	def __init__(self, slack_token, channel = 'C9CFE1J8J', keep_sound_files = False, sleeptime = 60, filecounter = 0):
		self.slack_token = slack_token

		self.sc = SlackClient(self.slack_token)
		self.slack_channel = channel
		
		self.keep_sound_files = keep_sound_files
		self.sleeptime = sleeptime
		
		self.filecounter = filecounter
		
	def __sleep_countdown(self, seconds = 60):
		for i in range(seconds, 0 , -1):
			sys.stdout.write("Waiting {} seconds\r".format(i))
			sys.stdout.flush()
			time.sleep(1)    
	
	def __startup_routine(self):
		os.system("aplay notify.wav")
		self.latestMsg = self.sc.api_call("channels.history",channel=self.slack_channel,count=1)
		self.prevTimestamp = self.latestMsg['messages'][0]['ts']
		self.latestMsgText = self.latestMsg['messages'][0]['text']
		
		userId = self.latestMsg['messages'][0]['user']
		user = self.sc.api_call("users.info",user=userId)
		pp.pprint(user)
		firstName = user['user']['profile']['first_name']
		
		msg_to_play = '{} says "{}"'.format(firstName, self.latestMsgText)
		print(msg_to_play)
		
		self.play_message(msg_to_play)
		
	def play_message(self, message, filename = None):
		tts = gTTS(text=message, lang='en-uk') # en-us is another option
		
		if not self.keep_sound_files:			
			tts.save(".temp.mp3")
			os.system('cvlc --play-and-exit .temp.mp3')
			os.remove(".temp.mp3")
		else:
			if filename is None:
				filename = "message_{}.mp3".format(self.filecounter)
				tts.save(filename)
				self.filecounter += 1
				
				os.system('cvlc --play-and-exit {}'.format(filename))
			else:
				tts.save("filename.mp3")
				os.system('cvlc --play-and-exit {}'.format(filename))

	def start(self):
		self.__startup_routine()
		
		while True:
			# get all msgs that are after the timestamp of the last seen msg
			newMsgs = self.sc.api_call("channels.history",channel=self.slack_channel,oldest=self.prevTimestamp)

			if newMsgs['messages']:
				# play notification sound
				os.system("aplay notify.wav")

				#for each message, print and say the msg
				for msg in newMsgs['messages'][::-1]: # reverse order the msgs so they are in chronological order

					msgText = msg['text']

					userId = msg['user']
					user = sc.api_call("users.info",user=userId)
					firstName = user['user']['profile']['first_name']
					
					msg_to_play = '{} says "{}"'.format(firstName, msgText)
					print(msg_to_play)
					
					self.play_message(msg_to_play)

					self.prevTimestamp = msg['ts']
			else:
				now = datetime.datetime.now()
				print ("No new messages at {}".format(now.strftime("%Y-%m-%d %H:%M:%S")))

			# wait a bit till we recheck the channel, in seconds	
			self.__sleep_countdown(self.sleeptime)

			
if __name__ == '__main__':
	msgr = SlackMessageCaller(slack_token = SLACK_TOKEN)
	msgr.start()
