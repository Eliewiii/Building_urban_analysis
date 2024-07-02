from urban_canopy.urban_canopy import UrbanCanopy



def eval_funct(urban_canopy_obj : UrbanCanopy,fitness_func,id_roof_technology :str =""):
    """

    """
    #run BIPV simulation

    #Run KPI

    # extract the KPI dict
    kpi_dict = urban_canopy_obj.get_kpi()  # something like this

    eval_it = fitness_func(kpi_dict)

    return "zob"





# Function to wrap the eval_func with a custom object
def create_eval_func_with_custom_object(custom_obj,fitness_func):
    def wrapped_eval_func(**kwargs):
        return eval_funct(custom_obj,fitness_func, **kwargs)
    return wrapped_eval_func





# Define the search space with different boundaries
CATEGORIES = ['A', 'B', 'C']
instrumentation = ng.p.Instrumentation(
    int_var_1=ng.p.Scalar(lower=0, upper=5).set_integer_casting(),  # Integer variable 1 with bounds 0 to 5
    int_var_2=ng.p.Scalar(lower=5, upper=10).set_integer_casting(),  # Integer variable 2 with bounds 5 to 10
    float_var_1=ng.p.Scalar(lower=0, upper=5),  # Float variable 1 with bounds 0 to 5
    float_var_2=ng.p.Scalar(lower=5, upper=10),  # Float variable 2 with bounds 5 to 10
    cat_var=ng.p.Choice(range(len(CATEGORIES)))  # Categorical variable with 3 categories
)

budget = 100