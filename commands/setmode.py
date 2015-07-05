from src.argument import *

def run(self, **kwargs):
	self.socket.userMode(self.commandData.botnick, kwargs.get('modes'))

config = {
	'name' : 'Set Mode',
	'command_str' : 'setmode',
	'args' : [Argument(type=Type.usermode, optional=True, name="modes"),],
	'auth' : True,
	'help' : "Sets the specified user modes for the bot."
}