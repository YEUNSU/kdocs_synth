import cv2
import numpy as np
import os
from typing import Dict, List, Tuple
from templates_juga import create_template
from data_factory import create_record

class DocumentRotator:
    """문서 회전 및 대량 생성 클래스"""
    
    def __init__(self, doc_type: str = "GA"):
        self.doc_type = doc_type
        self.rotation_config = {
            0: {"name": "0", "angle": 0, "prefix": f"{doc_type}-0"},
            90: {"name": "L", "angle": 90, "prefix": f"{doc_type}-L"},  # 왼쪽 90도
            -90: {"name": "R", "angle": -90, "prefix": f"{doc_type}-R"},  # 오른쪽 90도
            180: {"name": "180", "angle": 180, "prefix": f"{doc_type}-180"}
        }
    
    def rotate_document(self, image: np.ndarray, angle: int) -> np.ndarray:
        """문서를 지정된 각도로 회전합니다."""
        if angle == 0:
            return image
        elif angle == 90:  # 왼쪽 90도
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == -90:  # 오른쪽 90도
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:  # 180도
            return cv2.rotate(image, cv2.ROTATE_180)
        else:
            raise ValueError(f"지원하지 않는 회전 각도입니다: {angle}")
    
    def generate_single_document(self, template_name: str, data: Dict[str, str], 
                                output_dir: str = "outputs/dataset") -> str:
        """단일 문서를 생성합니다."""
        try:
            # 템플릿 생성
            template = create_template("GA", template_name)
            
            # 문서 렌더링
            document = template.render(data)
            
            # 출력 디렉토리 생성
            os.makedirs(output_dir, exist_ok=True)
            
            # 파일명 생성 (임시)
            filename = f"temp_{template_name}.jpg"
            output_path = os.path.join(output_dir, filename)
            
            # 저장
            cv2.imwrite(output_path, document)
            
            return output_path
            
        except Exception as e:
            print(f"문서 생성 실패 ({template_name}): {e}")
            return None
    
    def generate_rotated_documents(self, template_name: str, data: Dict[str, str], 
                                  index: int, output_dir: str = "outputs/dataset") -> List[str]:
        """4방향 회전된 문서들을 생성합니다."""
        generated_files = []
        
        # 원본 문서 생성
        original_path = self.generate_single_document(template_name, data, output_dir)
        if not original_path:
            return []
        
        # 원본 이미지 로드
        original_image = cv2.imread(original_path)
        if original_image is None:
            print(f"원본 이미지 로드 실패: {original_path}")
            return []
        
        # 각 회전별로 문서 생성
        for rotation_info in self.rotation_config.values():
            angle = rotation_info["angle"]
            prefix = rotation_info["prefix"]
            
            # 회전 적용
            rotated_image = self.rotate_document(original_image, angle)
            
            # 파일명 생성 (GA-0-0001.jpg 형식)
            filename = f"{prefix}-{index:04d}.jpg"
            output_path = os.path.join(output_dir, filename)
            
            # 저장
            cv2.imwrite(output_path, rotated_image)
            generated_files.append(output_path)
            
            print(f"생성됨: {filename}")
        
        # 임시 파일 삭제
        if os.path.exists(original_path):
            os.remove(original_path)
        
        return generated_files
    
    def generate_full_dataset(self, output_dir: str = "outputs/dataset", 
                             samples_per_template: int = 10) -> Dict[str, int]:
        """전체 데이터셋을 생성합니다 (320장)."""
        
        # 템플릿 정의
        templates = [
            ("GA_template1_child0", 0),  # 본인,부,모
            ("GA_template2_child0", 0),
            ("GA_template1_child1", 1),  # 본인,부,모,자녀1명
            ("GA_template2_child1", 1),
            ("GA_template1_child2", 2),  # 본인,부,모,자녀2명
            ("GA_template2_child2", 2),
            ("GA_template1_child3", 3),  # 본인,부,모,자녀3명
            ("GA_template2_child3", 3)
        ]
        
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        # 각 회전별 카운터
        counters = {"GA-0": 0, "GA-L": 0, "GA-R": 0, "GA-180": 0}
        total_generated = 0
        
        print("=== 가족관계증명서 데이터셋 생성 시작 ===")
        print(f"템플릿 수: {len(templates)}")
        print(f"템플릿당 샘플 수: {samples_per_template}")
        print(f"예상 총 생성 수: {len(templates) * samples_per_template * 4}장")
        print()
        
        for template_name, children_count in templates:
            print(f"📋 템플릿 처리 중: {template_name} (자녀 {children_count}명)")
            
            for i in range(samples_per_template):
                try:
                    # 랜덤 데이터 생성
                    data = create_record("GA", {"children_count": children_count})
                    
                    # 4방향 회전 문서 생성
                    generated_files = self.generate_rotated_documents(
                        template_name, data, 
                        counters["GA-0"] + 1,  # 인덱스는 1부터 시작
                        output_dir
                    )
                    
                    # 카운터 업데이트
                    for file_path in generated_files:
                        filename = os.path.basename(file_path)
                        if filename.startswith("GA-0"):
                            counters["GA-0"] += 1
                        elif filename.startswith("GA-L"):
                            counters["GA-L"] += 1
                        elif filename.startswith("GA-R"):
                            counters["GA-R"] += 1
                        elif filename.startswith("GA-180"):
                            counters["GA-180"] += 1
                    
                    total_generated += len(generated_files)
                    
                    if (i + 1) % 5 == 0:
                        print(f"   진행률: {i + 1}/{samples_per_template}")
                
                except Exception as e:
                    print(f"   오류 발생 (템플릿: {template_name}, 샘플: {i + 1}): {e}")
                    continue
            
            print(f"   ✅ {template_name} 완료: {samples_per_template * 4}장 생성")
            print()
        
        print("=== 데이터셋 생성 완료 ===")
        print(f"총 생성된 파일 수: {total_generated}장")
        print("회전별 생성 수:")
        for rotation, count in counters.items():
            print(f"  {rotation}: {count}장")
        
        return counters
    
    def create_manifest(self, output_dir: str = "outputs/dataset") -> str:
        """생성된 데이터셋의 매니페스트 파일을 생성합니다."""
        manifest_path = os.path.join(output_dir, "manifest.csv")
        
        manifest_data = []
        manifest_data.append("filename,doc_type,rotation,children_count,template_name")
        
        # 파일 목록 수집
        if os.path.exists(output_dir):
            for filename in os.listdir(output_dir):
                if filename.endswith('.jpg') and filename.startswith('GA-'):
                    # 파일명 파싱: GA-0-0001.jpg
                    parts = filename.replace('.jpg', '').split('-')
                    if len(parts) == 3:
                        doc_type = parts[0]  # GA
                        rotation = parts[1]  # 0, L, R, 180
                        index = parts[2]     # 0001
                        
                        # 템플릿명 추정 (인덱스 기반)
                        index_num = int(index)
                        template_index = (index_num - 1) // 10  # 10개씩 그룹
                        children_count = template_index % 4      # 0,1,2,3
                        template_num = (template_index // 4) + 1 # 1,2
                        
                        # 실제 파일명에서 children_count 추출
                        if "child0" in filename or index_num <= 20:
                            children_count = 0
                        elif "child1" in filename or (21 <= index_num <= 40):
                            children_count = 1
                        elif "child2" in filename or (41 <= index_num <= 60):
                            children_count = 2
                        elif "child3" in filename or (61 <= index_num <= 80):
                            children_count = 3
                        
                        template_name = f"GA_template{template_num}_child{children_count}"
                        
                        manifest_data.append(f"{filename},{doc_type},{rotation},{children_count},{template_name}")
        
        # 매니페스트 파일 저장
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(manifest_data))
        
        print(f"매니페스트 파일 생성: {manifest_path}")
        return manifest_path

    def save_rotations(self, image: np.ndarray, output_dir: str, 
                      base_filename: str, file_counter: Dict, extra_suffix: str = "") -> List[str]:
        """이미지를 4방향 회전하여 저장합니다."""
        
        generated_files = []
        os.makedirs(output_dir, exist_ok=True)
        
        # 각 회전별로 저장
        rotations = [
            {"angle": 0, "suffix": "0"},
            {"angle": 90, "suffix": "L"},     # 왼쪽 90도
            {"angle": -90, "suffix": "R"},    # 오른쪽 90도  
            {"angle": 180, "suffix": "180"}
        ]
        
        for rotation in rotations:
            angle = rotation["angle"]
            suffix = rotation["suffix"]
            
            # 회전 적용
            rotated_image = self.rotate_document(image, angle)
            
            # 파일명 생성: JU-0-OPEN-0001.jpg 형식
            if extra_suffix and isinstance(file_counter[suffix], dict):
                index = file_counter[suffix][extra_suffix]
                filename = f"{base_filename}-{suffix}-{extra_suffix}-{index:04d}.jpg"
                file_counter[suffix][extra_suffix] += 1
            else:
                index = file_counter[suffix] if isinstance(file_counter[suffix], int) else 1
                filename = f"{base_filename}-{suffix}-{index:04d}.jpg"
                if isinstance(file_counter[suffix], int):
                    file_counter[suffix] += 1
                    
            output_path = os.path.join(output_dir, filename)
            
            # 저장
            cv2.imwrite(output_path, rotated_image)
            generated_files.append(output_path)
            
        return generated_files


def main():
    """메인 실행 함수"""
    rotator = DocumentRotator()
    
    # 전체 데이터셋 생성
    counters = rotator.generate_full_dataset()
    
    # 매니페스트 생성
    manifest_path = rotator.create_manifest()
    
    print("\n🎉 가족관계증명서 데이터셋 생성 완료!")
    print(f"📁 저장 위치: outputs/dataset/")
    print(f"📋 매니페스트: {manifest_path}")


if __name__ == "__main__":
    main() 