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
		self.socketQueue = socketQueue(self.socket)
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
		if self.messageQueue.empty() is False and self.messageQueue.queue[_lastElementIndex] != '': # Last item was an incomplete line
			self.messageQueue.queue[_lastElementIndex] += lines[0] # Complete the line with the first data out of the socket
			for i in range(0,len(lines)-1): # Add all the other line elements to the queue
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
		self.socketQueue.addToQueue("NICK "+nick+"\r\n")
		time.sleep(0.2)
		self.socketQueue.addToQueue("USER "+ident+" "+userMode+" * :"+nick+"\r\n")
		self.runState = True
	def pong(self, host):
		'''Properly respond to server PINGs.'''
		print("PING Received, sending PONG "+host) ##DEBUG
		self.socketQueue.addToQueue("PONG "+host+"\r\n")
	def joinChannels(self, channels):
		'''Join all channels in a given array.'''
		if type(channels) == list:
			for _channel in channels:
				self.socketQueue.addToQueue("JOIN "+self.channelParse(_channel)+"\r\n")
		elif type(channels) == str:
			self.socketQueue.addToQueue("JOIN "+self.channelParse(channels)+"\r\n")
	def partChannels(self, channel, message=None):
		'''Leave a single channel with optional message.'''
		if message is not None:
			self.socketQueue.addToQueue("PART "+self.channelParse(channel)+" :"+message+"\r\n")
		else:
			self.socketQueue.addToQueue("PART "+self.channelParse(channel)+"\r\n")
	def sendToChannel(self, channel, message):
		'''Sends specified message to the specified channel.'''
		self.socketQueue.addToQueue("PRIVMSG "+self.channelParse(channel)+" :"+message+"\r\n")
	def quit(self, message=None):
		'''Disconnects from the irc server with optional message.'''
		if message is not None:
			self.socketQueue.addToQueue("QUIT :"+message+"\r\n")
		else:
			self.socketQueue.addToQueue("QUIT\r\n")
		self.socket.close()
		self.runState = False
	def nsIdentify(self, nick, password, waitForMask=False):
		'''Identifies nick with NickServ.'''
		if password is not None:
			self.socketQueue.addToQueue("NS IDENTIFY "+nick+" "+password+"\r\n")
		if waitForMask == True: # Halts further socket interaction until the bot is given its mask
			_backoffMax = 10 # Maximum wait time (in seconds)
			_backoff = 1
			while any("is now your hidden host (set by services.)" in i for i in self.readQueue()) is not True:
				self.buildMessageQueue()
				_backoff = min(_backoff * 1.05, _backoffMax)
				time.sleep(_backoff)
	def action(self, channel, action):
		'''Issues an ACTION command to specified channel.'''
		self.socketQueue.addToQueue("PRIVMSG "+self.channelParse(channel)+" :\u0001ACTION "+action+"\u0001\r\n")
	def channelParse(self, channel):
		if not channel.startswith("#"):
			return "#" + channel
		else:
			return channel

class socketQueue:
	def __init__(self, socket):
		self.socket = socket
		self.socketQueue = Queue()
		self.encoding = 'utf-8'
	def addToQueue(self, message):
		'''Adds a given string to the socket queue.'''
		self.socketQueue.put(message)
		self.emptyQueue()
	def emptyQueue(self):
		'''Sends out all messages in the queue to the socket.'''
		print("Hello I'm in the emptyQueue function") ##DEBUG
		while self.socketQueue.empty() is False:
			print("\tGonna empty out some messages") ##DEBUG
			self.socket.send((self.socketQueue.get()).encode(self.encoding))
