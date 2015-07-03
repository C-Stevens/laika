from src.argument import *

def run(self, **kwargs):
	message = kwargs.get('msg')
	channel = kwargs.get('channel')
	if channel:
		self.socket.sendToChannel(channel, message)
	else:
		self.socket.sendToChannel(self.commandData.channel, message)

config = {
	'name' : 'Echo',
	'command_str' : 'echo',
	'args' : [Argument(type=Type.channel, optional=True, name="channel"),
		Argument(type=Type.msg, optional=False, name="msg")],
	'auth' : False,
	'help' : "Repeats input back into the origin channel, or into a specified channel if given."
}