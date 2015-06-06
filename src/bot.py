import ssl
import os
import imp
from queue import Queue
import src.irc as irc
import src.format as format
import socket

class bot:
	def __init__(self, configFile):
		self.configFile = configFile
		
		if configFile.config['ssl'] is True:
			self.socket = ssl.wrap_socket(socket.socket())
		elif configFile.config['ssl'] is False:
			self.socket = socket.socket()
		else:
			print("Unable to determine ssl preferences, defaulting to no ssl") # TODO: Better error messages
			self.socket = socket.socket()
		self.socket.settimeout(600) # Default timeout is 10 minutes. Can be changed here
		self.messageQueue = Queue()
		self.socketWrapper = irc.socketConnection(self.socket, self.messageQueue)

		self.host = configFile.config['host']
		self.port = configFile.config['port']
		self.nick = configFile.config['nick']
		self.nickPass = configFile.config['nickPass']
		self.mask = configFile.config['mask']
		self.ident = configFile.config['ident']
		self.userMode = configFile.config['userMode']
		self.channels = configFile.config['channels']
		self.highlightChar = configFile.config['highlightChar']
		self.authList = configFile.config['authList']

		self.command_list = []
	def load_commands(self):
		'''Import all commands found in ./commands.'''
		command_paths = [os.path.abspath(os.path.join('./commands', i)) for i in os.listdir('./commands') if i.endswith('.py')]
		for i in command_paths:
			self.command_list.append(imp.load_source(os.path.splitext(os.path.basename(i))[0], i))
		print("\t[!!!!!] loaded commands: ",self.command_list) ##DEBUG
	def parse(self, line):
		'''Deal with pre-split lines coming off the socket.'''
		line = line.split(' ')
		if line[0] == "PING": # Respond to a network PINGs
			self.socketWrapper.pong(line[1])
			return
		if line[1] == "PRIVMSG":
			if len(line) < 4: # Malformed line. Pass to avoid going out of bounds
				return
			firstWordSplit = line[3].split(':',1)
			if len(firstWordSplit) < 2: # Line split improperly on ':', discard
				return
			firstWord = firstWordSplit[1]

			if len(firstWord) != 1 and firstWord.startswith(self.highlightChar): # Check for command words
				line_info = irc.commandData()
				
				if line[0].find('!~') != -1:
					line_info.identd = False
				else:
					line_info.identd = True
				if line_info.identd == True:
					splitOn = '!'
				elif line_info.identd == False:
					splitOn = '!~'
				line_info.nick = line[0].split(splitOn)[0][1:]
				line_info.user = line[0].split(splitOn)[1].split('@')[0]
				line_info.hostname = line[0].split(splitOn)[1].split('@')[1]
				line_info.msgType = line[1]
				line_info.channel = line[2]
				line_info.command = firstWord[1:]
				line_info.highlightChar = self.highlightChar
				line_info.args = line[4:]
					
				for i in self.command_list:
					if self.run_check(i,line_info) == 0:
						i.run(line_info,self.socketWrapper)
						return
					elif self.run_check(i, line_info) == 2:
						self.socketWrapper.sendToChannel(line_info.channel, line_info.nick + ": You are not authorized to use the " + format.bold(line_info.command) + " command")
						return
				self.socketWrapper.sendToChannel(line_info.channel, line_info.nick + ": Command " + format.bold(line_info.command) + " not found")
		if line[1] == "NOTICE":
			print("\t[!!!] Caught notice") ##DEBUG
			if line[0][1:].find("NickServ!NickServ@services") != -1: # NickServ notice
				print("\t[!!!] Caught ns") ##DEBUG
				nmMessage = ' '.join(str(i) for i in line[3:])[1:] # Reconstruct message
				if nmMessage.find("This nickname is registered.") != -1:
					print("\t[!!!] Authing to nickserv") ##DEBUG
					if self.mask is True:
						self.socketWrapper.nsIdentify(self.nick, self.nickPass, True)
					else:
						self.socketWrapper.nsIdentify(self.nick, self.nickPass)
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
		self.socketWrapper.connect(self.host, self.port, self.nick, self.ident, self.userMode)
		if self.nickPass is not None:
			if self.mask is True:
				self.socketWrapper.nsIdentify(self.nick, self.nickPass, True)
			else:
				self.socketWrapper.nsIdentify(self.nick, self.nickPass)
		self.socketWrapper.joinChannels(self.channels)
		while self.socketWrapper.runState is True:
			print("--> Requesting messages")
			self.socketWrapper.buildMessageQueue()
			while self.messageQueue.qsize() > 1: # Never touch last queue element, it will be cycled by buildMessageQueue()
				line = self.messageQueue.get_nowait()
				if line is not '': # Ignore leftover items from split('\r\n')
					try: # TODO: Better output printing
						print(line)
					except:
						pass
					self.parse(line)