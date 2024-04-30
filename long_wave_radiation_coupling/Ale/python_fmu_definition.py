from pythonfmu import Fmi2Causality, Fmi2Slave, Boolean, Integer, Real, String


class PythonSlave(Fmi2Slave):
    author = "Ale Stawsky"
    description = "Corrects the Long-wave Radiation."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.intOut = 1
        self.realOut = 3.0
        self.booleanVariable = True
        self.stringVariable = "Hello World!"
        self.input_variables = kwargs.get('input_variables')
        self.output_variables = kwargs.get('output_variables')
        for iv in self.input_variables:
            self.register_variable(Real(iv, causality=Fmi2Causality.input))
        for ov in self.output_variables:
            self.register_variable(Real(ov, causality=Fmi2Causality.output))

        # Note:
        # it is also possible to explicitly define getters and setters as lambdas in case the variable is not backed by a Python field.
        # self.register_variable(Real("myReal", causality=Fmi2Causality.output, getter=lambda: self.realOut, setter=lambda v: set_real_out(v))

    def do_step(self, current_time, step_size):
        self.input_variables += 1
        return True

