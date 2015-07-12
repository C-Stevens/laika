# `irc.py` Documentation

### Introduction
This file holds objects and methods related to sending messages out of the socket to the IRC server.

### Objects
#### socketConnection objects
This object and its methods serves as the bot's point of contact for sending things out of the socket and for utilizing various IRC-specific functionality.

*class* irc.**socketConnection**()

* socketConnection.**readFromSocket**(*self*)<br>
Attempts to return data received from the socket. a `socket.timeout` exception is caught, a message of the socket timing out will be logged to the bot's error log under log level `logging.ERROR`, and `runState` will be set to `False` to trigger socket termination.

* socketConnection.**buildMessageQueue**(*self*)<br>
Creates a message queue and adds messages received from the `socketConnection.readFromSocket()` method to the queue. If an existing queue is found, the messages will be added to that queue instead. This method will check if the last message in the queue was an incomplete message. If this is the case, the first line will be appended to this incomplete message queue instead of being separately added to the queue. This checking ensures that even if all the socket data is not delivered in a single call of `socketConnection.readFromSocket()`, all messages will be completed by the time they are parsed by the bot. If no incomplete line is found, lines received from the socket will be individually added to the queue. 


* socketConnection.**readQueue**(*self*)<br>
Safely assembles an array of items currently in the queue of received messages without popping any of the messages off the queue.

* socketConnection.**connect**(*self*, *host*, *port*, *nick*, *ident*, *userMode*[, *serverPass*])<br>
Attempts to establish and IRC connection by issuing `PASS`, `NICK`, and `USER` commands to the server after the socket is connected.


* socketConnection.**socketShutdown**(*self*)<br>
Safely issues a socket shutdown and close by passing `socket.SHUT_WR` and an argument to the socket's `shutdown()` method, as well as invoking the socket's `close()` method.


* socketConnection.**pong**(*self*, *host*)<br>
Issues a `PONG` to *host*.


* socketConnection.**joinChannels**(*self*, *channels*)<br>
If *channels* is an array (type `list`), it will individually issue `JOIN` commands for each item in the array. Otherwise (type `str`), it will issue just a single `JOIN` command.


* socketConnection.**partChannels**(*self*, *channel*[, *message*])<br>
Issues a `PART` command for *channel*, including a part message string, if supplied in *message*.


* socketConnection.**sendToChannel**(*self*, *channel*, *message*)<br>
Sends *message* to the specified *channel* with a `PRIVMSG` command.


* socketConnection.**quit**(*self*[, *message*)<br>
Disconnects from an IRC server with a `QUIT` command, including a quit string, if supplied in *message*.


* socketConnection.**kick**(*self*, *user*, *channel*[, *message*])<br>
Kicks *user* from *channel* with a `KICK` command, including a kick reason string, if supplied in *message*.


* socketConnection.**topic**(*self*, *channel*, *topic*)<br>
Sets the topic in *channel* to the string provided in *topic* with a `TOPIC` command.


* socketConnection.**userMode**(*self*, *user*, *mode*)<br>
Applies the specified modes in *mode* to *user* by issuing a `MODE` command.


* socketConnection.**channelMode**(*self*, *channel*, *modes*[, *extraArgs*])<br>
Applies the specified modes in *mode* to the channel specified in *channel*, with *extraArgs* appended to the command for data such as the user mask when setting a `+/- b` mode.


* socketConnection.**invite**(*self*, *nick*, *channel*)<br>
Invites the specified nick in *nick* to a particular channel given in *channel* with the `INVITE` command.


* socketConnection.**time**(*self*[, *server*])<br>
Issues a `TIME` command to the server the bot is connected to, or a specific server if given in *server*.


* socketConnection.**nick**(*self*, *nick*)<br>
Issues a `NICK` command to set the bot's nickname to the nickname supplied in *nick*.


* socketConnection.**nsIdentify**(*self*, *nick*, *password*[, *waitForMask*])<br>
Attempts to identify the bot's nickname with NickServ by issuing a `NS IDENTIFY` command with the supplied *nick* and *password*. if *waitForMask* is `True`, the method will loop and not return until it detects the string `"is now your hidden host (set by services.)"` in an IRC notice.

* socketConnection.**action**(*self*, *channel*, *action*)<br>
Issues a `PRIVMSG` to the channel given in *channel* with the *action* string wrapped in `\u0001ACTION` and `\u0001` to form a CTCP ACTION command.


* socketConnection.**notice**(*self*, *nick*, *message*)<br>
Issues a `NOTICE` command to *nick* with the message string supplied in *message*.

#### socketQueue objects
This object is created by the `irc.socketConnection` object to serve as its only point of exit for messages going outbound to the socket. Through this architecture, there is no risk of collisions of methods sending data out of the socket at the same time.

At spawn time, this object will create a `queue.Queue()` queuing object, then creating a thread with a target set to it's `flushQueue()` method. This thread is called `"socket_queueWorker"`.

*class* irc.**socketQueue**()

* socketQueue.**addToQueue**(*self*, *message*)<br>
Puts *message* onto the object's socket queue.


* socketQueue.**flushQueue**(*self*)<br>
Enters a loop, terminated if it's parent `irc.socketConnection.runState` boolean is set to `False`, at which point it will attempt to send all messages in it's socket queue out of the socket with the `send()` method of the socket. Messages sent out of the socket are first explicitly encoded with `utf-8` encoding. Items sent out of the socket are logged to the bot's socket log. If the socket loop terminates, this method will automatically shut down the socket connection by way of the `irc.socketConnection.socketShutdown()` method.