import logging
import logging.handlers
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
        defaultFormat = kwargs.get('defaultFormat') or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        if kwargs.get('critLog') or True:
            self.addStream(kwargs.get('critLogPath'), logging.CRITICAL, kwargs.get('critLogFormat') or defaultFormat)
        if kwargs.get('errLog') or True:
            self.addStream(kwargs.get('errLogPath'), logging.ERROR, kwargs.get('errLogFormat') or defaultFormat)
        if kwargs.get('warnLog') or True:
            self.addStream(kwargs.get('warnLogPath'), logging.WARNING, kwargs.get('warnLogFormat') or defaultFormat)
        if kwargs.get('infoLog') or False:
            self.addStream(kwargs.get('infoLogPath'), logging.INFO, kwargs.get('infoLogFormat') or defaultFormat)
        if kwargs.get('debugLog') or False:
            self.addStream(kwargs.get('debugLogPath'), logging.DEBUG, kwargs.get('debugLogFormat') or defaultFormat)
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

class basicSocketLogger(logging.Logger):
    def __init__(self):
        logging.Logger.__init__(self, self)
        self.setLevel(logging.NOTSET)
        socketHandler = logging.handlers.SocketHandler('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        self.addHandler(socketHandler)
    def log(self, msg):
        self.info(str(msg))

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
        self.info(self.kwargs.get('messageFormat') or u'<%(nick)s> %(msg)s', {'nick':nick, 'msg':msg})
        
class ircLogManager:
    def __init__(self):
        self.observers = []
    def register(self, observer):
        '''Adds a logging object to the observer pool for notifications.'''
        self.observers.append(observer)
    def notifyChannelLogs(self, *args, **kwargs):
        '''Notifies all observers channel logging methods.'''
        for logGroup in self.observers:
            logGroup.logChannelData(*args, **kwargs)
    def notifySocketLogs(self, *args, **kwargs):
        '''Notifies all observers socket logs.'''
        for logGroup in self.observers:
            logGroup.logSocketData(*args, **kwargs)
    def notifyServerLogs(self, *args, **kwargs):
        '''Notifies all observers server logs.'''
        for logGroup in self.observers:
            logGroup.logServerData(*args, **kwargs)

class ircLogGroup:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._logRoot = os.path.abspath(kwargs.get('logRoot','./log'))
        self.channelLogs = {}
        self.socketLogs = {}
        self.serverLogs = {}
        self.prepareDirs()
        self.prepareLogs()
    def prepareDirs(self):
        '''Makes sure all the dirs for logging are present. If not, create them.'''
        self.serverLogPath = os.path.join(self._logRoot, self.kwargs.get('botLogName'))
        if not os.path.exists(self.serverLogPath):
            os.makedirs(self.serverLogPath)
        self.channelLogPath = self.kwargs.get('channelLogDir') or os.path.join(self.serverLogPath, 'channel_log')
        if not os.path.exists(self.channelLogPath):
            os.makedirs(self.channelLogPath)
    def prepareLogs(self):
        '''Spawns two basicLogger objects for socket and server logging.'''
        self.serverLog = basicLogger(os.path.join(self.serverLogPath, self.kwargs.get('serverLogFile') or 'server_log.log'))
        self.socketLog = basicLogger(os.path.join(self.serverLogPath, self.kwargs.get('socketLogFile') or 'socket_log.log'))
    def logChannelData(self, channel, line):
        '''Creates logger for channel if it does not exist, otherwise logs line to appropriate logger.'''
        if not channel in self.channelLogs: # Log object for this channel needs to be created
            channelLog = channelLogger(os.path.join(self.channelLogPath, channel), **self.kwargs)
            self.channelLogs[channel] = channelLog
        try:
            nick = line[0][1:].split('!')[0]
            message = ' '.join(line[3:])[1:]
            self.channelLogs[channel].log(nick, message)
        except:
            # If an exception is thrown here, the method has most likely received a malformed line and it should not be logged anyway
            pass
    def logSocketData(self, *args, **kwargs):
        self.socketLog.log(*args, **kwargs)
    def logServerData(self, *args, **kwargs):
        self.serverLog.log(*args, **kwargs)
