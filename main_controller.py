import os
import time
import toml
from sd_mux_controller import SDMuxController
from test_framework import TestFramework
from os_image_manager import OSImageManager
from test_manager import TestManager

class MainController:
    def __init__(self, board_config):
        self.board_config = toml.load(board_config)
        self.sd_mux = SDMuxController()
        self.framework = TestFramework(self.board_config['test_framework'])
        self.os_manager = OSImageManager(self.board_config['os_list'], self.board_config['serial']['serial_name'])
    
    def run_test_suite(self, os_name, serial):
        os_info = self.board_config['os_list'][os_name]
        url = os_info['url']
        dd_params = os_info.get('dd_params', [])
        
        self.sd_mux.connect_to_ts(serial)
        
        image_path = self.os_manager.download_image(os_name, url)
        device = self.os_manager.detect_device()
        self.os_manager.flash_image(os_name, device, dd_params)
        
        self.sd_mux.connect_to_dut(serial)
        self.sd_mux.power_cycle_dut(serial)
        
        self.framework.start()
        
        test_config = os_info.get('test_config', './tests/default.toml')
        test_manager = TestManager(test_config)
        results = test_manager.execute_tests(self.framework)
        
        self.framework.stop()
        
        return results
    
    def generate_report(self, results):
        report = "\n".join([f"Test {i+1}: {'PASS' if result else 'FAIL'}" for i, result in enumerate(results)])
        with open("test_report.txt", "w") as f:
            f.write(report)
