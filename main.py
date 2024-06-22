if __name__ == "__main__":
    board_config_path = "./boards/visionfive_config.toml"
    controller = MainController(board_config_path)
    
    for os_name in controller.board_config['os_list']:
        results = controller.run_test_suite(os_name)
        controller.generate_report(results)
