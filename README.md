# KDOCS_SYNTH

한국 공문서 합성 데이터 생성 프로젝트

## 📋 프로젝트 개요

GA(가족관계증명서)와 JU(주민등록표) 양식에 합성 데이터를 생성하여 ML/AI 학습용 데이터셋을 제작하는 프로젝트입니다.

## 🚀 환경 설정

### 1. Python 환경 요구사항
- Python >= 3.9
- UV 패키지 관리자 (권장)

### 2. UV를 사용한 패키지 설치

```bash
# 핵심 패키지 설치
uv add opencv-contrib-python Pillow numpy PyYAML

# 추가 패키지 설치
uv add synthtiger faker timm albumentations
```

### 3. 전통적인 pip 설치 (대안)

```bash
pip install opencv-contrib-python Pillow numpy PyYAML synthtiger faker timm albumentations
```

## 📁 프로젝트 구조

```
kdocs_synth/
├─ assets/
│    ├─ fonts/         # mt.ttf (문체부 바탕체)
│    ├─ templates/     # GA, JU 빈 양식 이미지
│    └─ samples/       # 좌표 추출용 채워진 샘플
├─ configs/           # 좌표 YAML 파일
├─ manifests/         # manifest.csv
├─ scripts/           # 보조 스크립트 (extract_layout.py)
├─ src/               # 메인 소스 코드
├─ tests/             # 검수 스크립트
└─ data/              # 생성된 합성 데이터
```

## 🎯 사용 방법

### 1. 좌표 추출
```bash
python scripts/extract_layout.py
```

### 2. 합성 데이터 생성
```bash
python src/launcher.py
```

### 3. 검수 및 테스트
```bash
python tests/preview_boxes.py    # 좌표 시각 검증
python tests/test_counts.py      # 이미지 수 검증
python tests/test_hanja.py       # 한자 검증
```

## 📋 템플릿 파일명 규칙

### GA (가족관계증명서)
- **빈 양식**: `GA_template<stamp_no>_child<cnt>`
  - `stamp_no`: 1 또는 2 (도장 버전)
  - `cnt`: 0, 1, 2, 3 (자녀 행 수)
  - 예: `GA_template1_child0`, `GA_template2_child3`

### JU (주민등록표)
- **빈 양식**: `JU_template<region>_TY<top><bottom>`
  - `region`: 1, 2, 3 (지역)
  - `top`, `bottom`: 1=표시(O), 0=미표시(X)
  - 예: `JU_template1_TY11`, `JU_template3_TY00`

### 최종 저장 파일
- **저장 파일명**: `<DOC>-<ROT>-<INDEX:04d>.jpg`
  - `DOC`: GA 또는 JU
  - `ROT`: 0(정상), L(왼쪽90°), R(오른쪽90°), 180(180°)
  - `INDEX`: 각 회전별 1부터 시작하는 4자리 인덱스

## 🔧 개발 단계

1. ✅ **환경 설정** - Python, UV, 패키지 설치
2. ✅ **자산 준비** - 폰트, 템플릿, 샘플 이미지
3. 🔄 **좌표 추출** - extract_layout.py 실행
4. ⏳ **데이터 생성 헬퍼** - data_factory.py 구현
5. ⏳ **템플릿 클래스** - templates_juga.py 구현
6. ⏳ **매니페스트 작성** - manifest.csv
7. ⏳ **런처 및 회전** - launcher.py, rotator.py
8. ⏳ **검수 및 테스트** - tests/ 스크립트들

## 📦 주요 의존성

- **opencv-contrib-python**: 이미지 처리
- **Pillow**: 이미지 조작
- **numpy**: 수치 계산
- **PyYAML**: 설정 파일 처리
- **synthtiger**: 텍스트 합성
- **faker**: 가짜 데이터 생성
- **timm**: 모델 라이브러리
- **albumentations**: 이미지 증강

## 📄 라이선스

이 프로젝트는 연구 및 교육 목적으로만 사용됩니다. 