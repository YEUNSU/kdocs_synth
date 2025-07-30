#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
sys.path.append('src')

from data_factory import create_record
from templates_juga import create_template
import cv2

def test_ju_combinations():
    """주민등록등본(JU) 8가지 조합 테스트"""
    print("=== 주민등록등본(JU) 8가지 조합 테스트 ===")
    
    # 등본1의 8가지 조합
    combinations = [
        {"template": "JU_template1_TY00", "mask_jumin": True, "desc": "등본1 우측X 하단X 미공개"},
        {"template": "JU_template1_TY00", "mask_jumin": False, "desc": "등본1 우측X 하단X 전체공개"},
        {"template": "JU_template1_TY10", "mask_jumin": True, "desc": "등본1 우측O 하단X 미공개"},
        {"template": "JU_template1_TY10", "mask_jumin": False, "desc": "등본1 우측O 하단X 전체공개"},
        {"template": "JU_template1_TY01", "mask_jumin": True, "desc": "등본1 우측X 하단O 미공개"},
        {"template": "JU_template1_TY01", "mask_jumin": False, "desc": "등본1 우측X 하단O 전체공개"},
        {"template": "JU_template1_TY11", "mask_jumin": True, "desc": "등본1 우측O 하단O 미공개"},
        {"template": "JU_template1_TY11", "mask_jumin": False, "desc": "등본1 우측O 하단O 전체공개"},
    ]
    
    for i, combo in enumerate(combinations, 1):
        print(f"\n--- 테스트 {i}: {combo['desc']} ---")
        
        # 데이터 생성
        record = create_record("JU", options={"members_count": 3, "mask_jumin": combo["mask_jumin"]})
        
        # 주민번호 마스킹 확인
        jumin_fields = [k for k in record.keys() if k.endswith('_JUMIN')]
        masked_count = 0
        unmasked_count = 0
        
        for field in jumin_fields:
            jumin_value = record[field]
            if '******' in jumin_value:
                masked_count += 1
            else:
                unmasked_count += 1
        
        print(f"마스킹된 주민번호: {masked_count}개")
        print(f"전체공개 주민번호: {unmasked_count}개")
        
        # 세대구성 사유 및 일자 확인
        household_reason = record.get('HOUSEHOLD_REASON', 'N/A')
        household_date = record.get('HOUSEHOLD_DATE', 'N/A')
        print(f"세대구성 사유: {household_reason}")
        print(f"세대구성 일자: {household_date}")
        
        # 렌더링 테스트
        try:
            template = create_template("JU", combo["template"], max_members=3, mask_jumin=combo["mask_jumin"])
            
            result_img = template.render(record)
            
            # 파일명 생성
            mask_suffix = "MASK" if combo["mask_jumin"] else "OPEN"
            template_suffix = combo["template"].split("_")[-1]  # TY00, TY01, TY10, TY11
            output_path = f"outputs/test_ju_{template_suffix}_{mask_suffix}.jpg"
            
            os.makedirs("outputs", exist_ok=True)
            cv2.imwrite(output_path, result_img)
            
            print(f"✅ 렌더링 성공: {output_path}")
            
        except Exception as e:
            print(f"❌ 렌더링 실패: {e}")

def test_ju_member_counts():
    """주민등록등본(JU) 세대원 수별 테스트"""
    print("\n=== 주민등록등본(JU) 세대원 수별 테스트 ===")
    
    # 우측X 하단X (TY00) 기준으로 세대원 수별 테스트
    member_counts = [1, 2, 3, 4, 5]  # 1명, 2명, 3~5명
    
    for members_count in member_counts:
        print(f"\n--- 세대원 {members_count}명 테스트 ---")
        
        # 데이터 생성 (미공개)
        record = create_record("JU", options={"members_count": members_count, "mask_jumin": True})
        
        # 생성된 모든 필드 확인 (디버깅용)
        print(f"생성된 필드 수: {len(record)}개")
        member_fields = [k for k in record.keys() if k.startswith('MEMBER')]
        print(f"MEMBER 필드들: {member_fields}")
        
        # 세대원 수 확인 (정규표현식 사용)
        member_numbers = set()
        for k in record.keys():
            m = re.match(r'MEMBER(\d+)_NAME$', k)
            if m:
                member_numbers.add(int(m.group(1)))
        actual_members = len(member_numbers)
        print(f"요청된 세대원 수: {members_count}명")
        print(f"실제 생성된 세대원 수: {actual_members}명")
        
        # 세대원 정보 상세 확인
        print("\n=== 세대원 상세 정보 ===")
        for i in sorted(member_numbers):
            member_name = record.get(f'MEMBER{i}_NAME', 'N/A')
            member_name_cn = record.get(f'MEMBER{i}_NAME_CN', 'N/A')
            member_jumin = record.get(f'MEMBER{i}_JUMIN', 'N/A')
            member_relation = record.get(f'MEMBER{i}_RELATION', 'N/A')
            member_change_reason = record.get(f'MEMBER{i}_CHANGE_REASON', 'N/A')
            member_event_date = record.get(f'MEMBER{i}_EVENT_DATE', 'N/A')
            
            print(f"  세대원{i}:")
            print(f"    이름: '{member_name}' (한자: '{member_name_cn}')")
            print(f"    주민번호: '{member_jumin}'")
            print(f"    관계: '{member_relation}'")
            print(f"    변동사유: '{member_change_reason}'")
            print(f"    발생일/신고일: '{member_event_date}'")
        
        # 세대주 정보도 확인
        print("\n=== 세대주 정보 ===")
        main_name = record.get('MAIN_NAME', 'N/A')
        main_name_cn = record.get('MAIN_NAME_CN', 'N/A')
        main_jumin = record.get('MAIN_JUMIN', 'N/A')
        household_reason = record.get('HOUSEHOLD_REASON', 'N/A')
        household_date = record.get('HOUSEHOLD_DATE', 'N/A')
        
        print(f"세대주 이름: '{main_name}' (한자: '{main_name_cn}')")
        print(f"세대주 주민번호: '{main_jumin}'")
        print(f"세대구성 사유: '{household_reason}'")
        print(f"세대구성 일자: '{household_date}'")
        
        # 렌더링 테스트
        try:
            template = create_template("JU", "JU_template1_TY00", max_members=None, mask_jumin=True)
            
            # 간단한 디버깅 정보
            print(f"template.members_count: {template.members_count}")
            
            # 필터링된 데이터 확인
            filtered_data = {}
            for field_name, field_value in record.items():
                if field_name.startswith('MEMBER'):
                    match = re.match(r'MEMBER(\d+)', field_name)
                    if match:
                        member_num = int(match.group(1))
                        if member_num <= template.members_count:
                            filtered_data[field_name] = field_value
                else:
                    filtered_data[field_name] = field_value
            
            print(f"필터링된 MEMBER 필드들: {[k for k in filtered_data.keys() if k.startswith('MEMBER')]}")
            
            result_img = template.render(record)
            
            # 파일명 생성
            output_path = f"outputs/test_ju_TY00_MASK_{members_count}members.jpg"
            
            os.makedirs("outputs", exist_ok=True)
            cv2.imwrite(output_path, result_img)
            
            print(f"✅ 렌더링 성공: {output_path}")
            
        except Exception as e:
            print(f"❌ 렌더링 실패: {e}")

if __name__ == "__main__":
    test_ju_combinations()
    test_ju_member_counts() 