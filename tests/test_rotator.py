import os
from rotator import DocumentRotator
from data_factory import create_record

def test_rotation():
    """회전 기능 테스트"""
    print("=== 회전 기능 테스트 ===")
    
    rotator = DocumentRotator()
    
    # 테스트용 데이터 생성
    test_data = create_record("GA", {"children_count": 2})
    
    # GA_template1_child2로 테스트 (이미 완성된 템플릿)
    template_name = "GA_template1_child2"
    
    print(f"테스트 템플릿: {template_name}")
    print(f"테스트 데이터: {test_data['MAIN_NAME']} (자녀 {test_data.get('CHILD1_NAME', '없음')})")
    
    # 4방향 회전 문서 생성 (인덱스 1번)
    generated_files = rotator.generate_rotated_documents(
        template_name, test_data, 1, "outputs/test_rotation"
    )
    
    print(f"\n생성된 파일들:")
    for file_path in generated_files:
        filename = os.path.basename(file_path)
        print(f"  ✅ {filename}")
    
    print(f"\n총 {len(generated_files)}개 파일 생성 완료!")
    return generated_files

def test_small_dataset():
    """작은 규모 데이터셋 테스트"""
    print("\n=== 작은 규모 데이터셋 테스트 ===")
    
    rotator = DocumentRotator()
    
    # 2개 템플릿, 각각 2개 샘플로 테스트
    templates = [
        ("GA_template1_child0", 0),  # 본인,부,모
        ("GA_template1_child2", 2),  # 본인,부,모,자녀2명
    ]
    
    output_dir = "outputs/test_small_dataset"
    os.makedirs(output_dir, exist_ok=True)
    
    counters = {"GA-0": 0, "GA-L": 0, "GA-R": 0, "GA-180": 0}
    total_generated = 0
    
    for template_name, children_count in templates:
        print(f"📋 템플릿 처리 중: {template_name} (자녀 {children_count}명)")
        
        for i in range(2):  # 2개 샘플씩
            try:
                # 랜덤 데이터 생성
                data = create_record("GA", {"children_count": children_count})
                
                # 4방향 회전 문서 생성
                generated_files = rotator.generate_rotated_documents(
                    template_name, data, 
                    counters["GA-0"] + 1,
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
                print(f"   샘플 {i+1}/2 완료")
                
            except Exception as e:
                print(f"   오류 발생: {e}")
                continue
        
        print(f"   ✅ {template_name} 완료")
    
    print(f"\n=== 작은 규모 테스트 완료 ===")
    print(f"총 생성된 파일 수: {total_generated}장")
    print("회전별 생성 수:")
    for rotation, count in counters.items():
        print(f"  {rotation}: {count}장")
    
    # 매니페스트 생성
    manifest_path = rotator.create_manifest(output_dir)
    
    return counters

if __name__ == "__main__":
    # 1. 회전 기능 테스트
    test_rotation()
    
    # 2. 작은 규모 데이터셋 테스트
    test_small_dataset()
    
    print("\n🎉 모든 테스트 완료!")
    print("📁 결과물 확인:")
    print("  - outputs/test_rotation/ (회전 테스트)")
    print("  - outputs/test_small_dataset/ (작은 데이터셋 테스트)") 