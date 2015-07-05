from src.argument import *

def run(self, **kwargs):
	self.socket.channelMode(kwargs.get('channel'), "-o", kwargs.get('nick') or self.commandData.nick)

config = {
	'name' : 'Take Op',
	'command_str' : 'takeop',
	'args' : [Argument(type=Type.channel, optional=False, name="channel"),
		  Argument(type=Type.nick, optional=True, name="nick")],
	'auth' : True,
	'help' : "Sets -o mode in the specified channel. If no nick is specified, the bot sets -o for the command issuer."
}