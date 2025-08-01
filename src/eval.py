#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eval.py   (작성: 2025-08-01 16:08:32 KST)
-----------------------------------------
best_b0.pt 가중치를 로드해 dataset/test 으로 성능 측정
"""
import torch, timm, argparse, pathlib, seaborn as sns, matplotlib.pyplot as plt
from torchvision import datasets, transforms
from sklearn.metrics import classification_report, confusion_matrix

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", type=str, default="dataset/test")
parser.add_argument("--ckpt",     type=str, default="best_b0.pt")
args = parser.parse_args()

tf = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])
ds  = datasets.ImageFolder(args.data_dir, transform=tf)
loader = torch.utils.data.DataLoader(ds, batch_size=64, shuffle=False,
                                     num_workers=4, pin_memory=True)

model = timm.create_model("efficientnet_b0", num_classes=8)
model.classifier = torch.nn.Sequential(
    torch.nn.Dropout(0.3),
    torch.nn.Linear(model.classifier.in_features, 8)
)
model.load_state_dict(torch.load(args.ckpt, map_location="cpu"))
# CPU 환경에서 실행
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device).eval()

preds, gts = [], []
with torch.no_grad(), torch.amp.autocast(device_type='cpu'):
    for x,y in loader:
        p = model(x.to(device)).argmax(1).cpu()
        preds += p.tolist(); gts += y.tolist()

print(classification_report(gts, preds, target_names=ds.classes, digits=3))

cm = confusion_matrix(gts, preds)
sns.heatmap(cm, annot=True, fmt="d",
            xticklabels=ds.classes, yticklabels=ds.classes)
plt.title("Confusion Matrix (Test)"); plt.show()
