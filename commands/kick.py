from src.argument import *

def run(self, **kwargs):
	self.socket.kick(kwargs.get('nick'), kwargs.get('channel') or self.commandData.channel, kwargs.get('message'))

config = {
	'name' : 'Kick',
	'command_str' : 'kick',
	'args' : [Argument(type=Type.channel, optional=True, name="channel"),
		  Argument(type=Type.nick, optional=False, name="nick"),
		  Argument(type=Type.msg, optional=True, name="message")],
	'auth' : True,
	'help' : "Has the bot kick a user with an optional message. If no channel is supplied, it attempts to kick the user from the command origin channel."
}