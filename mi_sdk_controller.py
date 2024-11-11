import logging
from miio import Device, DeviceException

class MiSdkController:
    def __init__(self, token, ip_address, device_id):
        """
        Initialize MiSdkController class.

        Args:
            token (str): Xiaomi account token.
            ip_address (str): Device IP address.
            device_id (str): Device ID.
        """
        self.token = token
        self.ip_address = ip_address
        self.device_id = device_id
        self.device = Device(ip_address, token)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized MiSdkController for device {device_id} at {ip_address}")

    def turn_on(self):
        """
        Turn on the smart switch.

        Returns:
            bool: Whether the operation was successful.
        """
        try:
            self.device.send("set_power", ["on"])
            self.logger.info(f"Turned on device {self.device_id}")
            return True
        except DeviceException as e:
            self.logger.error(f"Failed to turn on device {self.device_id}: {e}")
            return False

    def turn_off(self):
        """
        Turn off the smart switch.

        Returns:
            bool: Whether the operation was successful.
        """
        try:
            self.device.send("set_power", ["off"])
            self.logger.info(f"Turned off device {self.device_id}")
            return True
        except DeviceException as e:
            self.logger.error(f"Failed to turn off device {self.device_id}: {e}")
            return False

    def get_status(self):
        """
        Get the status of the smart switch.

        Returns:
            dict: Device status information.
        """
        try:
            status = self.device.send("get_prop", ["power"])
            self.logger.info(f"Retrieved status for device {self.device_id}: {status}")
            return status
        except DeviceException as e:
            self.logger.error(f"Failed to get status for device {self.device_id}: {e}")
            return None

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     controller = MiSdkController(token="your_token", ip_address="192.168.1.100", device_id="your_device_id")
#     controller.turn_on()
#     status = controller.get_status()
#     print(f"Device status: {status}")
#     controller.turn_off()