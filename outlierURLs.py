import urllib2
import re
from pprint import pprint
from time import time, localtime, strftime
class outlierURLs(object):

	def __init__(self, output, match):
		self.output = output
		self.match = match
		self.PANTS_URL = "https://shop.outlier.nyc/shop/retail/pants"
		self.SHIRTS_URL = "https://shop.outlier.nyc/shop/retail/shirts"
		self.LAYERS_URL = "https://shop.outlier.nyc/shop/retail/layers"
		self.OBJECTS_URL = "https://shop.outlier.nyc/shop/retail/objects"
		self.DISCONTINUED_URL = "https://shop.outlier.nyc/shop/retail/discontinued"
		self.WTF_BOTTOM_URL = "https://shop.outlier.nyc/shop/retail/wtf-bottom.html"
		self.WTF_TOP_URL = "https://shop.outlier.nyc/shop/retail/wtf-top-pack.html"
		self.schedule = {}
		self.urls = {}
		self.urls['overview'] = [self.PANTS_URL, self.SHIRTS_URL, self.LAYERS_URL, self.OBJECTS_URL, self.DISCONTINUED_URL]
		self.urls['wtf'] = {self.WTF_TOP_URL, self.WTF_BOTTOM_URL}
		self.schedule['wtf'] = {
			'day_of_week':['Tue','Wed', 'Thu'], 
			'time_begin':17, 
			'time_end':23,
			'frequency': 60
		}
		self.schedule['products'] = {
			'day_of_week':['Tue','Thu'], 
			'time_begin':17, 
			'time_end':22,
			'frequency': 900
		}
		self.schedule['restock'] = {
			'day_of_week':['Tue', 'Thu'], 
			'time_begin':19, 
			'time_end':22,
			'frequency': 600
		}

	def checkSchedule(self, lasttime):
		now = localtime()
		actionlist = []
		frequency = 1000
		for scheduletype, scheduledata in self.schedule.iteritems():

			frequency = scheduledata['frequency'] if frequency > scheduledata['frequency'] else frequency
			if strftime('%a', now) in scheduledata['day_of_week'] and int(strftime('%H', now)) > scheduledata['time_begin'] and int(strftime('%H', now)) < scheduledata['time_end'] and time() > lasttime[scheduletype]+scheduledata['frequency']-1:
				print scheduletype
				print "---\n"
				actionlist.append(scheduletype)


		return actionlist, frequency


	def getLastTime(self, time):
		lasttime = {}
		for scheduletype in self.schedule.iterkeys():
			lasttime[scheduletype] = time
		return lasttime
	def getProducts(self):
		return self.parseOverview(self.PANTS_URL)
	def getWTF(self):
		return [{'product_id':6325, 'url':self.WTF_TOP_URL}, {'product_id':6361, 'url':self.WTF_BOTTOM_URL}]
	def parseOverview(self, url):
		print url
		url_count = 0
		warning_match="shop_post_title"
		url_match = "href=\"(.*)\" "
		image_url_match = "img src=\"(.*)\" width"
		product_id_match = "input type=\"hidden\" name=\"product\" value=\"(.*)\" "
		products = []
		product = {}
		infile = urllib2.urlopen(url)
		matches = {}
		for line in infile.readlines():
			utf8line = unicode(line, "utf8")
			if url_count == 0:
				match_warning = re.search(warning_match, utf8line)
				if match_warning: 
					url_count = 1
			else: 
				matches['url'] = re.search(url_match, utf8line)
				matches['image_url'] = re.search(image_url_match, utf8line)
				matches['product_id'] = re.search(product_id_match, utf8line)
				for k,v in matches.iteritems():
					if v:
						if k == 'url':
							product['url'] = v.group(1)
						if k == 'image_url':
							product['image_url'] = v.group(1)
						if k == 'product_id':
							product['product_id'] = v.group(1)
							url_count = 0
							products.append(product)
							product = {}
							matches = {}
		return products



def createfile_list(infile):
	print infile
	url_count = 0
	warning_match = "shop_post_title"
	url_match="href=\"(.*)\" "
	file_list = []
	infile = urllib2.urlopen(infile)
	for line in infile.readlines():
		utf8line = unicode(line, "utf8")
		if url_count == 0:
			match_warning = re.search(warning_match, utf8line)
			if match_warning:
				url_count = 1
		else: 
			match_url = re.search(url_match, utf8line)
			if match_url:
				file_list.append(match_url.group(1))
				url_count = 0
	return file_list