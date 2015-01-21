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
	def run(self):
		# Main loop for reading and parsing lines
		global data
		data = ''
		while True:
			data += self.socket.recv(1024).decode('utf-8')
			if data: # TODO: Supress output if user specifies no verbosity
				try:
					print(data)
				except:
					pass
			message = data.split("\r\n")
			for i in message[:-1]: # The last element will always either be blank or incomplete
				line = i.split(' ')
				#print("LINE IS: ",line) ##DEBUG
				if line[0] == "PING": # Respond to network PINGs
					self.pong(line[1])
			data = message[-1] # Add either the blank element, or the incomplete message to data for next loop

	def printData(self):
                print(self.configFile.config)
