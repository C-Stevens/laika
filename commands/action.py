from src.argument import *

def run(self, **kwargs):
	channel = kwargs.get('channel')
	msg = kwargs.get('message')
	if channel:
		self.socket.action(channel, msg)
	else:
		self.socket.action(self.commandData.channel,msg)

config = {
	'name' : 'Action',
	'command_str' : 'action',
	'args' : [ Argument(type=Type.channel, optional=True, name="channel"),
		   Argument(type=Type.msg, optional=False, name="message")],
	'auth' : False,
	'help' : "Performs a /me action in the specified channel.",
}