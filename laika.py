import os
import imp
import bot
from threading import Thread

if __name__ == "__main__":
	bot_files = [os.path.abspath(os.path.join('./config', i)) for i in os.listdir('./config') if i.endswith('.py')]
	bot_py = []
	for i in bot_files:
		bot_py.append(imp.load_source(os.path.splitext(os.path.basename(i))[0], i))
	print(bot_py) ##DEBUG
	print(bot_files) ##DEBUG
	threads = []
	for i in bot_py:
		j = bot.irc.bot(i)
		j.connect()
		t = Thread(target=j.run)
		threads.append(t)
		t.start()
	for i in threads:
		i.join()
