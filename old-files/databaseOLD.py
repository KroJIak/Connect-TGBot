import sqlite3

class dbWorker:
	def __init__(self, databaseFile):
		self.connection = sqlite3.connect(databaseFile)
		self.cursor = self.connection.cursor()
		self.createTable('users', (['userId', 'INT PRIMARY KEY'], ['userFullName', 'TEXT']))
		self.createTable('modes', (['userId', 'INT PRIMARY KEY'], ['mode', 'TEXT']))
		self.createTable('tempPosts', (['userId', 'INT PRIMARY KEY'], ['post', 'TEXT']))
		self.createTable('posts', (['userId', 'INT PRIMARY KEY'], ['messageId', 'TEXT']))
		self.createTable('tempQuestions', (['userId', 'INT PRIMARY KEY'], ['question', 'TEXT']))
		self.createTable('tempAnswers', (['userId', 'INT PRIMARY KEY'], ['answers', 'TEXT']))

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

	def addMode(self, userId, mode):
		'''Добавление режима пользователю'''
		with self.connection:
			return self.cursor.execute('INSERT INTO modes (userId, mode) VALUES(?, ?)', (userId, mode))

	def setMode(self, userId, mode):
		'''выставление режима пользователю'''
		with self.connection:
			return self.cursor.execute('UPDATE modes SET mode = ? WHERE userId = ?', (mode, userId))

	def getMode(self, userId):
		'''получение режима пользователя'''
		with self.connection:
			rawMode = self.cursor.execute('SELECT * FROM modes WHERE userId = ?',(userId, )).fetchone()[1]
			rawMode = rawMode.split('.')
			mode = [rawMode[0], int(rawMode[1])]
			return mode

	def tempPostExists(self, userId):
		'''Проверка есть ли временный пост пользователя в бд'''
		with self.connection:
			result = self.cursor.execute('SELECT * FROM tempPosts WHERE userId = ?', (userId, )).fetchall()
			return bool(len(result))

	def addTempPost(self, userId, post):
		'''Добавление временного поста пользователю'''
		with self.connection:
			return self.cursor.execute('INSERT INTO tempPosts (userId, post) VALUES(?, ?)', (userId, post))

	def setTempPost(self, userId, post):
		'''выставление временного поста пользователю'''
		with self.connection:
			return self.cursor.execute('UPDATE tempPosts SET post = ? WHERE userId = ?', (post, userId))

	def getTempPost(self, userId):
		'''получение временного поста пользователя'''
		with self.connection:
			return self.cursor.execute('SELECT * FROM tempPosts WHERE userId = ?',(userId, )).fetchone()[1]

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

	def getPosts(self, userId):
		'''получение ID постов пользователя'''
		with self.connection:
			return self.cursor.execute('SELECT * FROM posts WHERE userId = ?',(userId, )).fetchone()[1]

	def deleteUserData(self, userId):
		'''Удаление пользователя'''
		with self.connection:
			return self.cursor.execute('DELETE FROM users WHERE userId = ?',(userId, ))

	def tempQuestionExists(self, userId):
		'''Проверка есть ли временный вопрос пользователя в бд'''
		with self.connection:
			result = self.cursor.execute('SELECT * FROM tempQuestions WHERE userId = ?', (userId, )).fetchall()
			return bool(len(result))

	def addTempQuestion(self, userId, question):
		'''Добавление временного вопроса пользователю'''
		with self.connection:
			return self.cursor.execute('INSERT INTO tempQuestions (userId, question) VALUES(?, ?)', (userId, question))

	def setTempQuestion(self, userId, question):
		'''выставление временного вопроса пользователю'''
		with self.connection:
			return self.cursor.execute('UPDATE tempQuestions SET question = ? WHERE userId = ?', (question, userId))

	def getTempQuestion(self, userId):
		'''получение временного вопроса пользователя'''
		with self.connection:
			return self.cursor.execute('SELECT * FROM tempQuestions WHERE userId = ?',(userId, )).fetchone()[1]

	def tempAnswersExists(self, userId):
		'''Проверка есть ли временные ответы пользователя в бд'''
		with self.connection:
			result = self.cursor.execute('SELECT * FROM tempAnswers WHERE userId = ?', (userId, )).fetchall()
			return bool(len(result))

	def addTempAnswers(self, userId, answers):
		'''Добавление временных ответов пользователю'''
		with self.connection:
			return self.cursor.execute('INSERT INTO tempAnswers (userId, answers) VALUES(?, ?)', (userId, answers))

	def setTempAnswers(self, userId, answers):
		'''выставление временных ответов пользователю'''
		with self.connection:
			return self.cursor.execute('UPDATE tempAnswers SET answers = ? WHERE userId = ?', (answers, userId))

	def getTempAnswers(self, userId):
		'''получение временных ответов пользователя'''
		with self.connection:
			return self.cursor.execute('SELECT * FROM tempAnswers WHERE userId = ?',(userId, )).fetchone()[1]




	def create_profile(self,telegram_id,telegram_username,name,description,city,photo,sex,age,social_link):
		'''Создаём анкету'''
		with self.connection:
			return self.cursor.execute("INSERT INTO profile_list (telegram_id,telegram_username,name,description,city,photo,sex,age,social_link) VALUES(?,?,?,?,?,?,?,?,?)", (telegram_id,telegram_username,name,description,city,photo,sex,age,social_link))

	def profile_exists(self,user_id):
		'''Проверка есть ли анкета в бд'''
		with self.connection:
			result = self.cursor.execute('SELECT * FROM profile_list WHERE telegram_id = ?', (user_id,)).fetchall()
			return bool(len(result))

	def delete_profile(self,user_id):
		'''Удаление анкеты'''
		with self.connection:
			return self.cursor.execute("DELETE FROM profile_list WHERE telegram_id = ?",(user_id,))

	def all_profile(self,user_id):
		'''поиск по анкетам'''
		with self.connection:
			return self.cursor.execute("SELECT * FROM profile_list WHERE telegram_id = ?",(user_id,)).fetchall()


	def search_profile(self,city,age,sex):
		'''поиск хаты'''
		try:
			if str(sex) == 'мужчина':
				sex_search = 'женщина'
			else:
				sex_search = 'мужчина'
			with self.connection:
				return self.cursor.execute("SELECT telegram_id FROM profile_list WHERE city = ? AND sex = ? ORDER BY age DESC",(city,sex_search)).fetchall()
		except Exception as e:
			print(e)

	def get_info(self,user_id):
		'''получение ифнормации по профилю'''
		with self.connection:
			return self.cursor.execute("SELECT * FROM profile_list WHERE telegram_id = ?",(user_id,)).fetchone()

	def search_profile_status(self,user_id):
		'''возвращение статуса'''
		with self.connection:
			return self.cursor.execute("SELECT search_id FROM users WHERE telegram_id = ?",(user_id,)).fetchone()

	def edit_profile_status(self,user_id,num):
		'''изменение статуса'''
		with self.connection:
			return self.cursor.execute('UPDATE users SET search_id = ? WHERE telegram_id = ?',(str(num + 1),user_id))

	def edit_zero_profile_status(self,user_id):
		'''изменение статуса на 0 когда анкеты заканчиваются'''
		with self.connection:
			return self.cursor.execute('UPDATE users SET search_id = 0 WHERE telegram_id = ?',(user_id,))

	def set_city_search(self,city,user_id):
		'''задования города для поиска'''
		with self.connection:
			return self.cursor.execute('UPDATE users SET city_search = ? WHERE telegram_id = ?',(city,user_id))

	def get_info_user(self,user_id):
		'''получение информации по юзеру'''
		with self.connection:
			return self.cursor.execute("SELECT * FROM users WHERE telegram_id = ?",(user_id,)).fetchone()

	def check_rating(self,user_id):
		'''чек по рейтингу'''
		with self.connection:
			return self.cursor.execute("SELECT rating FROM profile_list WHERE telegram_id = ?",(user_id,)).fetchone()

	def up_rating(self,count,user_id):
		'''добавление по рейтингу'''
		with self.connection:
			return self.cursor.execute('UPDATE profile_list SET rating = ? WHERE telegram_id = ?',(count + 1,user_id))

	def top_rating(self):
		'''вывод топа по рейтингу'''
		with self.connection:
			return self.cursor.execute('SELECT telegram_id FROM profile_list ORDER BY rating DESC LIMIT 5').fetchall()

	def count_user(self):
		'''вывод кол-ва юзеров'''
		with self.connection:
			return self.cursor.execute('SELECT COUNT(*) FROM users').fetchone()

	def report_exists(self,user_id,recipent):
		'''Проверка есть ли репорт в бд'''
		with self.connection:
			result = self.cursor.execute('SELECT * FROM reports WHERE send = ? AND recipient = ?', (user_id,recipent)).fetchall()
			return bool(len(result))

	def throw_report(self,user_id,recipent):
		'''отправка репорта'''
		with self.connection:
			return self.cursor.execute("INSERT INTO reports (send, recipient) VALUES(?,?)", (user_id,recipent))

	def backup(self,name,age,city,description):
		'''откат действий'''
		with self.connection:
			return self.cursor.execute('SELECT telegram_id FROM profile_list WHERE name = ? AND age = ? AND city = ? AND description = ?', (name,age,city,description)).fetchall()

	def city_search_exists(self,user_id):
		'''есть ли city search у юзера'''
		with self.connection:
			result = self.cursor.execute('SELECT city_search FROM users WHERE telegram_id = ?', (user_id,)).fetchone()
			return result

	def add_like(self,sender,recipent):
		'''добавление лайка в таблицу'''
		with self.connection:
			return self.cursor.execute('INSERT INTO likes (sender,recipient) VALUES(?,?)', (sender,recipent))

	def add_like_exists(self,sender,recipient):
		with self.connection:
			result = self.cursor.execute('SELECT * FROM likes WHERE sender = ? AND recipient = ?', (sender,recipient)).fetchall()
			return bool(len(result))
