import sqlite3
import time
import cPickle
import telepot
from pprint import pprint
import config as config
import re
import logging
#todo: make addproduct more elegant
#todo product color sizes is broken
#todo: create populateProduct method
#was passiert: ich guck nur ob was dazu kam. speicher aber nicht wenns weggging


class outlierOutput(object):
	def __init__(self):
		self.logger = logging.getLogger('outlier')
		self.sqlite_file = "outlier.sqlite"
		self.conn = sqlite3.connect(self.sqlite_file)
		self.cursor = (self.conn.cursor())
		self.telegram_offset = self.getTelegramOffset()
		self.telegram_users = self.fetchTelegramUsers()
		self.logger.debug("Telegram users: "+", ".join([str(x) for x in self.telegram_users]))
		self.telegramSubscriptions = self.fetchTelegramSubscriptions()
		self.bot = telepot.Bot(config.telegram_code)
		#self.readTelegramMessages()
	
	def __del__(self):
		self.conn.close()

	def checkForProduct(self, product_id):
		query = 'SELECT product_id FROM product WHERE product_id = {id}'.format(id=product_id)
		self.cursor.execute(query)
		if self.cursor.fetchone(): 
			return True
		else: 
			return False

	def getProducts(self):
		returnproducts = []
		query = 'SELECT product_id, url FROM product'
		self.cursor.execute(query)
		for line in self.cursor.fetchall():
			returnproducts.append({'product_id':line[0], 'url':line[1]})
		return returnproducts



	def addProduct(self, product):
		query = 'INSERT INTO product (product_id, product_name, introduction, URL, story, description) VALUES(?, ?, ?, ?, ?, ?)'
		try: 
			self.cursor.execute(query, (product.product_id, product.name, time.time(), product.url, product.story, product.description))
			self.conn.commit()
			product.new = True
			self.telegramProductNotification(product)
		except:
			pass
	
	def checkProductColorSizes(self, product_color_id, sizes):
		query = 'SELECT sizes FROM product_color_size WHERE product_color_id = {pcid} ORDER BY timestamp DESC'.format(pcid=product_color_id)
		self.cursor.execute(query)
		result = self.cursor.fetchone()
		if result: 
			if cPickle.loads(str(result[0])) == sizes:
				self.logger.debug(str(product_color_id)+" sizes the same"+', '.join(cPickle.loads(str(result[0])))+" vs "+', '.join(sizes))
				return False
			else: 
				self.logger.debug(str(product_color_id)+" size different"+', '.join(cPickle.loads(str(result[0])))+" vs "+', '.join(sizes))
				return [[item for item in sizes if item not in cPickle.loads(str(result[0]))], [item for item in cPickle.loads(str(result[0])) if item not in sizes]]
		else: 
			return [sizes, []]

	def addProductColorSizes(self, product, color_id, sizes):
		product_color_id = self.getProductColorId(product.product_id, color_id)
		if not product_color_id: 
			return False
		sizeDifference = self.checkProductColorSizes(product_color_id, sizes)
		if sizeDifference:
			if sizeDifference[0] != sizeDifference[1]:
				query = 'INSERT INTO product_color_size (product_color_id, sizes, timestamp) VALUES ({pcid}, "{sizes}", {ts})'.format(pcid=product_color_id, sizes=cPickle.dumps(sizes), ts=time.time())
				try: 
					self.cursor.execute(query)
				except Exception as e:
					self.logger.debug(str(e))
					return False
				self.conn.commit()
			if len(sizeDifference[0])>0:
				self.logger.debug(("should send size notification "+", ".join(sizeDifference[0]))+" instead of "+", ".join(sizeDifference[1]))
				self.telegramSizeNotification(product, color_id, sizeDifference[0])
			if len(sizeDifference[1])>0:
				self.logger.debug("Less stock than new for "+product.name)
			return True
			
	def addProductColor(self, color_id, product_id):
		if not self.getProductColorId(product_id, color_id):
			query = 'INSERT INTO product_color (color_id, product_id, introduction) VALUES({color_id}, {product_id}, {introduction})'.format(color_id=color_id, product_id=product_id, introduction=time.time())
			try: 
				self.cursor.execute(query)
				self.conn.commit()
			except Exception as e: 
				pass
	def addColor(self, color_id, color_name):
		query = 'INSERT INTO color (color_id, color_name) VALUES ({id}, "{name}")'.format(id=color_id, name=color_name)
		try: 
			self.cursor.execute(query)
			self.conn.commit()
		except Exception as e: 
			self.logger.debug(str(e))
			pass

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
					self.logger.debug(str(e))
					pass
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
		for telegram_user in self.telegram_users:
			self.logger.debug("Sending Price notification to "+str(telegram_user))
			self.bot.sendMessage(telegram_user, price_message+'\nObject: '+product_name+"\nProductID"+str(product_id)+"\nColor: "+color_name+"\nSizes: "+", ".join(sizes)+"\nPrice: "+str(newprice)+" instead of "+str(oldprice))
	
	def telegramProductNotification(self, product):
		color_size_price_string = ""
		for v in product.color_size_price.itervalues():
			color_size_price_string = color_size_price_string+"\nColor: "+v['color']+"\nPrice: "+v['price']+"\nSizes: "+', '.join(v["sizes"])
		for telegram_user in self.telegram_users:
			self.logger.debug("Sending product notification to "+str(telegram_user))
			self.bot.sendMessage(telegram_user, "New Product!\nProduct ID:"+str(product.product_id)+"\nProduct Name: "+product.name+"\nProduct URL: "+product.url+"\nDescription:\n"+product.description+"\n"+color_size_price_string)

	def telegramSizeNotification(self, product, color_id, sizeDifference):		
		if product.new is False:
			for telegram_user in self.telegram_users:
				formURL = self.updateFormURLs(product, color_id, sizeDifference, telegram_user)
				if list(set(self.telegramSubscriptions[telegram_user]) & set(sizeDifference)) or 'all' in self.telegramSubscriptions[telegram_user]:
					self.logger.debug("Sent Restock to "+str(telegram_user)+" for "+product.name+" in Color: "+product.color_size_price[color_id]["color"]+" Sizes: "+", ".join(sizeDifference))
					self.bot.sendMessage(telegram_user, "Restock!\n"+product.name+" in Color: "+product.color_size_price[color_id]["color"]+"\nSizes: "+", ".join(sizeDifference)+"\n Order URLS: \n"+formURL)
				else: 
					self.logger.debug("User "+str(telegram_user)+" does not want size notification for sizes"+', '.join(sizeDifference)+" Subscriptions:"+', '.join(self.telegramSubscriptions[telegram_user]))

	def updateFormURLs(self, product, color_id, sizeDifference, telegram_user):
		returnURL = ""
		if 'all' in self.telegramSubscriptions[telegram_user]:
			sizeIntersection = sizeDifference
		else: 
			sizeIntersection = list(set(self.telegramSubscriptions[telegram_user]) & set(sizeDifference))
		formURL = product.formURL
		returnURL = "" 
		for size in sizeIntersection:
			if size == "28": 
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B158%5D=235&super_attribute%5B157%5D="+str(color_id)+" \n"
			elif size == "29": 
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B158%5D=236&super_attribute%5B157%5D="+str(color_id)+" \n"
			elif size == "30": 
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B158%5D=237&super_attribute%5B157%5D="+str(color_id)+" \n"
			elif size == "31": 
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B158%5D=238&super_attribute%5B157%5D="+str(color_id)+" \n"
			elif size == "32": 
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B158%5D=230&super_attribute%5B157%5D="+str(color_id)+" \n"
			elif size == "33": 
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B158%5D=240&super_attribute%5B157%5D="+str(color_id)+" \n"
			elif size == "34": 
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B158%5D=241&super_attribute%5B157%5D="+str(color_id)+" \n"
			elif size == "35": 
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B158%5D=242&super_attribute%5B157%5D="+str(color_id)+" \n"
			elif size == "36": 
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B158%5D=243&super_attribute%5B157%5D="+str(color_id)+" \n"
			elif size == "37": 
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B158%5D=244&super_attribute%5B157%5D="+str(color_id)+" \n"
			elif size == "38": 
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B158%5D=245&super_attribute%5B157%5D="+str(color_id)+" \n"
			elif size == "XS":
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B146%5D=389&super_attribute%5B147%5D="+str(color_id)+" \n"
			elif size == "S":
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B146%5D=390&super_attribute%5B147%5D="+str(color_id)+" \n"
			elif size == "M":
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B146%5D=392&super_attribute%5B147%5D="+str(color_id)+" \n"
			elif size == "L":
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B146%5D=394&super_attribute%5B147%5D="+str(color_id)+" \n"
			elif size == "XL":
				returnURL = returnURL+"URL for size "+size+" "+formURL+"super_attribute%5B146%5D=396&super_attribute%5B147%5D="+str(color_id)+" \n"
		print returnURL
		return returnURL
								
								
	def readTelegramMessages(self):
		try: 
			response = self.bot.getUpdates(offset=self.telegram_offset+1)
			offset = self.telegram_offset
			for message in response:
				if 'message' not in message.iterkeys():
					continue
				offset = int(message['update_id'])
				user_id = int(message['message']['chat']['id'])
				if 'username' in message['message']['chat'].keys():
					user_name = message['message']['chat']['username']
				elif 'last_name' in message['message']['chat'] and 'first_name' in message['message']['chat']:
					user_name = message['message']['chat']['first_name']+' '+message['message']['chat']['last_name']
				elif 'last_name' in message['message']['chat']:
					user_name = mmessage['message']['chat']['last_name']
				elif 'first_name' in message['message']['chat']:
					user_name = message['message']['chat']['first_name']
				else:
					user_name = 'Unknown'


				if message['message']['text'] == "/subscribe":
					if user_id not in self.telegram_users:
						self.addTelegramUser(user_id, user_name)
				elif message['message']['text'] == "/unsubscribe":
					if user_id in self.telegram_users:
						self.delTelegramUser(user_id)
				elif user_id in self.telegram_users: 
					self.parseTelegramMessage(message)
				self.saveTelegramOffset(offset)
		except: 
			pass
	
	def parseTelegramMessage(self, message):
		patterns = {}
		user_id = int(message['message']['chat']['id'])
		patterns['sizesubscription'] = "\/size ([a-zA-Z0-9]+)"
		patterns['sizeunsubscription'] = "\/unsize ([a-zA-Z0-9]+)"
		patterns['help'] = "\/help"
		patterns['sizes'] = "\/sizes"
		patterns['unsubscribe'] = "/unsubscribe"
		patterns['subscribe'] = "/subscribe"
		for patternName, pattern in patterns.iteritems():

			match = re.search(pattern,message['message']['text'])
			if match: 
				if patternName == 'sizesubscription':
					self.telegramAddSizeSubscription(user_id, match.group(1))
				elif patternName == 'sizeunsubscription':
					self.telegramDeleteSizeSubscription(user_id, match.group(1))
				elif patternName == 'help':
					self.telegramSendHelpMessage(user_id)
				elif patternName == 'sizes':
					self.telegramSendSubscriptionData(user_id)


	def telegramSendHelpMessage(self, user_id):
		helpMessage = """Use following commands:
/help - Receive this list

/size [size] - Subscribe to restock notifications for a size

/unsize [size] - Unsubscribe to restock notifications for a size

/unsubscribe - End subscription

/size all - subscribe to all restock notifications

/unsize all - unsubscribe from all restock notifications

/size (or unsize) one - subscribe/unsubscribe all restock notifications for one-size items

/sizes - list all your size subscriptions
		"""
		self.logger.debug("Help called by "+str(user_id))
		self.bot.sendMessage(user_id, helpMessage)

	def telegramAddSizeSubscription(self, user_id, size):
		if size == 'all':
			query = 'UPDATE telegram_users SET allsizes = 1 WHERE user_id = {user_id}'.format(user_id=user_id)
			self.cursor.execute(query)
			self.conn.commit()
			self.logger.debug("Subscribe all by "+str(user_id))
			self.bot.sendMessage(user_id, "You subscribed to all sizes. To unsubscribe send /unsize all")
			self.telegramSubscriptions[user_id] = ['all']
		else: 
			query = "SELECT * FROM telegram_user_sizes WHERE user_id = {user_id} AND size = '{size}'".format(user_id=user_id, size=size.upper())
			self.cursor.execute(query)
			if not self.cursor.fetchone():
				query = 'INSERT INTO telegram_user_sizes (user_id, size) VALUES ({user_id}, "{size}")'.format(user_id=user_id, size=size.upper())
				self.cursor.execute(query)
				self.conn.commit()
				self.logger.debug("Size subscribed Size: "+size+" User: "+str(user_id))
				self.bot.sendMessage(user_id, "Size "+size+" subscribed. To unsubscribe send /unsize [size]")
				self.telegramSubscriptions[user_id].append(size)
			else: 
				self.bot.sendMessage(user_id, "You already subscribed to size "+size)


	def telegramDeleteSizeSubscription(self, user_id, size):
		if size == 'all':
			self.logger.debug("unsize all called")
			query = 'UPDATE telegram_users SET allsizes = 0 WHERE user_id = {user_id}'.format(user_id=user_id)
			self.cursor.execute(query)
			self.conn.commit()
			self.logger.debug ("User "+str(user_id)+" unsubscribed all" )
			self.bot.sendMessage(user_id, "You unsubscribed from receiving messages for all sizes. To subscribe to individual sizes send /size [size]")
		else: 
			query = "DELETE FROM telegram_user_sizes WHERE user_id ={user_id} AND size = {size}".format(user_id=user_id, size=size.upper())
			self.cursor.execute(query)
			self.conn.commit()
			self.logger.debug("User "+str(user_id)+" unsubscribed "+size)
			self.bot.sendMessage(user_id, "You will no longer receive restock notifications for size "+size)
		if size in self.telegramSubscriptions[user_id]:
			self.telegramSubscriptions[user_id].remove(size)

	def telegramSendSubscriptionData(self, user_id):
		self.logger.debug("Sending subscription data to "+str(user_id))
		if 'all' in self.telegramSubscriptions[user_id]:
			self.bot.sendMessage(user_id, "You are currently subscribed to messages for all sizes. to unsubscribe send /unsize all")
		else: 
			query = 'SELECT size FROM telegram_user_sizes WHERE user_id = {user_id}'.format(user_id=user_id)
			self.cursor.execute(query)
			size_message = ""
			for line in self.cursor.fetchall():
				size_message = size_message+"\nSize: "+line[0]
			self.bot.sendMessage(user_id, "You are currently subscribed to restock notifications for the following sizes:"+size_message)

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
		query = 'DELETE FROM telegram_user_sizes WHERE user_id = {uid}'.format(uid=user_id)
		self.cursor.execute(query)
		self.conn.commit()
		self.telegram_users.remove(user_id)
		self.bot.sendMessage(user_id, "Unsubscribed!")


	def addTelegramUser(self, user_id, user_name):
		query = "INSERT INTO telegram_users (user_name, user_id, allsizes) VALUES ('{un}', {uid}, 0)".format(un=user_name, uid=user_id)
		self.cursor.execute(query)
		self.conn.commit()
		self.telegram_users.append(user_id)
		self.logger.debug("Subscribing Telegram user "+str(user_id))
		self.bot.sendMessage(user_id, "Subscribed! To Unsubscribe send a message with /unsubscribe. For Help send a message with /help")

	def fetchTelegramSubscriptions(self):
		telegramSubscriptions = {}
		query = 'SELECT user_id, allsizes FROM telegram_users'
		self.cursor.execute(query)
		for line in self.cursor.fetchall():
			telegramSubscriptions[line[0]] = []
			if line[1] != 1:
				query = 'SELECT size FROM telegram_user_sizes WHERE user_id = {uid}'.format(uid=line[0])
				self.cursor.execute(query)
				for size in self.cursor.fetchall():
					telegramSubscriptions[line[0]].append(size[0])
			elif line[1] == 1:
				telegramSubscriptions[line[0]].append('all')
		return telegramSubscriptions

	def fetchTelegramUsers(self):
		query = "SELECT user_id FROM telegram_users"
		self.cursor.execute(query)
		telegram_users = []
		for line in self.cursor.fetchall():
			telegram_users.append(line[0])	
		telegram_users = [111127184]
		return telegram_users