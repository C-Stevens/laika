import os
import imp
import src
from threading import Thread
from _version import __version__

if __name__ == "__main__":
	rootLog = src.log.logManager(infoLog=True, defaultFormat="%(message)s", debugLogFormat="[%(levelname)s] %(message)s") #TODO: Read in values from args and/or config file
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
		botObject = src.bot.bot(i)
		t = Thread(target=botObject.run, name=i.__name__)
		threads.append(t)
		t.start()
		rootLog.info("Bot '%s' started", i.__name__)
	for i in threads:
		i.join()
