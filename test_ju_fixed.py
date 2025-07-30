#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('src')

from data_factory import create_record
from templates_juga import create_template
import cv2
import numpy as np

def test_ju_fixed_logic():
    """수정된 세대구성 사유 및 일자 로직을 테스트합니다."""
    
    # 출력 디렉토리 생성
    output_dir = "outputs/test_ju_fixed"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== 수정된 JU 로직 테스트 ===\n")
    
    # JU_template1_TY11로 테스트
    template_name = "JU_template1_TY11"
    
    for i in range(5):  # 5개 샘플 생성
        print(f"[{i+1}/5] 테스트 샘플 생성")
        
        try:
            # 데이터 생성
            record = create_record(doc_type="JU", options={
                "members_count": 3,
                "mask_jumin": True
            })
            
            # 템플릿 생성
            template = create_template(
                doc_type="JU",
                template_name=template_name,
                max_members=3,
                mask_jumin=True
            )
            
            # 이미지 렌더링
            img = template.render(record)
            
            # 파일명 생성
            filename = f"JU_fixed_test_{i+1:02d}.jpg"
            filepath = os.path.join(output_dir, filename)
            
            # 저장
            cv2.imwrite(filepath, img)
            
            # 세대구성 사유 및 일자 확인
            household_reason = record.get("HOUSEHOLD_REASON", "없음")
            household_date = record.get("HOUSEHOLD_DATE", "없음")
            
            print(f"  ✓ 생성됨: {filename}")
            print(f"  ✓ 세대구성 사유: {household_reason}")
            print(f"  ✓ 세대구성 일자: '{household_date}'")
            
            # MEMBER의 EVENT_DATE 확인
            for j in range(1, 4):
                event_date = record.get(f"MEMBER{j}_EVENT_DATE", "없음")
                print(f"  ✓ MEMBER{j}_EVENT_DATE: '{event_date}'")
            
            print()
            
        except Exception as e:
            print(f"  ✗ 오류: {e}")
            print()
    
    print(f"=== 테스트 완료 ===")
    print(f"출력 폴더: {output_dir}")
    print(f"생성된 파일: 5개")

if __name__ == "__main__":
    test_ju_fixed_logic() 