# 챗봇 비교 애플리케이션

이 프로젝트는 Streamlit을 사용하여 두 개의 챗봇을 비교할 수 있는 웹 애플리케이션입니다.

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. OpenAI API 키 설정:
- `.env` 파일을 생성하고 다음 내용을 추가하세요:
```
OPENAI_API_KEY=your_api_key_here
```
- `your_api_key_here`를 실제 OpenAI API 키로 교체하세요.

## 실행 방법

다음 명령어로 애플리케이션을 실행하세요:
```bash
streamlit run app.py
```

## 기능

- 두 개의 독립적인 챗봇 인터페이스
- 각 챗봇은 동일한 temperature(0)로 설정되어 있어 일관된 응답 제공
- 대화 기록 유지
- 실시간 응답 표시 