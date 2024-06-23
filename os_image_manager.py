import requests
import subprocess
import os
import re
import time
from sd_mux_controller import SDMuxController

class OSImageManager:
    def __init__(self, os_list, serial):
        """Initialize the OS image manager with the given OS list and serial number."""
        self.os_list = os_list
        self.sd_mux = SDMuxController()
        self.serial = serial
    
    def download_image(self, os_name, url):
        """Download the OS image from the specified URL if not already downloaded."""
        image_path = f"./images/{os_name}.img"
        if not os.path.exists(image_path):
            response = requests.get(url)
            with open(image_path, 'wb') as file:
                file.write(response.content)
        return image_path

    def list_dev_directory():
        # 执行 'ls /dev' 命令并获取输出
        result = subprocess.run(['ls', '/dev'], capture_output=True, text=True)
        # 将输出字符串分割成列表，然后转换成集合
        devices = set(result.stdout.split())
        return devices

    def detect_device(self):
        """
        Detect the SD card device by connecting it to the test server and checking for new partitions.
        """
        self.sd_mux.connect_to_dut(self.serial)
        time.sleep(5)
        devices_before = set(os.listdir('/dev'))
        devices_before = {device for device in devices_before if "sd" in device}
        print(devices_before)
        input("Please insert the SD card and press Enter to continue...")
        self.sd_mux.connect_to_ts(self.serial)
        time.sleep(5)
        devices_after = set(os.listdir('/dev'))
        devices_after = {device for device in devices_after if "sd" in device}
        print(devices_after)
        
        # Find all base sd devices before and after
        base_devices_before = {device for device in devices_before if re.match(r'sd[a-z]$', device)}
        base_devices_after = {device for device in devices_after if re.match(r'sd[a-z]$', device)}
        
        # Find new partitions that appeared after the SD card was connected
        new_partitions = {device for device in devices_after if re.match(r'sd[a-z]\d+$', device)}
        old_partitions = {device for device in devices_before if re.match(r'sd[a-z]\d+$', device)}
        actual_new_partitions = {partition for partition in new_partitions if partition not in old_partitions}
        print(actual_new_partitions)
        print(old_partitions)
        
        # If there are new partitions, find the base device(s) they belong to
        if actual_new_partitions:
            for base_device in base_devices_after:
                if any(part.startswith(base_device) for part in actual_new_partitions):
                    return f'/dev/{base_device}'
        
        raise Exception("No new SD card device detected")
    
    def flash_image(self, os_name, device, dd_params):
        """Flash the OS image to the SD card with the specified dd parameters."""
        image_path = f"./images/{os_name}.img"
        dd_command = ['sudo', 'dd', f'if={image_path}', f'of={device}'] + dd_params
        print(f"Executing command: {' '.join(dd_command)}")
        input("Press Enter to confirm and continue...")
        subprocess.run(dd_command)
