#!/usr/bin/env python3
"""
데이터셋 무결성 점검 스크립트
- 파일 개수 및 클래스별 분포 확인
- 파일명 규칙 검증
"""

import pathlib
import collections
import re
import os

def check_dataset_integrity():
    """데이터셋 무결성을 점검합니다."""
    
    # 경로 설정
    root = pathlib.Path("outputs")
    
    if not root.exists():
        print("❌ outputs 폴더가 존재하지 않습니다.")
        return False
    
    # 1. 파일 개수 및 클래스별 분포 확인
    print("=== 1. 파일 개수 및 클래스별 분포 ===")
    
    jpg_files = list(root.glob("**/*.jpg"))
    print(f"총 JPG 파일 수: {len(jpg_files)}")
    
    if len(jpg_files) == 0:
        print("❌ JPG 파일이 없습니다.")
        return False
    
    # 파일명 패턴 분석
    pattern = re.compile(r'^(GA|JU)-(\d+)-(OPEN|CLOSE)-(\d+|L|R|180)-(\d{5})\.jpg$')
    
    class_counter = collections.Counter()
    valid_files = 0
    invalid_files = []
    
    for file_path in jpg_files:
        filename = file_path.name
        match = pattern.match(filename)
        
        if match:
            doc_type, template_num, disclosure, angle, sequence = match.groups()
            class_name = f"{doc_type}-{angle}"
            class_counter[class_name] += 1
            valid_files += 1
        else:
            invalid_files.append(filename)
    
    print(f"\n✅ 유효한 파일: {valid_files}개")
    print(f"❌ 잘못된 파일명: {len(invalid_files)}개")
    
    if invalid_files:
        print("잘못된 파일명들:")
        for filename in invalid_files[:10]:  # 처음 10개만 표시
            print(f"  - {filename}")
        if len(invalid_files) > 10:
            print(f"  ... 외 {len(invalid_files) - 10}개")
    
    # 클래스별 분포 출력
    print(f"\n📊 클래스별 분포:")
    for cls, count in sorted(class_counter.items()):
        print(f"  {cls:<10} : {count:4} files")
    
    # 2. 파일명 규칙 검증
    print(f"\n=== 2. 파일명 규칙 검증 ===")
    
    expected_classes = [
        "GA-0", "GA-L", "GA-R", "GA-180",
        "JU-0", "JU-L", "JU-R", "JU-180"
    ]
    
    missing_classes = []
    for expected_class in expected_classes:
        if expected_class not in class_counter:
            missing_classes.append(expected_class)
    
    if missing_classes:
        print(f"❌ 누락된 클래스: {missing_classes}")
    else:
        print("✅ 모든 클래스가 존재합니다.")
    
    # 3. 각 클래스별 파일 수 검증
    print(f"\n=== 3. 클래스별 파일 수 검증 ===")
    
    expected_count_per_class = 200  # 400장 ÷ 8클래스 = 50장, 회전 후 200장
    total_expected = 1600  # 400장 × 4회전
    
    actual_total = sum(class_counter.values())
    
    print(f"예상 총 파일 수: {total_expected}")
    print(f"실제 총 파일 수: {actual_total}")
    
    if actual_total == total_expected:
        print("✅ 총 파일 수가 정확합니다.")
    else:
        print(f"❌ 총 파일 수가 다릅니다. (차이: {actual_total - total_expected})")
    
    # 각 클래스별 검증
    for cls in sorted(class_counter.keys()):
        count = class_counter[cls]
        if count == expected_count_per_class:
            print(f"  ✅ {cls}: {count}개 (정상)")
        else:
            print(f"  ❌ {cls}: {count}개 (예상: {expected_count_per_class}개)")
    
    # 4. 요약
    print(f"\n=== 4. 요약 ===")
    
    if (valid_files == total_expected and 
        len(invalid_files) == 0 and 
        len(missing_classes) == 0):
        print("🎉 데이터셋이 완벽합니다!")
        return True
    else:
        print("⚠️ 데이터셋에 문제가 있습니다. 위의 내용을 확인해주세요.")
        return False

if __name__ == "__main__":
    check_dataset_integrity() 