from src.argument import *

def run(self, **kwargs):
	self.socket.partChannels(kwargs.get('channel') or self.commandData.channel, kwargs.get('quitMessage'))

config = {
	'name' : 'Part',
	'command_str' : 'part',
	'args' : [Argument(type=Type.channel, optional=True, name="channel"), Argument(type=Type.msg, optional=True, name="quitMessage")],
	'auth' : True,
	'help' : "Has the bot leave one channel with optional message."
}