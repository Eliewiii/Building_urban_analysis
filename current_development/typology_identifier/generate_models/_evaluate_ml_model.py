"""


"""

import os.path
import torch
import json
from torch.utils.data import DataLoader
from torchvision import transforms
from current_development.typology_identifier.generate_models._ml_datasets_and_network_classes import MultipleBuildingsDataset, Net
from current_development.typology_identifier.generate_models._load_ml_parameters import load_ml_parameters

def evaluate_ml_model(path_model_parameters_json, min_percentage=None):
    """

    :param path_model_parameters_json:
    :return:
    """
    # Load model parameter
    identifier, path_training_data, path_test_data, path_model_pkl, shapes, shapes_to_labels_dic, labels_to_shapes_dic, \
    nb_shapes, pixel_size = load_ml_parameters(path_model_parameters_json)

    path_folder_model = os.path.dirname(os.path.realpath(path_model_parameters_json))

    # Initialize the model
    model = Net(nb_classes=nb_shapes)  # open the model before the loop of the buildings
    # load the model
    model.load_state_dict(torch.load(path_model_pkl))
    # start evaluation
    model.eval()
    # Make the data set from the training images
    test_dataset = MultipleBuildingsDataset(classes=shapes,
                                            class_to_label=shapes_to_labels_dic,
                                            root_dir=path_test_data,
                                            transform=transforms.Compose([
                                                transforms.ToTensor(), transforms.Resize((pixel_size[0], pixel_size[1]))
                                            ]))
    # Load the dataset according to the batch size and shuffle the images
    test_loader = DataLoader(dataset=test_dataset)
    # Initialize evaluation dictionary
    evaluation_dictionary = make_evaluation_dictionary(shapes_to_labels_dic)

    # Initialize the evaluation variables
    total = 0
    correct = 0
    # Start evaluation
    print("Start evaluation")
    for data in test_loader:
        images = data['image']  # load image
        labels = data['label']  # load label of the image

        outputs = model(images)

        if float(torch.max(outputs.data)) > min_percentage:
            _, predicted = torch.max(outputs.data, 1)
            predicted = int(predicted)
            if predicted == int(labels[0]):
                correct += 1
                evaluation_dictionary[labels_to_shapes_dic[int(labels[0])]]["nb_identified"] = \
                    evaluation_dictionary[labels_to_shapes_dic[int(labels[0])]]["nb_identified"] + 1
        else:
            evaluation_dictionary[labels_to_shapes_dic[int(labels[0])]]["not_identified"] = \
                evaluation_dictionary[labels_to_shapes_dic[int(labels[0])]]["not_identified"] + 1

        total += labels.size(0)
        evaluation_dictionary[labels_to_shapes_dic[int(labels[0])]]["nb_image"] = \
            evaluation_dictionary[labels_to_shapes_dic[int(labels[0])]]["nb_image"] + 1

    print("Overall Accuracy: {} %".format(100 * correct / total))

    for shape in list(evaluation_dictionary.keys()):
        evaluation_dictionary[shape]["true positive (accuracy) [%]"] = evaluation_dictionary[shape]["nb_identified"] / \
                                                                       evaluation_dictionary[shape]["nb_image"] * 100
        evaluation_dictionary[shape]["false positive [%]"] = 100 - (evaluation_dictionary[shape]["nb_identified"] +
                                                              evaluation_dictionary[shape]["not_identified"]) / \
                                                             evaluation_dictionary[shape]["nb_image"] * 100
        evaluation_dictionary[shape]["false negative [%]"] = evaluation_dictionary[shape]["not_identified"] / \
                                                             evaluation_dictionary[shape]["nb_image"] * 100
    print(evaluation_dictionary)

    with open(os.path.join(path_folder_model, "eval_result.json"), "w") as out_file:
        json.dump(evaluation_dictionary, out_file, indent=4)


def make_evaluation_dictionary(shapes_to_labels_dic):
    """

    :param shapes_to_labels_dic:
    :return evaluation_dictionary:
    :return label_to_shape:
    """

    evaluation_dictionary = {}
    for shape in list(shapes_to_labels_dic.keys()):
        evaluation_dictionary[shape] = {"nb_image": 0, "nb_identified": 0, "not_identified": 0,
                                        "true positive (accuracy) [%]": None, "false positive [%]": None,
                                        "false negative [%]": None}

    return evaluation_dictionary

# Evaluation
if __name__ == "__main__":
    path_folder_model = "D:\Elie\PhD\Simulation\Input_Data\Typology\machine_learning_training\Tel_Aviv_MOE"
    path_model_parameters_json = os.path.join(path_folder_model, "model_param.json")
    evaluate_ml_model(path_model_parameters_json, min_percentage=0.90)
