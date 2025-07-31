#!/usr/bin/env python3
"""
문서 회전 처리기 - 새로운 파일명 규칙 적용

기능:
- 0도 문서들을 L, R, 180도로 회전
- OPEN/CLOSE/TEMP 문서 처리
- 새로운 파일명 규칙 적용
"""

import cv2
import numpy as np
import os
import glob
from typing import Dict, List, Tuple
import argparse

class RotationProcessor:
    """문서 회전 처리기"""
    
    def __init__(self, input_dir: str = "outputs/dataset", output_dir: str = "outputs/dataset"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 회전 설정 (0도 제외, 3방향만)
        self.rotation_config = {
            90: {"name": "L", "angle": 90},      # 왼쪽 90도
            -90: {"name": "R", "angle": -90},    # 오른쪽 90도 (270도)
            180: {"name": "180", "angle": 180}   # 180도
        }
    
    def rotate_image(self, image: np.ndarray, angle: int) -> np.ndarray:
        """이미지를 지정된 각도로 회전합니다."""
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
    
    def parse_filename(self, filename: str) -> Dict[str, str]:
        """새로운 파일명 규칙을 파싱합니다."""
        # 예: GA-1-CLOSE-0-00001.jpg
        parts = filename.replace('.jpg', '').split('-')
        
        if len(parts) >= 5:
            return {
                "doc_type": parts[0],      # GA 또는 JU
                "doc_kind": parts[1],      # 1, 2, 3
                "disclosure": parts[2],    # OPEN, CLOSE, TEMP
                "angle": parts[3],         # 0, L, R, 180
                "sequence": parts[4]       # 00001, 00002, ...
            }
        else:
            return None
    
    def generate_rotated_filename(self, base_info: Dict[str, str], rotation_name: str) -> str:
        """회전된 파일명을 생성합니다."""
        return f"{base_info['doc_type']}-{base_info['doc_kind']}-{base_info['disclosure']}-{rotation_name}-{base_info['sequence']}.jpg"
    
    def process_single_file(self, filepath: str) -> List[str]:
        """단일 파일을 처리하여 회전된 버전들을 생성합니다."""
        generated_files = []
        
        # 파일명 파싱
        filename = os.path.basename(filepath)
        file_info = self.parse_filename(filename)
        
        if not file_info:
            print(f"⚠️ 파일명 파싱 실패: {filename}")
            return []
        
        # 0도 파일만 처리
        if file_info["angle"] != "0":
            return []
        
        # 이미지 로드
        image = cv2.imread(filepath)
        if image is None:
            print(f"⚠️ 이미지 로드 실패: {filepath}")
            return []
        
        print(f"처리 중: {filename}")
        
        # 각 회전별로 처리
        for rotation_info in self.rotation_config.values():
            angle = rotation_info["angle"]
            rotation_name = rotation_info["name"]
            
            # 회전 적용
            rotated_image = self.rotate_image(image, angle)
            
            # 새로운 파일명 생성
            new_filename = self.generate_rotated_filename(file_info, rotation_name)
            new_filepath = os.path.join(self.output_dir, new_filename)
            
            # 저장
            cv2.imwrite(new_filepath, rotated_image)
            generated_files.append(new_filepath)
            
            print(f"  생성: {new_filename}")
        
        return generated_files
    
    def process_all_files(self, pattern: str = "*-0-*.jpg") -> Dict[str, int]:
        """모든 0도 파일들을 처리합니다."""
        stats = {
            "total_processed": 0,
            "total_generated": 0,
            "by_doc_type": {},
            "by_disclosure": {},
            "errors": 0
        }
        
        # 0도 파일들 검색
        search_pattern = os.path.join(self.input_dir, pattern)
        files = glob.glob(search_pattern)
        
        print(f"=== 회전 처리 시작 ===")
        print(f"검색 패턴: {search_pattern}")
        print(f"발견된 파일: {len(files)}개")
        
        for filepath in files:
            try:
                generated_files = self.process_single_file(filepath)
                
                if generated_files:
                    stats["total_processed"] += 1
                    stats["total_generated"] += len(generated_files)
                    
                    # 통계 업데이트
                    filename = os.path.basename(filepath)
                    file_info = self.parse_filename(filename)
                    
                    if file_info:
                        doc_type = file_info["doc_type"]
                        disclosure = file_info["disclosure"]
                        
                        stats["by_doc_type"][doc_type] = stats["by_doc_type"].get(doc_type, 0) + 1
                        stats["by_disclosure"][disclosure] = stats["by_disclosure"].get(disclosure, 0) + 1
                else:
                    stats["errors"] += 1
                    
            except Exception as e:
                print(f"❌ 처리 실패 ({filepath}): {e}")
                stats["errors"] += 1
        
        return stats
    
    def create_rotation_manifest(self) -> str:
        """회전된 파일들의 매니페스트를 생성합니다."""
        manifest_path = os.path.join(self.output_dir, "rotation_manifest.csv")
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write("filename,doc_type,doc_kind,disclosure,angle,sequence\n")
            
            # 모든 jpg 파일 검색 (0도 제외)
            for filename in os.listdir(self.output_dir):
                if filename.endswith('.jpg') and '-0-' not in filename:
                    file_info = self.parse_filename(filename)
                    if file_info:
                        f.write(f"{filename},{file_info['doc_type']},{file_info['doc_kind']},{file_info['disclosure']},{file_info['angle']},{file_info['sequence']}\n")
        
        print(f"회전 매니페스트 생성 완료: {manifest_path}")
        return manifest_path

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="문서 회전 처리기")
    parser.add_argument("--input", "-i", default="outputs/dataset", help="입력 디렉토리")
    parser.add_argument("--output", "-o", default="outputs/dataset", help="출력 디렉토리")
    parser.add_argument("--pattern", "-p", default="*-0-*.jpg", help="검색 패턴")
    
    args = parser.parse_args()
    
    print("=== 문서 회전 처리기 ===")
    print(f"입력 디렉토리: {args.input}")
    print(f"출력 디렉토리: {args.output}")
    print(f"검색 패턴: {args.pattern}")
    
    # 회전 처리기 생성
    processor = RotationProcessor(args.input, args.output)
    
    # 모든 파일 처리
    stats = processor.process_all_files(args.pattern)
    
    # 결과 출력
    print(f"\n=== 회전 처리 완료 ===")
    print(f"처리된 파일: {stats['total_processed']}개")
    print(f"생성된 파일: {stats['total_generated']}개")
    print(f"오류: {stats['errors']}개")
    
    print(f"\n📊 문서 종류별 통계:")
    for doc_type, count in stats["by_doc_type"].items():
        print(f"  {doc_type}: {count}개")
    
    print(f"\n📊 공개 방식별 통계:")
    for disclosure, count in stats["by_disclosure"].items():
        print(f"  {disclosure}: {count}개")
    
    # 매니페스트 생성
    processor.create_rotation_manifest()
    
    print(f"\n📁 저장 위치: {args.output}/")
    print(f"📋 총 회전된 이미지: {stats['total_generated']}개")

if __name__ == "__main__":
    main() 