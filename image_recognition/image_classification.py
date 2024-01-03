import json
import os
import sys

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image


def image_recognition(
    image_location: str, parent_folder: str = "images"
) -> str:
    img = Image.open(os.path.join(parent_folder, image_location))

    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

    model.eval()
    img_tensor = transforms.ToTensor()(img).unsqueeze_(0)
    outputs = model(img_tensor)
    _, predicted = torch.max(outputs.data, 1)

    with open("./imagenet-labels.json") as f:
        labels = json.load(f)

    result = labels[np.array(predicted)[0]]
    img_name = image_location.split("/")[-1]
    save_name = f"{img_name},{result}"

    print(f"{save_name}")

    return save_name


if __name__ == "__main__":
    url = str(sys.argv[1])
    image_recognition(image_location=url, parent_folder="data")
