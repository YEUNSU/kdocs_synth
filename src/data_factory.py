import random
from datetime import datetime, timedelta
from faker import Faker

# 한국어 데이터를 생성하기 위한 Faker 인스턴스 초기화
fake = Faker("ko_KR")

# --- 기본 데이터 생성 함수 ---

def generate_name():
    """ 한국어 이름 음절들로 자연스러운 가짜 이름을 생성합니다. """
    
    # 성씨에 쓰이는 음절들 (1글자)
    surname_syllables = [
        "강", "갑", "갈", "감", "갓", "갖", "개", "객", "갠", "갤", "거", "건", "걸", "검", "겁", "게", "겨", "격", "견", "결",
        "경", "계", "고", "곡", "곤", "골", "곰", "곱", "공", "곶", "과", "관", "광", "괘", "괴", "교", "구", "국", "군", "굴",
        "굿", "궁", "권", "귀", "규", "근", "글", "금", "급", "기", "긴", "길", "김", "까", "깅", "나", "낙", "난", "날", "남",
        "납", "낭", "내", "냉", "너", "널", "네", "녕", "노", "녹", "논", "놀", "농", "뇌", "누", "눈", "눌", "능", "다", "단",
        "달", "담", "답", "당", "대", "댁", "더", "덕", "도", "독", "돈", "동", "두", "둔", "득", "등", "라", "락", "란", "람",
        "랑", "래", "량", "려", "력", "련", "렬", "렴", "렵", "령", "례", "로", "록", "론", "롱", "료", "루", "류", "륙", "륜",
        "률", "륭", "르", "름", "릉", "리", "린", "림", "립", "링", "마", "막", "만", "말", "맘", "망", "매", "맥", "맹", "머",
        "먹", "멀", "멈", "멍", "메", "멘", "멸", "명", "모", "목", "몰", "몸", "몽", "뫼", "무", "묵", "문", "물", "뭄", "미",
        "민", "밀", "밈", "밍", "바", "박", "반", "발", "밤", "밥", "방", "배", "백", "뱀", "버", "번", "벌", "범", "법", "벽",
        "변", "별", "병", "보", "복", "본", "볼", "봄", "봉", "부", "북", "분", "불", "붐", "붕", "브", "블", "비", "빈", "빌",
        "빔", "빙", "빚", "빛", "사", "삭", "산", "살", "삼", "삽", "상", "새", "색", "생", "서", "석", "선", "설", "섬", "섭",
        "성", "세", "센", "셜", "소", "속", "손", "솔", "솜", "송", "쇄", "수", "숙", "순", "술", "숨", "숭", "스", "슬", "습",
        "승", "시", "신", "실", "심", "십", "싱", "쌍", "쏘", "쓰", "씨", "아", "악", "안", "알", "암", "압", "앙", "애", "액",
        "앵", "야", "약", "얀", "양", "어", "억", "언", "얼", "엄", "업", "에", "여", "역", "연", "열", "염", "엽", "영", "예",
        "오", "옥", "온", "올", "옴", "옹", "와", "완", "왈", "왕", "외", "요", "욕", "용", "우", "욱", "운", "울", "움", "웅",
        "원", "월", "위", "유", "육", "윤", "율", "융", "으", "은", "을", "음", "응", "의", "이", "익", "인", "일", "임", "입",
        "잉", "자", "작", "잔", "잠", "잡", "장", "재", "쟁", "저", "적", "전", "절", "점", "정", "제", "조", "족", "존", "종",
        "주", "죽", "준", "줄", "중", "즐", "즉", "즉", "증", "지", "직", "진", "질", "짐", "집", "징", "차", "착", "찬", "찰",
        "참", "창", "채", "책", "처", "척", "천", "철", "첨", "청", "체", "초", "촉", "총", "최", "추", "축", "춘", "출", "충",
        "취", "측", "층", "치", "친", "칠", "침", "칭", "카", "칸", "칼", "캄", "캅", "캉", "커", "컨", "컬", "컴", "컵", "케",
        "켄", "코", "콘", "콜", "콤", "콩", "쾌", "크", "큰", "클", "큼", "키", "킨", "킬", "킴", "킹", "타", "탁", "탄", "탈",
        "탐", "탑", "탕", "태", "택", "탱", "터", "턱", "턴", "털", "텀", "텝", "테", "텐", "토", "톤", "톨", "톰", "통", "퇴",
        "투", "툰", "툴", "툼", "트", "틀", "틈", "티", "틴", "틸", "팀", "팅", "파", "팍", "팎", "판", "팔", "팜", "팝", "팡",
        "패", "팩", "팬", "퍼", "펀", "펄", "펌", "펍", "페", "펜", "편", "펼", "평", "폐", "포", "폭", "폰", "폴", "폼", "퐁",
        "표", "푸", "푹", "푼", "풀", "품", "풍", "프", "플", "픔", "피", "핀", "필", "핌", "핑", "하", "학", "한", "할", "함",
        "합", "항", "해", "핵", "행", "향", "허", "헌", "헐", "험", "헙", "헝", "혀", "혁", "현", "혈", "혐", "협", "형", "혜",
        "호", "혹", "혼", "홀", "홈", "홉", "홍", "화", "확", "환", "활", "황", "홰", "횃", "회", "획", "횡", "효", "후", "훅",
        "훈", "훌", "훔", "훨", "휘", "휜", "휠", "휩", "휭", "흄", "흉", "흐", "흑", "흔", "흘", "흠", "흡", "흥", "희", "흰",
        "히", "힌", "힐", "힘"
    ]
    
    # 이름에 쓰이는 음절들 (자주 쓰이는 것들)
    name_syllables = [
        "가", "간", "갈", "감", "강", "개", "건", "걸", "검", "게", "겨", "격", "견", "결", "경", "계", "고", "곡", "곤", "골",
        "공", "과", "관", "광", "교", "구", "국", "군", "굴", "궁", "권", "규", "근", "글", "금", "기", "긴", "길", "김", "나",
        "낙", "난", "날", "남", "낭", "내", "냉", "너", "널", "네", "노", "녹", "논", "농", "누", "눈", "능", "다", "단", "달",
        "담", "당", "대", "더", "덕", "도", "독", "돈", "동", "두", "둔", "득", "등", "라", "락", "란", "람", "랑", "래", "량",
        "려", "력", "련", "렬", "령", "례", "로", "록", "론", "료", "루", "류", "륜", "률", "르", "름", "리", "린", "림", "립",
        "마", "막", "만", "말", "망", "매", "맥", "머", "먹", "멀", "멍", "메", "명", "모", "목", "몰", "몸", "무", "묵", "문",
        "물", "미", "민", "밀", "밍", "바", "박", "반", "발", "밤", "방", "배", "백", "버", "번", "벌", "범", "법", "변", "별",
        "병", "보", "복", "본", "볼", "봄", "봉", "부", "북", "분", "불", "붕", "비", "빈", "빌", "빛", "사", "삭", "산", "살",
        "삼", "상", "새", "색", "생", "서", "석", "선", "설", "섬", "성", "세", "소", "속", "손", "솔", "송", "수", "숙", "순",
        "술", "숨", "승", "시", "신", "실", "심", "싱", "아", "악", "안", "알", "암", "앙", "애", "야", "약", "양", "어", "억",
        "언", "얼", "엄", "에", "여", "역", "연", "열", "염", "영", "예", "오", "옥", "온", "올", "옴", "용", "우", "욱", "운",
        "울", "움", "원", "월", "위", "유", "육", "윤", "율", "융", "은", "을", "음", "응", "의", "이", "익", "인", "일", "임",
        "입", "자", "작", "잔", "장", "재", "저", "적", "전", "절", "점", "정", "제", "조", "족", "종", "주", "죽", "준", "줄",
        "중", "즉", "증", "지", "직", "진", "질", "짐", "집", "차", "착", "찬", "참", "창", "채", "처", "천", "철", "청", "체",
        "초", "총", "최", "추", "축", "춘", "출", "충", "취", "치", "친", "칠", "침", "카", "칸", "컬", "케", "코", "큰", "클",
        "키", "킨", "킬", "타", "탁", "탄", "탈", "탐", "탕", "태", "택", "터", "턴", "테", "토", "톤", "통", "투", "툰", "트",
        "티", "틴", "파", "판", "팔", "팜", "팡", "패", "퍼", "펀", "펄", "페", "편", "평", "포", "폭", "폰", "표", "푸", "풀",
        "품", "풍", "프", "피", "핀", "필", "하", "학", "한", "할", "함", "합", "항", "해", "행", "향", "허", "헌", "현", "혈",
        "형", "혜", "호", "혹", "혼", "홀", "홈", "홍", "화", "확", "환", "활", "황", "회", "효", "후", "훈", "훌", "휘", "흰",
        "희", "히", "힘"
    ]
    
    # 성씨 (1글자)
    surname = random.choice(surname_syllables)
    
    # 이름 (2글자)
    name_part = random.choice(name_syllables) + random.choice(name_syllables)
    
    return f"{surname}{name_part}"

