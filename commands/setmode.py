from src.argument import *

def run(self, **kwargs):
	modes = kwargs.get('modes')
	self.socket.userMode(self.commandData.botnick, modes)

config = {
	'name' : 'Set Mode',
	'command_str' : 'setmode',
	'args' : [Argument(type=Type.usermode, optional=True, name="modes"),],
	'auth' : True,
	'help' : "Sets the specified user modes for the bot."
}