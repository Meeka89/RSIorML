
#Knowledge Distillation in PyTorch
# Basic Setup
import os
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import random_split, DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torchvision import models
import torchvision.transforms as transforms
from torchvision.datasets import CIFAR10

print(f"PyTorch Version: {torch.__version__}")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device used: {device.type}")
# Load Dataset
# define transform for CIFAR-10 dataset
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.4914, 0.4822, 0.4465],  # CIFAR-10 means
                         std=[0.2023, 0.1994, 0.2010])
])

# load full CIFAR-10 train set
full_trainset = CIFAR10(root='./data', train=True, download=True, transform=transform)

# calculate split sizes for train and validation sets
train_size = int(0.9 * len(full_trainset))
val_size = len(full_trainset) - train_size

# perform split
train_subset, val_subset = random_split(full_trainset, [train_size, val_size])
print(f"Train samples: {train_size}")
print(f"Validation samples: {val_size}")

# create DataLoaders
train_loader = DataLoader(train_subset, batch_size=128, shuffle=True)
val_loader = DataLoader(val_subset, batch_size=128, shuffle=False)

# CIFAR-10 test set and loader for accuracy evaluation
test_set = CIFAR10(root='./data', train=False, download=True, transform=transform)
test_loader = DataLoader(test_set, batch_size=128, shuffle=False)
print(f"Test samples: {len(test_set)}")
# Define Models
def setup_models(device):
    """
    Setup teacher and student wrapper
    """

    # teacher: ResNet50 pretrained on ImageNet, re-headed for CIFAR-10
    teacher = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
    teacher.fc = nn.Linear(2048, 10)
    teacher = teacher.to(device)

    # student: ResNet18 without pretrained weights
    student = models.resnet18(weights=None)
    student.fc = nn.Linear(512, 10) 
    student = student.to(device) 

    # define the intermediate feature channels for both teacher and student
    student_channels = [64, 128, 256, 512] 
    teacher_channels = [256, 512, 1024, 2048]

    # create projection layers to align teacher's feature maps with student's feature maps
    proj_layers = [
        FeatureProjector(in_c, out_c).to(device)
        for in_c, out_c in zip(student_channels, teacher_channels)
    ]

    # wrap the student model with the projection layers
    student_wrapper = StudentWrapper(student, proj_layers).to(device)

    return teacher, student_wrapper

class FeatureProjector(nn.Module):
    """
    Feature projector to match student -> teacher feature shapes
    """

    def __init__(self, in_channels, out_channels):
        super().__init__()

        # define a 1x1 convolutional layer to project feature maps
        self.proj = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x, target_shape):
        
        # check if the spatial dimensions of the input match the target shape
        if x.shape[2:] != target_shape[2:]:
        
            # adjust spatial dimensions using adaptive average pooling
            x = F.adaptive_avg_pool2d(x, output_size=target_shape[2:])

        # apply the projection layer to transform feature maps
        return self.proj(x)

class StudentWrapper(nn.Module):
    """
    Wrapper for the student model with projection layers
    """

    def __init__(self, student_model, proj_layers):
        super().__init__()

        # store student model
        self.model = student_model  

        # store projection layers for feature alignment
        self.projections = nn.ModuleList(proj_layers)  

    def forward(self, x):
        
        # collect intermediate features from ResNet blocks
        features = []  
        x = self.model.conv1(x)
        x = self.model.bn1(x)
        x = self.model.relu(x)
        x = self.model.maxpool(x)
        for i, block in enumerate([self.model.layer1, self.model.layer2, self.model.layer3, self.model.layer4]):
            # pass through ResNet blocks
            x = block(x)  
            
            # append features from each block
            features.append(x)  

        # pool the final feature map and compute logits
        pooled = F.adaptive_avg_pool2d(x, (1, 1))  
        flat = torch.flatten(pooled, 1)  
        logits = self.model.fc(flat)  
        
        return logits, features  

    def project_features(self, features, target_shapes):
        """
        Project student features to match the shapes of teacher features.
        """

        return [
            proj(s_feat, t_shape)
            for s_feat, t_shape, proj in zip(features, target_shapes, self.projections)
        ]

def extract_teacher_features(model, x, layers=[1, 2, 3, 4]):
    """
    Extract teacher logits and intermediate features
    """

    # collect intermediate features from ResNet blocks
    features = []
    x = model.conv1(x)
    x = model.bn1(x)
    x = model.relu(x)
    x = model.maxpool(x)
    for i, block in enumerate([model.layer1, model.layer2, model.layer3, model.layer4]):
        x = block(x)
        if (i + 1) in layers:
            features.append(x)

    # pool the final feature map and compute logits
    pooled = F.adaptive_avg_pool2d(x, (1, 1))  # [B, C, 1, 1]
    flat = torch.flatten(pooled, 1)            # [B, C]
    logits = model.fc(flat)                    # [B, 10]
    return logits, features

# setup models
teacher, student_wrapper = setup_models(device)
# Evaluation Functions for Size, Latency and Accuracy
def count_params(model):
    """
    Function to count trainable parameters
    """

    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def measure_latency(model, input_size=(1, 3, 32, 32), device='cuda', repetitions=50):
    """
    Function to measure average inference latency over multiple runs
    """

    model.eval()
    inputs = torch.randn(input_size).to(device)
    with torch.no_grad():
        # Warm-up
        for _ in range(10):
            _ = model(inputs)
        # Measure
        times = []
        for _ in range(repetitions):
            start = time.time()
            _ = model(inputs)
            end = time.time()
            times.append(end - start)
    return (sum(times) / repetitions) * 1000  # ms

