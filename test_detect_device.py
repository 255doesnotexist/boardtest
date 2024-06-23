import os_image_manager
import unittest

class TestDetectDevice(unittest.TestCase):
    def test_detect_device(self):
        manager = os_image_manager.OSImageManager(os_list = [], serial='sdwirec_alpha')
        # 确保在调用 detect_device 之前没有 SD 卡插入
        detected_device = manager.detect_device()
        # 验证检测到的设备是否符合预期
        print(f'Detected SD device on: {detected_device}')
        self.assertTrue(detected_device.startswith('/dev/sd'))

if __name__ == '__main__':
    unittest.main()