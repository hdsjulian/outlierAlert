import praw
import time
import pprint

lasttime = time.time()

class outlierReddit(object):
	def __init__(self, output):
		self.output = output
		self.reddit = praw.Reddit(client_id="p6hLVrsRObt_1g", redirect_uri='http://localhost:8080', client_secret="0EPMfNaVu16S5rfxBJp8ZJE8Qls", password="stuh2s", username="hdsjulian", user_agent="testingthis")
		self.subreddit = self.reddit.subreddit("outliermarket")
		self.time = output.getRedditTime()
		print self.time
	def checkSubmissions(self):
		for submission in self.subreddit.submissions(start=self.time):
			self.output.saveRedditPost(submission.title, int(submission.created))