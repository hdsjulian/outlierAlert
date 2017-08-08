import re
import urllib2

from outlierProduct import outlierProduct
from outlierMatch import outlierMatch
from outlierOutput import outlierOutput
from outlierURLs import outlierURLs
from pprint import pprint
import time
from datetime import datetime
import logging
logger = logging.getLogger('outlier')
handler = logging.FileHandler('outliertest.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


output = outlierOutput()
URLs = outlierURLs(output, 1)
schedule_lasttime = URLs.getLastTime(0)

lasttime = time.time()
#products = URLs.getProducts()



def checkProduct(product, f):
	try: 
		page = urllib2.urlopen(product.getURL())
		f.write(product.getURL()+'\n\n')
		match = outlierMatch(page)
		match.matchPage(product)
		product.save()
	except: 
		logger.debug("URL could not be opened "+product.getURL())

while True:
	scheduled_tasks, frequency = URLs.checkSchedule(schedule_lasttime)
	output.readTelegramMessages()
	for task in scheduled_tasks: 
		f = open('outlier.log', "ab")
		f.write(str(datetime.now())+": "+task+" called\n")
		schedule_lasttime[task] = time.time()
		if task == 'restock':
			print 'restock called'
			products = output.getProducts()
		if task == 'products':
			print 'products called'
			products = URLs.getProducts()
		if task == 'wtf':
			print 'wtf called'
			products = URLs.getWTF()
		for product in products: 
			print 'checking '+product['url']
			product = outlierProduct(output, product)
			if task =='products':
				if not output.checkForProduct(product.getProductId()):
					checkProduct(product,f)
			else:
				checkProduct(product,f)
		f.close()
	nexttime = lasttime+frequency
	now = time.time()
	lasttime = now
	sleeptime = nexttime-now if nexttime-now > 0 else 1
	time.sleep(sleeptime)