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
		global data
		data = ''
		while True:
			data += self.socket.recv(1024).decode('utf-8')
			if data: # TODO: Supress output if user specifies no verbosity
				print(data)
			if not data.endswith("\r\n"): # If the message is incomplete
				message = data.rstrip().split("\r\n")
				for i in range(0,len(message)-1): # Loop for every element in data, except the last incomplete message
					line = message[i].rstrip().split(' ')
					#print("LINE IS: ",line) ##DEBUG
					if line[0] == "PING": # Respond to network PINGs
						self.pong(line[1])
				data='' # Empty buffer
				data+=message[-1] # Add the incomplete message to buffer for next loop
			else: # Else we've received n number of complete messages
				message = data.rstrip().split("\r\n")
				for i in message:
					line = i.rstrip().split(' ')
					#print("ELSE LINE IS: ",line) ##DEBUG
					if line[0] == "PING":
						self.pong(line[1])
					data = ''

	def printData(self):
                print(self.configFile.config)
