from src.argument import *

def run(self, **kwargs):
	channel = kwargs.get('channel')
	quitMsg = kwargs.get('quitMessage')
	if channel:
		if quitMsg:
			self.socket.partChannels(channel, quitMsg)
			return
		self.socket.partChannels(channel)
		return
	if quitMsg:
		self.socket.partChannels(self.commandData.channel, quitMsg)
		return
	self.socket.partChannels(self.commandData.channel)

config = {
	'name' : 'Part',
	'command_str' : 'part',
	'args' : [Argument(type=Type.channel, optional=True, name="channel"), Argument(type=Type.msg, optional=True, name="quitMessage")],
	'auth' : True,
	'help' : "Has the bot leave one channel with optional message."
}