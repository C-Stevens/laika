from src.argument import *

def run(self, **kwargs):
	channel = kwargs.get('channel')
	self.socket.joinChannels(channel)

config = {
	'name' : 'Join',
	'command_str' : 'join',
	'args' : [Argument(type=Type.channel, optional=False, name="channel")],
	'auth' : True,
	'help' : "Has the bot join a channel or a set of channels."
}