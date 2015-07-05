from src.argument import *

def run(self, **kwargs):
	self.socket.topic(kwargs.get('channel') or self.commandData.channel, kwargs.get('topic'))

config = {
	'name' : 'Set Topic',
	'command_str' : 'settopic',
	'args' : [Argument(type=Type.channel, optional=True, name="channel"),
		  Argument(type=Type.msg, optional=False, name="topic")],
	'auth' : True,
	'help' : "Sets the topic in the specified channel. If no channel is specified, it sets the topic in the command origin channel."
}