from src.argument import *

def run(self, **kwargs):
	message = kwargs.get('msg')
	self.socket.sendToChannel(self.commandData.channel, message)

config = {
	'name' : 'Echo',
	'command_str' : 'echo',
	'args' : [Argument(type=Type.msg, optional=False, name="msg")],
	'auth' : False,
	'help' : "Repeats input back into the origin channel."
}