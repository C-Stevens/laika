import time 
import socket
import sys
import string
import os
import threading
import queue
                
class socketConnection:
	def __init__(self, log, ircLog, socket, queue):
		self.log = log
		self.ircLog = ircLog
		self.socket = socket
		self.socket.settimeout(600) # Default 10 minutes
		self.messageQueue = queue
		self.buffer = ''
		self.runState = True
		self.socketQueue = socketQueue(self, self.socket, self.ircLog)
	def readFromSocket(self):
		'''Returns data out of the socket. Aborts the connection and runState if socket times out.'''
		if self.runState is False:
			return None
		try:
			return self.socket.recv(1024).decode('utf-8')
		except socket.timeout:
			self.log.error("Socket has timed out. Aborting.")
			self.runState = False
	def buildMessageQueue(self):
		'''Builds a message queue or adds message to an existing queue from socket data.'''
		self.buffer = self.readFromSocket()
		if self.buffer is None:
			return
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
		if not self.messageQueue.empty():
			for i in range(self.messageQueue.qsize()-1,-1,-1): # Walk backwards through items
				queue.append(self.messageQueue.queue[i])
		return queue
	def connect(self, host, port, nick, ident, userMode, serverPass=None,):
		'''Establish an IRC connection.'''
		self.socket.connect((host, port))
		time.sleep(0.2) # Wait to account for any slight network hiccups
		if serverPass is not None:
			self.socketQueue.addToQueue("PASS "+serverPass+"\r\n")
			time.sleep(0.2) # Ditto above
		self.socketQueue.addToQueue("NICK "+nick+"\r\n")
		time.sleep(0.2) # Ditto above
		self.socketQueue.addToQueue("USER "+ident+" "+userMode+" * :"+nick+"\r\n")
	def socketShutdown(self):
		'''Safely shuts down and closes the socket.'''
		self.socket.shutdown(socket.SHUT_WR)
		self.socket.close()
	def pong(self, host):
		'''Properly respond to server PINGs.'''
		self.log.info("PONG "+host)
		self.socketQueue.addToQueue("PONG "+host+"\r\n")
	def joinChannels(self, channels):
		'''Join given channel, or all channels in a given array.'''
		if type(channels) is list:
			for _channel in channels:
				self.socketQueue.addToQueue("JOIN "+_channel+"\r\n")
		elif type(channels) is str:
			self.socketQueue.addToQueue("JOIN "+channels+"\r\n")
	def partChannels(self, channel, message=None):
		'''Leave a single channel with optional message.'''
		if message is not None:
			self.socketQueue.addToQueue("PART "+channel+" :"+message+"\r\n")
		else:
			self.socketQueue.addToQueue("PART "+channel+"\r\n")
	def sendToChannel(self, channel, message):
		'''Sends specified message to the specified channel.'''
		self.socketQueue.addToQueue("PRIVMSG "+channel+" :"+message+"\r\n")
	def quit(self, message=None):
		'''Disconnects from the IRC server with optional message.'''
		if message is not None:
			self.socketQueue.addToQueue("QUIT :"+message+"\r\n")
		else:
			self.socketQueue.addToQueue("QUIT\r\n")
		time.sleep(.5) # Preventative wait measure to let any concurrent socket processes end
		self.runState = False # Terminate connection
	def kick(self, user, channel, message=None):
		'''Kicks specified user from specified channel with optional message.'''
		if message:
			self.socketQueue.addToQueue("KICK "+channel+" "+user+" :"+message+"\r\n")
		else:
			self.socketQueue.addToQueue("KICK "+channel+" "+user+"\r\n")
	def topic(self, channel, topic):
		'''Sets a new topic for the provided channel.'''
		self.socketQueue.addToQueue("TOPIC "+channel+" :"+topic+"\r\n")
	def userMode(self, user, mode):
		'''Applies the specified user modes.'''
		self.socketQueue.addToQueue("MODE "+user+" "+mode+"\r\n")
	def channelMode(self, channel, modes, extraArgs=None):
		'''Applies the specified modes to the specified channel, with an optional field at end for extra arguments.'''
		if extraArgs:
			self.socketQueue.addToQueue("MODE "+channel+" "+modes+" "+extraArgs+"\r\n")
		else:
			self.socketQueue.addToQueue("MODE "+channel+" "+modes+"\r\n")
	def invite(self, nick, channel):
		'''Invites specified nick to specified channel.'''
		self.socketQueue.addToQueue("INVITE "+nick+" "+channel+"\r\n")
	def time(self, server=None):
		'''Requests time from current server, or specified server if provided.'''
		if server:
			self.socketQueue.addToQueue("TIME "+server+"\r\n")
		else:
			self.socketQueue.addToQueue("TIME\r\n")
	def nick(self, nick):
		'''Sets nickname to specified nick.'''
		self.socketQueue.addToQueue("NICK "+nick+"\r\n")
	def nsIdentify(self, nick, password=None):
		'''Identifies the bot's nick with NickServ.'''
		if password is not None:
			self.socketQueue.addToQueue("NS IDENTIFY "+nick+" "+password+"\r\n")
	def action(self, channel, action):
		'''Issues a CTCP ACTION command to specified channel.'''
		self.socketQueue.addToQueue("PRIVMSG "+channel+" :\u0001ACTION "+action+"\u0001\r\n")
	def notice(self, nick, message):
		'''Issues a notice to the specified user with the specified message.'''
		self.socketQueue.addToQueue("NOTICE "+nick+" :"+message+"\r\n")

class socketQueue:
	def __init__(self, parent, socket, ircLog):
		self.parent = parent
		self.socket = socket
		self.ircLog = ircLog
		self.socketQueue = queue.Queue()
		self.encoding = 'utf-8'
		self.t = threading.Thread(target=self.flushQueue, name="socket_queueWorker")
		self.t.start()
	def addToQueue(self, message, reportToQueue=True):
		'''Adds a given string to the socket queue.'''
		self.socketQueue.put((message,reportToQueue))
	def flushQueue(self):
		'''Sends out all messages in the queue to the socket.'''
		while self.parent.runState is True:
			try:
				_queueItem = self.socketQueue.get(timeout=0.5)
			except queue.Empty:
				continue
			if self.parent.runState is True: # Additional runState check to avoid sending to a closed socket
				try:
					self.socket.send((_queueItem[0]).encode(self.encoding))
					if _queueItem[1]: # Report to socket log watchers unless explicitly told not to
						self.ircLog.notifySocketLogs(_queueItem[0].replace('\r\n','')) # Log socket send
				except BrokenPipeError:
					self.parent.runState = False
		self.parent.socketShutdown()
