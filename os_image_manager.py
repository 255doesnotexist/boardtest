import requests
import subprocess
import os

class OSImageManager:
    def __init__(self, os_list):
        self.os_list = os_list
    
    def download_image(self, os_name, url):
        response = requests.get(url)
        image_path = f"./images/{os_name}.img"
        with open(image_path, 'wb') as file:
            file.write(response.content)
        return image_path
    
    def flash_image(self, os_name, device):
        image_path = f"./images/{os_name}.img"
        subprocess.run(['sudo', 'dd', f'if={image_path}', f'of={device}', 'bs=4M', 'conv=fsync'])
