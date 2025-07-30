import sys
import os
sys.path.append('src')

from data_factory import create_record
from templates_juga import create_template
from rotator import DocumentRotator
import cv2

def generate_ga_batch():
    """가족관계증명서(GA) 배치 생성"""
    print("=== 가족관계증명서(GA) 배치 생성 시작 ===")
    
    # 출력 디렉토리 생성
    output_dir = "outputs/dataset"
    os.makedirs(output_dir, exist_ok=True)
    
    # 주민번호 설정 (GA는 주민번호 공개 여부 구분 없음)
    jumin_configs = [
        {"mask_jumin": True, "extra_suffix": "MASK"}
    ]
    
    # 파일 카운터 (각 회전별로 독립적으로 카운트)
    file_counter = {
        "0": {"MASK": 1},
        "L": {"MASK": 1}, 
        "R": {"MASK": 1},
        "180": {"MASK": 1}
    }
    
    # 템플릿별 설정
    templates = [
        ("GA_template1_child0", 0),  # 자녀 0명
        ("GA_template1_child1", 1),  # 자녀 1명
        ("GA_template1_child2", 2),  # 자녀 2명
        ("GA_template1_child3", 3),  # 자녀 3명
        ("GA_template2_child0", 0),  # 자녀 0명
        ("GA_template2_child1", 1),  # 자녀 1명
        ("GA_template2_child2", 2),  # 자녀 2명
        ("GA_template2_child3", 3),  # 자녀 3명
    ]
    
    total_generated = 0
    
    for template_name, children_count in templates:
        print(f"\n--- 템플릿: {template_name} (자녀 {children_count}명) ---")
        
        for jumin_config in jumin_configs:
            mask_jumin = jumin_config["mask_jumin"]
            extra_suffix = jumin_config["extra_suffix"]
            
            print(f"  주민번호 설정: {extra_suffix}")
            
            # 각 템플릿당 10장씩 생성
            for i in range(10):
                # 데이터 생성
                record = create_record("GA", options={"children_count": children_count, "mask_jumin": mask_jumin})
                
                # 템플릿 생성
                template = create_template("GA", template_name, mask_jumin=mask_jumin)
                
                # 이미지 렌더링
                result_img = template.render(record)
                
                # 회전 및 저장
                rotator = DocumentRotator("GA")
                rotator.save_rotations(result_img, output_dir, "GA", file_counter, extra_suffix)
                
                total_generated += 4  # 4방향 회전
    
    print(f"\n=== 가족관계증명서(GA) 배치 생성 완료 ===")
    print(f"총 생성된 이미지: {total_generated}장")
    print(f"예상 이미지: 320장 (8템플릿 × 10장 × 4회전)")

if __name__ == "__main__":
    generate_ga_batch() 