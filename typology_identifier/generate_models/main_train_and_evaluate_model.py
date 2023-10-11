"""


"""
import os
from typology_identifier.generate_models._train_ml_model import train_ml_model
from typology_identifier.generate_models._evaluate_ml_model import evaluate_ml_model

# Inputs parameters training
num_epochs = 2
batch_size = 8
learning_rate = 0.001
continue_training = False  # continue the training of an existing model (if it exist) or create a new one
# Inputs parameters evaluation
min_percentage = 0.90
path_folder_model = "D:\Elie\PhD\Simulation\Input_Data\Typology\machine_learning_training\\test_bastien"
#TODO make this path general
path_model_parameters_json = os.path.join(path_folder_model, "model_param.json")

# training
train_ml_model(path_model_parameters_json, num_epochs=num_epochs, batch_size=batch_size, learning_rate=learning_rate,
               continue_training=continue_training)
# Evaluation
evaluate_ml_model(path_model_parameters_json, min_percentage=min_percentage)