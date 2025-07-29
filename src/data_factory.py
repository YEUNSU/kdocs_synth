import random
from datetime import datetime, timedelta
from faker import Faker

# 한국어 데이터를 생성하기 위한 Faker 인스턴스 초기화
fake = Faker("ko_KR")

# --- 기본 데이터 생성 함수 ---

def generate_name():
    """ 랜덤 한국인 이름을 생성합니다. (예: 김민준) """
    return fake.name()

def generate_hanja_name(name):
    """
    주어진 한글 이름에 대해 랜덤 한자 이름을 생성합니다.
    (간단한 예시이며, 실제 한자 DB 연동 등으로 고도화 가능)
    """
    # 일반적인 이름에 사용되는 한자 목록
    hanja_chars = "明俊瑞娟智宇道潤夏恩秀斌"
    # 성씨에 대한 한자 매핑
    surname_map = {'김': '金', '이': '李', '박': '朴', '최': '崔', '정': '鄭', '강': '姜', '조': '趙', '윤': '尹', '장': '張'}
    
    surname = name[0]
    given_name = name[1:]
    
    hanja_surname = surname_map.get(surname, '〇')
    hanja_given_name = "".join(random.choices(hanja_chars, k=len(given_name)))
    
    return f"{hanja_surname}{hanja_given_name}"

def generate_address():
    """ 랜덤 한국 주소를 생성합니다. """
    return fake.address()

def generate_date(start_date, end_date):
    """ 지정된 날짜 범위 내에서 랜덤 날짜를 생성합니다. (YYYY.MM.DD 형식) """
    random_date = fake.date_between_dates(date_start=start_date, date_end=end_date)
    return random_date.strftime("%Y.%m.%d")

def generate_jumin(birthdate_str, gender):
    """ 생년월일과 성별을 기반으로 가짜 주민등록번호 앞 7자리를 생성합니다. """
    birth_dt = datetime.strptime(birthdate_str, "%Y.%m.%d")
    birth_yy = birth_dt.strftime('%y')
    birth_mmdd = birth_dt.strftime('%m%d')
    
    year = birth_dt.year
    if gender == "남":
        gender_digit = "3" if year >= 2000 else "1"
    else: # "여"
        gender_digit = "4" if year >= 2000 else "2"
        
    return f"{birth_yy}{birth_mmdd}-{gender_digit}******"

# --- 핵심 함수: 데이터 레코드 생성 ---

def create_person(relationship, min_age=0, max_age=80):
    """ 한 사람에 대한 데이터 묶음을 생성합니다. """
    start_date = datetime.now() - timedelta(days=max_age * 365)
    end_date = datetime.now() - timedelta(days=min_age * 365)
    
    name = generate_name()
    gender = random.choice(["남", "여"])
    birthdate = generate_date(start_date, end_date)
    
    return {
        "RELATION": relationship,
        "NAME": name,
        "NAME_CN": generate_hanja_name(name),
        "BIRTH": birthdate,
        "EVENT_DATE": birthdate, # 주민등록등본용 발생일
        "JUMIN": generate_jumin(birthdate, gender),
        "GENDER": gender,
        "ORIGIN": random.choice(["김해", "전주", "경주", "밀양", "안동"]), # 본관 예시
        "NUMBER": "", # 주민등록등본용 번호
        "REPORT_DATE": generate_date(datetime.strptime(birthdate, "%Y.%m.%d"), datetime.now()),
        "STATUS": "거주자",
        "CHANGE_REASON": random.choice(["전입", "출생등록"])
    }

def create_record(doc_type="GA", options=None):
    """
    한 장의 문서(가족관계증명서 또는 주민등록등본)를 채울 전체 데이터 레코드를 생성합니다.
    """
    if options is None:
        options = {}

    # --- 본인(MAIN) 정보 생성 ---
    main_person = create_person(relationship="본인", min_age=25, max_age=55)
    
    # 최종적으로 반환될 데이터 딕셔너리
    record = {}
    
    if doc_type == "GA":
        record.update({f"MAIN_{key}": value for key, value in main_person.items()})
        record["BASE_ADDRESS"] = generate_address()
    elif doc_type == "JU":
        record["MAIN_NAME"] = main_person["NAME"]
        record["MAIN_NAME_CN"] = main_person["NAME_CN"]
        record["MAIN_ADDRESS"] = generate_address()
        record["MAIN_EVENT_DATE"] = generate_date(datetime(2020,1,1), datetime.now())
        record["MAIN_REPORT_DATE"] = record["MAIN_EVENT_DATE"]

    record["APPLICANT"] = main_person["NAME"]

    # --- 문서 종류별 가족/세대원 정보 생성 ---
    if doc_type == "GA":
        children_count = options.get("children_count", random.randint(0, 3))
        
        main_birth_year = int(main_person["BIRTH"][:4])
        record.update({f"PARENT1_{k}": v for k, v in create_person("부", min_age=main_birth_year - 1960, max_age=main_birth_year - 1930).items()})
        record.update({f"PARENT2_{k}": v for k, v in create_person("모", min_age=main_birth_year - 1965, max_age=main_birth_year - 1935).items()})

        if random.random() > 0.3:
             record.update({f"SPOUSE_{k}": v for k, v in create_person("배우자", min_age=25, max_age=55).items()})

        for i in range(children_count):
            record.update({f"CHILD{i+1}_{k}": v for k, v in create_person("자녀", min_age=0, max_age=24).items()})

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
            member = create_person(rel, min_age=0, max_age=80)
            member['NUMBER'] = str(i)
            record.update({f"MEMBER{i}_{k}": v for k, v in member.items()})
    
    return record

# --- 테스트용 실행 블록 ---
if __name__ == '__main__':
    print("--- [Test] 가족관계증명서 데이터 생성 (자녀 2명) ---")
    ga_record = create_record(doc_type="GA", options={"children_count": 2})
    for key, value in ga_record.items():
        print(f"{key:<20}: {value}")
        
    print("\n" + "="*50 + "\n")
    
    print("--- [Test] 주민등록등본 데이터 생성 (세대원 4명) ---")
    ju_record = create_record(doc_type="JU", options={"members_count": 4})
    for key, value in ju_record.items():
        print(f"{key:<20}: {value}")
