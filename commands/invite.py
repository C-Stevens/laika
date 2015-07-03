from src.argument import *

def run(self, **kwargs):
	nick = kwargs.get('nick')
	channel = kwargs.get('channel')
	self.socket.invite(nick, channel)

config = {
	'name' : 'Invite',
	'command_str' : 'invite',
	'args' : [Argument(type=Type.nick, optional=False, name="nick"),
		  Argument(type=Type.channel, optional=False, name="channel")],
	'auth' : True,
	'help' : "Invites specified nick to specified channel."
}