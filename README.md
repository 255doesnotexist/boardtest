# Run

Example command

```bash
sudo PYTHONPATH=. /home/xyz/miniconda3/envs/autotest/bin/python main.py
```

# To-Do

- ~~flash image functionality~~ (done)
- test suite functionality

# Device Compatibility

- SD-Mux Devices: SDWireC (tested)
- Serial Devices: CP2102 USB-UART

# Dependency

- sd-mux-ctrl binary added to PATH
- pyserial, toml, and etc
- sudo permisson (to access /dev/sdX and /dev/ttyUSBX)