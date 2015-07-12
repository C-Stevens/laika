# `bot.py` Documentation

### Introduction
This file holds the objects and methods involved with the creation and management of logs, both for Laika, loaded bots, as well as every loaded bot's server, socket, and channel logs.

### Objects
#### bot objects
This object is the main object for each loaded bot. It handles the creation of all additional objects not supplied or created by Laika at program launch, and serves as a driver for

*class* bot.**bot**()

* bot.**loadConfig**(*self*, *config*)<br>
Loads expected values from expected keys from *config* into local variables. *config* is expected to be a dict, typically `yaml` parsed data files.


* bot.**load_commands**(*self*)<br>
Loads all files in `../laika/commands/` that end in `.py` as python modules. If there is an error while importing with `imp`, the exception will be caught and logged to the bot error log with level `logging.ERROR`. This method also will log a list of loaded modules to the debug log with level `logging.DEBUG`.


* bot.**parse**(*self*, *line*)<br>
Splits *line* on `' '` and determines the type of message from the IRC server that it is. if `line[1]` is `"PRIVMSG"`, the line will be logged as a channel message but sending it to the bot's `log.ircLogManager` object. If this `PRIVMSG` is found to start with the value in `self.highlightChar`, it is further parsed and expected to be a command. A `command.commandData()` object is filled with parsed data from *line* , and this object is sent to the bot's `command.commandManager.spawnThread()` method. If any exceptions are raised during parsing at this step, the exception and the line will be logged to the bot's error log under log level `logging.ERROR`.<br>
If `line[1]` is not `"PRIVMSG"`, the line is assumed to be some sort of data from the IRC server itself, and is logged to the bot's `log.ircLogManager.serverLog()` method. If `line[0]` is `"PING"`, the bot will issue a PONG with the `irc.socketConnection.pong()` method. If `line[1]` is `"NOTICE"`, an additional check is done to see if the notice is from NickServ. If this is found to be true, and the notice contains the string `"This nickname is registered."`, the bot will attempt to authenticate with NickServ by use of the `irc.socketConnection.nsIdentify()` method. The bot will also log a message of its attempt to authenticate to the bot log under logging level of `logging.INFO`.


* bot.**run**(*self*)<br>
This is the main driver and looping function of the bot object. When invoked, it will load commands, connect to the IRC server with the `irc.socketConnection.connect()` method, attempt to authenticate with NickServ early if there is a value stored in `self.nickPass` (loaded from the `bot.loadConfig()` method) with the `irc.socketConnection.nsIdentify()` method, join channels with the `irc.socketConnection.joinChannels()` method, then enter a run loop. This loop is terminated if the bot's socket object boolean (`irc.socketConnection.runState`) is `False`. While in the loop, the bot will request a message queue from the socket object with the `irc.socketConnection.buildMessageQueue()` method, and send all lines from the queue that are not `' '` to the `bot.parse()` method. These lines are additionally logged to the bot log with log level `logging.INFO`.

