from src.argument import *
import time

def run(self, **kwargs):
	self.socket.sendToChannel(self.commandData.channel, "Pong sent at: %f (%s) local system time."%(time.time(), time.asctime()))

config = {
	'name' : 'Ping',
	'command_str' : 'ping',
	'args' : [],
	'auth' : False,
	'help' : "Responds to origin channel with current local system time."
}