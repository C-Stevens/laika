from src.argument import *

def run(self, **kwargs):
	message = kwargs.get('quitMsg')
	if message:
		self.socket.quit(message)
		return
	self.socket.quit()

config = {
	'name' : 'quit',
	'command_str' : 'quit',
	'args' : [Argument(type=Type.msg, optional=True, name="quitMsg")],
	'auth' : True,
	'help' : "Has the bot disconnect from the server with optional message."
}