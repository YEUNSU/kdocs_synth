#!/usr/bin/env python3
"""
주민등록등본(JU) 대량 생성 시스템 - 새로운 파일명 규칙 적용

요구사항:
- 3개 등본 × 4개 바코드 조합 = 12개 템플릿
- 각 템플릿당: 1명(1장) + 2명(1장) + 3~5명(8장) = 10장
- 총 240장 (회전 전)
"""

import os
import sys
import random
import cv2
from typing import List, Dict, Tuple

# 모듈 경로 추가
sys.path.append('src')

from templates_juga import create_template
from data_factory import create_record

class JUBatchGenerator:
    """주민등록등본 대량 생성기"""
    
    def __init__(self, output_dir: str = "outputs/dataset"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 템플릿 설정
        self.regions = [1, 2, 3]  # 등본1, 등본2, 등본3
        self.barcodes = ["TY00", "TY01", "TY10", "TY11"]
        
        # 세대원 수별 생성 설정
        self.member_configs = [
            {"members_count": 1, "count": 1},   # 1명 → 1장
            {"members_count": 2, "count": 1},   # 2명 → 1장  
            {"members_count": 3, "count": 2},   # 3명 → 2장
            {"members_count": 4, "count": 3},   # 4명 → 3장
            {"members_count": 5, "count": 3},   # 5명 → 3장
        ]  # 총 10장 per 템플릿
        
        # 주민번호 공개 방식 2가지
        self.jumin_configs = [
            {"jumin_disclosure": "CLOSE", "name": "CLOSE"},
            {"jumin_disclosure": "OPEN", "name": "OPEN"}
        ]
        
    def generate_all_ju_documents(self) -> Dict[str, int]:
        """모든 JU 문서를 생성합니다."""
        
        stats = {"total": 0, "by_template": {}, "by_doc_kind": {}}
        
        # 문서 종류별 순차번호 카운터 (5자리)
        file_counter = {
            "JU-1": {"CLOSE": 1, "OPEN": 1},  # 등본1
            "JU-2": {"CLOSE": 1, "OPEN": 1},  # 등본2
            "JU-3": {"CLOSE": 1, "OPEN": 1},  # 등본3
        }
        
        print("=== JU 대량 생성 시작 ===")
        print(f"목표: {len(self.regions)} 등본 × {len(self.barcodes)} 바코드 × 10장 × 2주민번호방식 = {len(self.regions) * len(self.barcodes) * 10 * 2}장")
        
        for region in self.regions:
            doc_kind = f"JU-{region}"  # JU-1, JU-2, JU-3
            
            for barcode in self.barcodes:
                template_name = f"JU_template{region}_{barcode}"
                template_stats = self._generate_template_batch(template_name, doc_kind, file_counter)
                
                stats["by_template"][template_name] = template_stats
                stats["total"] += template_stats
                
                print(f"  ✓ {template_name} ({doc_kind}): {template_stats}장 생성")
        
        # 문서 종류별 통계 계산
        for doc_kind in ["JU-1", "JU-2", "JU-3"]:
            close_count = file_counter[doc_kind]["CLOSE"] - 1
            open_count = file_counter[doc_kind]["OPEN"] - 1
            stats["by_doc_kind"][doc_kind] = close_count + open_count
            
        print(f"\n📊 최종 파일 카운터 상태:")
        for doc_kind in ["JU-1", "JU-2", "JU-3"]:
            close_count = file_counter[doc_kind]["CLOSE"] - 1
            open_count = file_counter[doc_kind]["OPEN"] - 1
            total_count = close_count + open_count
            print(f"  {doc_kind}: CLOSE({close_count}) + OPEN({open_count}) = {total_count}장")
            
        self._print_final_stats(stats)
        return stats
    
    def _generate_template_batch(self, template_name: str, doc_kind: str, file_counter: Dict[str, int]) -> int:
        """특정 템플릿의 배치를 생성합니다."""
        
        generated_count = 0
        
        # 주민번호 방식별로 생성
        for jumin_config in self.jumin_configs:
            jumin_disclosure = jumin_config["jumin_disclosure"]
            jumin_name = jumin_config["name"]
            
            # 세대원 수별로 생성
            for member_config in self.member_configs:
                members_count = member_config["members_count"]
                count = member_config["count"]
                
                for i in range(count):
                    # 템플릿 생성 (세대원 수 제한)
                    template = create_template("JU", template_name, max_members=members_count, mask_jumin=(jumin_disclosure=="CLOSE"))
                    
                    # 데이터 생성 (주민번호 공개 설정 포함)
                    data = create_record("JU", {
                        "members_count": members_count,
                        "jumin_disclosure": jumin_disclosure
                    })
                    
                    # 디버깅: 주민번호 확인
                    jumin_sample = data.get("MEMBER1_JUMIN", "N/A")
                    print(f"      🔍 {jumin_name} | {members_count}명 | 주민번호샘플: {jumin_sample}")
                    
                    # 이미지 생성
                    img = template.render(data)
                    
                    # 새로운 파일명 규칙: JU-{문서종류}-{주민번호공개여부}-0-{순차번호5자리}
                    sequential_number = file_counter[doc_kind][jumin_name]
                    filename = f"{doc_kind}-{jumin_name}-0-{sequential_number:05d}.jpg"
                    
                    # 파일 저장 (0도만)
                    filepath = os.path.join(self.output_dir, filename)
                    cv2.imwrite(filepath, img)
                    
                    # 카운터 증가
                    file_counter[doc_kind][jumin_name] += 1
                    generated_count += 1
                    
                    print(f"        생성: {filename}")
        
        return generated_count
    
    def _print_final_stats(self, stats: Dict):
        """최종 통계를 출력합니다."""
        print("\n=== JU 생성 완료 ===")
        print(f"생성된 이미지: {stats['total']}장")
        print(f"구성: 3등본 × 4바코드 × 10장 × 2주민번호방식 = {3*4*10*2}장")
        print("\n📊 문서 종류별 통계:")
        for doc_kind, count in stats["by_doc_kind"].items():
            print(f"  - {doc_kind}: {count}장")
        
        print(f"\n📁 저장 위치: {self.output_dir}/")
        print(f"📋 총 학습용 이미지: {stats['total']}장 (회전 전)")

def main():
    """메인 실행 함수"""
    generator = JUBatchGenerator()
    generator.generate_all_ju_documents()

if __name__ == "__main__":
    main() 