# KDOCS\_SYNTH 프로젝트 플로우

## 1. 환경 설정

* **Conda 환경 생성** (`python>=3.9`)

  * 패키지: `opencv-contrib-python`, `Pillow`, `numpy`, `synthtiger`, `faker`, `timm`, `albumentations` 등
* **폴더 구조 초기화**

  ```
  kdocs_synth/
  ├─ assets/
  │    ├─ fonts/         # mt.ttf 등
  │    └─ templates/     # GA, JU 빈 양식 이미지
  ├─ configs/           # 좌표 YAML
  ├─ manifests/         # manifest.csv
  ├─ scripts/           # 보조 스크립트(extract_layout.py)
  ├─ src/               # data_factory.py, templates_juga.py, rotator.py, launcher.py (▶ launcher.py가 메인 진입점 역할)
  ├─ tests/             # 검수 스크립트
  └─ data/              # 생성 산출물
  ```

  ```
  ```

## 2. 자산 준비

* `assets/fonts/mt.ttf` (문체부 바탕체) 배치 ✔️

* `assets/templates/GA/` 에 빈 양식 이미지 **8종** 배치

  * 각 스탬프(2종) × 자녀 행 수(0,1,2,3) 버전 → 총 **8장**

* `assets/templates/JU/` 에 빈 양식 이미지 **12종** 배치

  * 각 지역(3종) × 바코드 조합(4종) → 총 **12장**

## 2.1. 템플릿 파일명 규칙

* **GA 빈 양식 이미지** 패턴: `GA_template<stamp_no>_child<cnt>.jpg`

  * `<stamp_no>`: 1 또는 2 (도장 버전)
  * `<cnt>`: 0, 1, 2, 3 (자녀 행 수)
  * 예: `GA_template1_child0.jpg`, `GA_template2_child3.jpg`

* **JU 빈 양식 이미지** 패턴: `JU_template<region>_TY<top><bottom>.jpg`

  * `<region>`: 1, 2, 3 (지역)
  * `<top>`, `<bottom>`: 1=표시(O), 0=미표시(X)
  * 예: `JU_template1_TY11.jpg`, `JU_template3_TY00.jpg`

## 2.2. 최종 저장 파일명 규칙. 최종 저장 파일명 규칙. 최종 저장 파일명 규칙

* **저장 파일명 포맷**: `<DOC>-<ROT>-<INDEX:04d>.jpg`

  * `<DOC>`: `GA` 또는 `JU`
  * `<ROT>`: `0` (정상), `L` (왼쪽 90°), `R` (오른쪽 90°), `180` (180°)
  * `<INDEX:04d>`: 각 회전별 1부터 시작하는 4자리 인덱스
* **예시**:

  * `GA-0-0001.jpg` (GA 정상)
  * `GA-L-0001.jpg` (GA 왼쪽)
  * `JU-0-0001.jpg` (JU 정상)
  * `JU-R-0012.jpg` (JU 오른쪽)

## 3. 좌표 추출 좌표 추출

* `scripts/extract_layout.py` 생성
* GA 빈 양식 → `configs/ga_layout.yaml`
* JU 빈 양식 → `configs/ju_layout.yaml`
* `field_boxes` (셀 영역), `row_height_child` 자동 계산

## 4. 데이터 생성 헬퍼 구현

* `src/data_factory.py`

  * 이름, 한자, 관계, 생년월일, 주민등록번호 등 랜덤 생성 함수
  * `make_record(doc_type, children_cnt)` 구현

## 5. 템플릿 클래스 구현

* `src/templates_juga.py`

  * **GACertificateTemplate**

    * 자녀 행 수(0\~n) 동적 렌더링
    * 한글+한자 병기, 자동 폰트 피팅
  * **JUCertificateTemplate**

    * 상단/하단 바코드 삽입
    * 고정 행 수 렌더링

## 6. 매니페스트 작성

* `manifests/manifest.csv`

  * `template_path`, `doc_type`, `children_cnt`, `n_random`, `rotations`

## 7. 런처 및 회전 자동화

* `src/launcher.py`

  * manifest 읽어 `Generator` 실행
  * `rotator.save_rotations()` 으로 4방향 회전·저장

## 8. 검수 및 테스트

* `tests/preview_boxes.py` → 좌표 시각 검증
* `tests/test_counts.py` → 이미지 수 검증
* `tests/test_hanja.py`, `tests/test_relation_hanja.py` → 한자 검증

## 9. 배포 및 문서화

* `README.md` 작성
* CI/CD (GitHub Actions)로 `pytest` 자동 실행
* `data/` 압축본 제공

---

### 다음 작업

* **좌표 추출 실행**: `scripts/extract_layout.py`로 GA·JU 빈 양식 레이아웃 YAML 생성 (`configs/ga_layout.yaml`, `configs/ju_layout.yaml`)
* **데이터 생성 헬퍼 구현**: `src/data_factory.py` 에 랜덤 데이터 함수(`make_record`) 초안 작성
* **템플릿 클래스 통합**: `src/templates_juga.py` 에 자동 폰트 피팅 및 dynamic 렌더링 로직 적용
* **매니페스트 작성**: `manifests/manifest.csv`에 템플릿별 생성 설정 추가
* **런처 및 회전 기능 테스트**: `src/launcher.py` + `src/rotator.py` 실행 검증
* **검수 스크립트 실행**: `tests/preview_boxes.py`, `tests/test_counts.py`, `tests/test_hanja.py` 등의 통합 실행
