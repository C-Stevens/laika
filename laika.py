import sys
import os
from bot import *
from threading import Thread

def importBotConfigs():
	botPool= os.listdir('./config/')
	badFilenames = []

	for i in botPool: # Find all files that aren't .py and remove them
		if not i.endswith('.py'):
			badFilenames.append(i)
	for i in badFilenames:
		botPool.remove(i)

	botPool = [ os.path.basename(f)[:-3] for f in botPool] # Strip extensions
	global loadedBots

	originalPath = sys.path[:]
	sys.path.insert(0, 'config') # Configure sys path for importing
	loadedBots = [__import__(x) for x in botPool] # Import the valid files
	sys.path = originalPath # Reset sys path

if __name__ == "__main__":
	importBotConfigs()
	threads = []
	for b in loadedBots:
		bot = irc.spawnBot(b)
		bot.connect()
		t = Thread(target=bot.run)
		threads.append(t)
		t.start()
	for i in threads:
		i.join()
