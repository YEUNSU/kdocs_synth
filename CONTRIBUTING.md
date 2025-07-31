# 기여 가이드 (Contributing Guide)

KDOCS_SYNTH 프로젝트에 기여해주셔서 감사합니다! 

## 🚀 시작하기

### 개발 환경 설정

1. **저장소 클론**
```bash
git clone https://github.com/YEUNSU/kdocs_synth.git
cd kdocs_synth
```

2. **Python 환경 설정**
```bash
# Python 3.9+ 필요
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate     # Windows
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

## 📋 개발 가이드라인

### 코드 스타일

- **Python**: PEP 8 스타일 가이드 준수
- **변수명**: 명확하고 설명적인 이름 사용
- **함수명**: 동사로 시작하는 명확한 이름
- **클래스명**: PascalCase 사용
- **파일명**: snake_case 사용

### 문서화

- **Docstring**: 모든 함수와 클래스에 작성
- **타입 힌트**: Python 타입 힌트 사용
- **주석**: 복잡한 로직에 상세한 주석
- **README**: 주요 변경사항 반영

### 테스트

- **단위 테스트**: 개별 함수/클래스 테스트
- **통합 테스트**: 전체 워크플로우 테스트
- **시각적 검증**: 생성된 이미지 품질 확인

## 🔒 보안 가이드라인

### 개인정보 보호

- **절대 금지**: 실제 개인정보 사용
- **가짜 데이터**: Faker 라이브러리만 사용
- **검증**: 생성된 데이터의 현실성 확인

### 파일 보안

- **로컬 저장**: 생성된 이미지는 로컬에만 저장
- **Git 제외**: 이미지 파일은 버전 관리에서 제외
- **백업**: 중요 설정 파일은 별도 백업

## 📝 Pull Request 가이드

### 1. 이슈 생성
- 버그 리포트 또는 기능 요청
- 명확한 설명과 재현 방법

### 2. 브랜치 생성
```bash
git checkout -b feature/새기능명
# 또는
git checkout -b fix/버그수정명
```

### 3. 개발 및 테스트
- 코드 작성
- 테스트 실행
- 문서 업데이트

### 4. 커밋
```bash
git add .
git commit -m "feat: 새로운 기능 추가"
git commit -m "fix: 버그 수정"
git commit -m "docs: 문서 업데이트"
```

### 5. Push 및 PR 생성
```bash
git push origin feature/새기능명
```

## 🏷️ 커밋 메시지 규칙

### 형식
```
type(scope): description

[optional body]

[optional footer]
```

### 타입
- **feat**: 새로운 기능
- **fix**: 버그 수정
- **docs**: 문서 변경
- **style**: 코드 스타일 변경
- **refactor**: 코드 리팩토링
- **test**: 테스트 추가/수정
- **chore**: 빌드 프로세스 또는 보조 도구 변경

### 예시
```
feat(data): 주민번호 OPEN/CLOSE 옵션 추가
fix(generator): 파일명 규칙 수정
docs(readme): 설치 방법 업데이트
```

## 🧪 테스트 가이드

### 테스트 실행
```bash
# 전체 테스트
python -m pytest tests/

# 특정 테스트
python -m pytest tests/test_ju_logic.py

# 커버리지 포함
python -m pytest --cov=src tests/
```

### 테스트 작성
- **테스트 파일명**: `test_*.py`
- **테스트 함수명**: `test_*`
- **설명적인 테스트명**: 무엇을 테스트하는지 명확히

## 📊 품질 기준

### 코드 품질
- **가독성**: 명확하고 이해하기 쉬운 코드
- **모듈화**: 기능별로 분리된 구조
- **재사용성**: 공통 기능은 별도 모듈로 분리

### 성능 기준
- **메모리 효율성**: 대량 생성 시 메모리 사용량 최적화
- **속도**: 적절한 처리 속도 유지
- **확장성**: 향후 기능 추가 고려

## 🐛 버그 리포트

### 버그 리포트 템플릿
```markdown
## 버그 설명
[명확한 버그 설명]

## 재현 방법
1. [단계 1]
2. [단계 2]
3. [단계 3]

## 예상 동작
[예상했던 정상 동작]

## 실제 동작
[실제로 발생한 동작]

## 환경 정보
- OS: [운영체제]
- Python: [버전]
- 라이브러리: [버전]

## 추가 정보
[스크린샷, 로그 등]
```

## 💡 기능 요청

### 기능 요청 템플릿
```markdown
## 기능 설명
[요청하는 기능의 명확한 설명]

## 사용 사례
[이 기능이 필요한 상황]

## 제안하는 구현 방법
[구현 방법에 대한 아이디어]

## 대안
[다른 해결 방법이 있다면]
```

## 📞 문의

- **이슈**: GitHub Issues 사용
- **토론**: GitHub Discussions 사용
- **보안**: 보안 관련 이슈는 비공개로 처리

---

**기여해주셔서 감사합니다!** 🎉 