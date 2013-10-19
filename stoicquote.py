#!/usr/bin/env python

'''
Program: StoicQuote for Twitter
By: e0s
Date: 10/18/13
Description: Posts a tweet related to Stoicism

'''

import tweepy, access, time, os

class Login:
    """
    Logs into the user's account using software application's
    and user's credentials
    """
    def __init__(self):
        self.cons_key = access.cons_key
        self.cons_secret = access.cons_secret
        self.access_token = access.access_token
        self.access_token_secret = access.access_token_secret

        self.auth = tweepy.OAuthHandler(self.cons_key,self.cons_secret)
        self.auth.set_access_token(self.access_token,self.access_token_secret)

    def getAPI(self):
        """
        Returns the main api object from the tweety twitter api to interact with
        twitter
        """
        self.api = tweepy.API(self.auth)
        return self.api
        

class QuoteHandler:
    """
    Handles pulling the next quote to the Stoicwriter
    """


    def __init__(self,p):
        self.p = p
        self.msg = ''
        self.nowwrite = 0
        self.txt = ''
        self.f = None
        self.cut = 0

    def yankMessage(self):
        """
        opens the file and returns the next quote
        """
        self.f = open(self.p,'r')
        self.txt = self.f.readlines()
        self.f.close()
        self.f = open(self.p,'w')

        for line in self.txt:

            if(self.nowwrite == 1):
                self.f.write(line)
            elif(line != '\r\n' and line !='\r' and line != '\n'):
                self.msg = line
                self.cut = self.msg.find('\r\n')
                self.msg = self.msg[0:self.cut]
                self.nowwrite = 1
                
        self.f.close()
        return self.msg
    
    def putLastMessage(self):
        """
        Use in case there is an error uploading the tweet. Reverts the file back to
        before it was overwritten
        """
        self.f = open(self.p,'w')
        self.f.write(self.txt)
        self.f.close()


class Stoicwriter:
    """
    Uses the Login and QuoteHandler class to publish tweets
    """

    def __init__(self,login,quotehandler):
        self.login = login
        self.api = self.login.getAPI()
        self.quotehandler = quotehandler
        self.next_message = self.quotehandler.yankMessage()
        self.message_list = []

    def ensureLimit(self,next_message):
        """
        Ensures each twitter message we send is not over 140 characters.
        If they are, it breaks them down and puts them in message_list
        """
        i=139
        self.next_message = next_message
        if len(self.next_message) > 140:
            while(self.next_message[i]!=' '):
                i = i - 1
            self.message_list.append(self.next_message[0:i])
            self.ensureLimit(self.next_message[i+1:])
        else:
            self.message_list.append(self.next_message)

    def tweet(self):
        """
        parses through message_list to send our tweets and sleeps 4 seconds after
        each attempt    
        """
        self.ensureLimit(self.next_message)
        for message in self.message_list:
            self.api.update_status(message)
            time.sleep(4)
         
directory = os.path.dirname(__file__)
os.chdir(directory)
path = 'data/meditations/meditations_pull.txt'
login = Login()
quotehandler = QuoteHandler(path)
try:
    stoicwriter = Stoicwriter(login, quotehandler)
    stoicwriter.tweet()
except:
    quotehandler.putLastMessage()

    
