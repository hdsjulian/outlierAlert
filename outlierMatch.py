import re
class outlierMatch(object):
	def __init__(self, page):
		self.page = page
		self.patterns = {}
		self.patterns["color"] = "^data-color\=\"([0-9]*).*item-color\">([A-Za-z\ ]+)"
		self.patterns["name"] = "\<h1\>(.*)\<\/h1\>"
		self.patterns["product_id"] = "<input type=\"hidden\" name=\"product\" value=\"([0-9]*)\""
		self.patterns["price"] = "setOption\(.*?,.*?,([0-9]+),.*?,.*?,'\$([0-9]+)"
		self.patterns["size"] = "^data-color\=\"([0-9]*).*?span>([A-Z0-9]+)"
		self.descriptionpattern ="class=\"std\">(.*)<"
		self.storyheadlinepattern = "<dt>Story</dt>"
		self.storybodypattern1 = "<dd>(.*)"
		self.storybodypattern1 = "(.*)</dd>"
		self.storybodypattern3 = "<dd>(.*)</dd>"

	def matchPage(self, product):
		for line in self.page.readlines():
			utfline = unicode(line, "utf8")
			self.matchColor(line, product)
			self.matchName(line, product)
			self.matchProductId(line, product)
			self.matchPrice(line, product)
			self.matchSize(line, product)

	def matchColor(self, line, product):
		matchcolor = re.search(self.patterns["color"], line)
		if matchcolor: 
			product.addColor(int(matchcolor.group(1)), matchcolor.group(2))

	def matchName(self, line, product):
		matchname = re.search(self.patterns["name"], line)
		if matchname:
			product.setName(matchname.group(1))

	def matchProductId(self, line, product):
		match_product_id = re.search(self.patterns["product_id"], line)
		if match_product_id:
			product.setProductId(int(match_product_id.group(1)))

	def matchPrice(self, line, product):
		matchprice = re.search(self.patterns["price"], line)
		if matchprice:
			product.addPrice(int(matchprice.group(1)), matchprice.group(2))

	def matchSize(self, line, product):
		matchsize = re.search(self.patterns["size"], line)
		if matchsize: 
			product.addSize(int(matchsize.group(1)), matchsize.group(2))
