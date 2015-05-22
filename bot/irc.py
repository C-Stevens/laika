import time 
import socket
import sys
import string
import ssl
import os
import imp

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
		self.socketWrapper = socketConnection(self.socket)
		self.host = configFile.config['host']
		self.port = configFile.config['port']
		self.nick = configFile.config['nick']
		self.ident = configFile.config['ident']
		self.userMode = configFile.config['userMode']
		self.channels = configFile.config['channels']
		self.highlightChar = configFile.config['highlightChar']
		self.command_list = []
	def connect(self):
		'''Establish an IRC connection'''
		self.socket.connect((self.host, self.port))
		time.sleep(0.2)
		self.socket.send(("NICK " + self.nick + "\r\n").encode('utf-8'))
		time.sleep(0.2)
		self.socket.send(("USER " + self.ident + " " + self.userMode + " * :" + self.nick + "\r\n").encode('utf-8'))
	def load_commands(self):
		'''Import all commands found in ./commands.'''
		command_paths = [os.path.abspath(os.path.join('./commands', i)) for i in os.listdir('./commands') if i.endswith('.py')]
		for i in command_paths:
			self.command_list.append(imp.load_source(os.path.splitext(os.path.basename(i))[0], i))
		print("\t[!!!!!] loaded commands: ",self.command_list) ##DEBUG
	def parse(self, line):
		'''Deal with pre-split lines coming off the socket.'''
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
				line_info.channel = line[2]
				line_info.command = firstWord[1:]
				line_info.args = line[4:]
					
				print("OMG SOMEONE IS TALKING TO ME\n") ##DEBUG
				for i in self.command_list:
					if i.run_check(line_info) == 0:
						print(i,"can take this command")
						i.run(line_info,self.socketWrapper)

	def run(self):
		'''Main loop for reading data off the socket.'''
		global buffer
		buffer = ''
		self.load_commands()
		self.socketWrapper.joinChannels(self.channels)
		while True:
			buffer += self.socket.recv(1024).decode('utf-8')
			#self.socketWrapper.dumpSocketData()
			#if data: # TODO: Supress output if user specifies no verbosity
				#try:
				#	print(data)
				#except:
				#	pass
			message = buffer.split("\r\n")
			for i in message[:-1]: # The last element will always either be blank or incomplete
				line = i.split(' ')
				print("LINE IS: ",repr(line)) ##DEBUG
				self.parse(line) # Send the line to be parsed
			buffer = message[-1] # Add either the blank element, or the incomplete message to data for next loop

	def printConfig(self):
                print(self.configFile.config)
                
class socketConnection:
	def __init__(self, socket):
		self.socket = socket
	def dumpSocketData(self):
		'''Print raw socket output to console for debug.'''
		try:
			print(self.socket.recv(1024).decode('utf-8'))
		except:
			pass
	def pong(self, host):
		'''Properly respond to server PINGs.'''
		print("PING Received, sending PONG + ",host,"+\r\n") ##DEBUG
		self.socket.send(("PONG " + host + "\r\n").encode('utf-8'))
	def joinChannels(self, channels):
		'''Join all channels in a given array.'''
		for i in channels:
			self.socket.send(("JOIN " + i + "\r\n").encode('utf-8'))
	def sendToChannel(self, channel, message):
		''' Sends specified message to the specified channel.'''
		if not channel.startswith("#"):
			channel = "#" + channel
		self.socket.send(("PRIVMSG " + channel + " :" + message + "\r\n").encode('utf-8'))
			
class commandData:
	def __init__(self):
		self.identd = ''
		self.nick = ''
		self.user = ''
		self.hostname = ''
		self.channel = ''
		self.command = ''
		self.args = []
	def printData(self):
		''' Print out all held data for debug.'''
		print("identd :",self.identd)
		print("nick :",self.nick)
		print("user :",self.user)
		print("hostname :",self.hostname)
		print("channel :",self.channel)
		print("command :",self.command)
		print("args :",self.args)