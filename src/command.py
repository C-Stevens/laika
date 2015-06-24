import sys
import threading
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
	def validateArgs(self, args, commandArgs):
		'''Assembles a regex match out of command arguments, and returns dict of matches from provided commands.'''
		requiredArgs = 0
		for i in commandArgs:
			if not i.optional:
				requiredArgs += 1
		if not args and requiredArgs != 0:
			raise commandError("Command requested arguments but recieved none.")
		if args and len(commandArgs) == 0:
			raise commandError("Command requested no arguments but arguments were recieved.")
		_regexMatch = ''
		if len(commandArgs) > 1:
			for arg in commandArgs[:-1]:
				if arg.optional:
					_regexMatch += "(%s\s)?"%(arg.baseRegex())
				else:
					_regexMatch += "(%s\s)"%(arg.baseRegex())
		if commandArgs[-1].optional:
			_regexMatch += "(%s)?"%(commandArgs[-1].baseRegex())
		else:
			_regexMatch += "(%s)"%(commandArgs[-1].baseRegex())
		_stringMatch = re.compile(r'^'+_regexMatch+'$')
		print("\t",_stringMatch) ##DEBUG
		result = _stringMatch.search(args)
		if result is None and len(commandArgs) != 0:
			raise commandError("Command failed to match arguments.")
		if result is not None:
			return result.groupdict()
		else:
			return {}
	def createUsage(self, command):
		'''Returns a formatted Usage string.'''
		if  not command.config['args']:
			return "Usage ([optional], <required>): %s%s\t<No arguments>"%(self.commandData.highlightChar, command.config['command_str'])
		else:
			return "Usage ([optional], <required>): %s%s\t%s"%(self.commandData.highlightChar,command.config['command_str'],self.argList(command.config['args']))
	def argList(self, args):
		'''Assembles and returns a formatted argument list.'''
		_argList = list(args)
		for i, arg in enumerate(_argList):
			_argList[i] = arg.describe()
		_argList = ' '.join(_argList)
		return _argList
	def run(self):
		'''Runs the command's run() function, then signals that the thread is finished.'''
		try:
			validArgs = self.validateArgs(self.commandData.args, self.command.config['args'])
		except Exception as e:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			errMsg = traceback.format_exception_only(exc_type,exc_value)[0]
			if exc_type is commandError:
				errMsg = errMsg.split(':')[1]
				self.socket.notice(self.commandData.nick, self.commandData.command+": Invalid syntax: "+errMsg)
				self.socket.notice(self.commandData.nick, self.createUsage(self.command))
			else:
				self.socket.notice(self.commandData.nick, "Command '"+str(self.command)+"' has critically failed. See logs for more information")
				self.parent.log.exception(e)
			self.parent.removeThread(self, self.user)
			return
		try:
			self.command.run(self, **validArgs)
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