def generate_hanja_name(name):
    """
    주어진 한글 이름에 대해 랜덤 한자 이름을 생성합니다.
    모든 이름에 한자가 나오도록 보장합니다.
    """
    # 더 많은 한자 문자 추가
    hanja_chars = "明俊瑞娟智宇道潤夏恩秀斌美英愛善良德仁義禮智信忠孝慈愛和平喜樂福慧賢淑雅純淸潔"
    
    # 성씨에 대한 한자 매핑 (더 많은 성씨 추가)
    surname_map = {
        '김': '金', '이': '李', '박': '朴', '최': '崔', '정': '鄭', '강': '姜', '조': '趙', '윤': '尹', '장': '張',
        '서': '徐', '지': '池', '한': '韓', '안': '安', '양': '梁', '손': '孫', '배': '裵', '고': '高', '문': '文',
        '송': '宋', '임': '林', '전': '全', '오': '吳', '백': '白', '남': '南', '심': '沈', '노': '盧', '하': '河',
        '곽': '郭', '성': '成', '차': '車', '주': '周', '위': '韋', '구': '具', '신': '申', '국': '國', '태': '太',
        '공': '孔', '마': '馬', '반': '潘', '민': '閔', '엄': '嚴', '유': '柳', '홍': '洪', '신': '申', '허': '許',
        '남궁': '南宮', '사공': '司空', '제갈': '諸葛', '독고': '獨孤', '황보': '皇甫', '선우': '鮮于'
    }
    
    # 복성 처리
    if len(name) >= 2 and name[:2] in surname_map:
        surname = name[:2]
        given_name = name[2:]
    else:
        surname = name[0]
        given_name = name[1:]
    
    # 성씨 한자 (매핑이 없으면 기본 한자 사용)
    hanja_surname = surname_map.get(surname, '金')  # 기본값으로 '金' 사용
    
    # 이름 한자 (최소 1글자 보장)
    if len(given_name) == 0:
        given_name = "철"  # 기본 이름
    
    hanja_given_name = "".join(random.choices(hanja_chars, k=len(given_name)))
    
    result = f"{hanja_surname}{hanja_given_name}"
    
    # 빈 값 방지 - 항상 한자 이름 반환 보장
    if not result or len(result) < 2:
        result = "金秀"  # 기본 한자 이름
    
    return result

