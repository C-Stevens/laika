import ssl
import os
import imp
import socket
import threading
from queue import Queue
import src.irc as irc
import src.format as format
import src.command as command
import src.log as log

class bot:
	def __init__(self, config, **kwargs):
		self.ircLogger = log.ircLogManager()
		self.loadConfig(config)
		self.logger = log.logger(**self.botLogConfig)
		self.messageQueue = Queue()
		self.socketWrapper = irc.socketConnection(self.logger, self.ircLogger, self.socket, self.messageQueue)
		self.command_list = []
		self.module_list = []
		self.commandWrapper = command.commandManager(self.logger, self.command_list, self.authList, self.threadPoolSize)
		self.load_modules()
	def loadConfig(self, config):
		'''Loads all needed config items into object.'''
		if config['server']['ssl'] is True:
			self.socket = ssl.wrap_socket(socket.socket())
		elif config['server']['ssl'] is False:
			self.socket = socket.socket()
		else:
			self.logger.warning("Unable to determine ssl preferences, defaulting to no ssl")
			self.socket = socket.socket()
		self.host 		= config['server']['host']
		self.port 		= config['server']['port']
		self.serverPass 	= config['server']['pass']
		self.nick 		= config['nick']
		self.nickPass 		= config['nickPass']
		self.ident 		= config['ident']
		self.userMode 		= str(config['userMode'])
		self.channels 		= config['channels']
		self.highlightPrefix 	= config['highlightPrefix']
		self.authList 		= config['authList']
		self.threadPoolSize	= config['threadPoolSize']
		self.botLogConfig	= config['botLog']
		for logGroup in config['ircLog']:
			if not config['ircLog'][logGroup]['botLogName']:
				config['ircLog'][logGroup]['botLogName'] = self.nick
			self.ircLogger.register(log.ircLogGroup(**config['ircLog'][logGroup]))
	def load_commands(self):
		'''Imports all files found in ./commands as commands.'''
		command_paths = [os.path.abspath(os.path.join('./commands', i)) for i in os.listdir('./commands') if i.endswith('.py')]
		for i in command_paths:
			try:
				self.command_list.append(imp.load_source(os.path.splitext(os.path.basename(i))[0], i))
			except Exception as e:
				self.logger.error("Failed to import command: %s", i)
				self.logger.exception(e)
		self.logger.debug("Loaded Commands: %s", self.command_list)
	def load_modules(self):
		'''Imports all files found in ./modules as modules.'''
		module_paths = [os.path.abspath(os.path.join('./modules', i)) for i in os.listdir('./modules') if i.endswith('.py')]
		for i in module_paths:
			try:
				self.module_list.append(imp.load_source(os.path.splitext(os.path.basename(i))[0], i))
			except Exception as e:
				self.logger.error("Failed to import module: %s", i)
				self.logger.exception(e)
		self.logger.debug("Loaded Modules: %s", self.command_list)
		for module in self.module_list:
			t = threading.Thread(target=module.run, name="module_"+module.__name__, args=(self.ircLogger, self.logger, self.socketWrapper, self.commandWrapper))
			t.start()
	def parse(self, line):
		'''Deal with lines coming off the socket.'''
		split_line = line.split(' ')
		if split_line[1] == "PRIVMSG":
			if len(split_line) < 4: # Malformed line. Pass to avoid going out of bounds
				return
			line_message = ' '.join(split_line[3:])[1:]

			self.ircLogger.notifyChannelLogs(split_line[2], split_line) # Log channel message

			if line_message[:len(self.highlightPrefix)] == self.highlightPrefix: # Check for command words
				line_info = command.commandData()
				
				if split_line[0].find('!~') != -1:
					line_info.identd = False
					splitOn = '!~'
				else:
					line_info.identd = True
					splitOn = '!'
				try:
					line_info.botnick = self.nick
					line_info.nick = split_line[0].split(splitOn)[0][1:]
					line_info.user = split_line[0].split(splitOn)[1].split('@')[0]
					line_info.hostname = split_line[0].split(splitOn)[1].split('@')[1]
					line_info.msgType = split_line[1]
					line_info.channel = split_line[2]
					if line_info.channel == self.nick: # Direct PM responses to the user who sent the PM
						line_info.channel = line_info.nick
					line_info.command = line_message[len(self.highlightPrefix):].split(' ')[0]
					line_info.highlightPrefix = self.highlightPrefix
					line_info.args = ' '.join(line_message[len(self.highlightPrefix):].split(' ')[1:])

					self.commandWrapper.spawnThread(line_info, self.socketWrapper)
				except Exception as e:
					self.logger.error("Failed to parse message: %s", line)
					self.logger.exception(e)
			return
		self.ircLogger.notifyServerLogs(line) # Log all non PRIVMSG server messages
		if split_line[0] == "PING": # Respond to a network PINGs
			self.socketWrapper.pong(split_line[1])
			return
		if split_line[1] == "NOTICE":
			if split_line[0][1:].find("NickServ!NickServ@services") != -1: # NickServ notice
				_nmMessage = ' '.join(str(i) for i in split_line[3:])[1:] # Reconstruct message
				if _nmMessage.find("This nickname is registered.") != -1:
					self.logger.info("Authing to NickServ")
					self.socketWrapper.nsIdentify(self.nick, self.nickPass)
			return
	def run(self):
		'''Main loop for reading data off the socket.'''
		self.load_commands()
		self.socketWrapper.connect(self.host, self.port, self.nick, self.ident, self.userMode, self.serverPass)
		if self.nickPass is not None:
			self.socketWrapper.nsIdentify(self.nick, self.nickPass)
		self.socketWrapper.joinChannels(self.channels)
		while self.socketWrapper.runState is True:
			self.socketWrapper.buildMessageQueue()
			while self.messageQueue.qsize() > 1: # Never touch last queue element, it will be cycled by buildMessageQueue()
				line = self.messageQueue.get_nowait()
				if line is not '': # Ignore leftover items from split('\r\n')
					try:
						self.logger.info(line)
					except:
						pass
					self.parse(line)
		self.logger.info("Bot exiting")
