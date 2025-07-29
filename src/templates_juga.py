import cv2
import numpy as np
import yaml
import os
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Optional
import math
import random

class BaseTemplate:
    """템플릿 클래스의 기본 클래스"""
    
    def __init__(self, template_path: str, layout_path: str, field_def_path: str):
        """
        Args:
            template_path: 템플릿 이미지 경로
            layout_path: 레이아웃 YAML 파일 경로
            field_def_path: 필드 정의 YAML 파일 경로
        """
        self.template_path = template_path
        self.layout_path = layout_path
        self.field_def_path = field_def_path
        
        # 템플릿 이미지 로드
        self.template_img = cv2.imread(template_path)
        if self.template_img is None:
            raise ValueError(f"템플릿 이미지를 로드할 수 없습니다: {template_path}")
        
        # 레이아웃 데이터 로드
        with open(layout_path, 'r', encoding='utf-8') as f:
            self.layout_data = yaml.safe_load(f)
        
        # 필드 정의 로드
        with open(field_def_path, 'r', encoding='utf-8') as f:
            self.field_def = yaml.safe_load(f)
        
        # 폰트 로드
        self.fonts = self._load_fonts()
        
        # 필드 박스 정보
        self.field_boxes = self.layout_data.get('field_boxes', {})
        
    def _load_fonts(self) -> Dict[str, ImageFont.FreeTypeFont]:
        """KoPub World 폰트를 로드합니다."""
        fonts = {}
        font_dir = "assets/fonts"
        font_path = os.path.join(font_dir, 'KoPubWorld Batang Medium.ttf')
        
        if os.path.exists(font_path):
            try:
                # 기본 크기로 로드 (나중에 조정)
                fonts['ko'] = ImageFont.truetype(font_path, 20)
                print(f"KoPub World 폰트 로드 성공: {font_path}")
            except Exception as e:
                print(f"KoPub World 폰트 로드 실패 {font_path}: {e}")
        else:
            print(f"KoPub World 폰트 파일이 없습니다: {font_path}")
        
        return fonts
    
    def _get_font_size(self, text: str, box_width: int, box_height: int, 
                      font_type: str = 'ko', max_size: int = 80, base_font_size: int = None) -> int:
        """텍스트가 박스에 맞도록 KoPub World 폰트 크기를 계산합니다."""
        if 'ko' not in self.fonts:
            return 20
        
        font = self.fonts['ko']
        
        # 기본 폰트 크기가 지정된 경우 해당 크기 사용
        if base_font_size is not None:
            return base_font_size
        
        # 텍스트 길이에 따른 최대 크기 조정 (더 작게)
        text_length = len(text)
        if text_length <= 2:  # "본인", "모", "자녀" 등
            max_size = min(max_size, 20)
        elif text_length <= 4:  # "전입", "출생등록" 등
            max_size = min(max_size, 18)
        elif text_length <= 8:  # 이름, 주소 등
            max_size = min(max_size, 22)
        else:  # 긴 텍스트
            max_size = min(max_size, 16)
        
        # 더 정교한 계산
        left, right = 8, max_size
        best_size = 8
        
        while left <= right:
            mid = (left + right) // 2
            try:
                test_font = ImageFont.truetype(font.path, mid)
                bbox = test_font.getbbox(text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 여백을 더 넉넉하게 (박스 높이의 20%)
                margin_x = max(4, box_width * 0.1)
                margin_y = max(4, box_height * 0.2)
                
                if text_width <= box_width - margin_x and text_height <= box_height - margin_y:
                    best_size = mid
                    left = mid + 1
                else:
                    right = mid - 1
            except Exception as e:
                right = mid - 1
        
        # 최소 크기 보장
        return max(best_size, 8)
    
    def _draw_text_on_image(self, img: np.ndarray, text: str, box_coords: List[int], 
                           font_type: str = 'ko', color: Tuple[int, int, int] = (50, 50, 50), 
                           base_font_size: int = None, align: str = 'center') -> np.ndarray:
        """이미지에 텍스트를 그립니다. (무조건 KoPub World 폰트 사용)"""
        if not text or not box_coords or len(box_coords) != 4:
            return img
        
        x1, y1, x2, y2 = box_coords
        box_width = x2 - x1
        box_height = y2 - y1
        
        # 폰트 크기 계산 (무조건 'ko' 폰트 사용)
        font_size = self._get_font_size(text, box_width, box_height, 'ko', base_font_size=base_font_size)
        
        if 'ko' not in self.fonts:
            # 기본 폰트 사용
            cv2.putText(img, text, (x1 + 2, y1 + box_height//2 + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_size/30, color, 1)
            return img
        
        # PIL을 사용한 고품질 텍스트 렌더링 (무조건 KoPub World 폰트 사용)
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        
        try:
            font = ImageFont.truetype(self.fonts['ko'].path, font_size)
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 텍스트 정렬 (중앙, 왼쪽, 오른쪽, 정교한 중앙)
            if align == 'left':
                text_x = x1 + 8  # 왼쪽 여백 8픽셀
            elif align == 'right':
                text_x = x2 - text_width - 8  # 오른쪽 여백 8픽셀
            elif align == 'center_precise':
                # 정교한 가운데 정렬 (박스 정중앙에 배치)
                text_x = x1 + (box_width - text_width) // 2
                # 약간의 오프셋 조정으로 시각적으로 더 정확한 중앙 배치
                if text_width < box_width * 0.3:  # 매우 짧은 텍스트
                    text_x = x1 + box_width // 2 - text_width // 2
            else:  # center
                text_x = x1 + (box_width - text_width) // 2
            
            # 세로 중앙 정렬도 더 정교하게
            if align == 'center_precise':
                text_y = y1 + box_height // 2 - text_height // 2
            else:
                text_y = y1 + (box_height - text_height) // 2
            
            # 색상 변환 (BGR -> RGB)
            rgb_color = (color[2], color[1], color[0])  # BGR을 RGB로 변환
            
            draw.text((text_x, text_y), text, font=font, fill=rgb_color)
            
            # OpenCV 형식으로 변환
            result_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
            # 합성된 텍스트만 살짝 블러 처리 (스캔 문서 느낌)
            # 텍스트 영역만 추출해서 블러 적용
            text_region = result_img[y1:y2, x1:x2]
            blurred_text = cv2.GaussianBlur(text_region, (3, 3), 0.7)
            result_img[y1:y2, x1:x2] = blurred_text
            
            return result_img
            
        except Exception as e:
            print(f"텍스트 렌더링 실패: {e}")
            # 폴백: OpenCV 기본 폰트 사용
            cv2.putText(img, text, (x1 + 2, y1 + box_height//2 + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_size/30, color, 1)
            return img
    
    def render(self, data: Dict[str, str]) -> np.ndarray:
        """데이터를 사용하여 템플릿을 렌더링합니다."""
        # 템플릿 이미지 복사
        result_img = self.template_img.copy()
        
        # 각 필드에 텍스트 렌더링 (모든 텍스트에 KoPub World 사용)
        for field_name, field_value in data.items():
            if field_name in self.field_boxes and field_value:
                box_coords = self.field_boxes[field_name]
                result_img = self._draw_text_on_image(result_img, field_value, box_coords, 'ko')
        
        return result_img
    
    def save(self, output_path: str, data: Dict[str, str]):
        """렌더링된 이미지를 저장합니다."""
        result_img = self.render(data)
        cv2.imwrite(output_path, result_img)
        print(f"이미지 저장됨: {output_path}")


class GACertificateTemplate(BaseTemplate):
    """가족관계증명서 템플릿 클래스"""
    
    def __init__(self, template_path: str, layout_path: str, field_def_path: str):
        super().__init__(template_path, layout_path, field_def_path)
        
        # 자녀 수 계산
        self.children_count = self._calculate_children_count()
        
    def _calculate_children_count(self) -> int:
        """템플릿에서 자녀 필드 수를 계산합니다."""
        children_count = 0
        for field_name in self.field_boxes.keys():
            if field_name.startswith('CHILD') and field_name.endswith('_NAME'):
                child_num = int(field_name[5])  # CHILD1_NAME -> 1
                children_count = max(children_count, child_num)
        return children_count
    
    def render(self, data: Dict[str, str]) -> np.ndarray:
        """가족관계증명서 특화 렌더링 (템플릿의 본인 박스 크기 기준으로 폰트 크기 통일)"""
        # 자녀 수에 맞는 데이터만 필터링
        filtered_data = {}
        
        for field_name, field_value in data.items():
            if field_name.startswith('CHILD'):
                child_num = int(field_name[5])  # CHILD1_NAME -> 1
                if child_num <= self.children_count:
                    filtered_data[field_name] = field_value
            else:
                filtered_data[field_name] = field_value
        
        # 템플릿의 "본인" 박스 크기를 기준으로 폰트 크기 계산 (실제로는 "본인" 텍스트 렌더링 안함)
        base_font_size = 20  # 기본값
        if 'MAIN_RELATION' in self.field_boxes:
            main_relation_box = self.field_boxes['MAIN_RELATION']
            x1, y1, x2, y2 = main_relation_box
            box_width = x2 - x1
            box_height = y2 - y1
            # "본인" 텍스트 크기로 폰트 크기 계산
            base_font_size = self._get_font_size("본인", box_width, box_height, 'ko')
            print(f"템플릿 '본인' 박스 기준 폰트 크기: {base_font_size}")
        
        # 템플릿 이미지 복사
        result_img = self.template_img.copy()
        
        # 각 필드에 텍스트 렌더링 (본인 관계만 제외, 나머지는 통일된 폰트 크기 사용)
        for field_name, field_value in filtered_data.items():
            if field_name in self.field_boxes and field_value:
                # "본인" 관계만 제외 (나머지 부, 모, 배우자, 자녀는 포함)
                if field_name == 'MAIN_RELATION':
                    continue
                
                # 한자명 필드는 이미 이름 필드에서 처리하므로 건너뛰기
                if field_name.endswith('_NAME_CN'):
                    continue
                
                # 생년월일 형식 변경 (1989.11.11 -> 1989년 11월 11일)
                if field_name.endswith('_BIRTH') and '.' in field_value:
                    year, month, day = field_value.split('.')
                    field_value = f"{year}년 {month}월 {day}일"
                
                # 성명(한자) 추가 - 이름 뒤에 한자 추가
                if field_name.endswith('_NAME'):
                    base_name = field_name.replace('_NAME', '')
                    name_cn = filtered_data.get(f"{base_name}_NAME_CN", "")
                    if name_cn:
                        field_value = f"{field_value}({name_cn})"
                
                # 본관을 한자로 표시 (예: 김해 -> 金海)
                if field_name.endswith('_ORIGIN'):
                    origin_map = {
                        '김해': '金海', '전주': '全州', '경주': '慶州', '밀양': '密陽', '안동': '安東',
                        '파평': '坡平', '청주': '淸州', '나주': '羅州', '광산': '光山', '달성': '達城'
                    }
                    field_value = origin_map.get(field_value, field_value)
                
                box_coords = self.field_boxes[field_name]
                
                # 필드별 폰트 크기 조정
                adjusted_font_size = base_font_size
                
                # 이름(한자) 필드는 폰트 크기를 조금 더 크게
                if field_name.endswith('_NAME') and '(' in field_value:
                    adjusted_font_size = int(base_font_size * 1.2)  # 20% 더 크게
                
                # 본관도 이름(한자)와 같은 크기로
                elif field_name.endswith('_ORIGIN'):
                    adjusted_font_size = int(base_font_size * 1.2)  # 20% 더 크게 (24포인트)
                
                # 성별, 등록기준지는 작은 증가
                elif field_name.endswith('_GENDER'):
                    adjusted_font_size = int(base_font_size * 1.05)  # 5% 더 크게 (등록기준지와 동일)
                elif field_name == 'BASE_ADDRESS':
                    adjusted_font_size = int(base_font_size * 1.05)  # 5% 더 크게
                
                # 정렬 방식 결정
                if field_name == 'BASE_ADDRESS':
                    align = 'left'
                elif field_name.endswith('_GENDER') or len(field_value) <= 2:
                    align = 'center_precise'  # 성별 등 짧은 텍스트는 정교한 가운데 정렬
                else:
                    align = 'center'
                
                # 모든 텍스트를 진한 회색으로 통일
                color = (60, 60, 60)
                
                result_img = self._draw_text_on_image(result_img, field_value, box_coords, 'ko', color, adjusted_font_size, align)
        
        return result_img


class JUCertificateTemplate(BaseTemplate):
    """주민등록등본 템플릿 클래스"""
    
    def __init__(self, template_path: str, layout_path: str, field_def_path: str):
        super().__init__(template_path, layout_path, field_def_path)
        
        # 세대원 수 계산
        self.members_count = self._calculate_members_count()
        
    def _calculate_members_count(self) -> int:
        """템플릿에서 세대원 필드 수를 계산합니다."""
        members_count = 0
        for field_name in self.field_boxes.keys():
            if field_name.startswith('MEMBER') and field_name.endswith('_NAME'):
                member_num = int(field_name[6])  # MEMBER1_NAME -> 1
                members_count = max(members_count, member_num)
        return members_count
    
    def render(self, data: Dict[str, str]) -> np.ndarray:
        """주민등록등본 특화 렌더링"""
        # 세대원 수에 맞는 데이터만 필터링
        filtered_data = {}
        
        for field_name, field_value in data.items():
            if field_name.startswith('MEMBER'):
                member_num = int(field_name[6])  # MEMBER1_NAME -> 1
                if member_num <= self.members_count:
                    filtered_data[field_name] = field_value
            else:
                filtered_data[field_name] = field_value
        
        return super().render(filtered_data)


def create_template(doc_type: str, template_name: str) -> BaseTemplate:
    """문서 타입에 따라 적절한 템플릿 객체를 생성합니다."""
    
    # 템플릿 경로 구성
    template_path = f"assets/templates/{doc_type}/{template_name}.jpg"
    layout_path = f"configs/{template_name}_layout.yaml"
    field_def_path = f"configs/field_definitions/{doc_type.lower()}_fields.yaml"
    
    # 파일 존재 확인
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"템플릿 이미지가 없습니다: {template_path}")
    if not os.path.exists(layout_path):
        raise FileNotFoundError(f"레이아웃 파일이 없습니다: {layout_path}")
    if not os.path.exists(field_def_path):
        raise FileNotFoundError(f"필드 정의 파일이 없습니다: {field_def_path}")
    
    # 문서 타입에 따라 템플릿 생성
    if doc_type == "GA":
        return GACertificateTemplate(template_path, layout_path, field_def_path)
    elif doc_type == "JU":
        return JUCertificateTemplate(template_path, layout_path, field_def_path)
    else:
        raise ValueError(f"지원하지 않는 문서 타입입니다: {doc_type}")


# 테스트용 코드
if __name__ == "__main__":
    from data_factory import create_record
    import os
    
    # 출력 폴더 생성
    os.makedirs("outputs", exist_ok=True)
    
    # 가족관계증명서 테스트만 실행
    print("=== 가족관계증명서 템플릿 테스트 ===")
    try:
        ga_template = create_template("GA", "GA_template1_child2")
        ga_data = create_record("GA", {"children_count": 2})
        ga_template.save("outputs/test_ga_output.jpg", ga_data)
        print(f"자녀 수: {ga_template.children_count}")
        print("가족관계증명서 테스트 완료!")
    except Exception as e:
        print(f"GA 템플릿 테스트 실패: {e}")
        import traceback
        traceback.print_exc() 