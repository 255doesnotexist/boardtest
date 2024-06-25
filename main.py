from main_controller import MainController


flash = False
test = True

if __name__ == "__main__":
    board_config_path = "./boards/visionfive_config.toml"
    serial = "sdwirec_alpha"
    controller = MainController(board_config_path)
    
    for os_name in controller.board_config['os_list']:
        print(f"Running test suite for OS: {os_name}...")
        results = controller.run_test_suite(os_name, serial, flash, test)
        controller.generate_report(results)