def generate_address():
    """ 랜덤 한국 주소를 생성합니다. """
    return fake.address()

def generate_date(start_date, end_date):
    """ 완전히 무작위 숫자로 가짜 날짜를 생성합니다. (YYYY.MM.DD 형식) """
    # 완전 임의 숫자 (형식만 맞춤)
    part1 = random.randint(1000, 9999)  # 4자리
    part2 = random.randint(10, 99)      # 2자리  
    part3 = random.randint(10, 99)      # 2자리
    
    return f"{part1}.{part2}.{part3}"

def generate_jumin(birthdate_str, gender, mask_suffix=True):
    """ 완전히 무작위 숫자로 가짜 주민등록번호를 생성합니다. 
    
    Args:
        birthdate_str: 생년월일 (사용하지 않음, 완전 무작위)
        gender: 성별 (사용하지 않음, 완전 무작위)
        mask_suffix: True이면 뒷자리 마스킹, False이면 전체 공개
    """
    # 완전 임의의 6자리 숫자 (아무 의미 없음)
    fake_digits = f"{random.randint(100000, 999999):06d}"
    
    # 임의의 성별 코드 (1-9, 더 다양하게)
    gender_digit = random.randint(1, 9)
    
    if mask_suffix:
        # 뒷자리 미공개: 123456-1******
        return f"{fake_digits}-{gender_digit}******"
    else:
        # 전부 공개: 123456-1234567
        fake_suffix = f"{random.randint(100000, 999999):06d}"
        return f"{fake_digits}-{gender_digit}{fake_suffix}"

