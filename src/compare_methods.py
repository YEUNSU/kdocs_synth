import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
from data_factory import create_record
from templates_juga import create_template
from templates_synthtiger import SynthTIGERDocumentGenerator

def create_comparison_image():
    """두 방식을 비교하는 이미지 생성"""
    
    # 출력 폴더 생성
    os.makedirs("outputs/comparison", exist_ok=True)
    
    print("=== 문서 합성 방식 비교 분석 ===")
    
    # 테스트 데이터 생성
    ga_data = create_record("GA", {"children_count": 2})
    ju_data = create_record("JU", {"members_count": 3})
    
    # 1. 기존 방식 (템플릿 오버레이)
    print("1. 기존 방식 생성 중...")
    try:
        ga_template = create_template("GA", "GA_template1_child2")
        ga_original = ga_template.render(ga_data)
        cv2.imwrite("outputs/comparison/original_ga.jpg", ga_original)
        print("   ✓ 기존 방식 가족관계증명서 생성 완료")
    except Exception as e:
        print(f"   ✗ 기존 방식 실패: {e}")
        ga_original = None
    
    # 2. SynthTIGER 방식 (완전 합성)
    print("2. SynthTIGER 방식 생성 중...")
    try:
        synthtiger_gen = SynthTIGERDocumentGenerator()
        ga_synthtiger = synthtiger_gen.generate_family_certificate_style(ga_data)
        cv2.imwrite("outputs/comparison/synthtiger_ga.jpg", ga_synthtiger)
        print("   ✓ SynthTIGER 방식 가족관계증명서 생성 완료")
    except Exception as e:
        print(f"   ✗ SynthTIGER 방식 실패: {e}")
        ga_synthtiger = None
    
    # 3. 비교 이미지 생성
    if ga_original is not None and ga_synthtiger is not None:
        print("3. 비교 이미지 생성 중...")
        
        # 이미지 크기 통일
        h1, w1 = ga_original.shape[:2]
        h2, w2 = ga_synthtiger.shape[:2]
        
        # 더 큰 크기로 통일
        max_h = max(h1, h2)
        max_w = max(w1, w2)
        
        # 기존 방식 이미지 리사이즈
        ga_original_resized = cv2.resize(ga_original, (max_w, max_h))
        
        # SynthTIGER 방식 이미지 리사이즈
        ga_synthtiger_resized = cv2.resize(ga_synthtiger, (max_w, max_h))
        
        # 가로로 연결
        comparison_img = np.hstack([ga_original_resized, ga_synthtiger_resized])
        
        # 제목 추가
        title_height = 50
        title_img = np.ones((title_height, comparison_img.shape[1], 3), dtype=np.uint8) * 255
        
        # OpenCV로 텍스트 추가
        cv2.putText(title_img, "Original Method (Template Overlay)", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(title_img, "SynthTIGER Method (Full Synthesis)", (max_w + 10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # 제목과 이미지 연결
        final_comparison = np.vstack([title_img, comparison_img])
        
        cv2.imwrite("outputs/comparison/method_comparison.jpg", final_comparison)
        print("   ✓ 비교 이미지 생성 완료")
    
    print("\n=== 비교 분석 완료 ===")
    print("생성된 파일들:")
    print("- outputs/comparison/original_ga.jpg (기존 방식)")
    print("- outputs/comparison/synthtiger_ga.jpg (SynthTIGER 방식)")
    print("- outputs/comparison/method_comparison.jpg (비교 이미지)")

def analyze_differences():
    """두 방식의 차이점 분석"""
    
    print("\n=== 방식별 차이점 분석 ===")
    
    differences = {
        "기존 방식 (Template Overlay)": {
            "장점": [
                "실제 문서 템플릿 기반으로 현실적",
                "정확한 레이아웃 제어 가능",
                "빠른 개발 및 커스터마이징",
                "의존성이 적고 안정적",
                "특정 문서 타입에 최적화"
            ],
            "단점": [
                "템플릿별 개별 작업 필요",
                "확장성이 제한적",
                "왜곡 효과가 단순함",
                "대규모 생성에 부적합"
            ],
            "적합한 용도": [
                "특정 공문서 합성",
                "프로토타입 개발",
                "소규모 데이터셋",
                "정확한 레이아웃 요구"
            ]
        },
        "SynthTIGER 방식 (Full Synthesis)": {
            "장점": [
                "완전 자동화된 합성",
                "다양한 왜곡 효과 (20+ 효과)",
                "대규모 병렬 생성 가능",
                "범용적이고 확장 가능",
                "AI 모델 학습에 최적화"
            ],
            "단점": [
                "복잡한 의존성",
                "개발 및 설정이 어려움",
                "실제 문서와 차이 가능성",
                "리소스 사용량 높음"
            ],
            "적합한 용도": [
                "대규모 AI 모델 학습",
                "STR(장면 텍스트 인식) 연구",
                "다양한 왜곡 환경 시뮬레이션",
                "범용 텍스트 합성"
            ]
        }
    }
    
    for method, analysis in differences.items():
        print(f"\n📋 {method}")
        print("✅ 장점:")
        for advantage in analysis["장점"]:
            print(f"   • {advantage}")
        print("❌ 단점:")
        for disadvantage in analysis["단점"]:
            print(f"   • {disadvantage}")
        print("🎯 적합한 용도:")
        for use_case in analysis["적합한 용도"]:
            print(f"   • {use_case}")

def generate_technical_comparison():
    """기술적 비교표 생성"""
    
    print("\n=== 기술적 비교표 ===")
    
    comparison_table = {
        "구분": ["생성 방식", "배경 처리", "폰트 관리", "효과 적용", "레이아웃", "확장성", "성능", "정확도"],
        "기존 방식": [
            "템플릿 오버레이",
            "실제 이미지 사용",
            "단일 폰트 (KoPub World)",
            "단순 블러 효과",
            "YAML 좌표 기반",
            "제한적 (템플릿별)",
            "빠름 (단순 처리)",
            "높음 (실제 템플릿)"
        ],
        "SynthTIGER 방식": [
            "완전 합성",
            "다양한 배경 생성",
            "다중 폰트 지원",
            "20+ 고급 효과",
            "동적 레이아웃",
            "높음 (범용적)",
            "느림 (복잡 처리)",
            "보통 (합성 기반)"
        ]
    }
    
    # 표 출력
    print(f"{'구분':<15} {'기존 방식':<25} {'SynthTIGER 방식':<25}")
    print("-" * 65)
    
    for i in range(len(comparison_table["구분"])):
        category = comparison_table["구분"][i]
        original = comparison_table["기존 방식"][i]
        synthtiger = comparison_table["SynthTIGER 방식"][i]
        print(f"{category:<15} {original:<25} {synthtiger:<25}")

def create_summary_report():
    """요약 리포트 생성"""
    
    report = """
# 문서 합성 방식 비교 분석 리포트

## 📊 개요
이 리포트는 공문서 합성을 위한 두 가지 접근 방식을 비교 분석합니다.

## 🔍 비교 대상
1. **기존 방식 (Template Overlay)**: 실제 템플릿 이미지에 텍스트 오버레이
2. **SynthTIGER 방식 (Full Synthesis)**: 완전 합성 방식으로 배경과 텍스트 생성

## 📈 주요 차이점

### 생성 방식
- **기존**: 실제 템플릿 + PIL/OpenCV 텍스트 오버레이
- **SynthTIGER**: 완전 합성 (배경 + 폰트 + 왜곡 다층 조합)

### 효과 적용
- **기존**: 가우시안 블러로 스캔 느낌 연출
- **SynthTIGER**: 20+ 고급 효과 (원근, 곡률, 모션블러, 조명 등)

### 확장성
- **기존**: 특정 문서 타입에 특화, 소규모
- **SynthTIGER**: 범용적, 대규모 병렬 생성 가능

## 🎯 권장 사용 사례

### 기존 방식 권장
- ✅ 특정 공문서 합성 (가족관계증명서, 주민등록등본)
- ✅ 정확한 레이아웃 요구
- ✅ 빠른 프로토타입 개발
- ✅ 소규모 데이터셋

### SynthTIGER 방식 권장
- ✅ 대규모 AI 모델 학습
- ✅ STR(장면 텍스트 인식) 연구
- ✅ 다양한 왜곡 환경 시뮬레이션
- ✅ 범용 텍스트 합성

## 📝 결론
각 방식은 서로 다른 목적과 요구사항에 최적화되어 있습니다. 
현재 프로젝트의 목적(공문서 합성)에는 기존 방식이 더 적합하며,
향후 AI 모델 학습이나 대규모 데이터셋 생성이 필요할 때 SynthTIGER 방식을 고려할 수 있습니다.
"""
    
    with open("outputs/comparison/analysis_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n📄 분석 리포트 생성 완료: outputs/comparison/analysis_report.md")

if __name__ == "__main__":
    # 1. 비교 이미지 생성
    create_comparison_image()
    
    # 2. 차이점 분석
    analyze_differences()
    
    # 3. 기술적 비교표
    generate_technical_comparison()
    
    # 4. 요약 리포트 생성
    create_summary_report()
    
    print("\n🎉 모든 비교 분석 완료!")
    print("📁 결과물 위치: outputs/comparison/") 