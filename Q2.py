from torchvision import models
import matplotlib.pyplot as plt
import torch
from torchinfo import summary
from captum.attr import Saliency, IntegratedGradients, DeepLift
import pickle
torch.manual_seed(42)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu") # For M1 chip, torch.device("mps") is used instead of torch.device("cuda")

def explainer(model, labels_human, DEVICE):
    model.to(DEVICE)
    model.eval()

    # Explainer
    attribution = Saliency(model)

    # Load images and labels
    with open("sample_imagenetdata", 'rb') as f:
        image_data = pickle.load(f)
    fig, ax = plt.subplots(5,3, figsize=(30,50))
    i=0
    for key,value in image_data.items():
        X = value['image']
        y = value['label']
        label = value['label_human']
        X, y = X.to(DEVICE), y.to(DEVICE)
        # Predict the label
        output = model(X)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        predicted_label = torch.max(probabilities, 0)[1].item()

        # Compute the attribution scores using Saliency for true label
        attr_true = attribution.attribute(inputs=X, target=y)

        # Compute the attribution scores using Saliency for predicted label
        attr_pred = attribution.attribute(inputs=X, target=predicted_label)

        # Transform the image to original scale
        X = X * torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1) + torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)

        # Visualize the attribution scores for true label
        explainer_true, _ = torch.max(attr_true.data.abs(), dim=1)
        explainer_true = explainer_true.cpu().detach().numpy()
        explainer_true = (explainer_true-explainer_true.min())/(explainer_true.max()-explainer_true.min())

        # Visualize the attribution scores for predicted label
        explainer_pred, _ = torch.max(attr_pred.data.abs(), dim=1)
        explainer_pred = explainer_pred.cpu().detach().numpy()
        explainer_pred = (explainer_pred-explainer_pred.min())/(explainer_pred.max()-explainer_pred.min())
        ax[i][0].imshow(X[0].permute(1, 2, 0).to('cpu'))
        ax[i][1].imshow(explainer_true[0])
        ax[i][1].set_title(f"True: {label[0]}", fontsize=48)
        ax[i][2].imshow(explainer_pred[0])
        ax[i][2].set_title(f"Predicted: {labels_human[predicted_label][0]}", fontsize=48)
        ax[i][0].set_xticks([])
        ax[i][0].set_yticks([])
        ax[i][1].set_xticks([])
        ax[i][1].set_yticks([])
        ax[i][2].set_xticks([])
        ax[i][2].set_yticks([])
        i+=1
    fig.subplots_adjust(wspace=0, hspace=0, top=1.0)
    plt.savefig("Saliency.png", bbox_inches='tight')

def bespoke_explainer(model, labels_human, DEVICE, images):
    model.to(DEVICE)
    model.eval()

    # Explainer
    attribution = Saliency(model)

    from torchvision import transforms
    from PIL import Image
    transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor()
    ])

    transform_normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )

    fig, ax = plt.subplots(5,3, figsize=(30,50))
    i=0
    for [image, id] in images:
        img = Image.open(image)
        transformed_img = transform(img)

        # Not using a GPU so ignore the "device"
        input = transform_normalize(transformed_img)
        input = input.unsqueeze(0)

        res = model(input)
        probabilities = torch.nn.functional.softmax(res[0], dim=0)
        predicted_label = torch.max(probabilities, 0)[1].item()

        attr_true = attribution.attribute(inputs=input, target=id)
        attr_pred = attribution.attribute(inputs=input, target=predicted_label)

        # Transform the image to original scale
        input = input * torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1) + torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)

        # Visualize the attribution scores for true label
        explainer_true, _ = torch.max(attr_true.data.abs(), dim=1)
        explainer_true = explainer_true.cpu().detach().numpy()
        explainer_true = (explainer_true-explainer_true.min())/(explainer_true.max()-explainer_true.min())

        # Visualize the attribution scores for predicted label
        explainer_pred, _ = torch.max(attr_pred.data.abs(), dim=1)
        explainer_pred = explainer_pred.cpu().detach().numpy()
        explainer_pred = (explainer_pred-explainer_pred.min())/(explainer_pred.max()-explainer_pred.min())
        ax[i][0].imshow(input[0].permute(1, 2, 0).to('cpu'))
        ax[i][1].imshow(explainer_true[0])
        ax[i][1].set_title(f"True: {labels_human[id][0]}", fontsize=48)
        ax[i][2].imshow(explainer_pred[0])
        ax[i][2].set_title(f"Predicted: {labels_human[predicted_label][0]}", fontsize=48)
        ax[i][0].set_xticks([])
        ax[i][0].set_yticks([])
        ax[i][1].set_xticks([])
        ax[i][1].set_yticks([])
        ax[i][2].set_xticks([])
        ax[i][2].set_yticks([])
        i+=1
    fig.subplots_adjust(wspace=0, hspace=0, top=1.0)
    plt.savefig("BespokeSaliency.png", bbox_inches='tight')

