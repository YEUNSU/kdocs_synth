#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국어 글씨체 테스트 스크립트
프로젝트에 있는 폰트들을 테스트하여 렌더링 결과를 확인합니다.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

# 폰트 파일들
FONT_FILES = {
    "KoPubWorld Batang": "assets/fonts/KoPubWorld Batang Medium.ttf",
    "Source Han Serif": "assets/fonts/SourceHanSerifK-Medium.otf", 
    "명조체 (MT)": "assets/fonts/mt.ttf"
}

# 테스트할 텍스트들
TEST_TEXTS = [
    "홍길동",
    "김민수", 
    "이영희",
    "박철수",
    "1990년 01월 01일",
    "서울특별시 강남구",
    "010101-1234567",
    "가족관계증명서",
    "주민등록등본"
]

def create_font_comparison(font_size=40):
    """각 폰트로 테스트 텍스트를 렌더링하여 비교 이미지를 생성합니다."""
    
    # 이미지 크기 설정
    img_width = 1200
    img_height = len(TEST_TEXTS) * 120 + 100  # 각 텍스트당 120px, 여백 100px
    
    # 폰트별로 이미지 생성
    font_images = {}
    
    for font_name, font_path in FONT_FILES.items():
        print(f"테스트 중: {font_name}")
        
        # 흰색 배경 이미지 생성
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            # 폰트 로드
            font = ImageFont.truetype(font_path, font_size)
            
            # 제목 그리기
            draw.text((20, 20), f"폰트: {font_name}", fill='black', font=font)
            
            # 각 테스트 텍스트 그리기
            y_offset = 80
            for i, text in enumerate(TEST_TEXTS):
                draw.text((20, y_offset + i * 60), text, fill='black', font=font)
                
        except Exception as e:
            print(f"폰트 로드 실패 ({font_name}): {e}")
            # 기본 폰트로 에러 메시지 표시
            draw.text((20, 20), f"폰트 로드 실패: {font_name}", fill='red')
            draw.text((20, 60), str(e), fill='red')
        
        font_images[font_name] = img
    
    return font_images

def create_side_by_side_comparison(font_images):
    """폰트들을 나란히 배치한 비교 이미지를 생성합니다."""
    
    if not font_images:
        print("생성할 폰트 이미지가 없습니다.")
        return None
    
    # 개별 이미지 크기
    single_width = list(font_images.values())[0].width
    single_height = list(font_images.values())[0].height
    
    # 전체 비교 이미지 크기 (가로로 나열)
    total_width = single_width * len(font_images)
    total_height = single_height
    
    # 비교 이미지 생성
    comparison_img = Image.new('RGB', (total_width, total_height), color='white')
    
    # 각 폰트 이미지를 가로로 배치
    x_offset = 0
    for font_name, img in font_images.items():
        comparison_img.paste(img, (x_offset, 0))
        x_offset += single_width
    
    return comparison_img

def create_single_line_comparison():
    """한 줄에 모든 폰트를 비교하는 이미지를 생성합니다."""
    
    sample_text = "홍길동 1990.01.01 서울특별시"
    font_size = 50
    
    img_width = 1400
    img_height = len(FONT_FILES) * 100 + 100
    
    # 흰색 배경 이미지 생성
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 제목
    title_font = ImageFont.load_default()
    draw.text((20, 20), "폰트 비교 (같은 텍스트)", fill='black', font=title_font)
    
    y_offset = 70
    for font_name, font_path in FONT_FILES.items():
        try:
            font = ImageFont.truetype(font_path, font_size)
            
            # 폰트 이름 표시
            draw.text((20, y_offset), f"{font_name}:", fill='blue', font=title_font)
            
            # 샘플 텍스트 렌더링
            draw.text((200, y_offset - 10), sample_text, fill='black', font=font)
            
        except Exception as e:
            print(f"폰트 로드 실패 ({font_name}): {e}")
            draw.text((20, y_offset), f"{font_name}: 로드 실패", fill='red', font=title_font)
        
        y_offset += 80
    
    return img

def main():
    """메인 실행 함수"""
    print("=== 한국어 글씨체 테스트 시작 ===")
    print(f"테스트할 폰트 수: {len(FONT_FILES)}")
    print()
    
    # 출력 폴더 생성
    output_dir = "font_test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 개별 폰트 테스트
    print("1. 개별 폰트 이미지 생성 중...")
    font_images = create_font_comparison()
    
    # 개별 이미지 저장
    for font_name, img in font_images.items():
        safe_name = font_name.replace(" ", "_").replace("(", "").replace(")", "")
        filename = f"{output_dir}/font_test_{safe_name}.png"
        img.save(filename)
        print(f"저장됨: {filename}")
    
    # 2. 나란히 비교 이미지
    print("\n2. 나란히 비교 이미지 생성 중...")
    comparison_img = create_side_by_side_comparison(font_images)
    if comparison_img:
        comparison_filename = f"{output_dir}/font_comparison_side_by_side.png"
        comparison_img.save(comparison_filename)
        print(f"저장됨: {comparison_filename}")
    
    # 3. 한 줄 비교 이미지
    print("\n3. 한 줄 비교 이미지 생성 중...")
    single_line_img = create_single_line_comparison()
    single_line_filename = f"{output_dir}/font_comparison_single_line.png"
    single_line_img.save(single_line_filename)
    print(f"저장됨: {single_line_filename}")
    
    print(f"\n=== 폰트 테스트 완료 ===")
    print(f"모든 결과는 '{output_dir}' 폴더에 저장되었습니다.")
    print("\n생성된 파일들:")
    for file in os.listdir(output_dir):
        if file.endswith('.png'):
            print(f"  - {file}")

if __name__ == "__main__":
    main() 