#!/usr/bin/env python3
"""
데이터셋 분할 스크립트
- outputs/dataset의 이미지들을 train/val/test로 분할
- 7:2:1 비율 (train 70%, val 20%, test 10%)
- 클래스별 균등 분할 보장
"""

import os
import shutil
import random
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import glob

class DatasetSplitter:
    """데이터셋 분할기"""
    
    def __init__(self, src_dir: str, dst_dir: str, train_ratio: float = 0.7, 
                 val_ratio: float = 0.2, test_ratio: float = 0.1, seed: int = 42):
        self.src_dir = Path(src_dir)
        self.dst_dir = Path(dst_dir)
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.seed = seed
        
        # 비율 검증
        total_ratio = train_ratio + val_ratio + test_ratio
        if abs(total_ratio - 1.0) > 0.001:
            raise ValueError(f"비율의 합이 1.0이어야 합니다. 현재: {total_ratio}")
        
        # 랜덤 시드 설정
        random.seed(seed)
        
        # 출력 디렉토리 생성
        self.dst_dir.mkdir(parents=True, exist_ok=True)
        (self.dst_dir / "train").mkdir(exist_ok=True)
        (self.dst_dir / "val").mkdir(exist_ok=True)
        (self.dst_dir / "test").mkdir(exist_ok=True)
    
    def get_class_files(self) -> Dict[str, List[Path]]:
        """클래스별 파일 목록을 가져옵니다."""
        class_files = {}
        
        # 모든 jpg 파일 검색
        jpg_files = list(self.src_dir.glob("*.jpg"))
        
        if not jpg_files:
            raise ValueError(f"소스 디렉토리에 jpg 파일이 없습니다: {self.src_dir}")
        
        # 파일명에서 클래스 추출 (예: GA-1-CLOSE-L-00001.jpg -> GA-L)
        for file_path in jpg_files:
            filename = file_path.name
            parts = filename.split('-')
            
            if len(parts) >= 4:
                doc_type = parts[0]  # GA 또는 JU
                angle = parts[3]     # 0, L, R, 180
                class_name = f"{doc_type}-{angle}"
                
                if class_name not in class_files:
                    class_files[class_name] = []
                class_files[class_name].append(file_path)
        
        return class_files
    
    def split_class_files(self, files: List[Path]) -> Tuple[List[Path], List[Path], List[Path]]:
        """클래스별 파일들을 분할합니다."""
        # 파일 순서 섞기
        shuffled_files = files.copy()
        random.shuffle(shuffled_files)
        
        total_files = len(shuffled_files)
        train_count = int(total_files * self.train_ratio)
        val_count = int(total_files * self.val_ratio)
        
        train_files = shuffled_files[:train_count]
        val_files = shuffled_files[train_count:train_count + val_count]
        test_files = shuffled_files[train_count + val_count:]
        
        return train_files, val_files, test_files
    
    def copy_files(self, files: List[Path], split_name: str, class_name: str):
        """파일들을 지정된 분할 디렉토리로 복사합니다."""
        split_dir = self.dst_dir / split_name / class_name
        split_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in files:
            dst_path = split_dir / file_path.name
            shutil.copy2(file_path, dst_path)
    
    def move_files(self, files: List[Path], split_name: str, class_name: str):
        """파일들을 지정된 분할 디렉토리로 이동합니다."""
        split_dir = self.dst_dir / split_name / class_name
        split_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in files:
            dst_path = split_dir / file_path.name
            shutil.move(str(file_path), str(dst_path))
    
    def split_dataset(self, move: bool = False) -> Dict[str, Dict[str, int]]:
        """전체 데이터셋을 분할합니다."""
        print(f"=== 데이터셋 분할 시작 ===")
        print(f"소스 디렉토리: {self.src_dir}")
        print(f"대상 디렉토리: {self.dst_dir}")
        print(f"분할 비율: train {self.train_ratio:.1%}, val {self.val_ratio:.1%}, test {self.test_ratio:.1%}")
        print(f"랜덤 시드: {self.seed}")
        print(f"모드: {'이동' if move else '복사'}")
        
        # 클래스별 파일 목록 가져오기
        class_files = self.get_class_files()
        
        if not class_files:
            raise ValueError("분할할 파일을 찾을 수 없습니다.")
        
        print(f"\n발견된 클래스: {len(class_files)}개")
        for class_name, files in class_files.items():
            print(f"  {class_name}: {len(files)}개 파일")
        
        # 분할 통계
        stats = {
            "train": {},
            "val": {},
            "test": {}
        }
        
        # 각 클래스별로 분할
        for class_name, files in class_files.items():
            print(f"\n--- {class_name} 분할 중 ---")
            
            train_files, val_files, test_files = self.split_class_files(files)
            
            # 파일 복사/이동
            if move:
                self.move_files(train_files, "train", class_name)
                self.move_files(val_files, "val", class_name)
                self.move_files(test_files, "test", class_name)
            else:
                self.copy_files(train_files, "train", class_name)
                self.copy_files(val_files, "val", class_name)
                self.copy_files(test_files, "test", class_name)
            
            # 통계 저장
            stats["train"][class_name] = len(train_files)
            stats["val"][class_name] = len(val_files)
            stats["test"][class_name] = len(test_files)
            
            print(f"  train: {len(train_files)}개")
            print(f"  val:   {len(val_files)}개")
            print(f"  test:  {len(test_files)}개")
        
        return stats
    
    def print_final_stats(self, stats: Dict[str, Dict[str, int]]):
        """최종 통계를 출력합니다."""
        print(f"\n=== 분할 완료 ===")
        
        total_train = sum(stats["train"].values())
        total_val = sum(stats["val"].values())
        total_test = sum(stats["test"].values())
        total_all = total_train + total_val + total_test
        
        print(f"총 파일 수: {total_all}개")
        print(f"train: {total_train}개 ({total_train/total_all:.1%})")
        print(f"val:   {total_val}개 ({total_val/total_all:.1%})")
        print(f"test:  {total_test}개 ({total_test/total_all:.1%})")
        
        print(f"\n📊 클래스별 분포:")
        for class_name in sorted(stats["train"].keys()):
            train_count = stats["train"][class_name]
            val_count = stats["val"][class_name]
            test_count = stats["test"][class_name]
            total_count = train_count + val_count + test_count
            
            print(f"  {class_name}: train({train_count}) + val({val_count}) + test({test_count}) = {total_count}개")

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="데이터셋 분할 스크립트")
    parser.add_argument("--src", "-s", required=True, help="소스 디렉토리 (outputs/dataset)")
    parser.add_argument("--dst", "-d", required=True, help="대상 디렉토리 (dataset)")
    parser.add_argument("--train", type=float, default=0.7, help="train 비율 (기본값: 0.7)")
    parser.add_argument("--val", type=float, default=0.2, help="val 비율 (기본값: 0.2)")
    parser.add_argument("--test", type=float, default=0.1, help="test 비율 (기본값: 0.1)")
    parser.add_argument("--seed", type=int, default=42, help="랜덤 시드 (기본값: 42)")
    parser.add_argument("--move", action="store_true", help="복사 대신 이동 (원본 파일 삭제)")
    
    args = parser.parse_args()
    
    try:
        # 분할기 생성
        splitter = DatasetSplitter(
            src_dir=args.src,
            dst_dir=args.dst,
            train_ratio=args.train,
            val_ratio=args.val,
            test_ratio=args.test,
            seed=args.seed
        )
        
        # 데이터셋 분할
        stats = splitter.split_dataset(move=args.move)
        
        # 최종 통계 출력
        splitter.print_final_stats(stats)
        
        print(f"\n📁 저장 위치: {args.dst}/")
        print(f"✅ 분할 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 