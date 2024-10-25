# Boardtest

## Run

Example usage command

```sh
sudo python main.py --help
```

```sh
usage: main.py [-h] [-f] [--no-flash] [-t] [--no-test]
               [-s] [--no-stdout-log] [-b BOARD_CONFIG]
               [-S SERIAL]

Main entry point for running test suites on different OS
images for a specific board.

options:
  -h, --help            show this help message and exit
  -f, --flash           Enable flashing the OS image
                        before testing. (default:
                        disabled)
  --no-flash            Disable flashing the OS image
                        before testing.
  -t, --test            Enable running tests after
                        flashing. (default: enabled)
  --no-test             Disable running tests after
                        flashing.
  -s, --stdout-log      Enable logging output to stdout.
                        (default: disabled)
  --no-stdout-log       Disable logging output to stdout.
  -b BOARD_CONFIG, --board-config BOARD_CONFIG
                        Path to the board configuration
                        file.
  -S SERIAL, --serial SERIAL
                        Serial number of the SD Mux
                        device.
```

## Server

```sh
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

## To-Do

- ~~flash image functionality~~ (done)
- ~~test suite functionality~~ (done)
- cut un-needed stdout logs (WIP)
- usbsdmux package support (WIP)

## Device Compatibility

- SD-Mux Devices: SDWireC (tested)
- Serial Devices: CP2102 USB-UART

- Boards (Compattibility depends on your own config) :
 1. Banana Pi BPI-F3 / SpacemiT K1
 2. StarFive VisionFive / JH7100 (flash partially supported but boot stucks on detecting block devices so testing unavailable) [Maybe a SDWireC problem]
 3. Milk-V Duo S

## Dependency

- sd-mux-ctrl binary added to PATH
- pyserial, toml, rich, texttable and etc
- sudo permisson (to access /dev/sdX and /dev/ttyUSBX)
- fastapi uvicorn websockets (for web server access)

## Example

```sh
(autotest) xyz@heartland:~/boardtest$ sudo /home/xyz/miniconda3/envs/autotest/bin/python main.py --no-stdout-log

          Serial: sdwirec_alpha
          Board config: ./boards/banana_pi_f3_config.toml
          Flashing: False
          Testing: True
          Stdout log: False
          
==================================================
Running test suite for OS: Bianbu...
==================================================

Preparing to start test framework for OS Bianbu...
Do you want to continue with testing?  [y/n] (n): y
Starting test framework...
root
-bash: root: 未找到命令
Linux k1 6.1.15 #1.0 SMP PREEMPT Thu May 30 13:16:13 UTC 2024 riscv64 riscv64 riscv64 GNU/Linux
PRETTY_NAME="Bianbu 1.0"
NAME="Bianbu"
VERSION_ID="1.0"
VERSION="1.0 (Mantic Minotaur)"
VERSION_CODENAME=mantic
ID=bianbu
ID_LIKE=debian
HOME_URL="coming soon"
SUPPORT_URL="coming soon"
BUG_REPORT_URL="coming soon"
PRIVACY_POLICY_URL="coming soon"
UBUNTU_CODENAME=mantic
LOGO=ubuntu-logo
processor       : 0
hart            : 0
model name      : Spacemit(R) X60
isa             : rv64imafdcv_sscofpmf_sstc_svpbmt_zicbom_zicboz_zicbop_zihintpause
mmu             : sv39
mvendorid       : 0x710
marchid         : 0x8000000058000001
mimpid          : 0x1000000049772200

processor       : 1
hart            : 1
model name      : Spacemit(R) X60
isa             : rv64imafdcv_sscofpmf_sstc_svpbmt_zicbom_zicboz_zicbop_zihintpause
mmu             : sv39
mvendorid       : 0x710
marchid         : 0x8000000058000001
mimpid          : 0x1000000049772200

