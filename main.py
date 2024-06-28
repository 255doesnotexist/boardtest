from main_controller import MainController


flash = False
test = True
stdout_log = True
board_config_path = "./boards/banana_pi_f3_config.toml"
serial = "sdwirec_alpha"

if __name__ == "__main__":
    controller = MainController(board_config_path)
    
    for os_name in controller.board_config['os_list']:
        print(f"Running test suite for OS: {os_name}...")
        results = controller.run_test_suite(os_name, serial, flash, test, stdout_log)
        controller.generate_report(results)
