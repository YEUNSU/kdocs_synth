#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
폰트 분석 및 진단 도구
폰트 파일의 상태와 렌더링 품질을 분석합니다.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

def check_font_files():
    """폰트 파일들의 상태를 확인합니다."""
    print("=== 폰트 파일 진단 ===")
    
    font_files = {
        "KoPubWorld Batang": "assets/fonts/KoPubWorld Batang Medium.ttf",
        "Source Han Serif": "assets/fonts/SourceHanSerifK-Medium.otf", 
        "명조체 (MT)": "assets/fonts/mt.ttf"
    }
    
    for font_name, font_path in font_files.items():
        print(f"\n📁 {font_name}")
        print(f"   경로: {font_path}")
        
        # 파일 존재 확인
        if not os.path.exists(font_path):
            print(f"   ❌ 파일이 존재하지 않습니다!")
            continue
            
        # 파일 크기 확인
        file_size = os.path.getsize(font_path)
        print(f"   📊 파일 크기: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
        # 폰트 로딩 테스트
        try:
            font = ImageFont.truetype(font_path, 30)
            print(f"   ✅ 폰트 로딩 성공")
            
            # 간단한 텍스트 렌더링 테스트
            test_img = Image.new('RGB', (200, 50), color='white')
            draw = ImageDraw.Draw(test_img)
            draw.text((10, 10), "테스트", fill='black', font=font)
            
            # 렌더링된 이미지가 빈 이미지인지 확인
            img_array = np.array(test_img)
            if np.all(img_array == 255):  # 모든 픽셀이 흰색인 경우
                print(f"   ⚠️  렌더링 결과가 비어있음 (한글 지원 문제 가능성)")
            else:
                print(f"   ✅ 텍스트 렌더링 성공")
                
        except Exception as e:
            print(f"   ❌ 폰트 로딩 실패: {e}")

def analyze_rendered_images():
    """렌더링된 이미지들을 분석합니다."""
    print("\n=== 렌더링 결과 분석 ===")
    
    output_dir = "font_test_output"
    if not os.path.exists(output_dir):
        print("폰트 테스트 결과가 없습니다. 먼저 font_test.py를 실행해주세요.")
        return
    
    # 개별 폰트 이미지들만 분석
    font_images = [
        "font_test_KoPubWorld_Batang.png",
        "font_test_Source_Han_Serif.png", 
        "font_test_명조체_MT.png"
    ]
    
    for img_name in font_images:
        img_path = os.path.join(output_dir, img_name)
        if not os.path.exists(img_path):
            continue
            
        font_name = img_name.replace("font_test_", "").replace(".png", "")
        print(f"\n📊 {font_name}")
        
        # 이미지 로드
        img = cv2.imread(img_path)
        if img is None:
            print(f"   ❌ 이미지 로드 실패")
            continue
        
        height, width, channels = img.shape
        file_size = os.path.getsize(img_path)
        
        print(f"   📐 크기: {width}x{height}")
        print(f"   📊 파일 크기: {file_size:,} bytes")
        
        # 이미지 내용 분석 (텍스트가 실제로 렌더링되었는지)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 흰색이 아닌 픽셀들의 비율 계산
        non_white_pixels = np.sum(gray < 250)  # 거의 흰색이 아닌 픽셀
        total_pixels = width * height
        text_ratio = non_white_pixels / total_pixels
        
        print(f"   📝 텍스트 픽셀 비율: {text_ratio*100:.2f}%")
        
        if text_ratio < 0.01:  # 1% 미만
            print(f"   ⚠️  텍스트 내용이 매우 적음 (렌더링 문제 가능성)")
        elif text_ratio < 0.05:  # 5% 미만
            print(f"   ⚠️  텍스트 내용이 적음")
        else:
            print(f"   ✅ 정상적인 텍스트 렌더링")

def create_detailed_font_test():
    """더 상세한 폰트 테스트를 수행합니다."""
    print("\n=== 상세 폰트 테스트 ===")
    
    font_files = {
        "KoPubWorld Batang": "assets/fonts/KoPubWorld Batang Medium.ttf",
        "Source Han Serif": "assets/fonts/SourceHanSerifK-Medium.otf", 
        "명조체 (MT)": "assets/fonts/mt.ttf"
    }
    
    # 다양한 테스트 케이스
    test_cases = [
        ("기본 한글", "한글 테스트"),
        ("이름", "홍길동"),
        ("숫자", "1234567890"),
        ("영문", "ABC abc"),
        ("특수문자", "()-.,"),
        ("긴 텍스트", "가나다라마바사아자차카타파하")
    ]
    
    for font_name, font_path in font_files.items():
        print(f"\n🔍 {font_name} 상세 테스트")
        
        if not os.path.exists(font_path):
            print(f"   파일이 존재하지 않습니다: {font_path}")
            continue
        
        try:
            font = ImageFont.truetype(font_path, 40)
            
            for test_name, test_text in test_cases:
                # 테스트 이미지 생성
                img = Image.new('RGB', (400, 80), color='white')
                draw = ImageDraw.Draw(img)
                
                try:
                    draw.text((10, 20), test_text, fill='black', font=font)
                    
                    # 렌더링 결과 확인
                    img_array = np.array(img)
                    non_white = np.sum(img_array < 250)
                    
                    if non_white > 0:
                        print(f"   ✅ {test_name}: 렌더링 성공")
                    else:
                        print(f"   ❌ {test_name}: 렌더링 실패")
                        
                except Exception as e:
                    print(f"   ❌ {test_name}: 에러 - {e}")
                    
        except Exception as e:
            print(f"   폰트 로딩 실패: {e}")

def main():
    """메인 메뉴"""
    while True:
        print("\n=== 폰트 분석 및 진단 도구 ===")
        print("1. 폰트 파일 상태 확인")
        print("2. 렌더링 결과 분석") 
        print("3. 상세 폰트 테스트")
        print("4. 전체 진단 실행")
        print("5. 종료")
        
        choice = input("\n선택하세요 (1-5): ").strip()
        
        if choice == '1':
            check_font_files()
        elif choice == '2':
            analyze_rendered_images()
        elif choice == '3':
            create_detailed_font_test()
        elif choice == '4':
            check_font_files()
            analyze_rendered_images() 
            create_detailed_font_test()
        elif choice == '5':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 1-5 중에서 선택해주세요.")

if __name__ == "__main__":
    main() 