import threading
from src.datatypes import Type
import re
import traceback

class commandError(Exception):
	'''Generic Exception class for catching errors while handling commands.'''
	def __init__(self, msg=''):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)

class commandManager:
	def __init__(self, log):
		self.log = log
		self.maxUserThreads = 5 # Default user thread pool size
		self.threadPools = {}
	def spawnThread(self, commandData, socket, commandModule):
		'''Spawns a command thread.'''
		user = commandData.hostname
		if self.userThreadCount(user) is None: # No threads exist. Create a thread pool for this user
			userThreads = []
			self.threadPools[user] = userThreads # Map nick to thread array
		if self.userThreadCount(user) > self.maxUserThreads - 1: # Subtract one to convert human-friendly bound to index-accurate bound
			socket.notice(commandData.nick, "Maximum number of pending commands ("+str(self.maxUserThreads)+") reached. Command '"+commandData.command+"' has been ignored")
			self.log.warning("User '"+user+"'has filled their command queue and been denied a command request")
			return
		t = commandThread(self, user, commandModule, commandData, socket)
		self.threadPools[user].append(t)
		t.start()
	def userThreadCount(self, user):
		'''Returns the number of active threads in the provided user's thread pool.'''
		try:
			return len(self.threadPools[user])
		except KeyError: # The user is not in the threadPool dict
			return None
	def reportThreads(self, user):
		'''Returns a list of active threads in a provided user's thread pool.'''
		try:
			return self.threadPools[user]
		except KeyError: # The user is not in the threadPool dict
			return None
	def removeThread(self, thread, user):
		'''Removes the provided thread from the provided user's thread pool.'''
		self.threadPools[user].remove(thread)

class commandThread(threading.Thread):
	def __init__(self, parent, user, commandModule, commandData, socket):
		threading.Thread.__init__(self)
		self.parent = parent
		self.user = user
		self.command = commandModule
		self.commandData = commandData
		self.name = self.commandData.command
		self.socket = socket
	def validateArgs(self):
		givenArgs = self.commandData.args
		commandArgs = self.command.config['args']
		if len(givenArgs) is 0 and commandArgs is not None:
			raise commandError("Command requested arguments but recieved none.")
		elif len(givenArgs) is not 0 and commandArgs is None:
			raise commandError("Command was provided arguments but requested none.")
		elif len(givenArgs) is 0 and commandArgs is None:
			return ()
		print(commandArgs) ##DEBUG
		
		_regexList = list(commandArgs)
		for i, type, in enumerate(_regexList):
			_regexList[i] = "(%s)"%type.validRegex()
		_stringMatch = re.compile(r'^'+' '.join(_regexList)+'$')
		print("givenArgs:",givenArgs) ##DEBUG
		argMatches = _stringMatch.match(givenArgs)
		if argMatches is None:
			raise commandError("Command failed to match arguments.")
		else:
			return argMatches.groups()
		print("TOTAL REGEX MATCH:",_stringMatch) ##DEBUG
	def run(self):
		'''Runs the command's run() function, then signals that the thread is finished.'''
		try:
			validArgs = self.validateArgs()
		except commandError as e:
			self.socket.notice(self.commandData.nick, self.commandData.command+": Invalid syntax - "+e.msg)
			self.socket.notice(self.commandData.nick, "Usage: %s%s %s"%(self.commandData.highlightChar,self.commandData.command,self.command.config['args']))
			self.parent.log.error(str(e))
			self.parent.removeThread(self, self.user)
			return
		try:
			self.command.run(self, *validArgs)
			self.parent.removeThread(self, self.user)
		except Exception as e:
			self.socket.notice(self.commandData.nick, "Command '"+self.command+"' has critically failed. See logs for more information")
			self.parent.log.exception(e)
			self.parent.removeThread(self, self.user)
			return

class commandData:
	def __init__(self):
		self.identd = ''
		self.nick = ''
		self.user = ''
		self.hostname = ''
		self.channel = ''
		self.command = ''
		self.highlightChar = ''
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
		print("highlightChar :",self.highlightChar)
		print("msgType :",self.msgType)
		print("args :",self.args)
