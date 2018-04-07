"""
Important Note. Make sure that apart from the python libraries below, you also have vlc installed.
You can do this by typing "sudo apt-get install vlc" in the command line.
"""
from slackclient import SlackClient
import pprint
from gtts import gTTS
import sys
import time
import datetime
import os


pp = pprint.PrettyPrinter(indent=4)

# --- HARD CODED PARAMS ---
# set up slack client
SLACK_TOKEN = 'Slack Token'

# set channel ID to get msgs from
CHANNEL = 'C9CFE1J8J'  # get all channels with sc.api_call("channels.list")


# / --- HARD CODED PARAMS ---


class SlackMessageCaller(object):
    """
    An object class for automatically fetching messages from a slack channel and reading them aloud.
    """

    def __init__(self, slack_token: str, channel: str = 'C9CFE1J8J', keep_sound_files: bool = False,
                 sound_filename_base: str = None, sleeptime: int = 60, filecounter: int = 0,
                 language: 'en-us' or 'en-uk' = 'en-uk'):
        # TODO: implement check whether the path to which filenames will be saved exists.
        """
        Initialize the attributes.
        :param slack_token: <string> The private token from the slack api. Look here on how to create a slack token:
            https://get.slack.help/hc/en-us/articles/215770388-Create-and-regenerate-API-tokens
        :param channel: <string> A code referring to a slack channel to the channel you which to read the messages from.
            Obtain a list of all channels by calling: sc = SlackClient(slack_token); sc.api_call("channels.list")
        :param keep_sound_files: <bool>. Set to True if you want to keep the mp3 files of the spoken messages.
        :param: sound_filename_base: <string> Only relevant when kee_sound_files == True.
            Parameter determines the start of the names of the mp3 files that are created.
            Do not include the file extension(.mp3) in the filename base. Only a name with which you can recognise the file.
            It is allowed to precede a path to which the files need to be saved.
        :param filecounter: <int> A counts the number of mp3 files that have been created.
            This counter will make sure that all created files get a different filename.
            Set this parameter to any integer, if you do not want the counter to start at 0.
        :param sleeptime: <int>. Time between different callouts.
        :param language: <str>. Either 'en-uk' or 'en-us'. The language in which the messages should be read.
        """
        self.slack_token = slack_token

        self.sc = SlackClient(self.slack_token)
        self.slack_channel = channel

        self.keep_sound_files = keep_sound_files
        self.sound_filename_base = sound_filename_base
        self.filecounter = filecounter

        self.sleeptime = sleeptime

        self.language = language

    def __sleep_countdown(self, seconds: int = 60):
        """
        A function that counts down until the next readout. The function visually counts down on stdout.
        :param seconds: <int> nr of seconds until the next readout.
        :return: None
        """
        for i in range(seconds, 0, -1):
            sys.stdout.write("Waiting {} seconds\r".format(i))
            sys.stdout.flush()
            time.sleep(1)

    def __startup_routine(self):
        """
        A startup routine that is invoced if self.start() is called.
        :return: None
        """
        os.system("aplay notify.wav")
        self.latestMsg = self.sc.api_call("channels.history", channel=self.slack_channel, count=1)
        self.prevTimestamp = self.latestMsg['messages'][0]['ts']
        self.latestMsgText = self.latestMsg['messages'][0]['text']

        userId = self.latestMsg['messages'][0]['user']
        user = self.sc.api_call("users.info", user=userId)
        pp.pprint(user)
        firstName = user['user']['profile']['first_name']

        msg_to_play = '{} says "{}"'.format(firstName, self.latestMsgText)
        print(msg_to_play)

        self.play_message(msg_to_play)

    def __generate_soundfilename(self):
        return "{base}_{num:02d}.mp3".format(base=self.sound_filename_base, num=self.filecounter)

    def play_message(self, message: str):
        """
        Generates an mp3 file of a readout of a given message and plays this message.
        If self.keep_sound_files == True, the mp3 file will be kept. Otherwise, it will be deleted.
        :param message:
        :return: None
        """
        tts = gTTS(text=message, lang=self.language)

        if not self.keep_sound_files:
            tts.save(".temp.mp3")
            os.system('cvlc --play-and-exit .temp.mp3')
            os.remove(".temp.mp3")
        else:
            filename = self.__generate_soundfilename()
            filename = "message_{}.mp3".format(self.filecounter)
            tts.save(filename)
            self.filecounter += 1
            os.system('cvlc --play-and-exit {}'.format(filename))

    def start(self):
        """
        Start an infinite loop that checks every N seconds whether there are new messages. If so, these messages are played.
        :return: None
        """
        # TODO: implement the possibility to define terminating criteria for the loop.
        self.__startup_routine()

        while True:
            # get all msgs that are after the timestamp of the last seen msg
            newMsgs = self.sc.api_call("channels.history", channel=self.slack_channel, oldest=self.prevTimestamp)

            if newMsgs['messages']:
                # play notification sound
                os.system("aplay notify.wav")

                # for each message, print and say the msg
                for msg in newMsgs['messages'][::-1]:  # reverse order the msgs so they are in chronological order

                    msgText = msg['text']

                    userId = msg['user']
                    user = self.sc.api_call("users.info", user=userId)
                    firstName = user['user']['profile']['first_name']

                    msg_to_play = '{} says "{}"'.format(firstName, msgText)
                    print(msg_to_play)

                    self.play_message(msg_to_play)

                    self.prevTimestamp = msg['ts']
            else:
                now = datetime.datetime.now()
                print("No new messages at {}".format(now.strftime("%Y-%m-%d %H:%M:%S")))

            # wait a bit till we recheck the channel, in seconds
            self.__sleep_countdown(self.sleeptime)


if __name__ == '__main__':
    msgr = SlackMessageCaller(slack_token=SLACK_TOKEN)
    msgr.start()
