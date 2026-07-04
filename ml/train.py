"""
Fine-tunes a pretrained MobileNetV3-Small on a small custom dataset of
artifact category photos, for the Heritage Trace AI tagging feature.

Expected folder structure before running:

    data/
      pottery/    (20-30 .jpg images)
      coin/
      sculpture/
      tool/
      jewelry/

Usage:
    python train.py

Output:
    model.pt          - the fine-tuned model weights
    class_names.json  - maps model output indices back to category names
"""

import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models

DATA_DIR = "data"
OUTPUT_MODEL = "model.pt"
OUTPUT_CLASSES = "class_names.json"
BATCH_SIZE = 8
EPOCHS = 10
LEARNING_RATE = 0.001


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Standard ImageNet normalization since we're using an ImageNet-pretrained backbone
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    full_dataset = datasets.ImageFolder(DATA_DIR, transform=transform)
    class_names = full_dataset.classes
    print(f"Found classes: {class_names}")
    print(f"Total images: {len(full_dataset)}")

    if len(full_dataset) < 10:
        print("\n⚠️  Very few images found. Add more to data/<category>/ before training "
              "for a model that generalizes at all — aim for at least 15-20 per category.\n")

    # 80/20 train/validation split
    val_size = max(1, int(0.2 * len(full_dataset)))
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)

    # Transfer learning: load ImageNet-pretrained MobileNetV3-Small, replace
    # the final classification layer with one sized for our categories.
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, len(class_names))
    model = model.to(device)

    # Freeze the backbone, only train the new classification head — this is
    # what makes fine-tuning feasible on a tiny dataset without overfitting
    # instantly or needing a GPU.
    for name, param in model.named_parameters():
        if "classifier" not in name:
            param.requires_grad = False

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.classifier.parameters(), lr=LEARNING_RATE)

    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        val_acc = 100 * correct / total if total > 0 else 0
        print(f"Epoch {epoch+1}/{EPOCHS} — loss: {running_loss/len(train_loader):.4f} — val accuracy: {val_acc:.1f}%")

    torch.save(model.state_dict(), OUTPUT_MODEL)
    with open(OUTPUT_CLASSES, "w") as f:
        json.dump(class_names, f)

    print(f"\nSaved model to {OUTPUT_MODEL}")
    print(f"Saved class names to {OUTPUT_CLASSES}")


if __name__ == "__main__":
    main()
