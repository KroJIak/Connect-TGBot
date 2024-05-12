import sqlite3

class dbWorker:
	def __init__(self, databaseFile):
		self.connection = sqlite3.connect(databaseFile)
		self.cursor = self.connection.cursor()
		self.createTable('users', (['userId', 'INT PRIMARY KEY'], ['userFullName', 'TEXT']))
		self.createTable('posts', (['userId', 'INT PRIMARY KEY'], ['messageId', 'TEXT']))
		self.createTable('feedbacks', (['userId', 'INT PRIMARY KEY'], ['feedback', 'TEXT']))

	def createTable(self, name, elements):
		with self.connection:
			command = f'CREATE TABLE IF NOT EXISTS {name}('
			for i, elm in enumerate(elements):
				ending = ','
				if i == len(elements)-1: ending = ');'
				command += f'{elm[0]} {elm[1]}{ending}'
			return self.cursor.execute(command)

	def userExists(self, userId):
		'''Проверка есть ли пользователь в бд'''
		with self.connection:
			result = self.cursor.execute('SELECT * FROM users WHERE userId = ?', (userId, )).fetchall()
			return bool(len(result))

	def addUser(self, userId, userFullName):
		'''Добавление нового пользователя'''
		with self.connection:
			return self.cursor.execute('INSERT INTO users (userId, userFullName) VALUES(?, ?)', (userId, userFullName))

	def postExists(self, userId):
		'''Проверка есть ли ID постов пользователя в бд'''
		with self.connection:
			result = self.cursor.execute('SELECT * FROM posts WHERE userId = ?', (userId, )).fetchall()
			return bool(len(result))

	def addPost(self, userId, messageId):
		'''Добавление ID первого поста пользователю'''
		with self.connection:
			return self.cursor.execute('INSERT INTO posts (userId, messageId) VALUES(?, ?)', (userId, messageId))

	def add2Posts(self, userId, messageId):
		'''Добавление к предыдущим ID постов новый ID поста пользователя'''
		with self.connection:
			postsId = self.getPosts(userId)
			postsId += ' ' + str(messageId)
			return self.cursor.execute('UPDATE posts SET messageId = ? WHERE userId = ?', (postsId, userId))

	def setPosts(self, userId, messageId):
		'''Выставить ID постов пользователя'''
		with self.connection:
			return self.cursor.execute('UPDATE posts SET messageId = ? WHERE userId = ?', (str(messageId), userId))

	def getPosts(self, userId):
		'''получение ID постов пользователя'''
		with self.connection:
			return self.cursor.execute('SELECT * FROM posts WHERE userId = ?',(userId, )).fetchone()[1]

	def feedbackExists(self, userId):
		'''Проверка есть ли отзыв пользователя в бд'''
		with self.connection:
			result = self.cursor.execute('SELECT * FROM feedbacks WHERE userId = ?', (userId, )).fetchall()
			return bool(len(result))

	def addFeedback(self, userId, feedback):
		'''Добавление отзыва пользователя'''
		with self.connection:
			return self.cursor.execute('INSERT INTO feedbacks (userId, feedback) VALUES(?, ?)', (userId, feedback))