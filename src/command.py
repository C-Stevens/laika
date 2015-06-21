import threading
from src.datatypes import Type
import re
import traceback
import src.format as format

class commandError(Exception):
	'''Generic Exception class for catching errors while handling commands.'''
	def __init__(self, msg=''):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)

class commandManager:
	def __init__(self, log, commandList, authList):
		self.log = log
		self.commandList = commandList
		self.authList = authList
		self.maxUserThreads = 5 # Default user thread pool size
		self.threadPools = {}
	def spawnThread(self, commandData, socket):
		'''Spawns a command thread if given the OK from runValidator'''
		for i in self.commandList:
			if commandData.command == i.config['command_str']:
				if i.config['auth'] is False or i.config['auth'] is True and commandData.nick in self.authList:
					user = commandData.hostname
					if self.userThreadCount(user) is None: # No threads exist. Create a thread pool for this user
						userThreads = []
						self.threadPools[user] = userThreads # Map nick to thread array
					if self.userThreadCount(user) > self.maxUserThreads - 1: # Subtract one to convert human-friendly bound to index-accurate bound
						socket.notice(commandData.nick, "Maximum number of pending commands ("+str(self.maxUserThreads)+") reached. Command '"+commandData.command+"' has been ignored")
						self.log.warning("User '"+user+"' has filled their command queue and has been denied a command request")
						return
					t = commandThread(self, user, i, commandData, socket)
					self.threadPools[user].append(t)
					t.start()
					return
				else:
					socket.notice(commandData.nick, "You are not authorized to use the "+format.bold(commandData.command)+" command")
					return
		socket.notice(commandData.nick, "Command "+format.bold(commandData.command)+" not found")
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
	def validateArgs(self, args, commandArgs, optional=False):
		'''Assembles a regex match out of command arguments, and returns matches from provided commands.'''
		givenArgs = args
		print("GIVEN ARGS:",givenArgs) ##DEBUG
		print("COMMAND ARGS:",commandArgs) ##DEBUG
		if not commandArgs:
			print("Returning") ##DEBUG
			return ()
		if len(givenArgs) is 0 and commandArgs is not None:
			if optional:
				return ()
			else:
				raise commandError("Command requested arguments but recieved none.")
		print(commandArgs) ##DEBUG
		
		_regexList = list(commandArgs)
		for i, type, in enumerate(_regexList):
			_regexList[i] = "(%s)"%type.validRegex()
		_stringMatch = re.compile(r'^'+' '.join(_regexList)+'$')

		argMatches = _stringMatch.match(givenArgs)
		if argMatches is None:
			raise commandError("Command failed to match arguments.")
		else:
			print("\tMATCHES:",argMatches.groups()) ##DBEUG
			return argMatches.groups()
		#print("TOTAL REGEX MATCH:",_stringMatch) ##DEBUG
	def createUsage(self, command):
		'''Returns a formatted Usage string.'''
		if  not command.config['args']:
			return "Usage: %s%s\t<No arguments>"%(self.commandData.highlightChar, command.config['command_str'])
		else:
			return "Usage: %s%s\t%s"%(self.commandData.highlightChar,command.config['command_str'],self.argList(command.config['args']))
	def argList(self, args):
		'''Assembles and returns a formatted argument list.'''
		_argList = list(args)
		for i, arg in enumerate(_argList):
			_argList[i] = '<'+repr(arg).split(':')[0][1:]+'>'
		_argList = ' '.join(_argList)
		return _argList
	def run(self):
		'''Runs the command's run() function, then signals that the thread is finished.'''
		try:
			validArgs = self.validateArgs(self.commandData.args, self.command.config['args'])
			print("VALID ARGS:",validArgs) ##DEBUG
			if self.command.config['op_args']:
				opArgs = self.validateArgs(self.commandData.args, self.command.config['op_args'], True)
			else:
				opArgs = None
		except commandError as e:
			self.socket.notice(self.commandData.nick, self.commandData.command+": Invalid syntax - "+e.msg)
			self.socket.notice(self.commandData.nick, self.createUsage(self.command))
			if self.command.config['op_args']:
				self.socket.notice(self.commandData.nick, "Optional Arguments:\t"+self.argList(self.command.config['op_args']))
			self.parent.log.error(str(e))
			self.parent.removeThread(self, self.user)
			return
		try:
			print("OPTIONAL ARGS:",opArgs) ##DEBUG
			self.command.run(self, *validArgs, optionalArgs=opArgs)
			self.parent.removeThread(self, self.user)
		except Exception as e:
			self.socket.notice(self.commandData.nick, "Command '"+str(self.command)+"' has critically failed. See logs for more information")
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
		self.args = ''
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
