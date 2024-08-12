"""


"""

import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image


class MultipleBuildingsDataset(Dataset):
    """
    Dataset for training and testing, extracting the data from a folder with a given tree/structure
    """

    def __init__(self, classes, class_to_label, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.len = 0
        self.idx_to_image = {}
        idx = 0
        for class_ in classes:
            files = os.listdir(os.path.join(root_dir, class_))
            self.len += len(files)
            for file in files:
                img_name = os.path.join(root_dir, class_, file)
                self.idx_to_image[idx] = [img_name, class_to_label[class_]]
                idx += 1

    def __len__(self):
        return self.len

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        img_name, label = self.idx_to_image[idx]
        image = Image.open(img_name)

        if self.transform:
            image = self.transform(image)

        sample = {'image': image, 'label': label}
        return sample

'''

# class SingleBuildingDataset(Dataset):
#     """
#     Dataset to tests only one images
#     """
#
#     def __init__(self, path_image, transform=None):
#         self.path_image = path_image
#         self.transform = transform
#         self.len = 1  # just one image
#         self.idx_to_image = {0: self.path_image}
#
#
#
#     def __len__(self):
#         return self.len
#
#     def __getitem__(self, idx):
#         if torch.is_tensor(idx):
#             idx = idx.tolist()
#         img_name = self.idx_to_image[idx]
#         image = Image.open(img_name)
#
#         if self.transform:
#             image = self.transform(image)
#
#         sample = {'image': image, 'label': label}
#         return sample
'''

class SingleBuildingDataset(Dataset):
    """
    Dataset to tests only one images
    """

    def __init__(self, path_image, transform=None):
        self.image = Image.open(path_image)
        self.len = 1  # just one image

        if transform:
            self.image = transform(self.image)

    def __len__(self):
        return self.len

    def __getitem__(self, idx):
        return self.image


class Net(nn.Module):
    def __init__(self, nb_classes):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(5776, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, nb_classes)
        self.softmax = nn.Softmax(1)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1)  # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        x = self.softmax(x)
        return x
