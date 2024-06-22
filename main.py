from boardtest.main_controller import MainController

if __name__ == "__main__":
    config = """
    log_dir = "./logs"
    [env]
    [serial]
    serial_file = "/dev/ttyUSB0"
    bund_rate   = 115200
    """
    os_list = ["Arch Linux", "Debian/RevyOS", "Fedora", "FreeBSD", "Gentoo", "openAnolis", "OpenBSD", "openCloudOS", "openEuler", "openKylin", "openSUSE", "Ubuntu", "Tina-Linux", "Android 13", "Armbian", "BuildRoot", "OpenHarmony", "FreeRTOS", "RT-Thread", "Zephyr", "OpenWRT", "ThreadX", "NuttX", "Melis", "Bianbu"]
    os_urls = {
        "Arch Linux": "URL_TO_ARCH_LINUX_IMAGE",
        "Debian/RevyOS": "URL_TO_DEBIAN_IMAGE",
        # Add URLs for other OS images here
    }
    
    controller = MainController(config, os_list)
    for os_name, url in os_urls.items():
        uname, os_release, cpu_info = controller.run_test_suite(os_name, url)
        controller.generate_report(uname, os_release, cpu_info)
