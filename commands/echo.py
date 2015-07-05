from src.argument import *

def run(self, **kwargs):
	self.socket.sendToChannel(kwargs.get('channel') or self.commandData.channel, kwargs.get('msg'))

config = {
	'name' : 'Echo',
	'command_str' : 'echo',
	'args' : [Argument(type=Type.channel, optional=True, name="channel"),
		Argument(type=Type.msg, optional=False, name="msg")],
	'auth' : False,
	'help' : "Repeats input back into the origin channel, or into a specified channel if given."
}