import re
import urllib2

from outlierProduct import outlierProduct
from outlierMatch import outlierMatch
from outlierOutput import outlierOutput
from outlierURLs import outlierURLs
from pprint import pprint
import time
from datetime import datetime
output = outlierOutput()
URLs = outlierURLs(output, 1)
schedule_lasttime = URLs.getLastTime(0)

print schedule_lasttime
lasttime = time.time()

#products = URLs.getProducts()

def checkProduct(product, f):
	product = outlierProduct(output, product)
	page = urllib2.urlopen(product.getURL())
	f.write(product.getURL()+'\n\n')
	match = outlierMatch(page)
	match.matchPage(product)
	product.save()

while True:
	scheduled_tasks, frequency = URLs.checkSchedule(schedule_lasttime)
	output.readTelegramMessages()
	print scheduled_tasks
	for task in scheduled_tasks: 
		f = open('outlier.log', "a")
		f.write(str(datetime.now())+": "+task+" called\n")
		schedule_lasttime[task] = time.time()
		if task == 'restock':
			products = output.getProducts()
		if task == 'products':
			products = URLs.getProducts()
		if task == 'wtf':
			products = URLs.getWTF()
		for product in products: 
			checkProduct(product,f)
		f.close()
	nexttime = lasttime+frequency
	now = time.time()
	lasttime = now
	sleeptime = nexttime-now if nexttime-now > 0 else 1
	time.sleep(sleeptime)