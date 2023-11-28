from pyfmi import load_fmu  #, compile_fmu
import numpy as np

# Define your custom Python model using PyFMI Model class
class MyModel:
    def __init__(self):
        pass

    def initialize(self, t0):
        self.time = t0
        self.x = 0.0

    def get_derivatives(self):
        dx_dt = np.cos(self.time)
        return [dx_dt]

    def event_update(self, events):
        pass

    def get_events(self):
        return []

    def event_iteration(self, solve_event):
        pass

    def finalize(self):
        pass

# Create an instance of your custom Python model
model = MyModel()

# Specify the model name and start time
model_name = 'MyModel'
start_time = 0.0

# # Compile the FMU using PyFMI
# fmu = compile_fmu(model, model_name, start_time=start_time)
#
# # Save the FMU to a file
# fmu_path = 'MyModel.fmu'
# fmu.save(fmu_path)


