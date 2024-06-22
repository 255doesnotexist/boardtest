import requests
import subprocess
import os

class OSImageManager:
    def __init__(self, os_list):
        self.os_list = os_list
    
    def download_image(self, os_name, url):
        image_path = f"./images/{os_name}.img"
        if not os.path.exists(image_path):
            response = requests.get(url)
            with open(image_path, 'wb') as file:
                file.write(response.content)
        return image_path
    
    def flash_image(self, os_name, device, dd_params):
        image_path = f"./images/{os_name}.img"
        dd_command = ['sudo', 'dd', f'if={image_path}', f'of={device}'] + dd_params
        subprocess.run(dd_command)
