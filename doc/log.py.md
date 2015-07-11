# `log.py` Documentation

### Introduction
This file holds the objects and methods involved with the creation and management of logs, both for Laika, loaded bots, as well as every loaded bot's server, socket, and channel logs.

### Objects
#### levelFilter objects
This object serves only to strictly and explicitly restrict message logging to a specified level. This object is added as a logging filter to a particular logging stream level.

*class* log.**levelFilter**()

* levelFilter.**filter**(*self*, *logRecord*)<br>
Returns boolean of the result of *logRecord*.levelno <= self._level, where `_level` is an internal logging level value supplied to the object while being added as a filter to the logging stream handler.

#### logger objects
This object is an inheritance of python's logging library's `logging.Logger` object. At creation time, this object will spawn up to five log streams, one for each log level of python's logging library methods (`logging.CRITICAL`,`logging.ERROR`,`logging.WARNING`,`logging.INFO`,`logging.DEBUG`).

By default, this object will spawn streams for critical, error, and warning logs and no streams for info or debug logs. This behavior can be modified at creation time through **kwargs.

*class* log.**logger(logging.Logger)**

* logger.**addStream**(*self*, *logDir*, *logLevel*, *logFormat*)<br>
Adds a log handler to the logger object of logging level *logLevel*. If *logDir* is `None`, this log stream will be of type `logging.StreamHandler`, otherwise it will attempt to be added as type `logging.FileHandler`, with *logDir* specified as the argument. If the path supplied in *logDir* is bad and raises a `FileNotFoundError` exception, this exception will be caught and printed, and the stream will be added as type `logging.StreamHandler` instead.
*logFormat* will be passed as an argument to `logging.Formatter()` and applied as a formatter to the handler being created. *logLevel* is passed as an argument to a `log.levelFilter` object and applied as a filter to the handler being created to restrict logging to only the type specified in *logLevel*.

#### basicLogger objects
This object is also an inheritance of python's logging library's `logging.Logger` object, however it differs from `log.logger()` in that it is a much more straightforward implementation, designed to log to only a single stream of a single log level.

At creation time, this object will spawn a single logging stream of level `logging.NOTSET`, and will add a `logging.FileHandler` handler to itself with a logging path supplied to it at creation time.

*class* log.**basicLogger(logging.Logger)**

* basicLogger.**log**(*self*, *msg*)<br>
Logs *msg* to itself as level `logging.INFO` by use of `logging.Logger`'s `info()` method, to which *msg* is supplied as an argument.

#### channelLogger objects
This object is created by the `log.ircLogManager` object to log individual channel messages. This, again, is an inheretance of python's logging library's `logging.Logger` and very similarly behaves as `log.basicLogger`, with added functionality for logging and formatting.

At creation time, this object spawns a single logging steam of level `logging.NOTSET`, and adds a `logging.FileHandler` handler to itself with a logging path supplied to it at creation time. It also will set a `logging.Formatter` formatter to this handler with "`%(asctime)s %(message)s` supplied as a first object, and passing a time stamp format as the second format. If this time stamp format cannot be found in keyword arguments, it will default to being `"[%Y-%m-%d %H:%M:%S]"`

*class* log.**channelLogger(logging.Logger)**

* channelLogger.**log**(*self*, *nick*, *msg*)<br>
Formats *msg* according to a keyword argument supplied to it at creation time (`messageFormat`), or defaults to "`<%(nick)s> %(msg)s`". The format here is supplied a dict, with *nick* and *msg* as keys. The final formatted message is logged to the `channelLogger` object under level `logging.INFO` by use of `logging.Logger`'s `info()` method.

#### ircLogManager objects
This object is created by a bot to spawn and manage logging to all channel logs, as well as logging data sent and received to and from the socket. At creation time, it will prepare logging directories and spawn necessary the socket-related logs. Logging to channels will create logging objects on an as-needed basis.

*class* log.**ircLogManager**()

* ircLogManager.**prepareDirs**(*self*)<br>
Ensures that all directories for logging are present before logs are created. If they are not present, it will attempt to create them with `os.makedirs()`


* ircLogManager.**prepareLogs**(*self*)<br>
Spawns two `log.basicLogger` objects. One for logging messages sent out of the socket, and another for logging data received coming from the socket.


* ircLogManager.**channelLog**(*self*, *channel*, *line*)<br>
Will attempt to find an existing logging object in a dictionary of channel logs under the key supplied with *channel*. If a value for this key cannot be found, a log will be created and added to this key as it's value. It will then attempt to parse *line* by setting an internal variable `nick` to ` line[0][1:].split('!')[0]` and an internal variable `message` to `' '.join(line[3:])[1:]`. If this parsing raises any exceptions, they will be caught and the traceback printed to `sys.stderr`. Otherwise, it will log to the channel log object, passing `nick` and `message` as arguments.