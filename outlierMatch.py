import re
class outlierMatch(object):
	def __init__(self, page):
		self.page = page
		self.patterns = {}
		self.patterns["color"] = "^data-color\=\"([0-9]*).*item-color\">([A-Za-z\ \(\_)]+)"
		self.patterns["name"] = "\<h1\>(.*)\<\/h1\>"
		self.patterns["product_id"] = "<input type=\"hidden\" name=\"product\" value=\"([0-9]*)\""
		self.patterns["price"] = "setOption\(.*?,.*?,([0-9]+),.*?,.*?,'\$([0-9]+)"
		self.patterns["size"] = "^data-color\=\"([0-9]*).*?span>([A-Z0-9]+)"
		self.patterns["description"] ="class=\"std\">(.*)<"
		self.patterns["story_headline_pattern"] = "<dt>Story</dt>"
		self.patterns["story_body_pattern_1"] = "<dd>(.*)"
		self.patterns["story_body_pattern_2"] = "(.*)</dd>"
		self.patterns["story_body_pattern_3"] = "<dd>(.*)</dd>"
		self.strip_html = re.compile('<.*?>')
		self.storymatch = 0
		self.story = ""
		self.story_ongoing = 0
		self.linecount = 0

	def matchPage(self, product):
		for line in self.page.readlines():
			self.linecount = self.linecount + 1
			utfline = unicode(line, "utf8")
			self.matchColor(line, product)
			self.matchName(line, product)
			self.matchProductId(line, product)
			self.matchPrice(line, product)
			self.matchSize(line, product)
			self.matchDescription(line, product)
			self.matchStory(line, product)

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
	def matchDescription(self, line, product):
		match_description = re.search(self.patterns["description"], line)
		if match_description:
			product.setDescription(match_description.group(1))
	def matchStory(self, line, product):
		match_story_headline = re.search(self.patterns["story_headline_pattern"], line)
		if self.storymatch == 1:
			match_story_1 = re.search(self.patterns["story_body_pattern_1"], line)
			match_story_3 = re.search(self.patterns["story_body_pattern_3"], line)
			if match_story_1:
				
				self.story = re.sub("<br>", "\n", match_story_1.group(1))
				self.story = re.sub(self.strip_html, '', self.story)
				self.story_ongoing = 1
				return 
			if self.story_ongoing == 1: 
				match_story_2 = re.search(self.patterns["story_body_pattern_2"], line)
				if match_story_2: 
					self.story_ongoing = 0
					self.storymatch = 0
					product.addStory(self.story)
				else:
					line = re.sub("\<br\>", "\n", line)
					line = re.sub(self.strip_html, "", line)
					self.story += line
			if match_story_3:
				print match_story_3.group(1)
				self.storymatch = 0
		if match_story_headline: 
			self.storymatch = 1

