from src.argument import *
import src.format

def run(self, **kwargs):
	user_threads = self.parent.reportThreads(kwargs.get('user_hostname'))
	if not user_threads:
		self.socket.notice(self.commandData.nick, "Unable to retrieve a list of running commands for %s"%(src.format.bold(kwargs.get('user_hostname'))))
	for thread in user_threads:
		if thread is not self:
			self.parent.removeThread(thread, kwargs.get('user_hostname'))
	self.socket.notice(self.commandData.nick, src.format.bold("NOTE: ")+"This command does not stop running commands, it only clears the user's pool to allow more commands to enter. Running commands still exist in memory, and use of this command will not prevent memory creep from stuck commands. Use with caution.")
	self.socket.notice(self.commandData.nick, src.format.bold("NOTE: ")+"This command may need to be re-issued several times to completely clear the pool in some cases.")

config = {
	'name' : 'Flush Commands',
	'command_str' : 'flushcommands',
	'args' : [Argument(type=Type.msg, optional=False, name="user_hostname")],
	'auth' : True,
	'help' : "Attempts to remove all running threads from a provided user's (users are based on IRC hostname) thread pool."
}