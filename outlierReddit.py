import praw
import time
import pprint
import config as config

lasttime = time.time()

class outlierReddit(object):
	def __init__(self, output):
		self.output = output
		self.reddit = praw.Reddit(client_id=config.client_id, redirect_uri='http://localhost:8080', client_secret=config.client_secret, password=config.password, username=config.username, user_agent=config.user_agent)
		self.subreddit = self.reddit.subreddit("outliermarket")
		self.time = output.getRedditTime()
		print self.time
	def checkSubmissions(self):
		for submission in self.subreddit.submissions(start=self.time):
			self.output.saveRedditPost(submission.title, int(submission.created))