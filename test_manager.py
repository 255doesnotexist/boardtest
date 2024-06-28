import os
import subprocess
import time
import toml

class TestManager:
    def __init__(self, test_config):
        """Initialize the test manager with the given test configuration."""
        self.test_config = toml.load(test_config)
    
    def execute_tests(self, framework):
        """Execute the tests defined in the test configuration."""
        results = []
        for test in self.test_config['tests']:
            cmd = test['command']
            expected_output = test.get('expected_output')
            timeout = test.get('timeout', 10)
            method = test.get('method', 'exact')
            
            output = framework.run_command(cmd, timeout)
            
            result = self.evaluate_result(output, expected_output, method, test)
            results.append(result)
        
        return results
    
    def evaluate_result(self, output, expected_output, method, test_case):
        """Evaluate the result of a test case based on the specified method."""
        result = {
            "command": test_case['command'],
            "output": output,
            "expected_output": expected_output,
            "method": method,
            "success": False,
            "reason": "",
            "return_code": None
        }

        if method == 'exact':
            result['success'] = output.strip() == expected_output
            if not result['success']:
                result['reason'] = f"Output does not match expected output. Got: {output.strip()}"
        elif method == 'contains':
            result['success'] = expected_output in output
            if not result['success']:
                result['reason'] = f"Expected output not found in output. Got: {output}"
        elif method == 'exit_code':
            process = subprocess.run(test_case['command'], shell=True)
            result['return_code'] = process.returncode
            result['success'] = process.returncode == expected_output
            if not result['success']:
                result['reason'] = f"Return code does not match expected output. Got: {process.returncode}"
        elif method == 'special_judge':
            result_process = subprocess.run(['./tests/{}_special_judge.sh'.format(test_case['name']), output], capture_output=True)
            result['return_code'] = result_process.returncode
            result['success'] = result_process.returncode == 0
            if not result['success']:
                result['reason'] = f"Special judge script returned non-zero exit code. Got: {result_process.returncode}"

        return result