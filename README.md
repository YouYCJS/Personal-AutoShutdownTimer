# Auto Shutdown Timer
**예약 종료 / 재시작 / 절전 타이머 (Python · tkinter)**

> 설정한 시간이 지나면 PC를 자동으로 종료·재시작·절전시키는 데스크탑 타이머.
> 장시간 자리를 비울 때(다운로드, 게임 잠수 등) 켜두면 알아서 꺼집니다.

<img width="797" height="483" alt="Image" src="https://github.com/user-attachments/assets/a23e6b78-c9c6-41b8-a104-235abb394711" />

## 기능
- **시간 설정**: 시(0~1000) / 분 / 초 콤보박스로 선택
- **동작 선택**: 종료 / 재시작 / 절전
- **타이머 제어**: Start / Pause / Resume / Stop
- **진행 표시**: 남은 시간 + 진행 바 + 퍼센트
- **반응형 UI**: 창 크기에 따라 폰트·요소 자동 스케일
- **크로스 플랫폼**: Windows / Linux / macOS 자동 분기

## 사용법
1. 시/분/초를 선택
2. 동작(종료/재시작/절전) 선택
3. Start로 시작 — Pause/Resume/Stop으로 제어

## 실행
```bash
python timer.py
```
표준 라이브러리(tkinter)만 사용 — 별도 설치 불필요.

> ⚠️ 타이머 종료 시 전원 명령이 실행됩니다. 작업은 미리 저장하세요.

## 환경
- Python 3.x (tkinter 포함)
