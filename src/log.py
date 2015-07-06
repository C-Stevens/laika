import logging
import os
import sys
import traceback

class levelFilter:
	def __init__(self, level):
		self._level = level
	def filter(self, logRecord):
		'''Only logs lines that match the specified log level.'''
		return logRecord.levelno <= self._level

class logger(logging.Logger):
	def __init__(self, **kwargs):
		logging.Logger.__init__(self, self)		
		defaultFormat = kwargs.get('defaultFormat', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

		if kwargs.get('critLog', True):
			self.addStream(kwargs.get('critLogDir'), logging.CRITICAL, kwargs.get('critLogFormat', defaultFormat))
		if kwargs.get('errLog', True):
			self.addStream(kwargs.get('errLogDir'), logging.ERROR, kwargs.get('errLogFormat', defaultFormat))
		if kwargs.get('warnLog', True):
			self.addStream(kwargs.get('warnLogDir'), logging.WARNING, kwargs.get('warnLogFormat', defaultFormat))
		if kwargs.get('infoLog', False):
			self.addStream(kwargs.get('infoLogDir'), logging.INFO, kwargs.get('infoLogFormat', defaultFormat))
		if kwargs.get('debugLog', False):
			self.addStream(kwargs.get('debugLogDir'), logging.DEBUG, kwargs.get('debugLogFormat', defaultFormat))
	def addStream(self, logDir, logLevel, logFormat):
		'''Adds a log handler with the specified options to the logger.'''
		if logDir is not None:
			try:
				handler = logging.FileHandler(logDir)
			except FileNotFoundError as e:
				print(e, "Defaulting message output for this stream to std_err")
				handler = logging.StreamHandler()
		else:
			handler = logging.StreamHandler()
		handler.setLevel(logLevel)
		handler.setFormatter(logging.Formatter(logFormat))
		handler.addFilter(levelFilter(logLevel))
		self.addHandler(handler)

class basicLogger(logging.Logger):
	def __init__(self, logPath):
		logging.Logger.__init__(self, self)
		self.logPath = logPath
		self.setLevel(logging.NOTSET)
		self.addHandler(logging.FileHandler(self.logPath))
	def log(self, msg):
		'''Log all messages to self only as of level logging.INFO.'''
		self.info(msg)

class channelLogger(logging.Logger):
	def __init__(self, logPath, **kwargs):
		logging.Logger.__init__(self, self)
		self.kwargs = kwargs
		self.setLevel(logging.NOTSET)
		fh = logging.FileHandler(logPath)
		fh.setFormatter(logging.Formatter("%(asctime)s %(message)s", kwargs.get('timeStampFormat') or '[%Y-%m-%d %H:%M:%S]'))
		self.addHandler(fh)
	def log(self, nick, msg):
		'''Format message and log to self as only of level logging.INFO.'''
		self.info(self.kwargs.get('messageFormat') or "<%(nick)s> %(msg)s", {'nick':nick, 'msg':msg})

class ircLogManager:
	def __init__(self, name, **kwargs):
		self.kwargs = kwargs
		self.botName = name
		self._logRoot = os.path.abspath(kwargs.get('logRoot','./log'))
		self.channelLogs = {}
		self.prepareDirs()
		self.prepareLogs()
	def prepareDirs(self):
		'''Makes sure all the dirs for logging are present. If not, create them.'''
		self.serverLogPath = os.path.join(self._logRoot, self.botName)
		if not os.path.exists(self.serverLogPath):
			os.makedirs(self.serverLogPath)
		self.channelLogPath = self.kwargs.get('channelLogPath') or os.path.join(self.serverLogPath, 'channel_log')
		if not os.path.exists(self.channelLogPath):
			os.makedirs(self.channelLogPath)
	def prepareLogs(self):
		'''Spawns two basicLogger objects for socket and server logging.'''
		self.serverLog = basicLogger(os.path.join(self.serverLogPath, self.kwargs.get('serverLogFile') or 'server_log.log'))
		self.socketLog = basicLogger(os.path.join(self.serverLogPath, self.kwargs.get('socketLogFile') or 'socket_log.log'))
	def channelLog(self, channel, line):
		'''Creates logger for channel if it does not exist, otherwise logs line to appropriate logger.'''
		if not channel in self.channelLogs: # Log object for this channel needs to be created
			channelLog = channelLogger(os.path.join(self.channelLogPath, channel), **self.kwargs)
			self.channelLogs[channel] = channelLog
		try:
			nick = line[0][1:].split('!')[0]
			message = ' '.join(line[3:])[1:]
			self.channelLogs[channel].log(nick, message)
		except Exception as e:
			## Unfortunately this logs directly to stderr in the console, making any truly silent or non-verbose
			## option for the program not possible. Passing this object the error logging object is ugly and this
			## object should not be able to depend on the error logging object existing in the first place. In the
			## future, there ought to be a broader umbrella log managing object that can be queried for individual
			## log objects. For now, it dumps to stderr if something messes up.
			traceback.print_exc(file=sys.stderr)
