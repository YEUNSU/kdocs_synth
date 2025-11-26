import random
import cv2
import numpy as np
from datetime import datetime, timedelta
from faker import Faker

# 한국어 데이터를 생성하기 위한 Faker 인스턴스 초기화
fake = Faker("ko_KR")

# --- 기본 데이터 생성 함수 ---

def generate_name():
    """ 실제 한국 이름에서 자주 사용되는 음절로 자연스러운 이름을 생성합니다. """

    # 실제 한국에서 가장 많이 쓰이는 성씨 (상위 20개로 제한)
    surnames = [
        "김", "이", "박", "최", "정", "강", "조", "윤", "장", "임",
        "한", "오", "서", "신", "권", "황", "안", "송", "전", "홍"
    ]

    # 정말 흔하고 쉬운 이름 음절만 (2020년대 인기 이름 기준)
    name_syllables_first = [
        "민", "서", "지", "수", "현", "예", "하", "주", "은", "도",
        "준", "영", "선", "정", "성", "재", "진", "혜", "미", "희"
    ]

    name_syllables_second = [
        "준", "서", "우", "진", "민", "호", "현", "수", "영", "희",
        "정", "은", "아", "연", "경", "미", "지", "선", "재", "훈"
    ]

    # 성씨 (1글자)
    surname = random.choice(surnames)

    # 이름 (2글자)
    name_part = random.choice(name_syllables_first) + random.choice(name_syllables_second)

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

def generate_date(start_date, end_date, min_age=None, max_age=None):
    """ 현실적인 날짜를 생성합니다. (YYYY.MM.DD 형식)

    Args:
        start_date: 사용하지 않음 (하위 호환성)
        end_date: 사용하지 않음 (하위 호환성)
        min_age: 최소 나이 (예: 0세)
        max_age: 최대 나이 (예: 19세)
    """
    from datetime import datetime

    current_year = datetime.now().year

    # min_age, max_age가 주어진 경우 해당 나이 범위로 생년월일 생성
    if min_age is not None and max_age is not None:
        # 나이를 년도로 변환 (max_age가 더 오래된 년도)
        min_year = current_year - max_age
        max_year = current_year - min_age

        # min_year와 max_year가 같으면 1년 범위로 조정
        if min_year == max_year:
            max_year = min_year + 1

        # 년도에서 3이 포함되지 않은 년도만 선택
        valid_years = [y for y in range(min_year, max_year + 1) if '3' not in str(y)]
        if valid_years:
            year = random.choice(valid_years)
        else:
            year = random.randint(min_year, max_year)  # 3 없는 년도가 없으면 그냥 선택
    else:
        # 기본값: 1950년부터 2025년까지 (3 제외)
        valid_years = [y for y in range(1950, 2026) if '3' not in str(y)]
        year = random.choice(valid_years)

    # 월에서 3 제외 (1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12)
    months_without_3 = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    month = random.choice(months_without_3)

    # 월별 일수 계산
    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:  # 2월
        # 윤년 확인
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            max_day = 29
        else:
            max_day = 28

    day = random.randint(1, max_day)

    return f"{year}.{month:02d}.{day:02d}"

def generate_jumin(birthdate_str, gender, jumin_disclosure="CLOSE"):
    """ 생년월일과 일관된 주민등록번호를 생성합니다.

    Args:
        birthdate_str: 생년월일 (YYYY.MM.DD 형식)
        gender: 성별 (남/여)
        jumin_disclosure: "OPEN"이면 전체 공개, "CLOSE"이면 뒷자리 마스킹
    """
    # 생년월일에서 앞 6자리 추출
    if '.' in birthdate_str:
        parts = birthdate_str.split('.')
        if len(parts) == 3:
            year = parts[0]
            month = parts[1]
            day = parts[2]

            # YY 형식으로 변환 (4자리 년도를 2자리로)
            yy = year[-2:]
            front_6 = f"{yy}{month}{day}"
        else:
            front_6 = f"{random.randint(100000, 999999):06d}"
    else:
        front_6 = f"{random.randint(100000, 999999):06d}"

    # 성별 코드 결정 (생년월일 기준)
    try:
        birth_year = int(parts[0])
        if birth_year >= 2000:
            # 2000년 이후 출생
            gender_digit = 3 if gender == "남" else 4
        elif birth_year >= 1900:
            # 1900-1999년 출생
            gender_digit = 1 if gender == "남" else 2
        else:
            # 1900년 이전
            gender_digit = 9 if gender == "남" else 0
    except:
        gender_digit = 1 if gender == "남" else 2

    if jumin_disclosure == "CLOSE":
        # 뒷자리 미공개: 890918-1******
        return f"{front_6}-{gender_digit}******"
    else:
        # 전체 공개: 890918-1234567
        fake_suffix = f"{random.randint(100000, 999999):06d}"
        return f"{front_6}-{gender_digit}{fake_suffix}"

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

