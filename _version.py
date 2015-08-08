__version__ = "Laika v1.2"
'''
Changelog
---------
Version 1.0
	* Initial full version release
Version 1.1
	* Removed "wait for mask" functionality.
	* Added support for multiple IRC logging locations for bots.
	* Fixed configuration values from "Dir" to "Path" or vise versa to improve clarity.
	* Made command thread pool size user-configurable.
	* Added runningcommands and flushcommands commands.
	* Change highlightChar to highlightPrefix and created functionality for entire strings to prefix commands.
Version 1.2
	* Added indication of command auth requirements in help command.
	* Added module functionality.
	* Made NickServ service user information configurable to allow use on non-freenode servers.
	* Forced utf-8 unicode encoding in channel logs to avoid ASCII failing to decode IRC control codes.
'''
