# `command.py` Documentation

### Introduction
This file holds the objects and methods involved with spawning, managing, verifying, and running command files. 

### Objects
#### commandError objects
This object is inherited from `Exception`. It's a basic exception class used for raising errors while preparing to run a command. If supplied a *msg* string, the string will be printed when cast as `str`.

*class* command.**commandError**(Exception)

* commandError.**`__str__`**(*self*)<br>
Returns `self.msg` to provide a method for accessing the exception details through `str` casting.



#### commandManager objects
This object is created by the main bot object to serve as the point of contact for spawning and running command threads. This object is provided with the bot's list of auth users (`self.authList`), a complete set of loaded commands (`self.commandList`), and the logging object used by the bot for bot logging (`self.log`). It does not have direct access to it's parents methods.

Users and their threadpools are kept managed in `self.threadPools`. This list is volatile and is clean every time the bots is initialized.

*class* command.**commandManager**()

* commandManager.**spawnThread**(*self*, *commandData*, *socket*)<br>
Will first run the command contained in the *commandData* object against all loaded commands. If a match is found, and either the user value found in the *commandData* object is found to be in the list of valid users, or the command's `auth` value is `False`, the manager will proceed. Otherwise it will issue an IRC socket notice to the command issuer of:
> You are not authorized to use the **`<command attempted>`**  command.

If the command failed the initial matching check against all loaded commands, the following IRC notice will be sent to the command issuer:
> Command **`<command attempted>`** not found

And a list of all loaded commands will be sent to the same user in an IRC notice.

Otherwise, the manager will then create a thread pool for the user based on the user's hostname (to avoid the user changing nickname to get a fresh thread pool in a spamming attack) if no thread pool exists, and attempt to add a `command.commandThread()` object to this user's pool. If the user's thread pool is at maximum size (by default, `5`), the command will not be run and the method will exit.


* commandManager.**userThreadCount**(*self*, *user*)<br>
Attempts to return the number of running threads in *user*'s thread pool. If a `KeyError` exception is raised due to a *user* that is not in the master thread pool dict, `None` will be returned.


* commandManager.**reportThreads**(*self*, *user*)<br>
Attempts to return a list of active threads for *user*. if a `KeyError` exception is raised due to a *user* that is not in the master thread pool dict, `None` will be returned.


* commandManager.**removeThread**(*self*, *thread*, *user*)<br>
Removes *thread* from *user*'s thread pool.



#### commandThread objects
This object is what is created by the commands themselves and how the command author interacts with the regex matching methods in `command.py`. 

This object takes three arguments: *type* (an `argument.Type` enum), *optional* (a boolean), and *name* (a string).

*class* command.**commandThread**(threading.Thread)

* commandThread.**validateArgs**(*self*, *args*, *commandArgs*)<br>
Will first ensure that the command was provided at least as many arguments as there are required arguments. If not, this method will raise a `command.commandError` exception. Otherwise, the method will begin to form a complete regex match string for the entire list of command arguments. If the application of the regex onto the `args` string stored in the object's `command.commandData()` object produces no matches and matches are expected from the command, a `command.commandError` exception will be raised. Otherwise, returns a dict of match groups.


* commandThread.**createUsage**(*self*, *command*)<br>
Returns a formatted usage string, prefixed with "`Usage ([optoinal], <required>):`".


* commandThread.**argList**(*self*, *args*)<br>
Returns a list of all command arguments by invoking their `describe()` method.


* commandThread.**run**(*self*)<br>
Validates arguments and receives a match dict from the `validateArgs()` method, and will attempt to pass this dict to the command's `run()` function. After `run()` returns to the object, the thread will remove itself from the thread pool by invoking it's parent method `removeThread()`.

If any `command.commandError` exceptions are raised during the above process, a notice of the failure will be sent to the command issuer with an IRC notice containing command-specific details of the nature of the failure. If the exception is not a `command.commandError` exception, the exception and traceback will be logged to the bot's log, and the command issuer will be sent an IRC notice that a general critical failure in the command has occurred.



#### commandData objects
This object is nothing more than a container object to hold various parsed data from the `bot.py` main bot object. This object is passed to the `command.commandManager()` object for use.

*class* command.**commandData**()

commandData objects store the following variables:
* `identd` : Boolean value. `True` if the user has "`!`" in their hostname, `False` if "`!~`".
* `botnick` : String value. The `nick` value from the bot's configuration file is stored here.
* `nick` : String value. This is the nickname of the command issuer.
* `user` : String value. This is the user value of the command issuer.
* `hostname` : String value. The hostname of the command issuer.
* `channel` : String value. The channel the command was issued from.
* `command` : String value. The command attempting to be issued.
* `highlightChar` : String value. The prefix used before the command.
* `msgType` : String value. The message type from the IRC server, usually "`PRIVMSG`".
* `args` : String value. This is the complete message after the command.


* commandData.**printData**(*self*)<br>
Prints all object variables. Can be useful for debugging from inside a command file.


