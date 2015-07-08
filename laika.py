import os
import sys
import imp
import src
from threading import Thread
import argparse
from _version import __version__
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib/pyyaml/lib3"))
import yaml

argParser = argparse.ArgumentParser(description="A modular chat bot for the IRC protocol.")
argParser.add_argument("--version", action='version', version=__version__, help="Displays version information and exits")
argParser.add_argument("-q", "--quiet", action='store_true', help="Prevents program from outputting to terminal. Does not apply to bot, channel, socket, or server logging")
argParser.add_argument("--config", type=argparse.FileType('r'), help="")
argParser.add_argument("--defaultFormat", help="Sets program default logging format")

argParser.add_argument("--critLog", action='store', default=None, help="Enables or disables logging for critical messages")
argParser.add_argument("--errLog", action='store', default=None, help="Enables or disables logging for error messages")
argParser.add_argument("--warnLog", action='store', default=None, help="Enables or disables logging for warning messages")
argParser.add_argument("--infoLog", action='store', default=None, help="Enables or disables logging for info messages")
argParser.add_argument("--debugLog", action='store', default=None, help="Enables or disables logging for debug messages")

argParser.add_argument("--critLogDir", help="Sets program critical logging path")
argParser.add_argument("--errLogDir", help="Sets program error logging path")
argParser.add_argument("--warnLogDir", help="Sets program warning logging path")
argParser.add_argument("--infoLogDir", help="Sets program info logging path")
argParser.add_argument("--debugLogDir", help="Sets program debug logging path")

argParser.add_argument("--critLogFormat", help="Sets program critical logging format")
argParser.add_argument("--errLogFormat", help="Sets program error logging format")
argParser.add_argument("--warnLogFormat", help="Sets program warning logging format")
argParser.add_argument("--infoLogFormat", help="Sets program info logging format")
argParser.add_argument("--debugLogFormat", help="Sets program debug logging format")
args = vars(argParser.parse_args())

def loadConfig():
	if args['config']:
		return yaml.load(args['config'].read(-1))
	else:
		return yaml.load(open(os.path.join(os.path.abspath('.'),'laika.cfg'), 'r').read(-1))
def applyArgs(config):
	for argVal in args:
		if args[argVal] and argVal in ("critLog","errLog","warnLog","infoLog","debugLog"):
			args[argVal] = validateBool(args[argVal])
	for val in config:
		if args[val] is not None and config[val] is not args[val]:
			print("arg: "+repr(val)) ##DEBUG
			print("swapping %s for %s"%(repr(config[val]),repr(args[val]))) ##DEBUG
			config[val] = args[val]
	if args['quiet']:
		for i in ('critLog','errLog','warnLog','infoLog','debugLog'):
			config[i] = False
def validateBool(arg):
	if arg.lower() in ("true", "t", "yes", 1):
		return True
	elif arg.lower() in ("false", "f", "no", 0):
		return False
def run():
	config = loadConfig()
	applyArgs(config)
	rootLog = src.log.logger(**config)
	rootLog.info("-------------\n"+__version__+"\n-------------")
	rootLog.info("Loading bot configuration files..")
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
		botObject = src.bot.bot(botPool[i])
		t = Thread(target=botObject.run, name=configFilename)
		threads.append(t)
		t.start()
		rootLog.info("Bot '%s' started", configFilename)
	for i in threads:
		i.join()

if __name__ == "__main__":
	run()
