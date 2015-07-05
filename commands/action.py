from src.argument import *

def run(self, **kwargs):
	self.socket.action(kwargs.get('channel') or self.commandData.channel, kwargs.get('message'))

config = {
	'name' : 'Action',
	'command_str' : 'action',
	'args' : [ Argument(type=Type.channel, optional=True, name="channel"),
		   Argument(type=Type.msg, optional=False, name="message")],
	'auth' : False,
	'help' : "Performs a /me action in the specified channel.",
}