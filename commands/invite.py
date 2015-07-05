from src.argument import *

def run(self, **kwargs):
	self.socket.invite(kwargs.get('nick'), kwargs.get('channel'))

config = {
	'name' : 'Invite',
	'command_str' : 'invite',
	'args' : [Argument(type=Type.nick, optional=False, name="nick"),
		  Argument(type=Type.channel, optional=False, name="channel")],
	'auth' : True,
	'help' : "Invites specified nick to specified channel."
}