# 한국 공문서 합성 데이터 생성기

가족관계증명서와 주민등록등본의 합성 이미지를 자동 생성하는 도구입니다.
OCR 학습용 데이터셋을 빠르게 만들 수 있습니다.

---

## 특징

- 현실적인 한국 이름, 생년월일, 주민번호 자동 생성
- 생년월일과 주민번호 일관성 유지 (예: `1987.05.12` → `870512-2******`)
- 주민번호 뒷자리 자동 마스킹 (OPEN/CLOSE 모드)
- OCR 최적화된 고품질 이미지 생성

---

## 빠른 시작

### 방법 1: pip 사용

```bash
# 1. 저장소 복제
git clone https://github.com/YEUNSU/kdocs_synth.git
cd kdocs_synth

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 샘플 생성 (10장)
python generate_samples.py
```

### 방법 2: conda 사용 (권장)

```bash
# 1. 저장소 복제
git clone https://github.com/YEUNSU/kdocs_synth.git
cd kdocs_synth

# 2. conda 환경 생성 및 활성화
conda create -n kdocs python=3.9 -y
conda activate kdocs

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 샘플 생성 (10장)
python generate_samples.py
```

> **결과**: `outputs/samples/` 폴더에 10장 생성 (가족관계 5장 + 주민등록 5장)
> **참고**: `outputs/` 폴더는 실행 시 자동으로 생성됩니다

---

## 대량 생성 (학습용)

샘플 생성으로 테스트 후, 학습용 데이터가 필요하면 대량 생성하세요:

```bash
# 가족관계증명서 192장
python src/synthdata/batch_generator_ga.py

# 주민등록등본 210장
python src/synthdata/batch_generator_ju.py
```

> **결과**: `outputs/dataset/` 폴더에 자동 생성됨
> - 가족관계증명서: 192장
> - 주민등록등본: 210장

### 왜 생성 개수가 다른가요?

템플릿 조합 개수가 달라서 정확히 200장씩 맞추기 어렵습니다:

| 문서 종류 | 템플릿 구성 | 총 조합 | 실제 생성 |
|---------|------------|---------|----------|
| **가족관계** | 2템플릿 × 4자녀수 × 2주민번호 | 16가지 | 192장 |
| **주민등록** | 3템플릿 × 4바코드 × 2주민번호 | 24가지 | 210장 |

**템플릿 상세**
- **가족관계증명서**: `GA_template1`, `GA_template2` (각각 child0/1/2/3 버전 → 총 8개)
- **주민등록등본**: `JU_template1/2/3` (각각 TY00/01/10/11 바코드 → 총 12개)
- **주민번호 공개**: 모든 템플릿에 OPEN(전체공개), CLOSE(뒷자리마스킹) 2가지 모드

---

## 프로젝트 구조

```
kdocs_synth/
├── generate_samples.py              # 메인 실행 스크립트 (샘플 생성)
├── src/synthdata/
│   ├── data_factory.py              # 가짜 데이터 생성 (이름, 생년월일, 주민번호)
│   ├── templates_juga.py            # 템플릿에 데이터 렌더링
│   ├── batch_generator_ga.py        # 가족관계 대량 생성
│   └── batch_generator_ju.py        # 주민등록 대량 생성
├── assets/
│   ├── fonts/                       # KoPub World 폰트
│   └── templates/
│       ├── GA/                      # 가족관계증명서 템플릿 8개
│       │   ├── GA_template1_child0.jpg  (자녀 0명)
│       │   ├── GA_template1_child1.jpg  (자녀 1명)
│       │   ├── GA_template1_child2.jpg  (자녀 2명)
│       │   ├── GA_template1_child3.jpg  (자녀 3명)
│       │   └── GA_template2_child*.jpg  (템플릿2, 자녀 0~3명)
│       └── JU/                      # 주민등록등본 템플릿 12개
│           ├── JU_template1_TY00.jpg  (바코드: 상O하O)
│           ├── JU_template1_TY01.jpg  (바코드: 상O하X)
│           ├── JU_template1_TY10.jpg  (바코드: 상X하O)
│           ├── JU_template1_TY11.jpg  (바코드: 상X하X)
│           └── JU_template2~3_*.jpg   (템플릿2, 3)
└── configs/
    ├── GA_template*_layout.yaml     # 가족관계 필드 좌표
    ├── JU_template*_layout.yaml     # 주민등록 필드 좌표
    └── field_definitions/
        ├── ga_fields.yaml           # 가족관계 필드 정의
        └── ju_fields.yaml           # 주민등록 필드 정의
```

