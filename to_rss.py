#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
from telegram_util import addToQueue, log_on_fail, getFilePath, getLinkFromMsg
import threading
import yaml
from feedgen.feed import FeedGenerator
from lxml import etree

INTERVAL = 1
LIMIT = 10

with open('CREDENTIALS') as f:
	CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)

tele = Updater(CREDENTIALS['bot_token'], use_context=True)
r = tele.bot.send_message(-1001198682178, 'start')
debug_group = r.chat

with open('SUBSCRIPTION') as f:
	SUBSCRIPTION = yaml.load(f, Loader=yaml.FullLoader)

test_channel = -1001159399317
EXPECTED_ERRORS = ['Message to forward not found', "Message can't be forwarded"]

def getFeedChannel(rss_detail):
	fg = FeedGenerator()
	fg.title(rss_detail['title'])
    fg.link(rss_detail['link'], rel='self')
    fg.description(rss_detail['description'])
    return fg

for k, v in SUBSCRIPTION.items():
	SUBSCRIPTION[k]['channel'] = getFeedChannel(v)

def getMsgLink(msg):
	return 't.me/' + msg.chat.username + '/' + str(msg.message_id)

def editFeedEntry(item, msg):
	item.id = getMsgLink(msg)
    item.link(href=getLinkFromMsg(msg) or getFilePath(msg))
    item.description(msg.text or getFilePath(msg))

def getEntry(fg, msg):
	for entry in fg.__feed_entries:
		if entry.id = getMsgLink(msg):
			return entry
	if len(fg.__feed_entries) > LIMIT:
		fg.__feed_entries.pop(0)
	return fg.add_entry()

def appendRss_(rss_name, msg):
	filename = 'rss/' + rss_name + '.xml'
	fg = SUBSCRIPTION[rss_name]['channel']
	item = getEntry(fg, msg)
	editFeedEntry(fg, msg)

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
		appendRss_(rss_name, r)
	print(msg_id)

@log_on_fail(debug_group, EXPECTED_ERRORS)
def _manageMsg(update):
	msg = update.effective_message
	if not msg or not msg.chat:
		return
	apendRss(msg.chat_id, msg.message_id)

@log_on_fail(debug_group)
def manageMsg(update, context):
	threading.Timer(INTERVAL, lambda: _manageMsg(update)).start() 

for msg_id in range(10):
	apendRss(-1001409716127, msg_id)

tele.dispatcher.add_handler(MessageHandler(Filters.update.channel_posts, manageMsg))

tele.start_polling()
tele.idle()