def create_person(relationship, min_age=0, max_age=80, jumin_disclosure="CLOSE"):
    """ 한 사람에 대한 데이터 묶음을 생성합니다.

    Args:
        relationship: 관계 (본인, 부, 모, 자녀 등)
        min_age: 최소 연령 (예: 0세)
        max_age: 최대 연령 (예: 19세)
        jumin_disclosure: "OPEN"이면 주민번호 전체 공개, "CLOSE"이면 뒷자리 마스킹
    """
    name = generate_name()
    gender = random.choice(["남", "여"])
    birthdate = generate_date(None, None, min_age=min_age, max_age=max_age)
    
    person_data = {
        "RELATION": relationship,
        "NAME": name,
        "NAME_CN": generate_hanja_name(name),
        "BIRTH": birthdate,
        "EVENT_DATE": random.choices(
            ["", "-------", "1212-23-23"],  # 빈칸, 대시, 날짜
            weights=[5, 42.5, 42.5]  # 가중치
        )[0], # 주민등록등본용 발생일
        "JUMIN": generate_jumin(birthdate, gender, jumin_disclosure=jumin_disclosure),
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

    # 주민번호 공개 설정 (기본값: 뒷자리 마스킹)
    jumin_disclosure = options.get("jumin_disclosure", "CLOSE")

    # --- 본인(MAIN) 정보 생성 ---
    main_person = create_person(relationship="본인", min_age=25, max_age=55, jumin_disclosure=jumin_disclosure)
    
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

    # 신청인은 본인과 다른 사람으로 생성 (별도 생성)
    applicant = generate_name()
    applicant_birth = generate_date(None, None)
    record["APPLICANT"] = applicant
    record["APPLICANT_BIRTH"] = applicant_birth
    
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
        record.update({f"PARENT1_{k}": v for k, v in create_person("부", min_age=main_birth_year - 1960, max_age=main_birth_year - 1930, jumin_disclosure=jumin_disclosure).items()})
        record.update({f"PARENT2_{k}": v for k, v in create_person("모", min_age=main_birth_year - 1965, max_age=main_birth_year - 1935, jumin_disclosure=jumin_disclosure).items()})

        # 자녀가 있으면 배우자도 생성
        if children_count > 0:
            record.update({f"SPOUSE_{k}": v for k, v in create_person("배우자", min_age=25, max_age=55, jumin_disclosure=jumin_disclosure).items()})

        # 자녀들 생성 (나이 차이를 1~5년으로 제한)
        children = []
        if children_count > 0:
            # 첫째 자녀: 5~19세
            first_child = create_person("자녀", min_age=5, max_age=19, jumin_disclosure=jumin_disclosure)
            children.append(first_child)

            # 나머지 자녀들: 첫째보다 1~5살 어리게
            from datetime import datetime
            first_birth_year = int(first_child["BIRTH"][:4])

            for i in range(1, children_count):
                # 이전 형제보다 1~5살 어리게
                age_gap = random.randint(1, 5)
                prev_birth_year = int(children[i-1]["BIRTH"][:4])
                child_birth_year_min = prev_birth_year + 1  # 최소 1년 차이
                child_birth_year_max = prev_birth_year + age_gap  # 최대 age_gap년 차이

                # 현재 년도 기준으로 나이 계산
                current_year = datetime.now().year
                child_max_age = current_year - child_birth_year_min
                child_min_age = max(0, current_year - child_birth_year_max)

                child = create_person("자녀", min_age=child_min_age, max_age=child_max_age, jumin_disclosure=jumin_disclosure)
                children.append(child)

        # 정렬된 자녀들을 record에 추가
        for i, child in enumerate(children):
            record.update({f"CHILD{i+1}_{k}": v for k, v in child.items()})

    elif doc_type == "JU":
        members_count = options.get("members_count", random.randint(1, 5))

        # 첫번째 멤버는 항상 본인(세대주)
        main_person['NUMBER'] = '1'
        main_person['RELATION'] = '본인'
        record.update({f"MEMBER1_{k}": v for k, v in main_person.items()})

        # 나머지 세대원 생성 - 순서: 배우자 → 자녀들 (본인/배우자/자녀로만 구성)

        # 1. 배우자 생성 (무조건 포함)
        spouse = create_person("배우자", min_age=25, max_age=55, jumin_disclosure=jumin_disclosure)
        spouse['NUMBER'] = '2'
        record.update({f"MEMBER2_{k}": v for k, v in spouse.items()})

        # 2. 자녀들 생성 (2~3명 중 랜덤, 나이 차이 1~5년)
        children_count = random.randint(2, 3)
        children = []

        if children_count > 0:
            # 첫째 자녀: 5~19세
            first_child = create_person("자녀", min_age=5, max_age=19, jumin_disclosure=jumin_disclosure)
            children.append(first_child)

            # 나머지 자녀들: 형제보다 1~5살 어리게
            from datetime import datetime
            current_year = datetime.now().year

            for i in range(1, children_count):
                age_gap = random.randint(1, 5)
                prev_birth_year = int(children[i-1]["BIRTH"][:4])
                child_birth_year_min = prev_birth_year + 1
                child_birth_year_max = prev_birth_year + age_gap

                child_max_age = current_year - child_birth_year_min
                child_min_age = max(0, current_year - child_birth_year_max)

                child = create_person("자녀", min_age=child_min_age, max_age=child_max_age, jumin_disclosure=jumin_disclosure)
                children.append(child)

        # 자녀들을 record에 추가
        for idx, child in enumerate(children):
            child['NUMBER'] = str(idx + 3)  # 본인(1), 배우자(2) 다음부터
            record.update({f"MEMBER{idx+3}_{k}": v for k, v in child.items()})
    
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
