
class outlierProduct(object):
	def __init__(self, infile, output):
		self.url = infile
		self.product_id = 0
		self.name = ""
		self.color_size_price = {}
		self.minPrice = 0
		self.maxPrice = 0
		self.output = output

	def setProductId(self, product_id):
		if product_id:
			self.product_id = product_id

	def getProductId(self):
		return self.product_id	

	def getColors(self):
		return self.color_size_price

	def getColor(self, color_id):
		return self.color_size_price[color_id]

	def getMinPrice(self):
		return self.minPrice

	def getMaxPrice(self):
		return self.maxPrice

	def setName(self, name):
		if name:
			self.name = name
	def getName(self):
		return self.name

	def addColor(self, color_key, color_name):
		if color_key not in self.color_size_price.keys():
			self.color_size_price[color_key] = {"sizes":[], "price":"", "color":color_name}
		else: 
			self.setColor(color_key, color_name)

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
	
	def minMaxPrice(self, price):
		if int(price) > self.maxPrice:
			self.maxPrice = price
		if int(price) < self.minPrice or self.minPrice == 0:
			self.minPrice = price
	def save(self):
		self.output.addProduct(self)
		for color_key, color in self.getColors().iteritems():
			self.output.addProductColor(color_key, self.product_id)
			self.output.addColor(color_key, color['color'])
			pricechange = self.output.addProductColorPrice(self.product_id, color_key, int(color['price']))
			if pricechange:
				if int(pricechange) != int(color['price']):
					self.output.telegramPriceNotification(self.product_id, self.name, color['color'], pricechange, color['price'], color['sizes'])
			sizechange = self.output.addProductColorSizes(self, color_key, color['sizes'])