def integrated_gradients_explainer(model, labels_human, DEVICE, images):
    model.to(DEVICE)
    model.eval()

    # Explainer
    attribution = IntegratedGradients(model)

    from torchvision import transforms
    from PIL import Image
    transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor()
    ])

    transform_normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )

    fig, ax = plt.subplots(5,3, figsize=(30,50))
    i=0
    for [image, id] in images:
        img = Image.open(image)
        transformed_img = transform(img)

        # Not using a GPU so ignore the "device"
        input = transform_normalize(transformed_img)
        input = input.unsqueeze(0)

        res = model(input)
        probabilities = torch.nn.functional.softmax(res[0], dim=0)
        predicted_label = torch.max(probabilities, 0)[1].item()

        attr_true = attribution.attribute(inputs=input, target=id)
        attr_pred = attribution.attribute(inputs=input, target=predicted_label)

        # Transform the image to original scale
        input = input * torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1) + torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)

        # Visualize the attribution scores for true label
        explainer_true, _ = torch.max(attr_true.data.abs(), dim=1)
        explainer_true = explainer_true.cpu().detach().numpy()
        explainer_true = (explainer_true-explainer_true.min())/(explainer_true.max()-explainer_true.min())

        # Visualize the attribution scores for predicted label
        explainer_pred, _ = torch.max(attr_pred.data.abs(), dim=1)
        explainer_pred = explainer_pred.cpu().detach().numpy()
        explainer_pred = (explainer_pred-explainer_pred.min())/(explainer_pred.max()-explainer_pred.min())
        ax[i][0].imshow(input[0].permute(1, 2, 0).to('cpu'))
        ax[i][1].imshow(explainer_true[0])
        ax[i][1].set_title(f"True: {labels_human[id][0]}", fontsize=48)
        ax[i][2].imshow(explainer_pred[0])
        ax[i][2].set_title(f"Predicted: {labels_human[predicted_label][0]}", fontsize=48)
        ax[i][0].set_xticks([])
        ax[i][0].set_yticks([])
        ax[i][1].set_xticks([])
        ax[i][1].set_yticks([])
        ax[i][2].set_xticks([])
        ax[i][2].set_yticks([])
        i+=1
    fig.subplots_adjust(wspace=0, hspace=0, top=1.0)
    plt.savefig("IntegratedGradients.png", bbox_inches='tight')

def deeplift_explainer(model, labels_human, DEVICE, images):
    model.to(DEVICE)
    model.eval()

    # Explainer
    attribution = DeepLift(model)

    from torchvision import transforms
    from PIL import Image
    transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor()
    ])

    transform_normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )

    fig, ax = plt.subplots(5,3, figsize=(30,50))
    i=0
    for [image, id] in images:
        img = Image.open(image)
        transformed_img = transform(img)

        # Not using a GPU so ignore the "device"
        input = transform_normalize(transformed_img)
        input = input.unsqueeze(0)

        res = model(input)
        probabilities = torch.nn.functional.softmax(res[0], dim=0)
        predicted_label = torch.max(probabilities, 0)[1].item()

        attr_true = attribution.attribute(inputs=input, target=id)
        attr_pred = attribution.attribute(inputs=input, target=predicted_label)

        # Transform the image to original scale
        input = input * torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1) + torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)

        # Visualize the attribution scores for true label
        explainer_true, _ = torch.max(attr_true.data.abs(), dim=1)
        explainer_true = explainer_true.cpu().detach().numpy()
        explainer_true = (explainer_true-explainer_true.min())/(explainer_true.max()-explainer_true.min())

        # Visualize the attribution scores for predicted label
        explainer_pred, _ = torch.max(attr_pred.data.abs(), dim=1)
        explainer_pred = explainer_pred.cpu().detach().numpy()
        explainer_pred = (explainer_pred-explainer_pred.min())/(explainer_pred.max()-explainer_pred.min())
        ax[i][0].imshow(input[0].permute(1, 2, 0).to('cpu'))
        ax[i][1].imshow(explainer_true[0])
        ax[i][1].set_title(f"True: {labels_human[id][0]}", fontsize=48)
        ax[i][2].imshow(explainer_pred[0])
        ax[i][2].set_title(f"Predicted: {labels_human[predicted_label][0]}", fontsize=48)
        ax[i][0].set_xticks([])
        ax[i][0].set_yticks([])
        ax[i][1].set_xticks([])
        ax[i][1].set_yticks([])
        ax[i][2].set_xticks([])
        ax[i][2].set_yticks([])
        i+=1
    fig.subplots_adjust(wspace=0, hspace=0, top=1.0)
    plt.savefig("DeepLift.png", bbox_inches='tight')

if __name__=="__main__":

    # Create the model
    model_googlenet= models.googlenet(pretrained=True)

    # Summary of the model
    print(summary(model=model_googlenet, input_size=(1, 3, 224, 224), col_width=20, col_names=['input_size', 'output_size', 'num_params', 'trainable'], row_settings=['var_names'], verbose=0))

    # Load classes to human readable labels
    labels_human = {}
    with open(f'imagenet1000_clsidx_to_labels.txt') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().replace("'", "").strip(",")
            if "{" in line or "}" in line:
                continue
            else:
                idx = int(line.split(":")[0])
                lbl = line.split(":")[1].split(",")
                labels_human[idx] = [x.strip() for x in lbl]
    # Explainer
    explainer(model_googlenet, labels_human,  DEVICE)

    images = [['golden_retriever.JPEG', 207], ['black_swan.JPEG', 100], ['goldfish.JPEG', 1], ['hummingbird.JPEG', 94], ['daisy.JPEG', 985]]

    bespoke_explainer(model_googlenet, labels_human, DEVICE, images)
    integrated_gradients_explainer(model_googlenet, labels_human, DEVICE, images)
    deeplift_explainer(model_googlenet, labels_human, DEVICE, images)