def generate_household_data():
    """
    세대구성 사유 및 일자를 생성합니다.
    """
    # 세대구성 일자는 랜덤 날짜로 생성 (YYYY-MM-DD 형식)
    household_date = generate_date(None, None)  # 무작위 날짜
    if '.' in household_date:  # YYYY.MM.DD 형식인 경우
        household_date = household_date.replace('.', '-')  # YYYY-MM-DD 형식으로 변경
    
    # 세대구성 사유 생성 (가중치 적용)
    household_reasons = [
        "전입", "분가", "세대합가", "혼인", "출생등록", 
        "이혼", "입양", "이전세대주전출", "세대주변경", "기타", "사망"
    ]
    weights = [30, 20, 15, 12, 8, 5, 3, 3, 2, 1, 1]  # 총 100%
    household_reason = random.choices(household_reasons, weights=weights)[0]
    
    return {
        "HOUSEHOLD_REASON": household_reason,
        "HOUSEHOLD_DATE": household_date
    }

# --- 핵심 함수: 데이터 레코드 생성 ---

def create_person(relationship, min_age=0, max_age=80, mask_jumin=True):
    """ 한 사람에 대한 데이터 묶음을 생성합니다. 
    
    Args:
        relationship: 관계 (본인, 부, 모, 자녀 등)
        min_age: 최소 연령 (사용하지 않음)
        max_age: 최대 연령 (사용하지 않음)
        mask_jumin: True이면 주민번호 뒷자리 마스킹, False이면 전체 공개
    """
    name = generate_name()
    gender = random.choice(["남", "여"])
    birthdate = generate_date(None, None)  # 무작위 날짜
    
    person_data = {
        "RELATION": relationship,
        "NAME": name,
        "NAME_CN": generate_hanja_name(name),
        "BIRTH": birthdate,
        "EVENT_DATE": random.choices(
            ["", "-------", "1212-23-23"],  # 빈칸, 대시, 날짜
            weights=[5, 42.5, 42.5]  # 가중치
        )[0], # 주민등록등본용 발생일
        "JUMIN": generate_jumin(birthdate, gender, mask_suffix=mask_jumin),
        "GENDER": gender,
        "ORIGIN": random.choice(["김해", "전주", "경주", "밀양", "안동"]), # 본관 예시
        "REPORT_DATE": generate_date(None, None),  # 무작위 날짜
        "STATUS": "거주자",
        "CHANGE_REASON": random.choices(
            ["", "전입", "전출", "출생등록", "분가", "세대합가", "혼인", "이혼", "기타"],
            weights=[30, 35, 14, 7, 5.6, 3.5, 2.8, 1.4, 0.7]  # 30% 공란, 전입이 35% 확률로 가장 많이
        )[0]
    }
    
    # 주민등록등본용 번호는 나중에 추가
    return person_data

