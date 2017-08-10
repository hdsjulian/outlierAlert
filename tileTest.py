import time
import logging


class fileTest(object):
	def __init__(self):
		self.logger = logging.getLogger('outlier')
		self.handler = logging.FileHandler('outliertest.log')
		self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
		self.handler.setFormatter(self.formatter)
		self.logger.addHandler(self.handler)
		self.logger.setLevel(logging.DEBUG)


filetest = fileTest()
i = 1
while True:
	i = i+1
	if i % 5 == 0:
		print "writing"
		filetest.logger.debug(str(i)+ " wrote")
	else: 
		filetest.logger.debug(str(i % 5)+" not wrote")
	time.sleep(2)
	logger2 = logging.getLogger('outlier')
	logger2.debug('jetz ma gucken')