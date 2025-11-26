#!/usr/bin/env python3
"""
간단한 샘플 생성 스크립트
- 가족관계증명서 5장 (주민번호 뒷자리 마스킹)
- 주민등록등본 5장 (주민번호 뒷자리 마스킹)
"""

import sys
import os
sys.path.append('src/synthdata')

from data_factory import create_record
from templates_juga import create_template
import cv2

def generate_samples():
    """가족관계증명서 5장, 주민등록등본 5장 생성"""

    # 출력 디렉토리 생성
    output_dir = "outputs/samples"
    os.makedirs(output_dir, exist_ok=True)

    print("=== 샘플 생성 시작 ===\n")

    # 1. 가족관계증명서 5장 생성
    print("[가족관계증명서] 5장 생성 중...")

    for i in range(1, 6):
        # 자녀 수 랜덤 선택 (2~3명)
        import random
        children_count = random.randint(2, 3)

        # 자녀 수에 따른 템플릿 선택
        if children_count == 1:
            ga_template_name = "GA_template1_child1"
        elif children_count == 2:
            ga_template_name = "GA_template1_child2"
        else:  # 3명
            ga_template_name = "GA_template1_child3"

        # 데이터 생성 (주민번호 뒷자리 마스킹)
        record = create_record("GA", options={
            "children_count": children_count,
            "jumin_disclosure": "CLOSE"
        })

        # 템플릿 생성
        template = create_template("GA", ga_template_name)

        # 이미지 렌더링
        result_img = template.render(record)

        # 파일 저장
        filename = f"GA_sample_{i:02d}.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, result_img)

        print(f"  > {filename} 생성 완료 (자녀 {children_count}명)")

    # 2. 주민등록등본 5장 생성
    print("\n[주민등록등본] 5장 생성 중...")
    ju_template_name = "JU_template1_TY11"  # 등본1 템플릿

    for i in range(1, 6):
        # 데이터 생성 (주민번호 뒷자리 마스킹, 세대원 3-5명)
        import random
        members_count = random.randint(3, 5)

        record = create_record("JU", options={
            "members_count": members_count,
            "jumin_disclosure": "CLOSE"
        })

        # 템플릿 생성
        template = create_template("JU", ju_template_name, max_members=members_count)

        # 이미지 렌더링
        result_img = template.render(record)

        # 파일 저장
        filename = f"JU_sample_{i:02d}.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, result_img)

        print(f"  > {filename} 생성 완료 (세대원 {members_count}명)")

    print(f"\n=== 샘플 생성 완료 ===")
    print(f"저장 위치: {output_dir}/")
    print(f"총 생성: 10장 (가족관계 5장 + 주민등록 5장)")
    print(f"주민번호: 뒷자리 마스킹 (******)")

if __name__ == "__main__":
    generate_samples()
