from src.argument import *
import src.format

def run(self, **kwargs):
	self.socket.notice(self.commandData.nick, "You (%s) have %s commands running (including this one) out of a total thread pool size of %s"%(src.format.bold(self.commandData.hostname), src.format.bold(str(self.parent.userThreadCount(self.commandData.hostname))), src.format.bold(str(self.parent.maxUserThreads))))

config = {
	'name' : 'Running Threads',
	'command_str' : 'runningcommands',
	'args' : [],
	'auth' : False,
	'help' : "Reports the number of command threads currently running out of a total possible number for the user."
}