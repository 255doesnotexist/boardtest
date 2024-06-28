import os
import time
import toml
from sd_mux_controller import SDMuxController  # 假设这个模块存在
from test_framework import TestFramework
from os_image_manager import OSImageManager  # 假设这个模块存在
from test_manager import TestManager  # 假设这个模块存在

class MainController:
    def __init__(self, board_config):
        """Initialize the main controller with the given board configuration."""
        self.board_config = toml.load(board_config)
        self.sd_mux = SDMuxController()
        self.sd_mux_device = self.board_config['serial']['sd_mux_device']
        self.board_name = self.board_config['board']['board_name']
        self.os_manager = OSImageManager(self.board_name, self.board_config['os_list'], self.board_config['serial']['serial_name'])
    
    def run_test_suite(self, os_name, serial, flash=True, test=True):
        """Run the test suite for the specified OS name and serial number."""
        os_info = self.board_config['os_list'][os_name]
        url = os_info['url']
        dd_params = os_info.get('dd_params', [])
        
        if flash:
            image_path = self.os_manager.download_image(os_name, url)
            device = self.sd_mux_device if self.sd_mux_device else self.os_manager.detect_device()
            
            print(f"Connecting SD card to test server for OS {os_name} flashing...")
            self.sd_mux.connect_to_ts(serial)
            self.os_manager.flash_image(os_name, device, dd_params, image_path)
            
            print(f"Connecting SD card to device under test for OS {os_name}...")
            self.sd_mux.connect_to_dut(serial)
            self.sd_mux.power_cycle_dut(serial)
        
        if test:
            print("Starting test framework...")
            
            # 获取OS相关的自动登录、默认用户名密码、login password shell prompt
            auto_login = os_info.get('auto_login', True)
            username = os_info.get('username', 'root')
            password = os_info.get('password', 'bianbu')
            login_prompts = os_info.get('login_prompts', ["login:", "用户名：", "Username:", "用户名:"])
            password_prompts = os_info.get('password_prompts', ["Password:", "密码：", "秘密："])
            shell_prompt = os_info.get('shell_prompt', 'root@k1:~#')
            
            self.framework = TestFramework(
                f"""
                log_dir = "{self.board_config['test_framework']['log_dir']}"
                [env]
                [serial]
                serial_file = "{self.board_config['serial']['serial_file']}"
                bund_rate   = {self.board_config['serial']['bund_rate']}
                auto_login = {str(auto_login).lower()}
                username = "{username}"
                password = "{password}"
                stdout_log = true
                login_prompts = {login_prompts}
                password_prompts = {password_prompts}
                shell_prompt = "{shell_prompt}"
                """
            )
            
            self.framework.start()
            
            test_config = os_info.get('test_config', './tests/default.toml')
            test_manager = TestManager(test_config)
            results = test_manager.execute_tests(self.framework)
            
            print("Stopping test framework...")
            self.framework.stop()
            
            return results
    
    def generate_report(self, results):
        """Generate a report based on the test results."""
        report = "\n".join([f"Test {i+1}: {'PASS' if result else 'FAIL'}" for i, result in enumerate(results)])
        with open("test_report.txt", "w") as f:
            f.write(report)
        print("Test report generated: test_report.txt")

# 示例用法
if __name__ == "__main__":
    board_config_path = "path_to_board_config.toml"  # 请替换为实际的配置文件路径
    main_controller = MainController(board_config_path)
    
    os_name = "example_os"  # 请替换为实际的OS名称
    serial = "123456"  # 请替换为实际的设备序列号
    
    results = main_controller.run_test_suite(os_name, serial)
    main_controller.generate_report(results)
