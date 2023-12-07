import timeit
import numpy as np

def calculate_rsi(close_data, period):
    # Placeholder implementation of RSI calculation
    return period

class IndicatorInterpreter:
    def __init__(self, indicators):
        self.indicators = indicators
        self.data = None

    def update_data(self, new_data):
        self.data = new_data

    def evaluate_constraints(self, buy_constraints):
        results = []
        for constraint in buy_constraints:
            try:
                # Replace "rsi(6)"-like strings with corresponding function calls
                modified_constraint = self.replace_indicators(constraint)
                # print(f"Modified Constraint: {modified_constraint}")
                # Measure execution time using timeit
                execution_time = timeit.timeit(lambda: eval(modified_constraint), number=1000)

                # Evaluate the modified constraint using eval
                result = eval(modified_constraint)
                results.append((constraint, result, execution_time))
            except Exception as e:
                print(f"Error evaluating constraint: {constraint}, {e}")
                results.append((constraint, None, None))
        return results

    def replace_indicators(self, constraint):
        # Replace "rsi(6)"-like strings with corresponding function calls and evaluate
        for name, (func, args) in self.indicators.items():
            placeholder = f"{name}"
            constraint = constraint.replace(placeholder, str(func(self.data, *args)))
        return constraint

# Example usage:

indicators = {'rsi(6)': (calculate_rsi, [6]), 'rsi(12)': (calculate_rsi, [12]), 'rsi(24)': (calculate_rsi, [24])}
buy_constraints = ["rsi(6) + rsi(6) + rsi(12) == - 12 + rsi(12) ", "rsi(12) > 10"]

interpreter = IndicatorInterpreter(indicators)

new_data = 20
interpreter.update_data(new_data)

results = interpreter.evaluate_constraints(buy_constraints)

for constraint, result, execution_time in results:
    print(f"Constraint: {constraint}, Result: {result}, Execution Time: {execution_time:.6f} seconds")

print(results)