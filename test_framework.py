# import pyautotest
# from pyautotest import Driver as PyautotestDriver
from pyautotest_driver import pyautotest_driver
import time

class TestFramework:
    def __init__(self, config):
        """Initialize the test framework with the given configuration."""
        self.driver = pyautotest_driver(config)
    
    def start(self):
        """Start the test framework."""
        self.driver.start()
    
    def stop(self):
        """Stop the test framework."""
        self.driver.stop()
    
    def run_command(self, cmd, timeout):
        """Run a command on the Device Under Test (DUT) with a timeout."""
        return self.driver.serial_assert_script_run(cmd, timeout)
    
    def check_output(self, patterns, timeout):
        """Check the output for specific patterns within a timeout."""
        for pattern in patterns:
            self.driver.serial_assert_wait_string(pattern, timeout)
