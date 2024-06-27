import serial
import time
import threading
import toml
import os
import logging

class pyautotest_driver:
    def __init__(self, config):
        self.config = toml.loads(config)
        self.serial_file = self.config['serial']['serial_file']
        self.bund_rate = self.config['serial']['bund_rate']
        self.timeout = self.config['serial'].get('timeout', 1)  # 新增timeout配置，默认1秒
        self.auto_login = self.config['serial']['auto_login']
        self.username = self.config['serial']['username']
        self.password = self.config['serial']['password']
        self.login_prompts = self.config['serial']['login_prompts']
        self.password_prompts = self.config['serial']['password_prompts']
        self.shell_prompt = self.config['serial']['shell_prompt']  # 新增shell提示符
        self.log_dir = self.config['log_dir']
        self.stdout_log = self.config['serial']['stdout_log']
        self.serial_conn = None
        self.running = False
        self.reopening = False  # 新增标志位
        self.lock = threading.Lock()  # 用于避免同时读写的锁
        self.login_event = threading.Event()  # 登录成功事件
        self.last_output_time = time.time()  # 记录最后一次输出的时间

        # 设置日志
        log_file_path = os.path.join(self.log_dir, f"serial_log_{int(time.time())}.log")
        logging.basicConfig(filename=log_file_path, level=logging.DEBUG, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()

    def start(self):
        self._open_serial_port()
        self.running = True
        read_thread = threading.Thread(target=self._read_serial)
        read_thread.start()
        
        if self.auto_login:
            self.login_event.wait()  # 等待登录成功事件被设置
            self.logger.info("Auto login successful")

    def stop(self):
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()

    def _open_serial_port(self):
        try:
            self.serial_conn = serial.Serial(
                self.serial_file, 
                self.bund_rate, 
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()
            self.logger.info(f"Opened serial port {self.serial_file} successfully.")
        except serial.SerialException as e:
            self.logger.error(f"Error opening serial port {self.serial_file}: {e}")
            self.serial_conn = None

    def _read_serial(self):
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    with self.lock:  # 获取锁，确保读写操作不会同时进行
                        line = self.serial_conn.readline().decode('utf-8', errors='ignore')
                    if self.stdout_log:
                        print(line, end='')
                    self.logger.debug(line)
                    self.last_output_time = time.time()  # 更新最后一次输出的时间
                    if self.auto_login:
                        self._handle_auto_login(line)
                elif self.serial_conn and self.serial_conn.in_waiting == 0:
                    # 处理设备未返回数据的情况
                    current_time = time.time()
                    if self.auto_login and not self.login_event.is_set() and (current_time - self.last_output_time > 5):
                        # 如果超过5秒没有接收到任何输出，并且登录事件未设置，则尝试输入用户名
                        with self.lock:  # 获取锁，确保读写操作不会同时进行
                            self.serial_conn.write((self.username + '\n').encode('utf-8'))
                        self.logger.info("No output detected for 5 seconds, sending username to provoke response.")
                        self.last_output_time = current_time  # 更新最后一次输出的时间
                    time.sleep(0.1)
            except (serial.SerialException, OSError, TypeError) as e:
                if not self.running:
                    self.logger.info("Serial read loop exiting due to stop signal.")
                    break
                self.logger.error(f"Error reading from serial port: {e}")
                self._attempt_reopen_serial_port()

    def _attempt_reopen_serial_port(self):
        if not self.reopening:  # 避免多次尝试重新打开
            self.reopening = True
            self.logger.info("Attempting to reopen serial port...")
            if self.serial_conn:
                try:
                    self.serial_conn.close()
                except Exception as e:
                    self.logger.error(f"Error closing serial port: {e}")
            time.sleep(1)  # 等待一段时间再重新打开
            self._open_serial_port()
            self.reopening = False  # 重置标志位

    def _handle_auto_login(self, line):
        if self.shell_prompt in line:
            self.login_event.set()  # 设置登录成功事件
            self.logger.info(f"Detected shell prompt: {line.strip()}")
            return
        
        for prompt in self.login_prompts:
            if prompt in line:
                with self.lock:  # 获取锁，确保读写操作不会同时进行
                    self.serial_conn.write((self.username + '\n').encode('utf-8'))
                self.logger.info(f"Detected login prompt: {line.strip()}")
                return
        for prompt in self.password_prompts:
            if prompt in line:
                with self.lock:  # 获取锁，确保读写操作不会同时进行
                    self.serial_conn.write((self.password + '\n').encode('utf-8'))
                self.logger.info(f"Detected password prompt: {line.strip()}")
                return

    def run_command_and_check_output(self, cmd, patterns, timeout):
        if not self.serial_conn or not self.serial_conn.is_open:
            self._open_serial_port()
        if not self.serial_conn:
            self.logger.error("Failed to open serial port.")
            return "", False

        self.logger.info(f"Running command: {cmd}")
        with self.lock:  # 获取锁，确保读写操作不会同时进行
            self.serial_conn.reset_input_buffer()  # 清空缓冲区
            self.serial_conn.write((cmd + '\n').encode('utf-8'))
            start_time = time.time()
            output = ""
            matched = False
            while time.time() - start_time < timeout:
                try:
                    if not self.running:  # 检查运行状态
                        break

                    if self.serial_conn.in_waiting > 0:
                        line = self.serial_conn.readline().decode('utf-8', errors='ignore')
                        
                        # 检测并去掉命令本身
                        if line.startswith(cmd):
                            line = line[len(cmd):].lstrip()
                        
                        # 检测到 shell 提示符，命令执行完成
                        if self.shell_prompt in line:
                            line = line.split(self.shell_prompt)[0].rstrip()
                            output += line
                            self.logger.debug(f"Detected shell prompt in output: {line.strip()}")
                            break

                        output += line
                        if self.stdout_log:
                            print(line, end='')
                        self.logger.debug(line)
                        
                        # 在去掉命令本身和shell_prompt之后进行匹配
                        for pattern in patterns:
                            if pattern in line:
                                matched = True
                                self.logger.info(f"Pattern matched: {pattern}")
                                break
                    elif self.serial_conn and self.serial_conn.in_waiting == 0:
                        # 处理设备未返回数据的情况
                        time.sleep(0.1)
                except (serial.SerialException, OSError, TypeError) as e:
                    self.logger.error(f"Error reading from serial port: {e}")
                    self._attempt_reopen_serial_port()
                    break

            self.logger.info(f"Command output: {output}")
            self.logger.info(f"Matched: {matched}")

        return output, matched

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
    
    def run_command_and_check_output(self, cmd, patterns, timeout):
        """Run a command on the Device Under Test (DUT) and check the output for specific patterns within a timeout."""
        return self.driver.run_command_and_check_output(cmd, patterns, timeout)

    def run_tests(self):
        """Run a series of predefined tests."""
        tests = [
            ("uname -a", ["Linux"], 10),
            ("cat /etc/os-release", ["ID=", "VERSION="], 10),
            ("cat /proc/cpuinfo", ["processor", "model name"], 10)
        ]
        for cmd, patterns, timeout in tests:
            output, matched = self.run_command_and_check_output(cmd, patterns, timeout)
            print(f"Command: {cmd}")
            print(f"Output: {output}")
            print(f"Matched: {matched}")
            print("-" * 50)

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
    framework.run_tests()
    framework.stop()