processor       : 2
hart            : 2
model name      : Spacemit(R) X60
isa             : rv64imafdcv_sscofpmf_sstc_svpbmt_zicbom_zicboz_zicbop_zihintpause
mmu             : sv39
mvendorid       : 0x710
marchid         : 0x8000000058000001
mimpid          : 0x1000000049772200

processor       : 3
hart            : 3
model name      : Spacemit(R) X60
isa             : rv64imafdcv_sscofpmf_sstc_svpbmt_zicbom_zicboz_zicbop_zihintpause
mmu             : sv39
mvendorid       : 0x710
marchid         : 0x8000000058000001
mimpid          : 0x1000000049772200

processor       : 4
hart            : 4
model name      : Spacemit(R) X60
isa             : rv64imafdcv_sscofpmf_sstc_svpbmt_zicbom_zicboz_zicbop_zihintpause
mmu             : sv39
mvendorid       : 0x710
marchid         : 0x8000000058000001
mimpid          : 0x1000000049772200

processor       : 5
hart            : 5
model name      : Spacemit(R) X60
isa             : rv64imafdcv_sscofpmf_sstc_svpbmt_zicbom_zicboz_zicbop_zihintpause
mmu             : sv39
mvendorid       : 0x710
marchid         : 0x8000000058000001
mimpid          : 0x1000000049772200

processor       : 6
hart            : 6
model name      : Spacemit(R) X60
isa             : rv64imafdcv_sscofpmf_sstc_svpbmt_zicbom_zicboz_zicbop_zihintpause
mmu             : sv39
mvendorid       : 0x710
marchid         : 0x8000000058000001
mimpid          : 0x1000000049772200

processor       : 7
hart            : 7
model name      : Spacemit(R) X60
isa             : rv64imafdcv_sscofpmf_sstc_svpbmt_zicbom_zicboz_zicbop_zihintpause
mmu             : sv39
mvendorid       : 0x710
marchid         : 0x8000000058000001
mimpid          : 0x1000000049772200

MemTotal:        3917196 kB
MemFree:         2789620 kB
MemAvailable:    3406960 kB
Buffers:           47528 kB
Cached:           570420 kB
SwapCached:            0 kB
Active:           128220 kB
Inactive:         803508 kB
Active(anon):       3472 kB
Inactive(anon):   319468 kB
Active(file):     124748 kB
Inactive(file):   484040 kB
Unevictable:           0 kB
Mlocked:               0 kB
SwapTotal:             0 kB
SwapFree:              0 kB
Dirty:                 0 kB
Writeback:             0 kB
AnonPages:        313836 kB
Mapped:           176172 kB
Shmem:              9160 kB
KReclaimable:      55640 kB
Slab:             107804 kB
SReclaimable:      55640 kB
SUnreclaim:        52164 kB
KernelStack:        7488 kB
PageTables:        10232 kB
SecPageTables:         0 kB
NFS_Unstable:          0 kB
Bounce:                0 kB
WritebackTmp:          0 kB
CommitLimit:     1958596 kB
Committed_AS:    2466648 kB
VmallocTotal:   67108864 kB
VmallocUsed:       30940 kB
VmallocChunk:          0 kB
Percpu:             2976 kB
CmaTotal:         409600 kB
CmaFree:          399136 kB
HugePages_Total:       0
HugePages_Free:        0
HugePages_Rsvd:        0
HugePages_Surp:        0
Hugepagesize:       2048 kB
Hugetlb:               0 kB
文件系统        大小  已用  可用 已用% 挂载点
tmpfs           383M  3.1M  380M    1% /run
/dev/mmcblk2p6   14G  8.2G  5.1G   62% /
tmpfs           1.9G     0  1.9G    0% /dev/shm
tmpfs           5.0M   12K  5.0M    1% /run/lock
/dev/mmcblk2p5  224M   27M  180M   13% /boot
tmpfs           383M   80K  383M    1% /run/user/120
tmpfs           383M   64K  383M    1% /run/user/0
Stopping test framework...


Test report generated: report.txt

```
