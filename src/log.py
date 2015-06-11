import logging

class logManager(logging.Logger):
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

class levelFilter:
	def __init__(self, level):
		self._level = level
	def filter(self, logRecord):
		'''Only logs lines that match the specified log level.'''
		return logRecord.levelno <= self._level
