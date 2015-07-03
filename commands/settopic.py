from src.argument import *

def run(self, **kwargs):
	channel = kwargs.get('channel')
	topic = kwargs.get('topic')
	if channel:
		self.socket.topic(channel, topic)
	else:
		self.socket.topic(self.commandData.channel, topic)

config = {
	'name' : 'Set Topic',
	'command_str' : 'settopic',
	'args' : [Argument(type=Type.channel, optional=True, name="channel"),
		  Argument(type=Type.msg, optional=False, name="topic")],
	'auth' : True,
	'help' : "Sets the topic in the specified channel. If no channel is specified, it sets the topic in the command origin channel."
}