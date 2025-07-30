import cv2
import numpy as np
import yaml
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from typing import Dict, List, Tuple, Optional
import math
import random
from dataclasses import dataclass
import json

@dataclass
class TextEffect:
    """텍스트 효과 설정"""
    perspective: bool = False
    curvature: bool = False
    motion_blur: bool = False
    lighting: bool = False
    noise: bool = False
    shadow: bool = False
    rotation: float = 0.0
    scale: float = 1.0

class SynthTIGERStyleTemplate:
    """SynthTIGER 스타일의 완전 합성 템플릿 클래스"""
    
    def __init__(self, config_path: str = None):
        """
        Args:
            config_path: SynthTIGER 스타일 설정 파일 경로
        """
        self.config = self._load_config(config_path)
        self.fonts = self._load_fonts()
        self.backgrounds = self._load_backgrounds()
        self.effects = self._create_effect_pipeline()
        
    def _load_config(self, config_path: str) -> Dict:
        """SynthTIGER 스타일 설정 로드"""
        default_config = {
            "canvas_size": (800, 600),
            "font_sizes": [12, 14, 16, 18, 20, 24, 28, 32],
            "colors": [(0, 0, 0), (50, 50, 50), (100, 100, 100), (150, 150, 150)],
            "background_types": ["paper", "card", "document"],
            "effect_probability": 0.7,
            "max_effects_per_text": 3,
            "text_placement": "grid",  # grid, random, structured
            "margin": 20,
            "line_spacing": 1.2
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _load_fonts(self) -> Dict[str, List[str]]:
        """다양한 폰트 로드 (SynthTIGER 스타일)"""
        fonts = {
            'korean': [],
            'english': [],
            'chinese': []
        }
        
        font_dir = "assets/fonts"
        if os.path.exists(font_dir):
            for font_file in os.listdir(font_dir):
                if font_file.endswith(('.ttf', '.otf')):
                    font_path = os.path.join(font_dir, font_file)
                    if 'ko' in font_file.lower() or 'korean' in font_file.lower():
                        fonts['korean'].append(font_path)
                    elif 'chinese' in font_file.lower() or 'han' in font_file.lower():
                        fonts['chinese'].append(font_path)
                    else:
                        fonts['english'].append(font_path)
        
        # 기본 폰트 추가
        if not fonts['korean']:
            fonts['korean'].append("assets/fonts/KoPubWorld Batang Medium.ttf")
        
        return fonts
    
    def _load_backgrounds(self) -> List[np.ndarray]:
        """배경 텍스처 로드 (SynthTIGER 스타일)"""
        backgrounds = []
        
        # 기본 배경 생성 (종이, 카드, 문서 느낌)
        canvas_size = self.config['canvas_size']
        
        # 1. 깨끗한 흰색 배경
        white_bg = np.ones((canvas_size[1], canvas_size[0], 3), dtype=np.uint8) * 255
        backgrounds.append(white_bg)
        
        # 2. 약간 노란 종이 배경
        paper_bg = np.ones((canvas_size[1], canvas_size[0], 3), dtype=np.uint8) * 255
        paper_bg[:, :, 0] = 250  # 약간 노란색
        paper_bg[:, :, 1] = 248
        backgrounds.append(paper_bg)
        
        # 3. 노이즈가 있는 배경
        noise_bg = np.ones((canvas_size[1], canvas_size[0], 3), dtype=np.uint8) * 255
        noise = np.random.normal(0, 5, (canvas_size[1], canvas_size[0], 3))
        noise_bg = np.clip(noise_bg + noise, 0, 255).astype(np.uint8)
        backgrounds.append(noise_bg)
        
        # 4. 그리드 라인이 있는 배경
        grid_bg = np.ones((canvas_size[1], canvas_size[0], 3), dtype=np.uint8) * 255
        for i in range(0, canvas_size[0], 50):
            cv2.line(grid_bg, (i, 0), (i, canvas_size[1]), (200, 200, 200), 1)
        for i in range(0, canvas_size[1], 50):
            cv2.line(grid_bg, (0, i), (canvas_size[0], i), (200, 200, 200), 1)
        backgrounds.append(grid_bg)
        
        return backgrounds
    
    def _create_effect_pipeline(self) -> List[callable]:
        """효과 파이프라인 생성 (SynthTIGER 스타일)"""
        effects = []
        
        def perspective_transform(img, text_region):
            """원근 변환 효과"""
            if random.random() < 0.3:
                h, w = text_region.shape[:2]
                pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
                pts2 = np.float32([[random.randint(-10, 10), random.randint(-5, 5)],
                                  [w + random.randint(-10, 10), random.randint(-5, 5)],
                                  [random.randint(-10, 10), h + random.randint(-5, 5)],
                                  [w + random.randint(-10, 10), h + random.randint(-5, 5)]])
                matrix = cv2.getPerspectiveTransform(pts1, pts2)
                return cv2.warpPerspective(text_region, matrix, (w, h))
            return text_region
        
        def curvature_effect(img, text_region):
            """곡률 효과"""
            if random.random() < 0.2:
                h, w = text_region.shape[:2]
                # 간단한 곡률 시뮬레이션
                curved = np.zeros_like(text_region)
                for y in range(h):
                    offset = int(5 * math.sin(y * math.pi / h))
                    if 0 <= y + offset < h:
                        curved[y] = text_region[y + offset]
                return curved
            return text_region
        
        def motion_blur_effect(img, text_region):
            """모션 블러 효과"""
            if random.random() < 0.4:
                kernel_size = random.choice([3, 5, 7])
                angle = random.uniform(0, 360)
                kernel = np.zeros((kernel_size, kernel_size))
                kernel[kernel_size//2, :] = 1
                kernel = cv2.warpAffine(kernel, cv2.getRotationMatrix2D((kernel_size//2, kernel_size//2), angle, 1), (kernel_size, kernel_size))
                kernel = kernel / kernel.sum()
                return cv2.filter2D(text_region, -1, kernel)
            return text_region
        
        def lighting_effect(img, text_region):
            """조명 효과"""
            if random.random() < 0.3:
                # 밝기 조정
                brightness = random.uniform(0.8, 1.2)
                return np.clip(text_region * brightness, 0, 255).astype(np.uint8)
            return text_region
        
        def noise_effect(img, text_region):
            """노이즈 효과"""
            if random.random() < 0.5:
                noise = np.random.normal(0, random.uniform(2, 8), text_region.shape)
                return np.clip(text_region + noise, 0, 255).astype(np.uint8)
            return text_region
        
        def shadow_effect(img, text_region, position):
            """그림자 효과"""
            if random.random() < 0.2:
                # 간단한 그림자 시뮬레이션
                shadow_offset = (2, 2)
                shadow_region = np.zeros_like(img)
                x, y = position
                h, w = text_region.shape[:2]
                shadow_region[y+shadow_offset[1]:y+h+shadow_offset[1], 
                             x+shadow_offset[0]:x+w+shadow_offset[0]] = text_region * 0.3
                return shadow_region
            return np.zeros_like(img)
        
        effects = [perspective_transform, curvature_effect, motion_blur_effect, 
                  lighting_effect, noise_effect]
        
        # shadow_effect를 클래스 변수로 저장
        self.shadow_effect = shadow_effect
        
        return effects
    
    def _generate_text_layout(self, texts: List[str]) -> List[Dict]:
        """텍스트 레이아웃 생성 (SynthTIGER 스타일)"""
        layout = []
        canvas_width, canvas_height = self.config['canvas_size']
        margin = self.config['margin']
        
        if self.config['text_placement'] == 'grid':
            # 그리드 레이아웃
            cols = 3
            rows = (len(texts) + cols - 1) // cols
            cell_width = (canvas_width - 2 * margin) // cols
            cell_height = (canvas_height - 2 * margin) // rows
            
            for i, text in enumerate(texts):
                row = i // cols
                col = i % cols
                x = margin + col * cell_width + random.randint(10, 30)
                y = margin + row * cell_height + random.randint(10, 30)
                layout.append({
                    'text': text,
                    'position': (x, y),
                    'font_size': random.choice(self.config['font_sizes']),
                    'color': random.choice(self.config['colors']),
                    'font_type': random.choice(['korean', 'english', 'chinese'])
                })
        
        elif self.config['text_placement'] == 'random':
            # 랜덤 레이아웃
            for text in texts:
                x = random.randint(margin, canvas_width - margin - 100)
                y = random.randint(margin, canvas_height - margin - 30)
                layout.append({
                    'text': text,
                    'position': (x, y),
                    'font_size': random.choice(self.config['font_sizes']),
                    'color': random.choice(self.config['colors']),
                    'font_type': random.choice(['korean', 'english', 'chinese'])
                })
        
        return layout
    
    def _apply_effects_to_text(self, img: np.ndarray, text_region: np.ndarray, 
                              position: Tuple[int, int]) -> np.ndarray:
        """텍스트에 효과 적용 (SynthTIGER 스타일)"""
        if random.random() > self.config['effect_probability']:
            return img
        
        x, y = position
        h, w = text_region.shape[:2]
        
        # 효과 개수 제한
        num_effects = random.randint(1, min(self.config['max_effects_per_text'], len(self.effects)))
        selected_effects = random.sample(self.effects, num_effects)
        
        # 효과 적용
        processed_region = text_region.copy()
        for effect in selected_effects:
            processed_region = effect(img, processed_region)
        
        # 그림자 효과 (별도 처리)
        if random.random() < 0.2:
            shadow = self.shadow_effect(img, text_region, position)
            img = cv2.add(img, shadow)
        
        # 처리된 텍스트 영역을 원본 이미지에 합성
        img[y:y+h, x:x+w] = processed_region
        
        return img
    
    def _render_text_with_effects(self, img: np.ndarray, text_info: Dict) -> np.ndarray:
        """효과가 적용된 텍스트 렌더링 (SynthTIGER 스타일)"""
        text = text_info['text']
        x, y = text_info['position']
        font_size = text_info['font_size']
        color = text_info['color']
        font_type = text_info['font_type']
        
        # 폰트 선택
        if self.fonts[font_type]:
            font_path = random.choice(self.fonts[font_type])
        else:
            font_path = self.fonts['korean'][0] if self.fonts['korean'] else None
        
        if not font_path or not os.path.exists(font_path):
            # 기본 OpenCV 폰트 사용
            cv2.putText(img, text, (x, y + font_size), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_size/30, color, 1)
            return img
        
        # PIL을 사용한 고품질 렌더링
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        
        try:
            font = ImageFont.truetype(font_path, font_size)
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 텍스트 영역 추출
            text_region = np.zeros((text_height + 10, text_width + 10, 3), dtype=np.uint8)
            text_pil = Image.new('RGB', (text_width + 10, text_height + 10), (255, 255, 255))
            text_draw = ImageDraw.Draw(text_pil)
            text_draw.text((5, 5), text, font=font, fill=color)
            text_region = np.array(text_pil)
            
            # 효과 적용
            img = self._apply_effects_to_text(img, text_region, (x, y))
            
            # 최종 텍스트 그리기
            draw.text((x, y), text, font=font, fill=color)
            result_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
            return result_img
            
        except Exception as e:
            print(f"텍스트 렌더링 실패: {e}")
            # 폴백
            cv2.putText(img, text, (x, y + font_size), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_size/30, color, 1)
            return img
    
    def generate_synthetic_document(self, texts: List[str], output_path: str = None) -> np.ndarray:
        """SynthTIGER 스타일로 합성 문서 생성"""
        # 배경 선택
        background = random.choice(self.backgrounds).copy()
        
        # 텍스트 레이아웃 생성
        text_layout = self._generate_text_layout(texts)
        
        # 각 텍스트에 효과 적용하여 렌더링
        for text_info in text_layout:
            background = self._render_text_with_effects(background, text_info)
        
        # 최종 후처리 효과
        if random.random() < 0.3:
            # 전체 이미지에 약간의 블러
            background = cv2.GaussianBlur(background, (3, 3), 0.5)
        
        if random.random() < 0.2:
            # JPEG 압축 시뮬레이션
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), random.randint(70, 95)]
            _, encoded = cv2.imencode('.jpg', background, encode_param)
            background = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        
        if output_path:
            cv2.imwrite(output_path, background)
            print(f"SynthTIGER 스타일 문서 생성: {output_path}")
        
        return background
    
    def generate_batch(self, text_corpus: List[List[str]], output_dir: str = "outputs/synthtiger") -> List[str]:
        """배치 생성 (SynthTIGER 스타일)"""
        os.makedirs(output_dir, exist_ok=True)
        output_paths = []
        
        for i, texts in enumerate(text_corpus):
            output_path = os.path.join(output_dir, f"synthtiger_doc_{i:04d}.jpg")
            self.generate_synthetic_document(texts, output_path)
            output_paths.append(output_path)
        
        print(f"SynthTIGER 스타일 배치 생성 완료: {len(output_paths)}개 파일")
        return output_paths


class SynthTIGERDocumentGenerator:
    """SynthTIGER 스타일 문서 생성기"""
    
    def __init__(self):
        self.template = SynthTIGERStyleTemplate()
    
    def generate_family_certificate_style(self, data: Dict[str, str]) -> np.ndarray:
        """가족관계증명서 스타일 생성"""
        texts = []
        
        # 데이터를 텍스트로 변환
        for key, value in data.items():
            if value:
                if key.endswith('_NAME') and not key.endswith('_NAME_CN'):
                    name_cn = data.get(key.replace('_NAME', '_NAME_CN'), '')
                    if name_cn:
                        texts.append(f"{value}({name_cn})")
                    else:
                        texts.append(value)
                elif key.endswith('_BIRTH') and '.' in value:
                    year, month, day = value.split('.')
                    texts.append(f"{year}년 {month}월 {day}일")
                elif key.endswith('_ORIGIN'):
                    origin_map = {
                        '김해': '金海', '전주': '全州', '경주': '慶州', '밀양': '密陽', '안동': '安東'
                    }
                    texts.append(origin_map.get(value, value))
                elif not key.endswith('_NAME_CN'):
                    texts.append(value)
        
        return self.template.generate_synthetic_document(texts)
    
    def generate_resident_certificate_style(self, data: Dict[str, str]) -> np.ndarray:
        """주민등록등본 스타일 생성"""
        texts = []
        
        for key, value in data.items():
            if value and not key.endswith('_NAME_CN'):
                texts.append(value)
        
        return self.template.generate_synthetic_document(texts)


# 테스트용 코드
if __name__ == "__main__":
    from data_factory import create_record
    import os
    
    # 출력 폴더 생성
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("outputs/synthtiger", exist_ok=True)
    
    print("=== SynthTIGER 스타일 문서 생성 테스트 ===")
    
    # SynthTIGER 생성기 초기화
    generator = SynthTIGERDocumentGenerator()
    
    try:
        # 가족관계증명서 스타일 생성
        ga_data = create_record("GA", {"children_count": 2})
        synthtiger_ga = generator.generate_family_certificate_style(ga_data)
        cv2.imwrite("outputs/synthtiger_ga_output.jpg", synthtiger_ga)
        print("SynthTIGER 스타일 가족관계증명서 생성 완료!")
        
        # 주민등록등본 스타일 생성
        ju_data = create_record("JU", {"members_count": 3})
        synthtiger_ju = generator.generate_resident_certificate_style(ju_data)
        cv2.imwrite("outputs/synthtiger_ju_output.jpg", synthtiger_ju)
        print("SynthTIGER 스타일 주민등록등본 생성 완료!")
        
        # 배치 생성 테스트
        text_corpus = [
            ["김철수", "1989년 11월 11일", "남", "김해", "서울시 강남구"],
            ["이영희", "1992년 3월 15일", "여", "전주", "서울시 서초구"],
            ["박민수", "1985년 7월 22일", "남", "경주", "부산시 해운대구"]
        ]
        
        output_paths = generator.template.generate_batch(text_corpus)
        print(f"배치 생성 완료: {len(output_paths)}개 파일")
        
    except Exception as e:
        print(f"SynthTIGER 테스트 실패: {e}")
        import traceback
        traceback.print_exc() 