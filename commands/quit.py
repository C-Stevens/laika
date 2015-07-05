from src.argument import *

def run(self, **kwargs):
	self.socket.quit(kwargs.get('quitMsg'))

config = {
	'name' : 'quit',
	'command_str' : 'quit',
	'args' : [Argument(type=Type.msg, optional=True, name="quitMsg")],
	'auth' : True,
	'help' : "Has the bot disconnect from the server with optional message."
}