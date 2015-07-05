from src.argument import *

def run(self, **kwargs):
	self.socket.sendToChannel(kwargs.get('nick'), kwargs.get('message'))

config = {
	'name' : 'Message',
	'command_str' : 'msg',
	'args' : [Argument(type=Type.nick, optional=False, name="nick"),
		  Argument(type=Type.msg, optional=False, name="message")],
	'auth' : False,
	'help' : "Sends a specified message to a specified nick."
}