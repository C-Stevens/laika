import logging
import os
import sys

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
		self.info(msg)

class channelLogger(logging.Logger):
	def __init__(self, logPath):
		logging.Logger.__init__(self, self)
		self.setLevel(logging.NOTSET)
		fh = logging.FileHandler(logPath)
		fh.setFormatter(logging.Formatter("%(asctime)s %(message)s", "[%Y-%m-%d %H:%M:%S]"))
		self.addHandler(fh)
	def log(self, nick, msg):
		self.info("<%(nick)s> %(msg)s", {'nick':nick, 'msg':msg})

class ircLogManager:
	def __init__(self, name):
		self.botName = name
		self._logRoot = os.path.abspath('./log') ## TODO: Make this less hacky
		self.channelLogs = {}
		self.prepareDirs()
		self.prepareLogs()
	def prepareDirs(self):
		self.serverLogPath = os.path.join(self._logRoot, self.botName)
		if not os.path.exists(self.serverLogPath):
			os.makedirs(self.serverLogPath)
		self.channelLogPath = os.path.join(self.serverLogPath, 'channel_log')
		if not os.path.exists(self.channelLogPath):
			os.makedirs(self.channelLogPath)
	def prepareLogs(self):
		self.serverLog = basicLogger(os.path.join(self.serverLogPath, 'server_log.log'))
		self.socketLog = basicLogger(os.path.join(self.serverLogPath, 'socket_log.log'))
	def channelLog(self, channel, line):
		if channel in self.channelLogs:
			self.channelLogs[channel]
		else: # No log for this channel exists
			channelLog = channelLogger(os.path.join(self.channelLogPath, channel))
			self.channelLogs[channel] = channelLog
		try:
			nick = line[0][1:].split('!')[0]
			message = ' '.join(line[3:])[1:]
			self.channelLogs[channel].log(nick, message)
		except Exception as e:
			sys.stderr.write(e)
			traceback.print_exc(file=sys.stderr)
