"""


"""
import os
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
import torch.nn as nn
import torch.optim as optim

from current_development.typology_identifier.generate_models._ml_datasets_and_network_classes import MultipleBuildingsDataset, Net
from current_development.typology_identifier.generate_models._load_ml_parameters import load_ml_parameters


def train_ml_model(path_model_parameters_json, num_epochs=10, batch_size=1, learning_rate=0.0001, continue_training=False):
    """
    Train the machine learning algorithm
    :param path_model_parameters_json:
    :param num_epochs [int]: number of loops of training ?
    :param batch_size [int]: todo ?
    :param learning_rate [float]: todo ?
    """
    # Load model parameter
    identifier, path_training_data, path_test_data, path_model_pkl, shapes, shapes_to_labels_dic, labels_to_shapes_dic,  \
    nb_shapes, pixel_size = load_ml_parameters(path_model_parameters_json)

    path_folder_model = os.path.dirname(os.path.realpath(path_model_parameters_json))

    # Make the data set from the training images
    train_dataset = MultipleBuildingsDataset(classes=shapes,
                                             class_to_label=shapes_to_labels_dic,
                                             root_dir=path_training_data,
                                             transform=transforms.Compose([
                                                 transforms.ToTensor(), transforms.Resize((pixel_size[0], pixel_size[1]))
                                             ]))

    # Load the dataset according to the batch size and shuffle the images
    train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)

    # Make the model
    model = Net(nb_classes=nb_shapes)
    if continue_training :  # if true we load the existing model
        if os.path.isfile(path_model_pkl):  # if the model exist of course
            model.load_state_dict(torch.load(path_model_pkl)) # load the model, otherwise do nothing, keep the default values

    criterion = nn.CrossEntropyLoss() # training criteria
    optimizer = optim.Adam(model.parameters(), lr=learning_rate) # choose optimizer

    # start the training of the model
    model.train()
    print("Start training")
    for e in range(num_epochs): # loop over the epochs
        running_loss = 0  # initialize loss
        for data in train_loader:
            images = data['image']  # load image
            labels = data['label']  # load the label of the image

            optimizer.zero_grad()

            output = model(images)  # pass the image through the model
            loss = criterion(output, labels)  # compute the loss

            loss.backward()

            optimizer.step()

            running_loss += loss.item()  # sums the loss
        else:
            print("Epoch {}/{} - Training loss: {}".format(e+1,num_epochs, running_loss / len(train_loader)))
    print("Training Done")

    # save model
    torch.save(model.state_dict(),path_model_pkl)

    # Write the training parameters in a txt file
    with open(os.path.join(path_folder_model,"model_training_param.txt"),"w") as training_par_file :
        #training_par_file.write(f"number of epochs = {num_epochs}, batch_size = {batch_size}, " \
        #                         "learning_rate = {learning_rate} ")
        training_par_file.write("The number of epochs is: {} and The batch_size is: {} and "
                                "The learning_rate: is: {} \n".format(num_epochs, batch_size,learning_rate ))

# Training
if __name__ == "__main__":
    path_folder_model ="D:\Elie\PhD\Simulation\Input_Data\Typology\machine_learning_training\Tel_Aviv_MOE_test"
    path_model_parameters_json = os.path.join(path_folder_model,"model_param.json")
    train_ml_model(path_model_parameters_json, num_epochs=2, batch_size=8, learning_rate=0.001, continue_training=True)