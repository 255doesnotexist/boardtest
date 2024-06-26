# from t-autotest repo: reverse shell. 
import pyautotest
import pty
import os

class PseudoTTY():
    def __init__(self):
        self.master, self.slave = pty.openpty()
        self.pts = os.ttyname(self.slave)

    def get_pts(self):
        return self.pts

class RevShell(PseudoTTY):
    def __init__(self):
        super().__init__()
        shell_pid = os.fork()
        if shell_pid == 0:
            os.setsid()
            os.dup2(self.master, 0)
            os.dup2(self.master, 1)
            os.dup2(self.master, 2)
            os.close(self.slave)
            os.execv("/bin/sh", ["sh"])
        else:
            os.close(self.master)

shell = RevShell()

conf = f"""
    log_dir = "./logs"
    [env]
    [serial]
    serial_file = "/dev/ttyUSB0"
    disable_echo = true
    """

print("pts:", shell.get_pts())

d = pyautotest.Driver(conf)
res = d.assert_script_run('whoami', 10)
print("whoami:", res)
d.stop()
