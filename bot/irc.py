import time 
import socket
import sys
import string

class spawnBot:
	def __init__(self, configFile):
		# Initialize all the variables needed
		self.configFile = configFile
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
		buffer = ''
		while True:
			data = self.socket.recv(1024)
			if data: # TODO: Suppress output if user specifies no verbosity
				print(data.decode('utf-8'))
			buffer = data.decode('utf-8').rstrip().split("\r\n")
			#print("BUFFER: ",buffer) ##DEBUG
			for i in buffer:
			#	print("INDV LINE: ",buffer) ##DEBUG
				line = i.split(' ')
				if line[0] == "PING":
					self.pong(line[1])
			buffer=''

	def printData(self):
                print(self.configFile.config)
