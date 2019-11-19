import os
import sys
from signal import signal, SIGINT
from sys import exit

def kill():
	os.system("ps aux | grep ython | grep 'to_rss.py' | awk '{print $2}' | xargs kill -9")
	os.system("ps aux | grep ython | grep 'rss_server.py' | awk '{print $2}' | xargs kill -9")
	exit(0)

def setup(arg = ''):
	if arg == 'kill':
		os.system("ps aux | grep ython | grep 'to_rss.py' | awk '{print $2}' | xargs kill -9")
		os.system("ps aux | grep ython | grep 'rss_server.py' | awk '{print $2}' | xargs kill -9")
		return

	os.system('mkdir rss')
	
	RUN_FILES = ['to_rss', 'rss_server']

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