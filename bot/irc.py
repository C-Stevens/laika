import time 
import socket
import sys
import string
import ssl
import os
import imp
from queue import Queue

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
		self.socketWrapper = socketConnection(self.socket, self.messageQueue)
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
				line_info = commandData()
				
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
				line_info.args = line[4:]
					
				print("OMG SOMEONE IS TALKING TO ME\n") ##DEBUG
				for i in self.command_list:
					if self.run_check(i,line_info) == 0:
						print(i,"can take this command")
						i.run(line_info,self.socketWrapper)
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
				return 1
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
				#try: # TODO: better output printing
					#print(line)
					#print(self.socketWrapper.readQueue(self.messageQueue))
				#except:
				#	pass
				if line is not '': # Ignore leftover items from split('\r\n')
					print(line)
					self.parse(line)
                
class socketConnection:
	def __init__(self, socket, queue):
		self.socket = socket
		self.messageQueue = queue
		self.buffer = ''
		self.runState = ''
	def readFromSocket(self):
		'''Reads and returns data out of the socket. Aborts the connection and runState if socket times out.'''
		try:
			return self.socket.recv(1024).decode('utf-8')
		except socket.timeout:
			print("Socket has timed out. Aborting.") # TODO: Better error printing
			self.socket.close()
			self.runState = False
	def buildMessageQueue(self):
		'''Builds a message queue or adds message to an existing queue from socket data.'''
		self.buffer = self.readFromSocket()
		lines = self.buffer.split('\r\n')
		if self.messageQueue.qsize() > 0:
			_lastElementIndex = self.messageQueue.qsize()-1
		else:
			_lastElementIndex = 0
		#print("DEBUG: qsize() = ",self.messageQueue.qsize())
		#print("DEBUG: _lastElementIndex =",_lastElementIndex)
		if self.messageQueue.empty() is False and self.messageQueue.queue[_lastElementIndex] != '': # Last item was an incomplete line
			self.messageQueue.queue[_lastElementIndex] += lines[0] # Complete the line with the first data out of the socket
			for i in range(0,len(lines)-1): # Add all the other line elements to the queue
				#print("DEBUG: lines =",lines)
				#print("DEBUG: putting lines[%d+1] which is %s",i,lines[i+1])
				self.messageQueue.put(lines[i+1])
			return
		else:
			for i in lines:
				self.messageQueue.put(i)
			return
	def readQueue(self, messageQueue):
		'''Safely assemble an array of queue items without popping anything off.'''
		queue = []
		if messageQueue.empty() is False:
			for i in range(messageQueue.qsize()-1,-1,-1): # Walk backwards through items
				queue.append(messageQueue.queue[i])
		return queue
	def connect(self, host, port, nick, ident, userMode):
		'''Establish an IRC connection'''
		self.socket.connect((host, port))
		time.sleep(0.2)
		self.socket.send(("NICK " + nick + "\r\n").encode('utf-8'))
		time.sleep(0.2)
		self.socket.send(("USER " + ident + " " + userMode + " * :" + nick + "\r\n").encode('utf-8'))
		self.runState = True
	def pong(self, host):
		'''Properly respond to server PINGs.'''
		print("PING Received, sending PONG + ",host,"+\r\n") ##DEBUG
		self.socket.send(("PONG " + host + "\r\n").encode('utf-8'))
	def joinChannels(self, channels):
		'''Join all channels in a given array.'''
		for i in channels:
			self.socket.send(("JOIN " + i + "\r\n").encode('utf-8'))
	def sendToChannel(self, channel, message):
		'''Sends specified message to the specified channel.'''
		if not channel.startswith("#"):
			channel = "#" + channel
		self.socket.send(("PRIVMSG " + channel + " :" + message + "\r\n").encode('utf-8'))
	def quit(self, message=None):
		'''Disconnects from the irc server with optional message.'''
		if message is not None:
			print("DEBUG: There's a message! it's :",message)
			#self.socket.send(("QUIT :" + message + "\r\n").encode('utf-8'))
			theMessage = ("QUIT " + message + "\r\n").encode('utf-8')
			print("The message :",theMessage)
			#print(("QUIT :" + message + "\r\n"))
			self.socket.send(theMessage)
		else:
			print("DEBUG: No message :(")
			self.socket.send(("QUIT\r\n").encode('utf-8'))
		self.socket.close()
		self.runState = False
	def nsIdentify(self, nick, password, waitForMask=False):
		'''Identifies nick with NickServ.'''
		if password is not None:
			self.socket.send(("NS IDENTIFY " + nick + " " + password + "\r\n").encode('utf-8'))
		if waitForMask == True: # Halts further socket interaction until the bot is given its mask
			msgs = self.readQueue(self.messageQueue)
			while any("is now your hidden host (set by services.)" in i for i in self.readQueue(self.messageQueue)) is not True:
				self.buildMessageQueue()
				time.sleep(2)

class commandData:
	def __init__(self):
		self.identd = ''
		self.nick = ''
		self.user = ''
		self.hostname = ''
		self.channel = ''
		self.command = ''
		self.msgType = ''
		self.args = []
	def printData(self):
		''' Print out all held data for debug.'''
		print("identd :",self.identd)
		print("nick :",self.nick)
		print("user :",self.user)
		print("hostname :",self.hostname)
		print("channel :",self.channel)
		print("command :",self.command)
		print("msgType :",self.msgType)
		print("args :",self.args)
