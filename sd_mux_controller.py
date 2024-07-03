import subprocess

class SDMuxBaseController:
    """Base class for SD-Mux controllers."""
    
    def list_devices(self):
        """List all devices connected to the SD-Mux controller."""
        raise NotImplementedError("Method 'list_devices' not implemented in subclass.")
    
    def set_serial(self, serial):
        """Set the serial number for the SD-Mux controller."""
        raise NotImplementedError("Method 'set_serial' not implemented in subclass.")
    
    def connect_to_dut(self, serial):
        """Connect the SD card to the Device Under Test (DUT)."""
        raise NotImplementedError("Method 'connect_to_dut' not implemented in subclass.")
    
    def connect_to_ts(self, serial):
        """Connect the SD card to the Test Server (TS)."""
        raise NotImplementedError("Method 'connect_to_ts' not implemented in subclass.")
    
    def power_cycle_dut(self, serial):
        """Power cycle the Device Under Test (DUT)."""
        raise NotImplementedError("Method 'power_cycle_dut' not implemented in subclass.")

class SDMuxCtrlController(SDMuxBaseController):
    """Controller for managing SD-Mux via sd-mux-ctrl."""
    
    def list_devices(self):
        """List all devices connected to the SD-Mux controller."""
        command = ['sudo', 'sd-mux-ctrl', '-l']
        print(f"Executing command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        print("Listing all connected devices:")
        print(result.stdout)
    
    def set_serial(self, serial):
        """Set the serial number for the SD-Mux controller."""
        command = ['sudo', 'sd-mux-ctrl', '--set-serial', serial]
        print(f"Executing command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        print(f"Setting serial number to {serial}:")
        print(result.stdout if result.stdout else "Serial number set successfully.")
    
    def connect_to_dut(self, serial):
        """Connect the SD card to the Device Under Test (DUT)."""
        command = ['sudo', 'sd-mux-ctrl', '--dut', f'--device-serial={serial}']
        print(f"Executing command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        print(f"Connecting SD card to DUT with serial {serial}:")
        print(result.stdout if result.stdout else "Connected to DUT successfully.")
    
    def connect_to_ts(self, serial):
        """Connect the SD card to the Test Server (TS)."""
        command = ['sudo', 'sd-mux-ctrl', '--ts', f'--device-serial={serial}']
        print(f"Executing command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        print(f"Connecting SD card to TS with serial {serial}:")
        print(result.stdout if result.stdout else "Connected to TS successfully.")
    
    def power_cycle_dut(self, serial):
        """Power cycle the Device Under Test (DUT)."""
        command = ['sudo', 'sd-mux-ctrl', '--tick', '--tick-time=2000', f'--device-serial={serial}']
        print(f"Executing command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        print(f"Power cycling DUT with serial {serial}:")
        print(result.stdout if result.stdout else "Power cycle completed successfully.")

class UsbSDMuxController(SDMuxBaseController):
    """Controller for managing SD-Mux via usbsdmux."""
    
    def __init__(self):
        self.sda_device = self._detect_sda_device()
        self.sg_device = self._detect_sg_device()
    
    def _detect_sda_device(self):
        """Detect /dev/sda device, or read from configuration."""
        # TODO: Implement detection logic here
        # Maybe read from dd config?
        return '/dev/sda'
    
    def _detect_sg_device(self):
        """Detect /dev/sg0 device, or read from configuration."""
        # TODO: Implement detection logic here
        # With lsscsi or scan the /sys/class/scsi_generic/sgX/device/block?
        return '/dev/sg0'
    
    def list_devices(self):
        """List all devices connected to the SD-Mux controller."""
        print("usbsdmux does not support listing devices.")
    
    def set_serial(self, serial):
        """Set the serial number for the SD-Mux controller."""
        print("usbsdmux does not support setting serial number.")
    
    def connect_to_dut(self, serial=None):
        """Connect the SD card to the Device Under Test (DUT)."""
        command = ['sudo', 'usbsdmux', self.sg_device, 'dut']
        print(f"Executing command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        print("Connecting SD card to DUT:")
        print(result.stdout if result.stdout else "Connected to DUT successfully.")
    
    def connect_to_ts(self, serial=None):
        """Connect the SD card to the Test Server (TS)."""
        command = ['sudo', 'usbsdmux', self.sg_device, 'host']
        print(f"Executing command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        print("Connecting SD card to TS:")
        print(result.stdout if result.stdout else "Connected to TS successfully.")
    
    def power_cycle_dut(self, serial=None):
        """Power cycle the Device Under Test (DUT)."""
        print("usbsdmux does not support power cycling.")

class SDMuxController:
    """High-level controller for managing SD-Mux devices using different implementations."""
    
    def __init__(self, use_usbsdmux=False):
        self.controller = UsbSDMuxController() if use_usbsdmux else SDMuxCtrlController()
    
    def list_devices(self):
        """List all devices connected to the SD-Mux controller."""
        self.controller.list_devices()
    
    def set_serial(self, serial):
        """Set the serial number for the SD-Mux controller."""
        self.controller.set_serial(serial)
    
    def connect_to_dut(self, serial=None):
        """Connect the SD card to the Device Under Test (DUT)."""
        self.controller.connect_to_dut(serial)
    
    def connect_to_ts(self, serial=None):
        """Connect the SD card to the Test Server (TS)."""
        self.controller.connect_to_ts(serial)
    
    def power_cycle_dut(self, serial=None):
        """Power cycle the Device Under Test (DUT)."""
        self.controller.power_cycle_dut(serial)