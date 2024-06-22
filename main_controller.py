import os
import time
from sd_mux_controller import SDMuxController
from test_framework import TestFramework
from os_image_manager import OSImageManager

class MainController:
    def __init__(self, config, os_list):
        self.sd_mux = SDMuxController()
        self.framework = TestFramework(config)
        self.os_manager = OSImageManager(os_list)
    
    def run_test_suite(self, os_name, url):
        self.sd_mux.connect_to_ts()
        
        image_path = self.os_manager.download_image(os_name, url)
        self.os_manager.flash_image(os_name, "/dev/sdX")  # should be actual sdmux device path
        
        self.sd_mux.connect_to_dut()
        self.sd_mux.power_cycle_dut()
        
        self.framework.start()
        
        # Example commands to verify OS
        self.framework.run_command("\x03")
        self.framework.check_output(["login"])
        self.framework.run_command("pi")
        self.framework.check_output(["Password"])
        self.framework.run_command("pi")
        
        # Check system information
        uname = self.framework.run_command("uname -a")
        os_release = self.framework.run_command("cat /etc/os-release")
        cpu_info = self.framework.run_command("cat /proc/cpuinfo")
        
        self.framework.stop()
        
        return uname, os_release, cpu_info
    
    def generate_report(self, uname, os_release, cpu_info):
        report = f"uname: {uname}\n\nos_release: {os_release}\n\ncpu_info: {cpu_info}\n"
        with open("test_report.txt", "w") as f:
            f.write(report)
