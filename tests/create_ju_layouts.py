#!/usr/bin/env python3
"""
JU 템플릿의 모든 레이아웃 파일을 일괄 생성하는 스크립트
"""

import os
import shutil

def create_ju_layout_files():
    """JU 템플릿의 모든 레이아웃 파일을 생성합니다."""
    
    # 기준 파일 (이미 존재하는 레이아웃)
    base_file = "configs/JU_template1_TY11_layout.yaml"
    
    # 생성할 파일 목록
    templates = []
    
    # 3개 지역 × 4개 바코드 조합 = 12개 템플릿
    for region in [1, 2, 3]:
        for barcode in ["TY00", "TY01", "TY10", "TY11"]:
            template_name = f"JU_template{region}_{barcode}"
            templates.append(template_name)
    
    print(f"생성할 JU 레이아웃 파일들 ({len(templates)}개):")
    
    for template_name in templates:
        target_file = f"configs/{template_name}_layout.yaml"
        
        # 이미 존재하는 파일은 건너뛰기
        if os.path.exists(target_file):
            print(f"  ✓ 이미 존재: {template_name}_layout.yaml")
            continue
            
        try:
            # 기준 파일을 복사
            shutil.copy2(base_file, target_file)
            
            # 파일 내용에서 source_image 업데이트
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # source_image 경로 업데이트
            updated_content = content.replace(
                "source_image: JU_template1_TY11.jpg",
                f"source_image: {template_name}.jpg"
            )
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            print(f"  ✓ 생성됨: {template_name}_layout.yaml")
            
        except Exception as e:
            print(f"  ✗ 실패: {template_name}_layout.yaml - {e}")
    
    print(f"\nJU 레이아웃 파일 생성 완료!")

if __name__ == "__main__":
    create_ju_layout_files() 