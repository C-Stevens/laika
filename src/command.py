import threading

class commandManager:
	def __init__(self):
		self.maxUserThreads = 5 # Default user thread pool size
		self.threadPools = {}
	def spawnThread(self, commandData, socket, commandModule):
		'''Spawns a command thread.'''
		if self.userThreadCount(commandData.nick) is None: # No threads exist. Create a thread pool for this user
			userThreads = []
			self.threadPools[commandData.nick] = userThreads # Map nick to thread array
		if self.userThreadCount(commandData.nick) > self.maxUserThreads - 1: # Subtract one to convert human-friendly bound to index-accurate bound
			socket.notice(commandData.nick, "Maximum number of pending commands ("+str(self.maxUserThreads)+") reached. Command '"+commandData.command+"' has been ignored")
			return
		t = commandThread(self, commandData.nick, commandModule, commandData, socket)
		self.threadPools[commandData.nick].append(t)
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
	def __init__(self, parent, user, commandModule, *args):
		threading.Thread.__init__(self)
		self.parent = parent
		self.user = user
		self.command = commandModule
		self.args = args
	def run(self):
		'''Runs the command's run() function, then signals that it's finished'''
		self.command.run(*self.args)
		self.parent.removeThread(self, self.user)

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