def evaluate_accuracy(model, dataloader):
    """
    Evaluate accuracy given model and loader
    """

    model.eval()
    model.to(device)
    correct, total = 0, 0
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    accuracy = correct / total
    return accuracy
# Fine-tuning the Teacher
def train_teacher(teacher, loader, epochs, tag, lr=1e-3, save_path="model.pth"):
    """
    Trains a model with Adam and cross-entropy loss.
    Loads from save_path if it exists.
    """

    if os.path.exists(save_path):
        print(f"Model already trained. Loading from {save_path}")
        teacher.load_state_dict(torch.load(save_path))
        return teacher

    # no saved model found. training from given model state

    optimizer = torch.optim.Adam(teacher.parameters(), lr=1e-3)
    teacher.train()

    for epoch in range(epochs):
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            logits, _ = extract_teacher_features(teacher, inputs)

            loss = F.cross_entropy(logits, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        accuracy = evaluate_accuracy(teacher, val_loader)
        print(f"({tag})\tEpoch {epoch+1}: loss={loss.item():.4f}, Accuracy (validation): {accuracy*100:.2f}%")
        teacher.train()

    if save_path:
        torch.save(teacher.state_dict(), save_path)
        print(f"Training complete. Model saved to {save_path}")

    return teacher

# train the teacher on CIFAR-10
teacher = train_teacher(teacher, train_loader, epochs=25, tag="Fine-tuning teacher", save_path="tuned_pretrained_resnet50_on_CIFAR10.pth")
# Training the Student via Distillation
def distillation_loss(student_logits, teacher_logits, targets, T=5.0, alpha=0.7):
    """
    Combine soft and hard targets using KL divergence and cross-entropy
    T = temperature, alpha = weighting between soft and hard losses
    """

    # soft target loss (teacher softmax vs student softmax)
    soft_targets = F.kl_div(
        F.log_softmax(student_logits / T, dim=1),
        F.softmax(teacher_logits / T, dim=1),
        reduction='batchmean'
    ) * (T * T)

    # hard label loss
    hard_loss = F.cross_entropy(student_logits, targets)
    return alpha * soft_targets + (1 - alpha) * hard_loss

def student_training_step(inputs, labels, teacher, student_wrapper, optimizer, device):
    """
    Perform a single training step for the student model using knowledge distillation.
    """

    inputs, labels = inputs.to(device), labels.to(device)

    # extract teacher logits and intermediate features
    with torch.no_grad():
        teacher_logits, teacher_feats = extract_teacher_features(teacher, inputs)

    # extract student logits and intermediate features
    student_logits, student_feats = student_wrapper(inputs)
    projected_feats = student_wrapper.project_features(student_feats, [t.shape for t in teacher_feats])
    
    # calculate loss from features difference
    feat_loss = sum(F.mse_loss(p, t.detach()) for p, t in zip(projected_feats, teacher_feats))

    # calculate loss from output distribution, and include feature loss
    loss = distillation_loss(student_logits, teacher_logits, labels) + 0.1 * feat_loss

    # optimize with loss
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss.item()

def train_student(teacher, student_wrapper, dataloader, epochs, save_path="student_distilled.pth"):
    """
    Trains a student model using knowledge distillation from a teacher model.
    """

    # setup optimizer
    optimizer = torch.optim.Adam(student_wrapper.parameters(), lr=1e-3)

    # train the student using the teacher's output as soft targets
    teacher.eval()  

    best_val_acc = 0.0
    
    # reduce LR if validation loss doesn't improve for 3 epochs
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)

    for epoch in range(epochs):
        student_wrapper.train()
        running_loss = 0
        for inputs, labels in dataloader:
            loss = student_training_step(inputs, labels, teacher, student_wrapper, optimizer, device)
            running_loss += loss

        val_acc = evaluate_accuracy(student_wrapper.model, val_loader)
        print(f"[(Training student)\tEpoch {epoch+1}] Loss = {running_loss/len(dataloader):.4f} | Val Acc = {val_acc*100:.2f}%")
        scheduler.step(loss)

        # save best checkpoint
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(student_wrapper.state_dict(), save_path)
            print("New best model saved.")

    # load best checkpoint
    student_wrapper.load_state_dict(torch.load(save_path))
    student = student_wrapper.model

    return student

# trigger student training
student = train_student(teacher, student_wrapper, train_loader, epochs = 25)
# Model Comparison Code
# compare size, latency, and accuracy
teacher_params = count_params(teacher)
student_params = count_params(student)

teacher_latency = measure_latency(teacher, device=device)
student_latency = measure_latency(student, device=device)

teacher_acc = evaluate_accuracy(teacher, test_loader)
student_acc = evaluate_accuracy(student, test_loader)

print(f"Teacher Params: {teacher_params / 1e6:.2f}M")
print(f"Student Params: {student_params / 1e6:.2f}M")
print(f"Teacher Latency: {teacher_latency:.2f} ms")
print(f"Student Latency: {student_latency:.2f} ms")
print(f"Teacher Test Accuracy: {teacher_acc * 100:.2f}%")
print(f"Student Test Accuracy: {student_acc * 100:.2f}%")
# Training a baseline student (ResNet18 from scratch)
# define baseline student: ResNet18 training from scratch on its own, re-headed for CIFAR-10
baseline_student = models.resnet18(weights=None)
baseline_student.fc = nn.Linear(512, 10).to(device)
baseline_student = baseline_student.to(device)

# Train the baseline student on CIFAR-10
baseline_student = train_teacher(baseline_student, train_loader, epochs=25, tag="baseline-student", save_path="baseline_student.pth")

# Evaluate baseline student
baseline_student_acc = evaluate_accuracy(baseline_student, test_loader)
print(f"\nBaseline Student Test Accuracy: {baseline_student_acc * 100:.2f}%")