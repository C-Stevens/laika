import sys
import os
from bot import *

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
	print(sys.path)
	for b in loadedBots:
		print(b)
		bot = irc.spawnBot(b)
		bot.printData()
		bot.connect()
		bot.run()
