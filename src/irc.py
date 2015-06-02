import time 
import socket
import sys
import string
import os
from queue import Queue
                
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
	def readQueue(self):
		'''Safely assemble an array of queue items without popping anything off.'''
		queue = []
		if self.messageQueue.empty() is False:
			for i in range(self.messageQueue.qsize()-1,-1,-1): # Walk backwards through items
				queue.append(self.messageQueue.queue[i])
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
			while any("is now your hidden host (set by services.)" in i for i in self.readQueue()) is not True:
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
