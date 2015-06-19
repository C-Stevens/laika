import ssl
import os
import imp
import socket
from queue import Queue
import src.irc as irc
import src.format as format
import src.command as command
import src.log as log

class bot:
	def __init__(self, config, botLog, **kwargs):
		self.loadConfig(config)
		self.logger = botLog
		self.ircLogger = log.ircLogManager(kwargs.get('botLogName', config['nick'])) ##DEBUG
		self.messageQueue = Queue()
		self.socketWrapper = irc.socketConnection(self.logger, self.ircLogger, self.socket, self.messageQueue)
		self.commandWrapper = command.commandManager(self.logger)
		self.command_list = []
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
		self.mask 		= config['mask']
		self.ident 		= config['ident']
		self.userMode 		= str(config['userMode'])
		self.channels 		= config['channels']
		self.highlightChar 	= config['highlightChar']
		self.authList 		= config['authList']

	def load_commands(self):
		'''Import all commands found in ./commands.'''
		command_paths = [os.path.abspath(os.path.join('./commands', i)) for i in os.listdir('./commands') if i.endswith('.py')]
		for i in command_paths:
			self.command_list.append(imp.load_source(os.path.splitext(os.path.basename(i))[0], i))
		self.logger.debug("Loaded Commands: %s", self.command_list)
	def parse(self, line):
		'''Deal with lines coming off the socket.'''
		line = line.split(' ')
		if line[1] == "PRIVMSG":
			if len(line) < 4: # Malformed line. Pass to avoid going out of bounds
				return
			firstWordSplit = line[3].split(':',1)
			if len(firstWordSplit) < 2: # Line split improperly on ':', discard
				return
			firstWord = firstWordSplit[1]

			self.ircLogger.channelLog(line[2], line) # Log channel message

			if len(firstWord) != 1 and firstWord.startswith(self.highlightChar): # Check for command words
				line_info = command.commandData()
				
				if line[0].find('!~') != -1:
					line_info.identd = False
					splitOn = '!~'
				else:
					line_info.identd = True
					splitOn = '!'
				try:
					line_info.nick = line[0].split(splitOn)[0][1:]
					line_info.user = line[0].split(splitOn)[1].split('@')[0]
					line_info.hostname = line[0].split(splitOn)[1].split('@')[1]
					line_info.msgType = line[1]
					line_info.channel = line[2]
					line_info.command = firstWord[1:]
					line_info.highlightChar = self.highlightChar
					line_info.args = ' '.join(line[4:])

					for commandModule in self.command_list:
						if self.run_check(commandModule,line_info) == 0:
							self.commandWrapper.spawnThread(line_info, self.socketWrapper, commandModule)
							return
						elif self.run_check(commandModule, line_info) == 2:
							self.socketWrapper.notice(line_info.nick, "You are not authorized to use the "+format.bold(line_info.command)+" command")
							return
					self.socketWrapper.notice(line_info.nick, "Command "+format.bold(line_info.command)+" not found")
				except Exception as e:
					self.logger.error("Failed to parse message: %s", line)
					self.logger.exception(e)
			return
		self.ircLogger.serverLog.info(' '.join(line)) # Log all non PRIVMSG server messages
		if line[0] == "PING": # Respond to a network PINGs
			self.socketWrapper.pong(line[1])
			return
		if line[1] == "NOTICE":
			if line[0][1:].find("NickServ!NickServ@services") != -1: # NickServ notice
				_nmMessage = ' '.join(str(i) for i in line[3:])[1:] # Reconstruct message
				if _nmMessage.find("This nickname is registered.") != -1:
					self.logger.info("Authing to nickserv")
					if self.mask is True:
						self.socketWrapper.nsIdentify(self.nick, self.nickPass, True)
					else:
						self.socketWrapper.nsIdentify(self.nick, self.nickPass)
			return
	def run_check(self, command, line_info):
		'''Checks if the command being called is the command requested, and checks if user is allowed to call that command.'''
		if line_info.command == command.config['command_str']:
			if command.config['auth'] is False:
				return 0
			elif command.config['auth'] is True and line_info.nick in self.authList:
				return 0
			else:
				return 2
		else:
			return 1
	def printConfig(self):
		'''Prints the object's loaded config for debug.'''
		print(self.configFile.config)
	def run(self):
		'''Main loop for reading data off the socket.'''
		self.load_commands()
		self.socketWrapper.connect(self.host, self.port, self.nick, self.ident, self.userMode, self.serverPass)
		if self.nickPass is not None:
			self.socketWrapper.nsIdentify(self.nick, self.nickPass, self.mask)
		self.socketWrapper.joinChannels(self.channels)
		while self.socketWrapper.runState is True:
			self.socketWrapper.buildMessageQueue()
			while self.messageQueue.qsize() > 1: # Never touch last queue element, it will be cycled by buildMessageQueue()
				line = self.messageQueue.get_nowait()
				if line is not '': # Ignore leftover items from split('\r\n')
					try:
						self.logger.info(line) # TODO: seperate irc logging
					except:
						pass
					self.parse(line)
