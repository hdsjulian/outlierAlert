import praw
import time
import pprint
import config as config

lasttime = time.time()

class outlierReddit(object):
	def __init__(self, output):
		self.output = output
		self.reddit = praw.Reddit(settings.client_id, redirect_uri='http://localhost:8080', settings.client_secret, settings.password, settings.username, settings.user_agent)
		self.subreddit = self.reddit.subreddit("outliermarket")
		self.time = output.getRedditTime()
		print self.time
	def checkSubmissions(self):
		for submission in self.subreddit.submissions(start=self.time):
			self.output.saveRedditPost(submission.title, int(submission.created))