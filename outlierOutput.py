import sqlite3
import time
import cPickle
import telepot
from pprint import pprint
class outlierOutput(object):
	def __init__(self):
		self.sqlite_file = "/Users/Julian/Work/outlier.sqlite"
		self.conn = sqlite3.connect(self.sqlite_file)
		self.cursor = (self.conn.cursor())
		self.telegram_offset = self.getTelegramOffset()
		self.telegram_users = self.fetchTelegramUsers()
		self.telegram_user = "111127184"
		print "Telegram Users"
		print self.telegram_users
		self.bot = telepot.Bot('438558984:AAHbJtczAw5W7qx7cS67969RE0VSRhqm5Sc')
		self.readTelegramMessages()
	def __del__(self):
		self.conn.close()

	def readTelegramMessages(self):
		response = self.bot.getUpdates(offset=self.telegram_offset)
		offset = self.telegram_offset
		for message in response:
			offset = int(message['update_id'])
			user_id = int(message['message']['chat']['id'])
			user_name = message['message']['chat']['username']

			if message['message']['text'] == "/subscribe":
				if user_id not in self.telegram_users:
					self.addTelegramUser(user_id, user_name)

			elif message['message']['text'] == "/unsubscribe":
				if user_id in self.telegram_users:
					self.delTelegramUser(user_id)
		if offset > self.telegram_offset: 
			self.saveTelegramOffset(offset+1)

	def getTelegramOffset(self):
		query = "SELECT offset FROM telegram_offset"
		self.cursor.execute(query)
		return self.cursor.fetchone()[0]

	def saveTelegramOffset(self, offset):
		query = "UPDATE telegram_offset SET offset = {new_offset} WHERE offset = {offset}".format(new_offset = offset, offset=self.telegram_offset)
		self.cursor.execute(query)
		self.conn.commit()
		self.telegram_offset = offset

	def delTelegramUser(self, user_id):
		query = "DELETE FROM telegram_users WHERE user_id = {uid}".format(uid=user_id)
		self.cursor.execute(query)
		self.conn.commit()
		self.telegram_users.remove(user_id)
		self.bot.sendMessage(user_id, "Unsubscribed!")


	def addTelegramUser(self, user_id, user_name):
		query = "INSERT INTO telegram_users (user_name, user_id) VALUES ('{un}', {uid})".format(un=user_name, uid=user_id)
		self.cursor.execute(query)
		self.conn.commit()
		self.telegram_users.append(user_id)
		self.bot.sendMessage(user_id, "Subscribed! To Unsubscribe send a message with /unsubscribe")

	def fetchTelegramUsers(self):
		query = "SELECT user_id FROM telegram_users"
		self.cursor.execute(query)
		telegram_users = []
		for line in self.cursor.fetchall():
			telegram_users.append(line[0])	
		return telegram_users

	def checkForProduct(self, product_id):
		query = 'SELECT product_id FROM product WHERE product_id = {id}'.format(id=product_id)
		self.cursor.execute(query)
		if self.cursor.fetchone(): 
			return True
		else: 
			return False

	def addProduct(self, product):
		query = 'INSERT INTO product (product_id, product_name, introduction, URL) VALUES({id}, "{name}", {ts}, "{url})"'.format(id=product.product_id, name = product.name, ts = time.time(), url=product.url)
		try:
			self.cursor.execute(query)
			self.conn.commit()
			self.telegram.telegramProductNotification(product_id, product_name)
		except Exception as e: 
			print query
			print e
	def checkProductColorSizes(self, product_color_id, sizes):
		query = 'SELECT sizes FROM product_color_size WHERE product_color_id = {pcid} ORDER BY timestamp DESC'.format(pcid=product_color_id)
		self.cursor.execute(query)
		result = self.cursor.fetchone()
		if result and cPickle.loads(str(result[0])) == sizes:
			return True
		else: 
			return False

	def addProductColorSizes(self, product_id, color_id, sizes):
		product_color_id = self.getProductColorId(product_id, color_id)
		if not product_color_id: 
			return False
		if not self.checkProductColorSizes(product_color_id, sizes):
			query = 'INSERT INTO product_color_size (product_color_id, sizes, timestamp) VALUES ({pcid}, "{sizes}", {ts})'.format(pcid=product_color_id, sizes=cPickle.dumps(sizes), ts=time.time())
			try: 
				self.cursor.execute(query)
				return True
			except Exception as e:
				print query
				print e
				return False
	"""
	def findProductColor(self, color_id, product_id):
		query = 'SELECT color_id, product_id FROM product_color WHERE color_id = {color_id} AND product_id = {product_id}'.format(color_id=color_id, product_id=product_id)
		self.cursor.execute(query)

		if self.cursor.fetchone():
			return True
		else:
			return False
	"""
	def addProductColor(self, color_id, product_id):
		if not self.getProductColorId(product_id, color_id):
			query = 'INSERT INTO product_color (color_id, product_id, introduction) VALUES({color_id}, {product_id}, {introduction})'.format(color_id=color_id, product_id=product_id, introduction=time.time())
			try: 
				self.cursor.execute(query)
				self.conn.commit()
			except Exception as e: 
				print query
				print e

	def addColor(self, color_id, color_name):
		query = 'INSERT INTO color (color_id, color_name) VALUES ({id}, "{name}")'.format(id=color_id, name=color_name)
		try: 
			self.cursor.execute(query)
			self.conn.commit()
		except Exception as e: 
			print e

	def getProductColorId(self, product_id, color_id):
		query = "SELECT product_color_id FROM product_color WHERE product_id = {pid} AND color_id = {cid}".format(pid=product_id, cid=color_id)
		self.cursor.execute(query)
		result = self.cursor.fetchone()
		if result: 
			return result[0]
		else: 
			return False
	def addProductColorPrice(self, product_id, color_id, price):
		product_color_id = self.getProductColorId(product_id, color_id)
		if product_color_id:
			query = 'SELECT price FROM product_color_price WHERE product_color_id = {pcid} ORDER BY timestamp DESC '.format(pcid=product_color_id)
			self.cursor.execute(query)
			oldprice = self.cursor.fetchone()
			if not oldprice or oldprice[0] != price:
				query = 'INSERT INTO product_color_price (product_color_id, price, timestamp) VALUES({pcid}, {price}, {ts})'.format(pcid=product_color_id, price=price, ts=time.time())
				try: 
					self.cursor.execute(query)
				except Exception as e: 
					print e
			self.conn.commit()
			if oldprice:
				return oldprice[0]
			else: 
				return price
		else:
			return False

	def telegramPriceNotification(self, product_id, product_name, color_name, oldprice, newprice, sizes):
		if oldprice > newprice: 
			price_message = "Price Drop!"
		else: 
			price_message = "Price Change!"
		self.bot.sendMessage(self.telegram_user, price_message+'\nObject: '+product_name+"\nProductID"+str(product_id)+"\nColor: "+color_name+"\nSizes: "+", ".join(sizes)+"\nPrice: "+str(newprice)+"instead of "+str(oldprice))
	
	def telegramProductNotification(self, product_id, product_name):
		for user in self.telegram_users:
			self.bot.sendMessage(user, "New Product!\nProduct ID:"+str(product_id)+"\nProduct Name: "+product_name)


