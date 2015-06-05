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
		if type(channels) == list:
			for i in channels:
				if not i.startswith("#"):
					i = "#" + i
				self.socket.send(("JOIN " + i + "\r\n").encode('utf-8'))
		elif type(channels) == str:
			if not channels.startswith("#"):
				channels = "#" + channels
			self.socket.send(("JOIN " + channels + "\r\n").encode('utf-8'))
	def partChannels(self, channel, message=None):
		'''Leave a single channel with optional message.'''
		if not channel.startswith("#"):
			channel = "#" + channel
		if message is not None:
			self.socket.send(("PART " + channel + " :" + message + "\r\n").encode('utf-8'))
		else:
			self.socket.send(("PART " + channel + "\r\n").encode('utf-8'))
	def sendToChannel(self, channel, message):
		'''Sends specified message to the specified channel.'''
		if not channel.startswith("#"):
			channel = "#" + channel
		self.socket.send(("PRIVMSG " + channel + " :" + message + "\r\n").encode('utf-8'))
	def quit(self, message=None):
		'''Disconnects from the irc server with optional message.'''
		if message is not None:
			self.socket.send(("QUIT :" + message + "\r\n").encode('utf-8'))
		else:
			self.socket.send(("QUIT\r\n").encode('utf-8'))
		self.socket.close()
		self.runState = False
	def nsIdentify(self, nick, password, waitForMask=False):
		'''Identifies nick with NickServ.'''
		if password is not None:
			self.socket.send(("NS IDENTIFY " + nick + " " + password + "\r\n").encode('utf-8'))
		if waitForMask == True: # Halts further socket interaction until the bot is given its mask
			_backoffMax = 90 # Maximum wait time (in seconds)
			_backoff = 1
			while any("is now your hidden host (set by services.)" in i for i in self.readQueue()) is not True:
				self.buildMessageQueue()
				_backoff = min(_backoff * 2, _backoffMax)
				time.sleep(_backoff)

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
