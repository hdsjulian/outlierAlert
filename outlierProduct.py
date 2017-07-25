
class outlierProduct(object):
	def __init__(self, output, inproduct):
		if inproduct:
			if 'product_id' in inproduct.keys():
				self.product_id = inproduct['product_id']
			if 'url' in inproduct.keys():
				self.url = inproduct['url']
			if 'image_url' in inproduct.keys():
				self.image_url = inproduct['image_url']
		self.name = ""
		self.color_size_price = {}
		self.minPrice = 0
		self.maxPrice = 0
		self.output = output
		self.new = False
		self.story = ""
		self.description = ""

	def setProductId(self, product_id):
		if product_id:
			self.product_id = product_id

	def getProductId(self):
		return self.product_id

	def getColors(self):
		return self.color_size_price

	def getURL(self):
		return self.url
	
	def setURL(self, url):
		if url:
			self.url=url

	def getColor(self, color_id):
		return self.color_size_price[color_id]

	def getMinPrice(self):
		return self.minPrice

	def getMaxPrice(self):
		return self.maxPrice

	def setProductName(self, name):
		if name:
			self.name = name

	def getName(self):
		return self.name

	def addColor(self, color_key, color_name):
		if color_key not in self.color_size_price.keys():
			self.color_size_price[color_key] = {"sizes":[], "price":"", "color":color_name}
		else: 
			self.setColor(color_key, color_name)

	def addStory(self, story):
		self.story = story

	def setColor(self, color_key, color_name):
		self.color_size_price[color_key]["color"] = color_name

	def addSize(self, color_key, size):
		if color_key not in self.color_size_price.keys():
			self.addColor(color_key, "")
		self.color_size_price[color_key]["sizes"].append(size)

	def getSizes(self, color_key):
		return self.color_size_price[color_key]["sizes"]	

	def addPrice(self, color_key, price):
		if color_key not in self.color_size_price.keys():
			self.addColor(color_key, "")
		self.color_size_price[color_key]["price"] = price
		self.minMaxPrice(price)

	def setDescription(self, description):
		self.description = description
	
	def minMaxPrice(self, price):
		if int(price) > self.maxPrice:
			self.maxPrice = price
		if int(price) < self.minPrice or self.minPrice == 0:
			self.minPrice = price
	def save(self):
		print "save called"+str(self.getProductId())
		self.output.addProduct(self)
		for color_key, color in self.getColors().iteritems():
			self.output.addProductColor(color_key, self.product_id)
			self.output.addColor(color_key, color['color'])
			pricechange = self.output.addProductColorPrice(self.product_id, color_key, int(color['price']))
			if pricechange:
				if int(pricechange) != int(color['price']):
					self.output.telegramPriceNotification(self.product_id, self.name, color['color'], pricechange, color['price'], color['sizes'])
			sizechange = self.output.addProductColorSizes(self, color_key, color['sizes'])


