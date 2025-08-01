#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
train.py   (최초 작성: 2025-08-01 16:08:32 KST)
-----------------------------------------------
• dataset/train · val 하위 폴더를 읽어 EfficientNet-B0 8-class 분류 학습
• class_weights.json → 불균형 보정
• AMP + CosineWarmup 스케줄러 적용
"""

import json, math, time, argparse, pathlib, torch, timm, torch.nn as nn
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import datasets, transforms
from torch.cuda.amp import autocast, GradScaler
from torch.optim.lr_scheduler import CosineAnnealingLR
from sklearn.metrics import confusion_matrix, classification_report

# --------- 하이퍼파라미터 & 인자 ---------
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", type=str, default="dataset")
    p.add_argument("--epochs",   type=int, default=50)
    p.add_argument("--batch",    type=int, default=32)
    p.add_argument("--lr",       type=float, default=1e-4)
    p.add_argument("--wd",       type=float, default=1e-2)
    p.add_argument("--weights",  type=str, default="class_weights.json")
    p.add_argument("--ckpt",     type=str, default="best_b0.pt")
    return p.parse_args()

# --------- 데이터 변환 ---------
train_tf = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.RandomRotation(10, fill=255),
    transforms.ColorJitter(0.2,0.2,0,0),
    transforms.GaussianBlur(3),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])
val_tf = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])

# --------- 메인 ---------
def main():
    args = parse_args()
    root = pathlib.Path(args.data_dir)

# ---------- ① 데이터셋 & 샘플러 ----------  # 2025-08-01 18:07 KST
    train_ds = datasets.ImageFolder(root/"train", transform=train_tf)
    val_ds   = datasets.ImageFolder(root/"val",   transform=val_tf)

    # 클래스 가중치 로드 (2025-08-01 21:15 KST - 이중 보정 제거)
    weights_dict = json.load(open(args.weights))
    # 클래스 순서에 맞게 가중치 배열 생성
    cls_w = torch.tensor([weights_dict[cls] for cls in train_ds.classes], dtype=torch.float)
    sample_w = [cls_w[y] for _,y in train_ds.samples]
    sampler = WeightedRandomSampler(sample_w, len(sample_w), replacement=True)

    train_loader = DataLoader(train_ds, batch_size=args.batch,
                              sampler=sampler,  num_workers=4, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch*2,
                              shuffle=False, num_workers=4, pin_memory=True)

    # ── 모델 & 옵티마이저 ───────────────────────────────────────────────
    model = timm.create_model("efficientnet_b0", pretrained=True)
    model.classifier = nn.Sequential(
        nn.Dropout(0.3), nn.Linear(model.classifier.in_features, 8)
    )
    # CPU 환경에서 실행
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    opt  = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.wd)
    sched= CosineAnnealingLR(opt, T_max=args.epochs*len(train_loader))
    scaler = GradScaler()
    criterion = nn.CrossEntropyLoss()  # 가중치 제거 - Sampler만 사용

    best_f1 = 0.0
    for epoch in range(1, args.epochs+1):
        # ── Train ──────────────────────────────────────────────
        model.train();   t0=time.time()
        for x,y in train_loader:
            x,y = x.to(device), y.to(device)
            opt.zero_grad(set_to_none=True)
            with autocast():
                loss = criterion(model(x), y)
            scaler.scale(loss).backward()
            scaler.step(opt); scaler.update(); sched.step()
        # ── Validate ───────────────────────────────────────────
        model.eval();  correct, preds, gts = 0, [], []
        with torch.no_grad(), autocast():
            for x,y in val_loader:
                out = model(x.to(device))
                p   = out.argmax(1).cpu()
                preds += p.tolist();  gts += y.tolist()
        preds_t = torch.tensor(preds);  gts_t = torch.tensor(gts)
        acc = (preds_t==gts_t).float().mean().item()
        # macro-F1 직접 계산 (간단 버전)
        f1 = 0
        for c in range(8):
            tp = ((preds_t==c)&(gts_t==c)).sum()
            fp = ((preds_t==c)&(gts_t!=c)).sum()
            fn = ((preds_t!=c)&(gts_t==c)).sum()
            if tp+fp and tp+fn:
                prec, rec = tp/(tp+fp), tp/(tp+fn)
                f1 += 2*prec*rec/(prec+rec)
        f1 /= 8

        print(f"E{epoch:02d}  acc={acc:.3f}  f1={f1:.3f}  "
              f"loss={loss.item():.4f}  [{time.time()-t0:.1f}s]")

        # 5 에포크마다 혼동 행렬 출력 (2025-08-01 21:15 KST 추가)
        if epoch % 5 == 0:
            print(f"\n📊 Epoch {epoch} Confusion Matrix:")
            cm = confusion_matrix(gts, preds)
            print(cm)
            print(f"📈 Classification Report:")
            print(classification_report(gts, preds, target_names=val_ds.classes, digits=3))

        if f1 > best_f1:
            best_f1 = f1
            torch.save(model.state_dict(), args.ckpt)
            print(f"  ↳ ✅ best updated!  (f1={best_f1:.3f})")

if __name__ == "__main__":
    main()
