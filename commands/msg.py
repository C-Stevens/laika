from src.argument import *

def run(self, **kwargs):
	nick = kwargs.get('nick')
	message = kwargs.get('msg')
	self.socket.sendToChannel(nick, message)

config = {
	'name' : 'Message',
	'command_str' : 'msg',
	'args' : [Argument(type=Type.nick, optional=False, name="nick"),
		  Argument(type=Type.msg, optional=False, name="msg")],
	'auth' : False,
	'help' : "Sends a specified message to a specified nick."
}