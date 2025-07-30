#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('src')

from data_factory import generate_household_data
from collections import Counter

def test_household_weights():
    """세대구성 사유 가중치를 테스트합니다."""
    
    print("=== 세대구성 사유 가중치 테스트 ===\n")
    
    # 1000번 생성해서 빈도 확인
    n_samples = 1000
    reasons = []
    
    print(f"{n_samples}개 샘플 생성 중...")
    
    for i in range(n_samples):
        household_data = generate_household_data()
        reasons.append(household_data["HOUSEHOLD_REASON"])
        
        if (i + 1) % 100 == 0:
            print(f"진행률: {i + 1}/{n_samples}")
    
    # 빈도 계산
    reason_counts = Counter(reasons)
    
    print(f"\n=== 결과 (총 {n_samples}개) ===")
    print("사유\t\t\t개수\t\t비율")
    print("-" * 50)
    
    # 예상 가중치
    expected_weights = {
        "전입": 30,
        "분가": 20, 
        "세대합가": 15,
        "혼인": 12,
        "출생등록": 8,
        "이혼": 5,
        "입양": 3,
        "이전세대주전출": 3,
        "세대주변경": 2,
        "기타": 1,
        "사망": 1
    }
    
    # 결과 출력
    for reason, count in reason_counts.most_common():
        percentage = (count / n_samples) * 100
        expected = expected_weights.get(reason, 0)
        print(f"{reason:<15}\t{count:>4}개\t\t{percentage:>5.1f}% (예상: {expected}%)")
    
    print("\n=== 세대구성 일자 확인 ===")
    household_data = generate_household_data()
    print(f"세대구성 일자: '{household_data['HOUSEHOLD_DATE']}'")
    
    print(f"\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_household_weights() 