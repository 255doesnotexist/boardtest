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
        """Run a command on the Device Under Test (DUT) and check the output for specific patterns within a timeout."""
        return self.driver.run_command(cmd, timeout)
    
    def run_command_and_check_output(self, cmd, patterns, timeout):
        """Run a command on the Device Under Test (DUT) and check the output for specific patterns within a timeout."""
        return self.driver.run_command_and_check_output(cmd, patterns, timeout)


# 示例用法
if __name__ == "__main__":
    config = """
    log_dir = "./logs"
    [env]
    [serial]
    serial_file = "/dev/ttyUSB0"
    bund_rate   = 115200
    timeout = 1  # 新增timeout配置
    auto_login = true
    username = "root"
    password = "bianbu"
    stdout_log = true
    login_prompts = ["login:", "用户名：", "Username:", "用户名:"]
    password_prompts = ["Password:", "密码：", "秘密："]
    shell_prompt = "root@k1:~#"  # 新增shell提示符
    """

    framework = TestFramework(config)
    framework.start()
    print(framework.run_command_and_check_output("uname -a", ["Linux"], 10))
    print(framework.run_command_and_check_output("cat /etc/os-release", ["Bianbu", "ID=", "VERSION="], 10))
    print(framework.run_command_and_check_output("cat /proc/cpuinfo", ["processor", "model name"], 10))
    framework.stop()
