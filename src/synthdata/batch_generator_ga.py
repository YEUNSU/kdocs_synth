import sys
import os
sys.path.append('src')

from data_factory import create_record
from templates_juga import create_template
import cv2
import numpy as np

def rotate_image(image, angle):
    """이미지를 지정된 각도로 회전"""
    if angle == 0:
        return image
    elif angle == 90:  # 시계방향 90도
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif angle == -90:  # 반시계방향 90도
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif angle == 180:  # 180도
        return cv2.rotate(image, cv2.ROTATE_180)
    else:
        raise ValueError(f"지원하지 않는 회전 각도: {angle}")

def generate_ga_batch():
    """가족관계증명서(GA) 배치 생성 - 0/L/R/180도 모든 방향 생성"""
    print("=== 가족관계증명서(GA) 배치 생성 시작 ===")
    
    # 출력 디렉토리 생성
    output_dir = "outputs/dataset"
    os.makedirs(output_dir, exist_ok=True)
    
    # 주민번호 공개 방식 설정 (OPEN/CLOSE)
    jumin_configs = [
        {"jumin_disclosure": "CLOSE", "name": "CLOSE"},
        {"jumin_disclosure": "OPEN", "name": "OPEN"}
    ]
    
    # 문서 종류별 순차번호 카운터 (5자리)
    file_counter = {
        "GA-1": {"CLOSE": 1, "OPEN": 1},  # 가족1
        "GA-2": {"CLOSE": 1, "OPEN": 1},  # 가족2
    }
    
    # 템플릿별 설정 (문서 종류 매핑)
    templates = [
        # 가족1 (GA-1)
        ("GA_template1_child0", 0, "GA-1"),  # 자녀 0명
        ("GA_template1_child1", 1, "GA-1"),  # 자녀 1명
        ("GA_template1_child2", 2, "GA-1"),  # 자녀 2명
        ("GA_template1_child3", 3, "GA-1"),  # 자녀 3명
        # 가족2 (GA-2)
        ("GA_template2_child0", 0, "GA-2"),  # 자녀 0명
        ("GA_template2_child1", 1, "GA-2"),  # 자녀 1명
        ("GA_template2_child2", 2, "GA-2"),  # 자녀 2명
        ("GA_template2_child3", 3, "GA-2"),  # 자녀 3명
    ]
    
    total_generated = 0
    
    for template_name, children_count, doc_kind in templates:
        print(f"\n--- 템플릿: {template_name} ({doc_kind}, 자녀 {children_count}명) ---")
        
        for jumin_config in jumin_configs:
            jumin_disclosure = jumin_config["jumin_disclosure"]
            jumin_name = jumin_config["name"]
            
            print(f"  주민번호 설정: {jumin_name}")
            
            # 각 템플릿당 12~13장씩 생성 (총 200장)
            # 8템플릿 × 2주민번호방식 = 16조합, 200/16 ≈ 12.5장
            images_per_combo = 13 if file_counter[doc_kind][jumin_name] % 2 == 0 else 12
            for i in range(images_per_combo):
                # 데이터 생성
                record = create_record("GA", options={
                    "children_count": children_count, 
                    "jumin_disclosure": jumin_disclosure
                })
                
                # 템플릿 생성
                template = create_template("GA", template_name, mask_jumin=(jumin_disclosure=="CLOSE"))
                
                # 이미지 렌더링
                result_img = template.render(record)
                
                # 새로운 파일명 규칙: GA-{문서종류}-{주민번호공개여부}-0-{순차번호5자리}
                sequential_number = file_counter[doc_kind][jumin_name]
                filename = f"{doc_kind}-{jumin_name}-0-{sequential_number:05d}.jpg"
                
                # 파일 저장 (0도만)
                filepath = os.path.join(output_dir, filename)
                cv2.imwrite(filepath, result_img)
                
                # 카운터 증가
                file_counter[doc_kind][jumin_name] += 1
                total_generated += 1
                
                print(f"    생성: {filename}")
    
    print(f"\n=== 가족관계증명서(GA) 배치 생성 완료 ===")
    print(f"총 생성된 이미지: {total_generated}장")
    print(f"예상 이미지: 200장 (8템플릿 × 12~13장 × 2주민번호방식)")
    
    # 최종 카운터 상태 출력
    print(f"\n[통계] 최종 파일 카운터 상태:")
    for doc_kind in ["GA-1", "GA-2"]:
        close_count = file_counter[doc_kind]["CLOSE"] - 1
        open_count = file_counter[doc_kind]["OPEN"] - 1
        total_count = close_count + open_count
        print(f"  {doc_kind}: CLOSE({close_count}) + OPEN({open_count}) = {total_count}장")

if __name__ == "__main__":
    generate_ga_batch() 