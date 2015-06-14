import os
import imp
import src
from threading import Thread
from _version import __version__

rootLog = src.log.logger(infoLog=True, defaultFormat="%(message)s", debugLogFormat="[%(levelname)s] %(message)s") #TODO: Read in values from args and/or config file

if __name__ == "__main__":
	rootLog.info("Laika version "+__version__+" starting..")

	rootLog.info("Loading bot config files..")
	botConfigs = [os.path.abspath(os.path.join('./config', i)) for i in os.listdir('./config') if i.endswith('.py')]
	botPool = []
	for i in botConfigs:
		botPool.append(imp.load_source(os.path.splitext(os.path.basename(i))[0], i))
	rootLog.info("Bot config files loaded")
	rootLog.debug("Bot Pool: %s",botPool)

	threads = []
	for i in botPool:
		rootLog.info("Starting bot '%s'..",i.__name__)
		botLog = src.log.logger(infoLog=True, infoLogFormat="%(asctime)s %(message)s", defaultFormat="%(asctime)s [%(threadName)s] - %(levelname)s - %(message)s") #TODO: Get these args from somewhere else
		botObject = src.bot.bot(i, botLog)
		t = Thread(target=botObject.run, name=i.__name__)
		threads.append(t)
		t.start()
		rootLog.info("Bot '%s' started", i.__name__)
	for i in threads:
		i.join()
