from src.argument import *

def run(self, **kwargs):
	nick = kwargs.get('nick')
	channel = kwargs.get('channel')
	if nick:
		self.socket.channelMode(channel, "-o", nick)
	else:
		self.socket.channelMode(channel, "-o", self.commandData.nick)

config = {
	'name' : 'Take Op',
	'command_str' : 'takeop',
	'args' : [Argument(type=Type.channel, optional=False, name="channel"),
		  Argument(type=Type.nick, optional=True, name="nick")],
	'auth' : True,
	'help' : "Sets -o mode in the specified channel. If no nick is specified, the bot sets -o for the command issuer."
}