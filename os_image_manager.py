import requests
import subprocess
import os
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
    
    def detect_device(self):
        """
        Detect the SD card device by connecting it to the test server.
        """
        self.sd_mux.connect_to_ts(self.serial)
        devices_before = set(os.listdir('/dev'))
        input("Please insert the SD card and press Enter to continue...")
        devices_after = set(os.listdir('/dev'))
        new_devices = devices_after - devices_before
        for device in new_devices:
            if 'sd' in device:
                return f'/dev/{device}'
        raise Exception("No new SD card device detected")
    
    def flash_image(self, os_name, device, dd_params):
        """Flash the OS image to the SD card with the specified dd parameters."""
        image_path = f"./images/{os_name}.img"
        dd_command = ['sudo', 'dd', f'if={image_path}', f'of={device}'] + dd_params
        print(f"Executing command: {' '.join(dd_command)}")
        input("Press Enter to confirm and continue...")
        subprocess.run(dd_command)
