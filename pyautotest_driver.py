import serial
import time
import threading
import toml
import os
import sys

class pyautotest_driver:
    def __init__(self, config):
        self.config = toml.loads(config)
        self.serial_file = self.config['serial']['serial_file']
        self.bund_rate = self.config['serial']['bund_rate']
        self.auto_login = self.config['serial']['auto_login']
        self.username = self.config['serial']['username']
        self.password = self.config['serial']['password']
        self.log_dir = self.config['log_dir']
        self.stdout_log = self.config['serial']['stdout_log']
        self.serial_conn = None
        self.log_file = None
        self.running = False

    def start(self):
        self._open_serial_port()
        log_file_path = os.path.join(self.log_dir, f"serial_log_{int(time.time())}.log")
        self.log_file = open(log_file_path, 'w')
        self.running = True
        threading.Thread(target=self._read_serial).start()

    def stop(self):
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
        if self.log_file:
            self.log_file.close()

    def _open_serial_port(self):
        try:
            self.serial_conn = serial.Serial(self.serial_file, self.bund_rate, timeout=1)
            print(f"Opened serial port {self.serial_file} successfully.")
        except serial.SerialException as e:
            print(f"Error opening serial port {self.serial_file}: {e}")
            self.serial_conn = None

    def _read_serial(self):
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore')
                    if self.stdout_log:
                        print(line, end='')
                    if self.log_file:
                        self.log_file.write(line)
                        self.log_file.flush()
                    if self.auto_login:
                        self._handle_auto_login(line)
            except serial.SerialException as e:
                print(f"Error reading from serial port: {e}")
                self.stop()
            except TypeError as e:
                print(f"TypeError encountered: {e}")
                self.stop()

    def _handle_auto_login(self, line):
        if "login:" in line:
            self.serial_conn.write((self.username + '\n').encode('utf-8'))
        elif "Password:" in line:
            self.serial_conn.write((self.password + '\n').encode('utf-8'))

    def serial_assert_script_run(self, cmd, timeout):
        if not self.serial_conn or not self.serial_conn.is_open:
            self._open_serial_port()
        if not self.serial_conn:
            print("Failed to open serial port.")
            return ""

        self.serial_conn.write((cmd + '\n').encode('utf-8'))
        start_time = time.time()
        output = ""
        while time.time() - start_time < timeout:
            try:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore')
                    output += line
                    if self.stdout_log:
                        print(line, end='')
                    if self.log_file:
                        self.log_file.write(line)
                        self.log_file.flush()
            except serial.SerialException as e:
                print(f"Error reading from serial port: {e}")
                break
            except TypeError as e:
                print(f"TypeError encountered: {e}")
                break
        return output

    def serial_assert_wait_string(self, pattern, timeout):
        if not self.serial_conn or not self.serial_conn.is_open:
            self._open_serial_port()
        if not self.serial_conn:
            print("Failed to open serial port.")
            return False

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore')
                    if self.stdout_log:
                        print(line, end='')
                    if self.log_file:
                        self.log_file.write(line)
                        self.log_file.flush()
                    if pattern in line:
                        return True
            except serial.SerialException as e:
                print(f"Error reading from serial port: {e}")
                break
            except TypeError as e:
                print(f"TypeError encountered: {e}")
                break
        return False

# 示例用法
if __name__ == "__main__":
    config = """
    log_dir = "./logs"
    [env]
    [serial]
    serial_file = "/dev/ttyUSB0"
    bund_rate   = 115200
    auto_login = true
    username = "root"
    password = "bianbu"
    stdout_log = true
    """

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

    # 使用示例
    framework = TestFramework(config)
    framework.start()
    time.sleep(2)  # 等待设备启动
    framework.run_command("ls", 5)
    framework.check_output(["root", "login"], 10)
    framework.stop()
