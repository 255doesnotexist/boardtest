import subprocess

class SDMuxController:
    def list_devices(self):
        result = subprocess.run(['sudo', 'sd-mux-ctrl', '-l'], capture_output=True, text=True)
        print(result.stdout)
    
    def set_serial(self, serial):
        subprocess.run(['sudo', 'sd-mux-ctrl', '--set-serial', serial])
    
    def connect_to_dut(self, serial):
        subprocess.run(['sudo', 'sd-mux-ctrl', '--dut', f'--device-serial={serial}'])
    
    def connect_to_ts(self, serial):
        subprocess.run(['sudo', 'sd-mux-ctrl', '--ts', f'--device-serial={serial}'])
    
    def power_cycle_dut(self, serial):
        subprocess.run(['sudo', 'sd-mux-ctrl', '--tick', '--tick-time=2000', f'--device-serial={serial}'])
