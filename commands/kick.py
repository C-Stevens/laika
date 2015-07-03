from src.argument import *

def run(self, **kwargs):
	nick = kwargs.get('nick')
	channel = kwargs.get('channel')
	if not channel:
		channel = self.commandData.channel
	message = kwargs.get('message')
	self.socket.kick(nick, channel, message)

config = {
	'name' : 'Kick',
	'command_str' : 'kick',
	'args' : [Argument(type=Type.channel, optional=True, name="channel"),
		  Argument(type=Type.nick, optional=False, name="nick"),
		  Argument(type=Type.msg, optional=True, name="message")],
	'auth' : True,
	'help' : "Has the bot kick a user with an optional message. If no channel is supplied, it attempts to kick the user from the command origin channel."
}