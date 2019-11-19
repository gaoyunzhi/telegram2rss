#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
from telegram_util import addToQueue, log_on_fail, getFilePath, getLinkFromMsg
import threading
import yaml
from feedgen.feed import FeedGenerator
import os

INTERVAL = 1
LIMIT = 3
REWIND = 60 # LIMIT * 2

with open('CREDENTIALS') as f:
	CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)

tele = Updater(CREDENTIALS['bot_token'], use_context=True)
r = tele.bot.send_message(-1001198682178, 'start')
debug_group = r.chat

with open('SUBSCRIPTION') as f:
	SUBSCRIPTION = yaml.load(f, Loader=yaml.FullLoader)

test_channel = -1001159399317
EXPECTED_ERRORS = ['Message to forward not found', "Message can't be forwarded"]

def getFeedChannel(rss_name, chat):
	fg = FeedGenerator()
	fg.title(chat.title)
	fg.link(href = '%s/rss/%s.xml' % (CREDENTIALS['host'], rss_name), rel='self')
	fg.description(chat.description or chat.title)
	return fg

def editFeedEntry(item, msg, guid):
	item.guid(guid)
	print(msg_id, getLinkFromMsg(msg))
	item.link(href=getLinkFromMsg(msg) or getFilePath(msg))
	item.description(msg.text or getFilePath(msg))

def getEntry(subscription, msg_id):
	entries = subscription['entries']
	fg = subscription['channel']
	for mid, entry in entries:
		if mid == msg_id:
			return entry
	if len(entries) > LIMIT:
		entries.pop(0)
		fg.remove_entry(0)
	entry = fg.add_entry()
	entries.append((msg_id, entry))
	return entry

def appendRss_(rss_name, msg, msg_id):
	filename = 'rss/' + rss_name + '.xml'
	subscription = SUBSCRIPTION[rss_name]
	fg = SUBSCRIPTION[rss_name]['channel']
	item = getEntry(subscription, msg_id)
	editFeedEntry(item, msg, subscription['link'] + '/' + str(msg_id))
	print('[DEBUG] saving file')
	fg.rss_file(filename)
	print('[DEBUG] file saved')
	

def getSubscription(chat_id):
	for rss_name, detail in SUBSCRIPTION.items():
		if chat_id == detail['subscription']:
			yield rss_name

@log_on_fail(debug_group, EXPECTED_ERRORS)
def apendRss(chat_id, msg_id):
	rss_names = list(getSubscription(chat_id))
	if not rss_names:
		return
	r = tele.bot.forward_message(
		chat_id = test_channel, message_id = msg_id, from_chat_id = chat_id)
	for rss_name in rss_names:
		appendRss_(rss_name, r, msg_id)


@log_on_fail(debug_group, EXPECTED_ERRORS)
def _manageMsg(update):
	msg = update.effective_message
	if not msg or not msg.chat:
		return
	apendRss(msg.chat_id, msg.message_id)

@log_on_fail(debug_group)
def manageMsg(update, context):
	threading.Timer(INTERVAL, lambda: _manageMsg(update)).start() 

print('[DEBUG] INIT')
for k, v in SUBSCRIPTION.items():
	chat_id = SUBSCRIPTION[k]['subscription']
	r = tele.bot.send_message(chat_id = chat_id, text = 'test')
	r.delete()
	SUBSCRIPTION[k]['channel'] = getFeedChannel(k, r.chat)
	SUBSCRIPTION[k]['entries'] = []
	SUBSCRIPTION[k]['link'] = 'http://t.me/' + r.chat.username
	for msg_id in range(r.message_id - REWIND, r.message_id):
		apendRss(chat_id, msg_id)
print('[DEBUG] INIT END')

tele.dispatcher.add_handler(MessageHandler(Filters.update.channel_posts, manageMsg))

tele.start_polling()
tele.idle()