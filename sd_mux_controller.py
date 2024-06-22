import subprocess

class SDMuxController:
    def list_devices(self):
        """List all devices connected to the SD-Mux controller."""
        result = subprocess.run(['sudo', 'sd-mux-ctrl', '-l'], capture_output=True, text=True)
        print(result.stdout)
    
    def set_serial(self, serial):
        """Set the serial number for the SD-Mux controller."""
        subprocess.run(['sudo', 'sd-mux-ctrl', '--set-serial', serial])
    
    def connect_to_dut(self, serial):
        """Connect the SD card to the Device Under Test (DUT)."""
        subprocess.run(['sudo', 'sd-mux-ctrl', '--dut', f'--device-serial={serial}'])
    
    def connect_to_ts(self, serial):
        """Connect the SD card to the Test Server (TS)."""
        subprocess.run(['sudo', 'sd-mux-ctrl', '--ts', f'--device-serial={serial}'])
    
    def power_cycle_dut(self, serial):
        """Power cycle the Device Under Test (DUT)."""
        subprocess.run(['sudo', 'sd-mux-ctrl', '--tick', '--tick-time=2000', f'--device-serial={serial}'])
