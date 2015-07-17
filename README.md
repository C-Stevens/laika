#Laika
Laika is an extensible bot written in Python for the IRC protocol. Laika is principled upon concurrency, threading, ease of use, and easy command writing.

#####Table of Contents
* [Quickstart](#quickstart)
* [Configuration](#configuration)
    * [Laika.cfg](#laikacfg)
        * [Configuration values](#configuration-values)
        * [Example configuration](#example-configuration)
    * [Bot configurations](#bot-configurations)
        * [Configuration values](#configuration-values-1)
        * [Example configuration](#example-configuration-1)
* [Command Line Arguments](#command-line-arguments)
    * [Notable arguments](#some-notable-arguments)
* [Modules](#modules)
* [Writing Commands](#writing-commands)
    * [Configuration values](#configuration-values-2)
    * [Example configuration dict](#example-configuration-dict)
    * [What commands have access to](#what-commands-have-access-to)
    * [Potential behaviors](#potential-behaviors)
        * [Thread pool maxed](#thread-pool-maxed)
        * [User not authorized](#user-not-authorized)
        * [CommandError: No arguments supplied](#commanderror-no-arguments-supplied)
        * [CommandError: Arguments supplied when none requested](#commanderror-arguments-supplied-when-none-requested)
        * [CommandError: Regex matching failed](#commanderror-regex-matching-failed)
* [Help](#help)
* [License](#license)
* [Version and Changelog](#version-and-changelog)
* [Author](#author)
* [TODO](#todo)

##Quickstart
Laika makes use of the [`pyyaml`](https://github.com/yaml/pyyaml) library as a git submodule. As such, git needs to be supplied the `recursive` flag to ensure proper configuration file loading.
To get started, first clone the repository:
```Bash
$ git clone --recursive git@github.com:C-Stevens/laika.git && cd laika/
```
Copy configuration templates:
```Bash
$ cp ./laika.cfg.template ./laika.cfg && cp ./config/example_config.yaml.example ./config/<bot config filename>.yaml
```
Add appropriate values:
```Bash
$ $EDITOR ./laika.cfg
$ $EDITOR ./config/<bot config filename>.yaml
```
Start laika:
```Bash
$ python ./laika.py
```
For arguments, reference the [command line arguments](#command-line-arguments) section.

If python is raising syntax related errors on first-run, ensure your python version is at least version `3.4.3`.


##Configuration
Laika uses one configuration file for itself to set up how the program logs messages, and any number of bot configuration files for starting bot objects.

**NOTE:** While filling config files, keep in mind that yaml will treat `None` as a string ('None'), and not as python's `NoneType`. To specify `None`, use either `null`, or leave the value blank.
####Laika.cfg
This configuration file is used to specify how the program will log various messages. The values here do **not** affect how bot objects themselves will log messages.

An alternate or explicit config file can be specified with the `--config` argument (For more information of command arguments, see the [argument section](#Command-Line-Arguments)), so long as it is parseable by [`pyyaml`](https://github.com/yaml/pyyaml). If an alternate configuration file is not supplied at run time, Laika will look for a `laika.cfg` file in the current directory ('.'). This means it will search for whatever the current shell directory is for a `laika.cfg` file, not necessarily the Laika project directory. 


######Configuration values:
* `defaultFormat`: This is the default logging format log levels will use if not explicitly provided with any of the below log format options. By default, this is `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
* `critLog`: Boolean option to enable or disable logging for critical messages. Defaults to `True`.
* `critLogDir`: Specifies a directory to log critical messages to. If `null` or left blank, it will default to send messages to the terminal.
* `critLogFormat`: Specifies an explicit logging format for critical messages. For more information on logging formats, view the [log.py documentation](doc/log.py.md), and python's [logging documentation](https://docs.python.org/3.4/howto/logging-cookbook.html#use-of-alternative-formatting-styles).
* `errLog`: Boolean option to enable or disable logging for error messages. Defaults to `True`.
* `errLogDir`: Specifies a directory to log error messages to. If `null` or left blank, it will default to send messages to the terminal.
* `errLogFormat`: Specifies an explicit logging format for error messages. For more information on logging formats, view the [log.py documentation](doc/log.py.md), and python's [logging documentation](https://docs.python.org/3.4/howto/logging-cookbook.html#use-of-alternative-formatting-styles).
* `warnLog`: Boolean option to enable or disable logging for warning messages. Defaults to `True`.
* `warnLogDir`: Specifies a directory to log warning messages to. If `null` or left blank, it will default to send messages to the terminal.
* `warnLogFormat`: Specifies an explicit logging format for warning messages. For more information on logging formats, view the [log.py documentation](doc/log.py.md), and python's [logging documentation](https://docs.python.org/3.4/howto/logging-cookbook.html#use-of-alternative-formatting-styles).
* `infoLog`: Boolean option to enable or disable logging for info messages. Defaults to `False`.
* `infoLogDir`: Specifies a directory to log info messages to. If `null` or left blank, it will default to send messages to the terminal.
* `infoLogFormat`: Specifies an explicit logging format for info messages. For more information on logging formats, view the [log.py documentation](doc/log.py.md), and python's [logging documentation](https://docs.python.org/3.4/howto/logging-cookbook.html#use-of-alternative-formatting-styles).
* `debugLog`: Boolean option to enable or disable logging for debug messages. Defaults to `False`.
* `debugLogDir`: Specifies a directory to log debug messages to. If `null` or left blank, it will default to send messages to the terminal.
* `debugLogFormat`: Specifies an explicit logging format for debug messages. For more information on logging formats, view the [log.py documentation](doc/log.py.md), and python's [logging documentation](https://docs.python.org/3.4/howto/logging-cookbook.html#use-of-alternative-formatting-styles).

######Example configuration:
```yaml
defaultFormat   : "%(message)s"
critLog         : True
critLogDir      : 
critLogFormat   : "CRITICAL - %(message)s"
errLog          : True
errLogDir       : /var/log/Laika/errors
errLogFormat    :
warnLog         : False
warnLogDir      : 
warnLogFormat   : 
infoLog         : True
infoLogDir      : 
infoLogFormat   :
debugLog        : True
debugLogDir     : 
debugLogFormat  : "[%(levelname)s] %(message)s"
```

####Bot configurations
Laika will load a theoretically infinite number of valid configuration files from inside `[...]/laika/config` and will load each as a separate bot object on an individual thread.

For a bot to be loaded, the configuration file must be parseable by [`pyyaml`](https://github.com/yaml/pyyaml), be located in `[...]/laika/config/`, and end with a `.yaml` extension.

Unlike Laika's program logging and the various levels of bot logging, bot objects are allowed to log in any number of locations at the same time. Logging details are supplied as sections under the `ircLog` section. Each section will configure a [`log.ircLogGroup()` object](doc/log.py.md) and be sent relevant logging data.

######Configuration values:
* `server` : This section specifies how the bot will connect with the IRC server.
    * `host` : The URL or IP address to the IRC server.
    * `port` : The port on which to connect.
    * `ssl` : Boolean to enable or disable wrapping the socket connection in an SSL layer for connecting to IRC servers over SSL. If set to something other than `True` or `False`, it will default to `False`. 
    * `pass` : If provided, the bot will pass this password value to the IRC server while connecting. **THIS PASSWORD IS NOT OBFUSCATED AND WILL REMAIN IN PLAINTEXT**. Additionally, if you are not connecting over an SSL connection to the IRC server, this password will also be sent to the server in plaintext.
* `nick` : The nick/nickname the bot will use.
* `nickPass` : If not `null` or blank, this password will be sent to NickServ (NickServ!NickServ@services) for nickname authentification if the bot is sent an IRC notice about needing to authenticate.
* `nickServiceIdent` : This is the ident of the IRC network's nickname service manager and is used to determine if the bot is being queried for nickname-specific information. If `null` or left blank, this will default to freenode's NickServ ident of "`NickServ!NickServ@services`".
* `nickAuthMsg` : This is the string that will be sent by the `nickServiceIdent` service user to notify the bot that they need to authenticate their nickname. If `null` or left blank, the bot will attempt to authenticate with the `nickServiceIdent` service user every time they are sent a notice by it. For freenode servers, this should be set to "`This nickname is registered.`".
* `ident` : The ident the bot will use. If unsure what to set this to, use the `nick` value here again.
* `userMode` : Bot's user mode sent to the IRC server during initial connection. If unsure what to set this to, set it to `8`.
* `channels` : List of channels that the bot will attempt to join after successful connection. This uses yaml's list/array syntax, so each channel should be listed on an individual line, indented, and prefixed with a dash (-). Additional channels can be joined/left after initial launch with the core [join](commands/join.py) and [part](commands/part.py) commands.
* `highLightPrefix` : Prefix used for recognizing commands. It's safer to explicitly wrap this value in quotes to avoid yaml attempting to parse certain characters as yaml-specific code (for example, `'!'` as opposed to `!`).
* `authList` : A list of users who will be allowed to use commands that have the `auth` value in their config dict set to `True`. This, like `channels`, uses yaml's list/array syntax.
* `threadPoolSize` : Defines the maximum number of running command threads a user can have at once. If `null` or left blank, this value will default to `5`.
* `botLog` : These values specify how the bot will handle logging it's own messages. These values share the documentation and syntax of the above values listed under [Laika.cfg](#laikacfg) configuration section. If you don't wish to bother with these, they can safely all be left blank or `null` and they will use defaults.
* `ircLog` : This section holds log specifications for how the bot will handle logging for messages sent and received through the socket, as well as IRC channel messages.
    * `botLogName` : This value serves as the default logging folder. If `null` or left blank, will default to value supplied for `nick`.
    * `logRoot` : Specifies an explicit path for all logging. `botLogName` is appended to this path to form the complete log root.
    * `serverLogFile` : Name of the log that records all messages received from the IRC server, with the path "`logRoot`/`botLogName`/`serverLogFile`". If `null` or left blank, will default to `server_log.log`.
    * `socketLogFile` : Name of the log that records all messages sent to the IRC server, with the path "`logRoot`/`botLogName`/`socketLogFile`". If `null` or left blank, will default to `socket_log.log`.
    * `channelLogPath` : Path to all channel logs. This path can be independent of the log root used for the above socket and server logs. if `null` or left blank, will default to "`logRoot`/`botLogName`/channel_log/". If an absolute path is not supplied for this value, the path will be assumed to have root in the Laika project directory.
    * `timeStampFormat` : How timestamps will appear in channel logs. This can either be a raw string and function as a prefix, or you can supply [`strftime` formats](https://docs.python.org/3.4/library/time.html#time.strftime). It's safer to wrap this value in quotes so yaml does not attempt to parse any characters (`%`, for example) as yaml-specific. If `null` or left blank, will default to `[%Y-%m-%d %H:%M:%S]`.
    * `messageFormat` : How messages will appear after the `timeStampFormat` prefix. values for nickname and message are passed to this string, if you so wish to use them. If `null` or left blank, will default to `<%(nick)s> %(msg)s`. 

######Example configuration:
```yaml
server:
        host : irc.example.net
        port : 6667
        ssl  : False
        pass : my_super_secret_password
nick : Laika
nickPass : null
nickServiceIdent : 
nickAuthMsg : "This nickname is registered."
ident : Laika
userMode : 8
channels:
        - '#foo'
        - '&bar'
highlightPrefix : 'Laika, would you kindly '
authList:
        - GeorgeWashington
        - Abraham_Lincoln
threadPoolSize: 12
botLog:
        defaultFormat   : "%(asctime)s - Laika - %(levelname)s - %(message)s"
        critLog         : 
        critLogPath     : 
        critLogFormat   : 
        errLog          : 
        errLogPath      : 
        errLogFormat    : 
        warnLog         : 
        warnLogPath     : 
        warnLogFormat   : 
        infoLog         : True
        infoLogPath     : /home/laika/irc/infoLogs
        infoLogFormat   : "%(message)s"
        debugLog        : 
        debugLogPath    : 
        debugLogFormat  : 
ircLog:
        log0:
                botLogName      : Laika
                logRoot         : /var/log/irc/
                serverLogFile   : serv-sock.log
                socketLogFile   : serv-sock.log
                channelLogDir   : /usr/share/Laika/chanlog
                timeStampFormat : "At %H:%M:%S on %Y-%m-%d,"
                messageFormat   : "%(nick)s said this: %(msg)s"
        log1:
                botLogName      : Laika
                logRoot         : /home/laika
                serverLogFile   : socket_log.txt
                socketLogFile   : server_log.log
                channelLogPath  : null
                timeStampFormat : null
                messageFormat   : null

```


##Command Line Arguments
Laika can accept a small handful of command line arguments, and the complete set of program logging values can be replaced with command line arguments. If a command line argument is specified that also exists in a loaded configuration file, the command line argument will be given precedence and replace the value when creating the program logs.

It should be noted that Laika requires loading a *full* config file, even if all values are replaced by command line arguments. This can either be the default `laika.cfg` file or a file specified with the `--config` argument.

Laika has a built in help flag which can print complete usage information by supppplying the `-h` or `--help` flags.

######Some notable arguments
* `--version` : Prints program version information and exits.
* `-q`,`--quiet` : Will override both config file values and supplied values from arguments and force all program logs to be silent. This does *not* apply to logging done by individual bots or their objects.
* `--config` : A full path to an alternate program config file. This will act as the loaded configuration file in lieu of the default `laika.cfg`. The same precedence and replacement rules of supplied command line config values still apply to configuration files supplied with this argument.
* `--critLog`, `--errLog`, `--warnLog`, `--infoLog`, `--debugLog` : These are boolean flags that must be explicitly be set to a case insensitive `'True'`, `'t'`, `'yes'`, or `1` for `True` and likewise `'False'`,`'f'`,`'no'`, or `0` for `False`. If something other than these values is supplied, these flags will be silently ignored.

##Modules
Laika cannot cleanly implement every feature a bot operator might want. In order to keep the source code for Laika sane but also allow even more freedom for bot operators to implement their own features and functionality, Laika comes with a modules feature. Modules are `.py` files loaded from inside `./modules` that are spawned on their own individual threads, and provided with the following objects as arguments:
* The bot's IRC logging manager, a `log.ircLogManager` object.
* The bot's logging object, a `log.logger` object.
* The bot's `irc.socketConnection` object.
* The bot's command manager, a `command.commandManager` object.

The only stipulation expected from module files is that they have a `run()` function that is able to receive these above arguments, which most likely will look like this:
```python
def run(*args):
```

##Writing Commands
Laika was designed from the start to make writing commands quick and easy. All `.py` files located in `[...]/laika/commands` are loaded as commands at launch time, so adding or removing a command requires a restart of the bot.

For more information about how the command objects behave and function, refer to command.py's [documentation()](doc/command.py.md).

Commands require only two things, a `run()` function with the following signature:
```python
def run(self, **kwargs):
```
and the following configuration dictionary:
```python
config = {
    'name' : '',
    'command_str' : '',
    'args' : [],
    'auth' : ,
    'help : ''
}
```
######Configuration values:
* `name` : This is the user-friendly name of the command that appears on generated help usage for the command.
* `command_str` : A string used to identify if the command is being called or not.
* `args` : Custom type Arguments used to regex match various string types. More information about these arguments is mentioned later, and also in [argument.py's documentation](doc/argument.py.md).
* `auth` : Boolean value to indicate whether or not the command issuer needs to be in the `authlist` list to run the command. The command will not run if this is set to `False`, and the user is not in the `authList` list.
* `help` : General information about what the command does and/or how it functions. This is used in generated help usage for the command.

######Example Configuration Dict:
```python
config = {
	'name' : 'Echo',
	'command_str' : 'echo',
	'args' : [Argument(type=Type.channel, optional=True, name="channel"),
		      Argument(type=Type.msg, optional=False, name="msg")],
	'auth' : False,
    'help' : "Repeats input back into the origin channel, or into a specified channel if given."
}
```

Other than the above `run()` function and the `config` dict, command authors are given a large amount of freedom in their command writing. There is no timeout limit to commands, and you are free to write any number of classes, functions, and import any libraries you wish.

For interacting with the socket and with the IRC server, it's recommended to become very familiar with the functions and methods found in [irc.py's documentation](doc/irc.py.md).

#####What Commands Have Access to
Commands themselves are not objects, but their `run()` function is called directly from a thread object. As such, the command file, through `run()` has access to a number of bot objects through its parent.

* `self.socket` : Allows access to any of `irc.py`'s [functions](doc/irc.py.md).
* `self.command` : A module object for the command being issued (if accessed from inside a command, this is itself).
* `self.commandData` : A [`commandData()`](doc/command.py.md) object full of command-specific parsed data.
* `self.parent` : A method of accessing the command thread's parent, the [`commandManager()`](doc/command.py.md) object. Through this, values and methods under the `commandManager()` object can be accessed.
* Any methods in the [`commandThread`](doc/command.py.md) object are accessible as well.

#####Arguments
Laika comes with a sophisticated set of custom argument data types that use regex to validate and match data specified after the command when it's issued.
These arguments are detailed in [argument.py's documentation](doc/argument.py.md), but below will serve as a general guide to using them.

If you wish to utilize Laika's argument matching, you must import the argument type library with:
```python
from src.argument import *
```
Having done this, you can now specify arguments in the `args` field of the config by supplying (in order) the argument types you expect to receive. 
This is done by supplying `Argument()` objects in an array for the value of `args` in the `config` dict.

A quick explanation of `Argument()` object arguments:
* `type` : Where you specify what kind of match you are expecting. For a list of all custom argument types, refer to `argument.py`'s [documentation](doc/argument.py.md).
* `optional` : Boolean value to indicate whether or not the argument is optional. If `True`, the command will fail to run if a valid match for this argument cannot be found.
* `name` : If a valid match is found for this argument, the match will be supplied to the command under this dictionary key in `**kwargs`.

From the supplied argument types, a regex matching string will be created and applied to the string after the command. (for example, if a user issues `!echo foo bar baz` (assuming `!` is the `highlightChar`), the regex match will be applied to `'foo bar baz'`).

Regex match groups to individual arguments will be returned to the command as keyword arguments, under the name specified by the `name` option in the `Argument()` object.

To illustrate:
in the above `echo.py` configuration, a valid match for a channel name would be returned as `channel: <matched channel>` and a valid matched message would be returned as `msg: <matched message>` in keyword arguments to the command. These values can then be accessed just like any other python keyword arguments.

If you don't wish to use Laika's custom argument types, you can specify a single argument of type `msg`. Everything after the command will match to this argument, and the entire string will be returned to the command. From there, you can parse this string however you wish.

#####Potential Behaviors
Each command is spawned on its own thread and will run concurrently alongside other command threads if more than one command is issued or running at the same time. There is no timeout for how long commands can exist, but each IRC user is given a thread pool max size of `5` by default, or can be configured with the `threadPoolSize` value in a bot's configuration file. If your command fatally crashes and raises an exception, the thread and command will die, but be removed from the thread pool. However, if your command results in an infinite loop that will never exit, fatally or otherwise, the thread will remain in the user's thread pool until the bot is restarted. As of version 1.1, the number of running commands can be queried with the [`runningcommands`](commands/runningcommands.py) command, and a user's thread pool can be cleared by users who are in the `authList` list with the [`flushcommands`](commads/flushcommands.py) command.

More details on how commands are spawned and how the thread pool is managed can be found in `command.py`'s [documentation](doc/command.py.md).

When a command attempts to run, several outcomes are possible. These outcomes usually have some kind of log message or built in notification with an IRC notice, but are listed below for the sake of documentation.

######Thread Pool Maxed
If a user attempts to issue a command while they currently have the maximum number of allowed command threads running at one time (By default: `5`), the command will be refused and the user will be issued the following IRC notice:

> Maximum number of pending commands (`<thread pool size>`) reached. Command `<name of command attempted>` has been ignored.

Additionally, the bot operator is made aware that a user has filled their thread pool and been denied running a command with the following message:

> User `<thread pool owner>` has filled their command queue and has been denied a command request

This log message is of level `warning`.

######User Not Authorized
If a user attempts to issue a command that has the `auth` value in the command's `config` dict set to `True` and their nickname is not in the `authList` list, the command will be refused and the user will be issued the following IRC notice:

> You are not authorized to use the `<name of command attempted>` command

This message is not logged anywhere else.

######CommandError: No Arguments Supplied
If the `args` key in a command's `config` dict is non-empty but no *non-optional* arguments were passed to the command, it will raise a `commandError` with the following detail string:

> Command requested arguments but received none.

######CommandError: Arguments Supplied When None Requested
If the `args` key in a command's `config` dict is empty but the command was supplied with arguments, it will raise a `commandError` with the following detail string:

> Command requested no arguments but arguments were received.

######CommandError: Regex Matching Failed
If the result of the regex match applied to the arguments results in `None` and the command expected at least one non-optional argument to match, it will raise a `commandError` with the following detail string:

> Command failed to match arguments.

In the case of all the above `commandError` behaviors, the command issuer will be sent an IRC notice with a message concerning "Invalid syntax", the `commandError` detail string, and a generated usage for the attempted command.

In the event a command raises an exception other than `commandError`, its name and traceback will be logged, and the command issuer will be sent the following IRC notice:

> Command `<name of attempted command>` has critically failed. See logs for more information

In this event, the command thread is removed from the thread pool and the thread exits.

##Help
For more information and documentation, you can view complete documentation for most of Laika's files in the [doc](doc) folder.

For command specific help, Laika comes prepackaged with a [help command](commands/help.py), which can be used to generate help and usage information for commands. This functionality is only available while interacting with the bot through IRC.


##License
For licensing information, refer to the [LICENSE](LICENSE) file.


##Version and Changelog
Version information for the current release, and a changelog is available in the [version](_version.py) file.


##Author
Laika was written by Colin Stevens.

I can be reached at [mail@colinjstevens.com](mailto:mail@colinjstevens.com)


##TODO
* ~~Variable length `highlightChar` prefix.~~
* Make `readQueue()` function useful.
* ~~Flush command to empty command thread pool.~~
* ~~Config value to set thread pool size.~~
* ~~Add module functionality.~~
* ~~Make NickServ ident configurable to allow use on non-freenode servers.~~
