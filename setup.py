import os
import sys
from signal import signal, SIGINT
from sys import exit

RUN_FILES = ['to_rss', 'rss_server']

def kill():
	template = "ps aux | grep ython | grep '%s.py' | awk '{print $2}' | xargs kill -9"
	for f in RUN_FILES:
		os.system(template % f)
	exit(0)

def setup(arg = ''):
	if arg == 'kill':
		kill()
		return

	os.system('mkdir rss')

	if arg != 'debug':
		r = os.system('sudo pip3 install -r requirements.txt')
		if r != 0:
			os.system('curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py')
			os.system('sudo python3 get-pip.py')
			os.system('rm get-pip.py')
			os.system('sudo pip3 install -r requirements.txt')
	try:
		from telegram.ext import Updater, MessageHandler, Filters
	except:
		os.system('sudo pip3 install python-telegram-bot --upgrade') # need to use some experiement feature, e.g. message filtering
			
	kill()

	template = "nohup python3 -u %s.py &"
	for f in RUN_FILES:
		os.system(template % f)

	if arg.startswith('debug'):
		signal(SIGINT, kill)
		os.system('tail -F nohup.out')


if __name__ == '__main__':
	if len(sys.argv) > 1:
		setup(sys.argv[1])
	else:
		setup('')