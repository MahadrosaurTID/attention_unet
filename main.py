from utils import *
from model import AttentionUNet
from torchvision.utils import make_grid
from train import train_and_test
from loss import dice_coeff, FocalLoss
from dataset import SegmentationDataset
import torch.nn as nn

batch_size = 64
epochs = 100
# dataloaders = get_data_loaders(data_dir, batch_size=batch_size)

data_transforms = {
    # Resize((592, 576), (592, 576)),
    'training': transforms.Compose([HorizontalFlip(), ApplyClaheColor(), Denoise(), ToTensor(), Normalize()]),
    'test': transforms.Compose([HorizontalFlip(), ApplyClaheColor(), Denoise(), ToTensor(), Normalize()]),
}

train_ds = SegmentationDataset("/content/cropped_dataset/train_data", "images", "masks", data_transforms["training"],
                               fraction=None, mask_colormode="rgb")
val_ds = SegmentationDataset("//content/cropped_dataset/val_data", "images", "masks", data_transforms["test"],
                             fraction=None, mask_colormode="rgb")
dataloaders = {"training": DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0),
               "test": DataLoader(val_ds, batch_size=batch_size, shuffle=True, num_workers=0)}


def train():
    model = AttentionUNet()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = FocalLoss()

    trained_model = train_and_test(model, dataloaders, optimizer, criterion, num_epochs=epochs)

    return trained_model


def plot_prediction(model, dataloaders):
    dataiter = iter(dataloaders['test'])
    batch = dataiter.next()

    f = plt.figure(figsize=(20, 20))
    grid_img = make_grid(batch['mask'])
    grid_img = grid_img.permute(1, 2, 0)
    plt.imshow(grid_img)
    plt.title('Ground truth')
    plt.show()

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    inputs = batch['image'].to(device)
    prediction = model(inputs).detach().cpu()

    f = plt.figure(figsize=(20, 20))
    grid_img = make_grid(prediction)
    grid_img = grid_img.permute(1, 2, 0)
    plt.imshow(grid_img)
    plt.title('Prediction')
    plt.show()


trained_model = train()
plot_prediction(trained_model, dataloaders)

plot_batch_from_dataloader(dataloaders, 4)

'''image = cv2.imread('data/training/images/21_training.tif')
image = cv2.copyMakeBorder(image, top=4, bottom=4, left=6, right=5,
                           borderType=cv2.BORDER_CONSTANT)

img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
clahe = cv2.createCLAHE(clipLimit=2.0)
img_yuv[:, :, 0] = clahe.apply(img_yuv[:, :, 0])
img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)
plt.imshow(img_output)
plt.show()'''
