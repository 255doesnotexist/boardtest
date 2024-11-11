import argparse
from main_controller import MainController

def parse_args():
    parser = argparse.ArgumentParser(
        description="Main entry point for running test suites on different OS images for a specific board."
    )
    
    parser.add_argument(
        "-f", "--flash", action="store_true", default=False,
        help="Enable flashing the OS image before testing. (default: disabled)"
    )
    parser.add_argument(
        "--no-flash", dest="flash", action="store_false",
        help="Disable flashing the OS image before testing."
    )
    parser.add_argument(
        "-t", "--test", action="store_true", default=True,
        help="Enable running tests after flashing. (default: enabled)"
    )
    parser.add_argument(
        "--no-test", dest="test", action="store_false",
        help="Disable running tests after flashing."
    )
    parser.add_argument(
        "-s", "--stdout-log", action="store_true", default=False,
        help="Enable logging output to stdout. (default: disabled)"
    )
    parser.add_argument(
        "--no-stdout-log", dest="stdout_log", action="store_false",
        help="Disable logging output to stdout."
    )
    parser.add_argument(
        "-b", "--board-config", type=str, default="./boards/banana_pi_f3_config.toml",
        help="Path to the board configuration file."
    )
    parser.add_argument(
        "-S", "--serial", type=str, default="sdwirec_alpha",
        help="Serial number of the SD Mux device."
    )
    parser.add_argument(
        "-y", "--yes", action="store_true", default=False,
        help="Always say yes to all prompts. (may dangerous!!!)"
    )
    parser.add_argument(
        "-M", "--mi-sdk-enabled", action="store_true", default=False,
        help="Enable Mi SDK controller for power control. (default: disabled)"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    controller = MainController(args.board_config)
    
    print(f"""
          Serial: {args.serial}
          Board config: {args.board_config}
          Flashing: {args.flash}
          Testing: {args.test}
          Stdout log: {args.stdout_log}
          Mi SDK enabled: {args.mi_sdk_enabled}
          """)

    for os_name in controller.board_config['os_list']:
        print("="*50)
        print(f"Running test suite for OS: {os_name}...")
        print("="*50)
        results = controller.run_test_suite(os_name, args.serial, args.flash, args.test, args.stdout_log, args.yes, args.mi_sdk_enabled)
        print("\n")
        if results is not None:
            controller.generate_report(results)
        else:
            print("No test results need to generate report.")
        print("\n")
