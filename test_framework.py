import pyautotest
import time

class TestFramework:
    def __init__(self, config):
        self.driver = pyautotest.Driver(config)
    
    def start(self):
        self.driver.start()
    
    def stop(self):
        self.driver.stop()
    
    def run_command(self, cmd, timeout):
        return self.driver.assert_script_run(cmd, timeout)
    
    def check_output(self, patterns, timeout):
        for pattern in patterns:
            self.driver.assert_wait_string_ntimes(pattern, 1, timeout)
