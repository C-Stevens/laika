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
			print("Unable to determine ssl preferences, defaulting to no ssl")
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
		if line[0] == "PING": # First things first, respond to a network PING if one shows up
			self.pong(line[1])
		if line[1] == "PRIVMSG" and line[3].split(':')[-1].startswith(self.highlightChar): # Deal with bot highlights
			print("OMG SOMEONE IS TALKING TO ME\r\n")
	def run(self):
		# Main loop for reading and parsing lines
		global data
		data = ''
		while True:
			data += self.socket.recv(1024).decode('utf-8')
			#if data: # TODO: Supress output if user specifies no verbosity
				#try:
				#	print(data)
				#except:
				#	pass
			message = data.split("\r\n")
			for i in message[:-1]: # The last element will always either be blank or incomplete
				line = i.split(' ')
				print("LINE IS: ",line) ##DEBUG
				self.parse(line) # Send the line to be parsed
			data = message[-1] # Add either the blank element, or the incomplete message to data for next loop

	def printData(self):
                print(self.configFile.config)
