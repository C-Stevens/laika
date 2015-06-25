import os
import sys
import imp
import src
from threading import Thread
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib/pyyaml/lib3"))
import yaml
import argparse
from _version import __version__

argParser = argparse.ArgumentParser(description="A modular chat bot for the IRC protocol.")
argParser.add_argument("--version", action='version', version=__version__, help="Displays version information and exits")
args = argParser.parse_args()

rootLog = src.log.logger(infoLog=True, defaultFormat="%(message)s", debugLogFormat="[%(levelname)s] %(message)s") #TODO: Read in values from args and/or config file

if __name__ == "__main__":
	rootLog.info("-------------\n"+__version__+"\n-------------")

	rootLog.info("Loading bot config files..")
	botConfigs = [os.path.abspath(os.path.join('./config', i)) for i in os.listdir('./config') if i.endswith('.yaml')]
	botPool = {}
	for i in botConfigs:
		try:
			botPool[i] = yaml.load(open(i, "r").read(-1))
			if type(botPool[i]) is not dict:
				rootLog.error("Config '"+i+"' malformed, import aborted")
				del botPool[i]
		except Exception as e:
			rootLog.error("Failed to load log:"+i)
			rootLog.exception(e)
	if not botPool:
		rootLog.critical("No bots could be loaded")
		sys.exit(1)
	rootLog.info("Bot config files loaded")
	rootLog.debug("Bot Pool: %s",botPool)

	threads = []
	for i in botPool:
		configFilename = i.split('/')[-1].replace('.yaml','')
		rootLog.info("Starting bot '%s'..",configFilename)
		botLog = src.log.logger(infoLog=False, infoLogFormat="%(asctime)s %(message)s", defaultFormat="%(asctime)s [%(threadName)s] - %(levelname)s - %(message)s") #TODO: Get these args from somewhere else
		botObject = src.bot.bot(botPool[i], botLog)
		t = Thread(target=botObject.run, name=configFilename)
		threads.append(t)
		t.start()
		rootLog.info("Bot '%s' started", configFilename)
	for i in threads:
		i.join()
