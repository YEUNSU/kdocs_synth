#!/usr/bin/env python3
"""
클래스 가중치 계산 스크립트
- train 데이터셋의 클래스별 분포를 분석하여 가중치 계산
- 데이터 불균형 해결을 위한 가중치 생성
"""

import json
import torch
import pathlib
from typing import Dict, List
import argparse

def compute_class_weights(train_dir: str, output_file: str = "class_weights.json") -> Dict[str, float]:
    """클래스별 가중치를 계산합니다."""
    
    train_path = pathlib.Path(train_dir)
    
    if not train_path.exists():
        raise ValueError(f"train 디렉토리가 존재하지 않습니다: {train_dir}")
    
    # 클래스별 파일 수 계산
    class_counts = {}
    class_names = []
    
    for class_dir in train_path.iterdir():
        if class_dir.is_dir():
            class_name = class_dir.name
            # dataset 폴더는 제외 (분할 결과가 아닌 실제 클래스만)
            if class_name == "dataset":
                continue
            file_count = len(list(class_dir.glob("*.jpg")))
            class_counts[class_name] = file_count
            class_names.append(class_name)
    
    if not class_counts:
        raise ValueError(f"train 디렉토리에 클래스 폴더가 없습니다: {train_dir}")
    
    # 클래스 이름 정렬
    class_names.sort()
    
    # 파일 수를 리스트로 변환 (정렬된 순서)
    frequencies = [class_counts[name] for name in class_names]
    
    print(f"=== 클래스별 파일 수 ===")
    for i, class_name in enumerate(class_names):
        print(f"  {class_name}: {frequencies[i]}개")
    
    # 가중치 계산 (로그 기반)
    # log1p(x * 0.02)를 사용하여 작은 값에도 적절한 가중치 부여
    weights = (1.0 / torch.log1p(torch.tensor(frequencies, dtype=torch.float) * 0.02)).tolist()
    
    # 가중치 정규화 (최대값을 1.0으로)
    max_weight = max(weights)
    normalized_weights = [w / max_weight for w in weights]
    
    # 결과 딕셔너리 생성
    weight_dict = dict(zip(class_names, normalized_weights))
    
    print(f"\n=== 계산된 가중치 ===")
    for class_name in class_names:
        print(f"  {class_name}: {weight_dict[class_name]:.4f}")
    
    # JSON 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(weight_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 가중치 파일 저장 완료: {output_file}")
    
    return weight_dict

def analyze_class_distribution(train_dir: str):
    """클래스 분포를 분석합니다."""
    
    train_path = pathlib.Path(train_dir)
    
    if not train_path.exists():
        print(f"❌ train 디렉토리가 존재하지 않습니다: {train_dir}")
        return
    
    # 클래스별 파일 수 계산
    class_counts = {}
    total_files = 0
    
    for class_dir in train_path.iterdir():
        if class_dir.is_dir():
            class_name = class_dir.name
            # dataset 폴더는 제외 (분할 결과가 아닌 실제 클래스만)
            if class_name == "dataset":
                continue
            file_count = len(list(class_dir.glob("*.jpg")))
            class_counts[class_name] = file_count
            total_files += file_count
    
    if not class_counts:
        print(f"❌ train 디렉토리에 클래스 폴더가 없습니다: {train_dir}")
        return
    
    print(f"=== 클래스 분포 분석 ===")
    print(f"총 파일 수: {total_files}개")
    print(f"클래스 수: {len(class_counts)}개")
    
    # 클래스별 비율 계산
    class_names = sorted(class_counts.keys())
    
    print(f"\n📊 클래스별 분포:")
    for class_name in class_names:
        count = class_counts[class_name]
        ratio = count / total_files * 100
        print(f"  {class_name}: {count:4}개 ({ratio:5.1f}%)")
    
    # 불균형도 계산
    min_count = min(class_counts.values())
    max_count = max(class_counts.values())
    imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
    
    print(f"\n📈 불균형도 분석:")
    print(f"  최소 클래스: {min_count}개")
    print(f"  최대 클래스: {max_count}개")
    print(f"  불균형 비율: {imbalance_ratio:.2f}:1")
    
    if imbalance_ratio > 2.0:
        print(f"  ⚠️  클래스 불균형이 심합니다. 가중치 적용을 권장합니다.")
    else:
        print(f"  ✅ 클래스 분포가 비교적 균형적입니다.")

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="클래스 가중치 계산 스크립트")
    parser.add_argument("--train_dir", "-t", default="dataset/train", help="train 디렉토리 경로")
    parser.add_argument("--output", "-o", default="class_weights.json", help="출력 파일명")
    parser.add_argument("--analyze", "-a", action="store_true", help="분포 분석만 실행")
    
    args = parser.parse_args()
    
    try:
        if args.analyze:
            # 분포 분석만 실행
            analyze_class_distribution(args.train_dir)
        else:
            # 가중치 계산 및 저장
            weights = compute_class_weights(args.train_dir, args.output)
            
            # 추가 분석
            print(f"\n" + "="*50)
            analyze_class_distribution(args.train_dir)
            
            print(f"\n✅ 가중치 계산 완료!")
            print(f"📁 저장 위치: {args.output}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 