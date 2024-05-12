from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from configparser import ConfigParser
from database import dbWorker
from time import sleep, time
import requests
import logging
import asyncio
import openai
import json
import os
import re

#SETTINGS
logging.basicConfig(level=logging.INFO)
config = ConfigParser()
config.read("config.ini")
token = config['Telegram']['token']
channelChatId = config['Telegram']['channelChatId']
openai.api_key = config['ChatGPT']['token']
model = config['ChatGPT']['model']
namedbFile = config['Data']['namedbFile']
nameJsonFile = config['Data']['nameJsonFile']
db = dbWorker(namedbFile)
jsonFile = open(nameJsonFile, encoding='utf-8')
langJson = json.load(jsonFile)
bot = Bot(token)
dp = Dispatcher(bot=bot)

def getTranslation(name, inserts=[]):
    text = langJson[name]
    if len(inserts) > 0:
        splitText = text.split('%{}%')
        resultText = splitText[0]
        for i, ins in enumerate(inserts, start=1):
            resultText += ins
            if i < len(splitText): resultText += splitText[i]
        return resultText
    else: return text

def getMainKeyboard():
    mainKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mainButtons = [getTranslation('button.post'), getTranslation('button.poll'),
                   getTranslation('button.delete'), getTranslation('button.feedback')]
    mainKeyboard.add(*mainButtons)
    return mainKeyboard

def getDeleteKeyboard():
    deleteKeyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text=getTranslation('button.delete.true'), callback_data="delete.true"),
        types.InlineKeyboardButton(text=getTranslation('button.delete.false'), callback_data="delete.false"),
    ]
    deleteKeyboard.add(*buttons)
    return deleteKeyboard

#CHATGPT
def requestGPT(pmt):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            { 'role': 'user', 'content': pmt }
        ])
    return completion.choices[0].message.content

def checkAnswers(text):
    rawAnswers = re.sub(r'[^\d\w;]', ' ', text)
    try: answers = list(map(lambda text: text.lower(), rawAnswers.split(';')))
    except: return False, None
    if len(answers) < 2 or len(answers) > 10: return False, None
    for ans in answers:
        if len(ans) > 100: return False, None
    rawAnswerGPT = requestGPT(getTranslation('poll.promptGPT.step.2', ', '.join(answers)))
    answerGPT = rawAnswerGPT.strip().lower()
    if 'false' in answerGPT: return False, None
    return True, answers

def checkHashtags(text):
    rawHashtags = re.sub(r'[^\d\w]', ' ', text)
    try: hashtags = list(map(lambda text: f'#{text}'.lower(), rawHashtags.split()))
    except: return False, None
    if len(hashtags) < 3: return False, None
    for tag in hashtags:
        if len(tag) > 20: return False, None
    rawAnswerGPT = requestGPT(getTranslation('post.promptGPT.step.2', ' '.join(hashtags)))
    answerGPT = rawAnswerGPT.strip().lower()
    if 'false' in answerGPT: return False, None
    return True, hashtags

def getUserInfo(message): return [message.from_user.id,
                                  message.from_user.first_name,
                                  message.from_user.full_name,
                                  message.message_id,
                                  message.text]

#COMMANDS
@dp.message_handler(commands=['start', 'about'])
async def startHandler(message: types.Message):
    userId, userName, userFullName, messageId, userText = getUserInfo(message)
    if not db.userExists(userId):
        db.addUser(userId, userFullName)
        db.addMode(userId, 'start.0')
    mainKeyboard = getMainKeyboard()
    await message.answer(getTranslation('start.message', [userName]), reply_markup=mainKeyboard)

@dp.message_handler(lambda message: message.text in ['/post', getTranslation('button.post')])
async def postHandler(message: types.Message):
    userId, userName, userFullName, messageId, userText = getUserInfo(message)
    await bot.delete_message(userId, messageId)

    db.setMode(userId, 'post.0')
    await message.answer(getTranslation('post.message'))

@dp.message_handler(lambda message: message.text in ['/poll', getTranslation('button.poll')])
async def pollHandler(message: types.Message):
    userId, userName, userFullName, messageId, userText = getUserInfo(message)
    await bot.delete_message(userId, messageId)

    db.setMode(userId, 'poll.0')
    await message.answer(getTranslation('poll.message'))

