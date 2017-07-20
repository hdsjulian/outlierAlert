import re
import urllib2

from outlierProduct import outlierProduct
from outlierMatch import outlierMatch
from outlierOutput import outlierOutput


pants = "https://shop.outlier.nyc/shop/retail/pants"
shirts = "https://shop.outlier.nyc/shop/retail/shirts"
layers = "https://shop.outlier.nyc/shop/retail/layers"
objects = "https://shop.outlier.nyc/shop/retail/objects"
discontinued = "https://shop.outlier.nyc/shop/retail/discontinued"
output = outlierOutput()

filelist = []

def createFileList(infile):
	urlcount = 0
	warningmatch = "shop_post_title"
	urlmatch="href=\"(.*)\" "
	filelist = []
	infile = urllib2.urlopen(infile)
	for line in infile.readlines():
		utf8line = unicode(line, "utf8")
		if urlcount == 0:
			matchwarning = re.search(warningmatch, utf8line)
			if matchwarning:
				urlcount = 1
		else: 
			matchurl = re.search(urlmatch, utf8line)
			if matchurl:
				filelist.append(matchurl.group(1))
				urlcount = 0
	return filelist
filelist = filelist + createFileList(pants)
filelist = filelist + createFileList(shirts)
filelist = filelist + createFileList(layers)
filelist = filelist + createFileList(objects)
#filelist = ["https://shop.outlier.nyc/shop/retail/slim-dungarees.html"]
for infile in filelist:
	product = outlierProduct(infile, output)
	page = urllib2.urlopen(infile)
	match = outlierMatch(page)
	match.matchPage(product)
	"""print product.getProductId()
	print product.getColors()
	print product.getMinPrice()
	print product.getMaxPrice()
	"""
	product.save()
	

conn.close()

