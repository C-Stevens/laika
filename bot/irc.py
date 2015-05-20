import time 
import socket
import sys
import string
import ssl

class spawnBot:
	def __init__(self, configFile):
		# Initialize all the variables needed
		self.configFile = configFile
		if configFile.config['ssl'] is True:
			self.socket = ssl.wrap_socket(socket.socket())
		elif configFile.config['ssl'] is False:
			self.socket = socket.socket()
		else:
			print("Unable to determine ssl preferences, defaulting to no ssl") # TODO: Better error messages
			self.socket = socket.socket()
		self.host = configFile.config['host']
		self.port = configFile.config['port']
		self.nick = configFile.config['nick']
		self.ident = configFile.config['ident']
		self.userMode = configFile.config['userMode']
		self.channels = configFile.config['channels']
		self.highlightChar = configFile.config['highlightChar']
	def connect(self):
		# Establish an IRC connection
		self.socket.connect((self.host, self.port))
		time.sleep(0.2)
		self.socket.send(("NICK " + self.nick + "\r\n").encode('utf-8'))
		time.sleep(0.2)
		self.socket.send(("USER " + self.ident + " " + self.userMode + " * :" + self.nick + "\r\n").encode('utf-8'))
		self.joinChannels(self.channels)
	def joinChannels(self, channels):
		for i in channels:
			self.socket.send(("JOIN " + i + "\r\n").encode('utf-8'))
	def pong(self, data):
		# Properly respond to server PINGs
		print("PING Received, sending PONG + ",data,"+\r\n") ##DEBUG
		self.socket.send(("PONG " + data + "\r\n").encode('utf-8'))
	def parse(self, line):
		# Deal with pre-split lines coming off the socket
		if len(line) < 4: # Malformed line. Pass to avoid going out of bounds
			pass
		if line[0] == "PING": # Respond to a network PING if one shows up
			self.pong(line[1])
			return
		if line[1] == "PRIVMSG":
			firstWordSplit = line[3].split(':',1)
			if len(firstWordSplit) < 2:
				return
			firstWord = firstWordSplit[1]

			if not len(firstWord) == 1 and firstWord.startswith(self.highlightChar): # Check for commands
				print("OMG SOMEONE IS TALKING TO ME\r\n")
				print(">> Command is ",firstWord)
	def run(self):
		# Main loop for reading and parsing lines
		global buffer
		buffer = ''
		while True:
			buffer += self.socket.recv(1024).decode('utf-8')
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
