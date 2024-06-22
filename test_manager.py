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
        if method == 'exact':
            return output == expected_output
        elif method == 'contains':
            return expected_output in output
        elif method == 'exit_code':
            return subprocess.run(test_case['command'], shell=True).returncode == expected_output
        elif method == 'special_judge':
            result = subprocess.run(['./tests/{}_special_judge.sh'.format(test_case['name']), output], capture_output=True)
            return result.returncode == 0