def create_record(doc_type="GA", options=None):
    """
    한 장의 문서(가족관계증명서 또는 주민등록등본)를 채울 전체 데이터 레코드를 생성합니다.
    """
    if options is None:
        options = {}

    # 주민번호 마스킹 설정 (기본값: 뒷자리 마스킹)
    mask_jumin = options.get("mask_jumin", True)
    
    # --- 본인(MAIN) 정보 생성 ---
    main_person = create_person(relationship="본인", min_age=25, max_age=55, mask_jumin=mask_jumin)
    
    # 최종적으로 반환될 데이터 딕셔너리
    record = {}
    
    if doc_type == "GA":
        record.update({f"MAIN_{key}": value for key, value in main_person.items()})
        record["BASE_ADDRESS"] = generate_address()
    elif doc_type == "JU":
        record["MAIN_NAME"] = main_person["NAME"]
        record["MAIN_NAME_CN"] = main_person["NAME_CN"]
        record["MAIN_BIRTH"] = main_person["BIRTH"]  # 신청인 생년월일 추가
        record["MAIN_ADDRESS"] = generate_address()
        record["MAIN_EVENT_DATE"] = generate_date(None, None)  # 무작위 날짜
        record["MAIN_REPORT_DATE"] = record["MAIN_EVENT_DATE"]
        
        # 세대구성 사유 및 일자 추가
        household_data = generate_household_data()
        record.update(household_data)

    record["APPLICANT"] = main_person["NAME"]
    record["APPLICANT_BIRTH"] = main_person["BIRTH"]
    
    # 발급기관 정보 (상단, 하단 동일)
    cities = ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시"]
    districts = ["강남구", "강서구", "서초구", "송파구", "영등포구", "마포구", "종로구", "중구", "용산구", "성동구"]
    issuer_name = f"{random.choice(cities)} {random.choice(districts)}청장"
    record["ISSUER_TOP"] = issuer_name
    record["ISSUER_BOTTOM"] = issuer_name

    # --- 문서 종류별 가족/세대원 정보 생성 ---
    if doc_type == "GA":
        children_count = options.get("children_count", random.randint(0, 3))
        
        main_birth_year = int(main_person["BIRTH"][:4])
        record.update({f"PARENT1_{k}": v for k, v in create_person("부", min_age=main_birth_year - 1960, max_age=main_birth_year - 1930, mask_jumin=mask_jumin).items()})
        record.update({f"PARENT2_{k}": v for k, v in create_person("모", min_age=main_birth_year - 1965, max_age=main_birth_year - 1935, mask_jumin=mask_jumin).items()})

        # 자녀가 있으면 배우자도 생성
        if children_count > 0:
            record.update({f"SPOUSE_{k}": v for k, v in create_person("배우자", min_age=25, max_age=55, mask_jumin=mask_jumin).items()})

        for i in range(children_count):
            record.update({f"CHILD{i+1}_{k}": v for k, v in create_person("자녀", min_age=0, max_age=24, mask_jumin=mask_jumin).items()})

    elif doc_type == "JU":
        members_count = options.get("members_count", random.randint(1, 5))
        
        # 첫번째 멤버는 항상 본인(세대주)
        main_person['NUMBER'] = '1'
        main_person['RELATION'] = '본인'
        record.update({f"MEMBER1_{k}": v for k, v in main_person.items()})

        # 나머지 세대원 생성
        relationships = ["배우자", "자녀", "부", "모"]
        random.shuffle(relationships)
        
        for i in range(2, members_count + 1):
            rel = relationships.pop(0) if relationships else "동거인"
            member = create_person(rel, min_age=0, max_age=80, mask_jumin=mask_jumin)
            member['NUMBER'] = str(i)
            record.update({f"MEMBER{i}_{k}": v for k, v in member.items()})
    
    return record

# --- 테스트용 실행 블록 ---
if __name__ == '__main__':
    import json
    from datetime import datetime
    
    # 결과 저장할 디렉토리 생성
    import os
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    print("--- [Test] 가족관계증명서 데이터 생성 (자녀 2명) ---")
    ga_record = create_record(doc_type="GA", options={"children_count": 2})
    for key, value in ga_record.items():
        print(f"{key:<20}: {value}")
    
    # 가족관계증명서 데이터를 JSON 파일로 저장
    ga_filename = f"data/ga_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(ga_filename, 'w', encoding='utf-8') as f:
        json.dump(ga_record, f, ensure_ascii=False, indent=2)
    print(f"\n[저장됨] 가족관계증명서 데이터: {ga_filename}")
        
    print("\n" + "="*50 + "\n")
    
    print("--- [Test] 주민등록등본 데이터 생성 (세대원 4명) ---")
    ju_record = create_record(doc_type="JU", options={"members_count": 4})
    for key, value in ju_record.items():
        print(f"{key:<20}: {value}")
    
    # 주민등록등본 데이터를 JSON 파일로 저장
    ju_filename = f"data/ju_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(ju_filename, 'w', encoding='utf-8') as f:
        json.dump(ju_record, f, ensure_ascii=False, indent=2)
    print(f"\n[저장됨] 주민등록등본 데이터: {ju_filename}")
    
    print(f"\n=== 생성 완료 ===")
    print(f"가족관계증명서: {ga_filename}")
    print(f"주민등록등본: {ju_filename}")
    print(f"데이터 폴더: {output_dir}/")
