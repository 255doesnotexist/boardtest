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

class SDMuxController:
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
        print(result)
    
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