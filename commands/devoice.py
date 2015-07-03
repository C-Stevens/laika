from src.argument import *

def run(self, **kwargs):
	nick = kwargs.get('nick')
	channel = kwargs.get('channel')
	if nick:
		self.socket.channelMode(channel, "-v", nick)
	else:
		self.socket.channelMode(channel, "-v", self.commandData.nick)

config = {
	'name' : 'Devoice',
	'command_str' : 'devoice',
	'args' : [Argument(type=Type.channel, optional=False, name="channel"),
		  Argument(type=Type.nick, optional=True, name="nick")],
	'auth' : True,
	'help' : "Sets -v mode in the specified channel. If no nick is specified, the bot gives -v to the command issuer."
}