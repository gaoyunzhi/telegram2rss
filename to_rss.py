#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import traceback as tb
import json
import tweepy
import yaml
import time
import os
import urllib.request
import threading
from telegram_util import matchKey, parseUrl, isMeaningful, getTmpFile, log_on_fail

with open('CREDENTIALS') as f:
	CREDENTIALS = json.load(f)

tele = Updater(CREDENTIALS['bot_token'], use_context=True)
r = tele.bot.send_message(-1001198682178, 'start')
debug_group = r.chat

with open('KEYS') as f:
	KEYS = set(yaml.load(f, Loader=yaml.FullLoader))

with open('SUBSCRIPTION') as f:
	SUBSCRIPTION = yaml.load(f, Loader=yaml.FullLoader).keys()

LOOP_INTERVAL = 1 # 7200

test_channel = -1001159399317
queue = []

EXPECTED_ERRORS = ['Message to forward not found', "Message can't be forwarded"]

def tweetMsg(msg):
	if msg.photo:
		filename = getTmpFile(msg)
		r = api.update_with_media(filename)
		os.system('rm ' + filename)
		return r
	return api.update_status(parseUrl(msg.text))

def tweet(msg, chat):
	if not matchKey(msg.text, KEYS) and not matchKey(chat.title, KEYS): 
		return
	if not isMeaningful(msg):
		return
	tweetMsg(msg)

@log_on_fail(debug_group)
def manageMsg(update, context):
	global queue
	msg = update.effective_message 
	if not msg:
		return
	if not update.effective_chat:
		return
	if update.effective_chat.id not in SUBSCRIPTION:
		return
	queue.append((update.effective_chat.id, msg.message_id))

@log_on_fail(debug_group)
def start(update, context):
	if update.message:
		update.message.reply_text('pong')

def backfill(chat_id, fill_range):
	for message_id in fill_range:
		queue.append((chat_id, message_id))
 
auth = tweepy.OAuthHandler(CREDENTIALS['twitter_consumer_key'], CREDENTIALS['twitter_consumer_secret'])
auth.set_access_token(CREDENTIALS['twitter_access_token'], CREDENTIALS['twitter_access_secret'])
api = tweepy.API(auth)

tele.dispatcher.add_handler(MessageHandler(Filters.update.channel_posts, manageMsg))
tele.dispatcher.add_handler(MessageHandler(Filters.private, start))

@log_on_fail(debug_group, EXPECTED_ERRORS)
def loopImp():
	if not queue:
		return
	chat_id, msg_id = queue.pop()
	r = tele.bot.forward_message(
		chat_id = test_channel, message_id = msg_id, from_chat_id = chat_id)
	tweet(r, r.forward_from_chat)

def loop():
    loopImp()
    threading.Timer(LOOP_INTERVAL, loop).start() 

threading.Timer(1, loop).start()

tele.start_polling()
tele.idle()