---

## 동작 원리

1. **템플릿 선택** → 자녀 수/세대원 수에 맞는 템플릿 이미지 선택
2. **데이터 생성** → `data_factory.py`가 랜덤 이름, 생년월일, 주민번호 생성
3. **좌표 매핑** → `configs/*.yaml`에서 각 필드의 위치(좌표) 읽기
4. **텍스트 렌더링** → `templates_juga.py`가 템플릿에 데이터 삽입
5. **이미지 저장** → 완성된 합성 이미지를 `outputs/` 폴더에 저장

---

## 생성 데이터 예시

| 항목 | 예시 |
|------|------|
| **이름** | 김민준, 이서연, 박지우 (2020년대 흔한 이름) |
| **생년월일** | 1987.05.12, 2010.11.07 (유효한 날짜만) |
| **주민번호** | 870512-2****** (생년월일과 일치) |
| **한자명** | 金民俊 (자동 생성) |
| **주소** | 경상남도 의정부시 (비현실적, 가짜임 명시) |

---

## 커스터마이징

### 1. 이름 변경

[src/synthdata/data_factory.py](src/synthdata/data_factory.py) → `generate_name()` 함수 수정:

```python
surnames = ["김", "이", "박", ...]            # 성씨 목록
name_syllables_first = ["민", "서", ...]      # 이름 첫 음절
name_syllables_second = ["준", "서", ...]     # 이름 둘째 음절
```

### 2. 생성 개수 변경

#### 샘플 생성 ([generate_samples.py](generate_samples.py))

```python
# 가족관계증명서 생성 개수
for i in range(1, 6):  # 5장 → 원하는 개수로 변경 (예: range(1, 11)이면 10장)

# 주민등록등본 생성 개수
for i in range(1, 6):  # 5장 → 원하는 개수로 변경
```

#### 대량 생성 - 가족관계 ([batch_generator_ga.py](src/synthdata/batch_generator_ga.py))

```python
# 각 조합당 12~13장씩 생성 (총 192장)
images_per_combo = 13 if file_counter[doc_kind][jumin_name] % 2 == 0 else 12
```

- **더 많이**: `13 → 20`, `12 → 20` (약 320장)
- **더 적게**: `13 → 6`, `12 → 6` (약 96장)

#### 대량 생성 - 주민등록 ([batch_generator_ju.py](src/synthdata/batch_generator_ju.py))

```python
# 각 바코드 조합별로 8~9장씩 생성 (총 210장)
images_per_combo = 9 if file_counter[doc_kind][jumin_name] % 3 == 0 else 8
```

- **더 많이**: `9 → 15`, `8 → 15` (약 360장)
- **더 적게**: `9 → 4`, `8 → 4` (약 96장)

---

## 요구사항

- **Python**: 3.7 이상
- **패키지**: opencv-python, Pillow, PyYAML, Faker
  - 설치: `pip install -r requirements.txt`

---

## 주의사항

> **교육/연구 목적으로만 사용하세요**

- 생성된 데이터는 모두 **가짜**입니다
- 실제 개인정보가 **아닙니다**
- 불법 목적 사용 금지

---

## 문제 해결

| 문제 | 해결 방법 |
|------|----------|
| 폰트 로드 실패 | `assets/fonts/KoPubWorld Batang Medium.ttf` 파일 확인 |
| 템플릿 없음 | `assets/templates/GA/`, `JU/` 폴더 확인 |
| 레이아웃 오류 | `configs/*_layout.yaml` 파일 확인 |

---

## 라이선스

MIT License
