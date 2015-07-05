from src.argument import *

def run(self, **kwargs):
	self.socket.channelMode(self.commandData.channel, "+b", kwargs.get('banmask'))

config = {
	'name' : 'Ban',
	'command_str' : 'ban',
	'args' : [Argument(type=Type.msg, optional=True, name="banmask")],
	'auth' : True,
	'help' : "Applies a +b mode to the specified mask but does not kick the user from the channel."
}