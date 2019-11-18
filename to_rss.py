#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
from telegram_util import addToQueue, log_on_fail
import threading
import yaml

INTERVAL = 1

with open('CREDENTIALS') as f:
	CREDENTIALS = json.load(f)

tele = Updater(CREDENTIALS['bot_token'], use_context=True)
r = tele.bot.send_message(-1001198682178, 'start')
debug_group = r.chat

with open('SUBSCRIPTION') as f:
	SUBSCRIPTION = yaml.load(f, Loader=yaml.FullLoader)

test_channel = -1001159399317
EXPECTED_ERRORS = ['Message to forward not found', "Message can't be forwarded"]

def appendRss(rss_name, msg):
	with open('rss/' + rss_name + '.xml', 'a') as f:
		f.write('test\n') # TODO

@log_on_fail(debug_group, EXPECTED_ERRORS)
def _manageMsg(update):
	msg = update.effective_message
	if not msg or not msg.chat:
		return
	r = None
	for rss_name, subscriptions in SUBSCRIPTION:
		if msg.chat.id in subscriptions:
			if not r:
				r = msg.forward(test_channel)
			appendRss(rss_name, r)

@log_on_fail(debug_group)
def manageMsg(update, context):
	threading.Timer(LOOP_INTERVAL, _manageMsg).start() 

@log_on_fail(debug_group, EXPECTED_ERRORS)
def backfill(chat_id, msg_id):
	r = tele.bot.forward_message(
		chat_id = test_channel, message_id = msg_id, from_chat_id = chat_id)

for msg_id in range(300):
	backfill(-1001409716127, msg_id)

tele.dispatcher.add_handler(MessageHandler(Filters.update.channel_posts, manageMsg))

tele.start_polling()
tele.idle()