@dp.message_handler(lambda message: message.text in ['/delete', getTranslation('button.delete')])
async def deleteHandler(message: types.Message):
    userId, userName, userFullName, messageId, userText = getUserInfo(message)
    await bot.delete_message(userId, messageId)

    deleteKeyboard = getDeleteKeyboard()
    db.setMode(userId, 'delete.0')
    await message.answer(getTranslation('delete.message'), reply_markup=deleteKeyboard)
    
@dp.message_handler(lambda message: message.text in ['/feedback', getTranslation('button.feedback')])
async def feedbackHandler(message: types.Message):
    userId, userName, userFullName, messageId, userText = getUserInfo(message)
    await bot.delete_message(userId, messageId)

    db.setMode(userId, 'feedback.0')
    await message.answer(getTranslation('feedback.message'))

@dp.message_handler()
async def mainHandler(message: types.Message):
    userId, userName, userFullName, messageId, userText = getUserInfo(message)
    mode = db.getMode(userId)

    if mode[0] == 'post':
        if mode[1] == 0:
            rawAnswerGPT = requestGPT(getTranslation('post.promptGPT.step.1', userText))
            answerGPT = rawAnswerGPT.strip().lower()
            if 'true' in answerGPT:
                db.setMode(userId, 'post.1')
                if not db.tempPostExists(userId): db.addTempPost(userId, userText)
                else: db.setTempPost(userId, userText)
                await message.answer(getTranslation('post.true.step.1'))
            else:
                await message.answer(getTranslation('post.false.step.1'))
        elif mode[1] == 1:
            flagHashtags, hashtags = checkHashtags(userText)
            if flagHashtags:
                if len(hashtags) > 6: hashtags = hashtags[:6]
                resultText = ' '.join(hashtags) + '\n\n'
                resultText += db.getTempPost(userId)
                db.setMode(userId, 'start.0')
                mainKeyboard = getMainKeyboard()
                await message.answer(getTranslation('post.true.step.2', channelChatId), reply_markup=mainKeyboard)
                channelMessage = await bot.send_message(channelChatId, resultText)
                if not db.postExists(userId): db.addPost(userId, channelMessage.message_id)
                else: db.add2Posts(userId, channelMessage.message_id)
            else:
                await message.answer(getTranslation('post.false.step.2'))
    elif mode[0] == 'poll':
        if mode[1] == 0:
            rawAnswerGPT = requestGPT(getTranslation('poll.promptGPT.step.1', userText))
            answerGPT = rawAnswerGPT.strip().lower()
            if 'true' in answerGPT:
                db.setMode(userId, 'poll.1')
                if not db.tempQuestionExists(userId): db.addTempQuestion(userId, userText)
                else: db.setTempQuestion(userId, userText)
                await message.answer(getTranslation('poll.true.step.1'))
            else:
                await message.answer(getTranslation('poll.false.step.1'))
        elif mode[1] == 1:
            flagAnswers, answers = checkAnswers(userText)
            if flagAnswers:
                resultAnswers = ' %|% '.join(answers)
                db.setMode(userId, 'poll.2')
                if not db.tempAnswersExists(userId): db.addTempAnswers(userId, resultAnswers)
                else: db.setTempAnswers(userId, resultAnswers)
                await message.answer(getTranslation('poll.true.step.2'))
            else:
                await message.answer(getTranslation('poll.false.step.2'))
        elif mode[1] == 2:
            flagHashtags, hashtags = checkHashtags(userText)
            if flagHashtags:
                if len(hashtags) > 6: hashtags = hashtags[:6]
                resultQuestion = ' '.join(hashtags) + '\n\n'
                resultQuestion += db.getTempQuestion(userId)
                rawAnswers = db.getTempAnswers(userId)
                resultAnswers = rawAnswers.split(' %|% ')
                db.setMode(userId, 'start.0')
                mainKeyboard = getMainKeyboard()
                await message.answer(getTranslation('poll.true.step.3', channelChatId), reply_markup=mainKeyboard)
                channelMessage = await bot.send_poll(channelChatId,
                                                    question=resultQuestion,
                                                    options=resultAnswers,
                                                    is_anonymous=True,
                                                    allows_multiple_answers=True)
                if not db.postExists(userId): db.addPost(userId, channelMessage.message_id)
                else: db.add2Posts(userId, channelMessage.message_id)
            else:
                await message.answer(getTranslation('poll.false.step.3'))

def main():
    executor.start_polling(dp)

if __name__ == '__main__':
    main()