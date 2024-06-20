import pyautotest

if __name__ == "__main__":
    d = pyautotest.Driver(
        """
        log_dir = "./logs"
        [env]
        [serial]
        serial_file = "/dev/ttyUSB0"
        bund_rate   = 115200
        """
    )

    d.writeln("\x03")
    d.assert_wait_string_ntimes("login", 1, 10)

    d.sleep(3)
    d.writeln("pi")
    d.assert_wait_string_ntimes("Password", 1, 10)

    d.sleep(3)
    d.writeln("pi")

    d.sleep(3)
    res = d.assert_script_run("whoami", 5)