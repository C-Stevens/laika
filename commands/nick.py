from src.argument import *

def run(self, **kwargs):
	self.socket.nick(kwargs.get('nick'))

config = {
	'name' : 'nick',
	'command_str' : 'nick',
	'args' : [Argument(type=Type.nick, optional=False, name="nick")],
	'auth' : True,
	'help' : "Changes the bot's nick to a specified nickname."
}