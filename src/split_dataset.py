#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
split_dataset.py  (작성: 2025-08-01 15:02:17 KST)
-------------------------------------------------
원본 이미지 폴더를 train/val/test 하위 폴더로 비율에 맞춰 분할 복사한다.

예시:
    python split_dataset.py ^
        --src  c:/workspace/kdocs_synth/outputs ^
        --dst  c:/workspace/kdocs_synth/dataset ^
        --train 0.7 --val 0.2 --test 0.1 ^
        --seed  42
"""
import argparse, random, shutil, sys, time
from pathlib import Path

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}  # 허용 확장자

# -------------------------------------------------------------- #
def parse_args():
    p = argparse.ArgumentParser(description="이미지 폴더 train/val/test 분할 스크립트")
    p.add_argument("--src", required=True, help="원본 이미지 루트 폴더")
    p.add_argument("--dst", required=True, help="출력 루트 폴더(train/val/test)")
    p.add_argument("--train", type=float, default=0.7, help="train 비율 (기본 0.7)")
    p.add_argument("--val",   type=float, default=0.2, help="val   비율 (기본 0.2)")
    p.add_argument("--test",  type=float, default=0.1, help="test  비율 (기본 0.1)")
    p.add_argument("--seed",  type=int,   default=0,   help="랜덤 시드 고정 값")
    p.add_argument("--move",  action="store_true",
                   help="복사 대신 이동(shutil.move) 수행")
    return p.parse_args()

# -------------------------------------------------------------- #
def get_class_dirs(src_root: Path):
    """클래스별 하위 폴더 목록 반환"""
    return [d for d in src_root.iterdir() if d.is_dir()]

def split_indices(n, ratios):
    """개수 n을 ratios(tuple) 비율로 split한 인덱스 슬라이스 반환"""
    tr, va, te = ratios
    tr_n = round(n * tr)
    va_n = round(n * va)
    te_n = n - tr_n - va_n  # 합이 n이 되도록 보정
    return tr_n, va_n, te_n

def copy_items(file_list, dest_root, class_name, move=False):
    """파일 리스트를 dest_root/class_name/ 경로로 복사/이동"""
    dest_class = dest_root / class_name
    dest_class.mkdir(parents=True, exist_ok=True)
    for src_path in file_list:
        dest_path = dest_class / src_path.name
        if move:
            shutil.move(src_path, dest_path)
        else:
            shutil.copy2(src_path, dest_path)

def main():
    args   = parse_args()
    random.seed(args.seed)
    src    = Path(args.src).expanduser()
    dst    = Path(args.dst).expanduser()
    ratios = (args.train, args.val, args.test)

    if abs(sum(ratios) - 1.0) > 1e-6:
        sys.exit(f"[ERROR] 비율 합계가 1이 아닙니다: train+val+test={sum(ratios)}")

    # 출력 폴더 초기화 안내
    if dst.exists() and any(dst.iterdir()):
        print(f"[WARN] {dst} 폴더가 이미 존재합니다. 기존 파일과 병합될 수 있습니다.", file=sys.stderr)

    class_dirs = get_class_dirs(src)
    if not class_dirs:
        sys.exit(f"[ERROR] {src} 하위에 클래스 폴더가 없습니다.")

    start = time.time()
    for cls_dir in sorted(class_dirs):
        cls_name  = cls_dir.name
        img_files = [p for p in cls_dir.glob("**/*") if p.suffix.lower() in IMG_EXTS]
        if not img_files:
            print(f"[SKIP] {cls_name}: 이미지 없음", file=sys.stderr);  continue

        random.shuffle(img_files)
        tr_n, va_n, te_n = split_indices(len(img_files), ratios)

        # 슬라이스
        tr_files = img_files[:tr_n]
        va_files = img_files[tr_n:tr_n + va_n]
        te_files = img_files[tr_n + va_n:]

        # 복사/이동
        copy_items(tr_files, dst / "train", cls_name, args.move)
        copy_items(va_files, dst / "val",   cls_name, args.move)
        copy_items(te_files, dst / "test",  cls_name, args.move)

        print(f"{cls_name:<10} | train {len(tr_files):4d}  val {len(va_files):4d}  "
              f"test {len(te_files):4d}  (총 {len(img_files)})")

    elapsed = time.time() - start
    print(f"\n✅ 완료! 경과시간: {elapsed:.1f}초  → {dst} 에 train/val/test 폴더가 생성되었습니다.")

# -------------------------------------------------------------- #
if __name__ == "__main__":
    main()
