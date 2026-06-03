# Hidden Object Game OCR Bot 🔍

Mac App Store 숨은그림찾기 게임용 자동 클릭 봇입니다.  
화면 하단의 한국어 단어를 OCR로 읽고, 미리 저장된 좌표로 자동 클릭합니다.

---

## 파일 구조

```
OCRBotTesting/
├── bot.py            # 메인 봇 스크립트
├── map_coords.py     # 좌표 매핑 도우미
├── coord_map.json    # 자동 생성되는 좌표 사전
├── requirements.txt  # 의존성 패키지 목록
└── README.md
```

---

## 설치 방법

### 1. Python 3.10+ 확인
```bash
python3 --version
```

### 2. 가상환경 생성 (권장)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. Mac 권한 설정 (중요!)
Mac의 **개인 정보 보호 & 보안** 설정에서 다음을 허용해야 합니다:
- **손쉬운 사용(Accessibility)** → Terminal (또는 사용 중인 IDE)
- **화면 기록(Screen Recording)** → Terminal

`시스템 설정 → 개인 정보 보호 및 보안 → 손쉬운 사용 / 화면 기록`에서 추가하세요.

---

## 사용 순서

### Step 1 — 좌표 매핑 (처음 한 번만)

게임 내 35개 아이템의 화면 좌표를 기록합니다.

1. `map_coords.py` 상단의 `ITEM_NAMES` 리스트를 실제 게임 단어로 수정합니다.
2. 스크립트를 실행합니다:
   ```bash
   python3 map_coords.py
   ```
3. 3초 안에 게임 창으로 전환합니다.
4. 터미널에서 안내하는 단어가 가리키는 아이템을 화면에서 클릭합니다.
5. 35개 완료 시 `coord_map.json`이 자동으로 저장됩니다.
6. 중간에 ESC를 누르면 저장 후 종료 — 재실행하면 이어서 진행합니다.

### Step 2 — 캡처 영역 조정

`bot.py`의 `CAPTURE_REGION` 딕셔너리를 게임 창 하단 단어 표시 영역에 맞게 조정합니다:

```python
CAPTURE_REGION = {
    "top":    1300,  # 단어 바 상단 y 좌표
    "left":   400,   # 단어 바 좌측 x 좌표
    "width":  1200,  # 너비
    "height": 120,   # 높이
}
```

> 💡 좌표를 모르겠다면 macOS **스크린샷 도구** (⌘+Shift+4) 로 단어 바 영역을 드래그해보면 좌표를 확인할 수 있습니다.

### Step 3 — 봇 실행

```bash
python3 bot.py
```

3초 카운트다운이 시작되면 게임 창으로 전환하세요. 봇이 자동으로 단어를 읽고 클릭합니다.

---

## 설정값 요약 (`bot.py`)

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `COORD_MAP_FILE` | `"coord_map.json"` | 좌표 파일 경로 |
| `CAPTURE_REGION` | 화면 하단 영역 | OCR 캡처 영역 |
| `OCR_CONFIDENCE_THRESHOLD` | `0.4` | 이 값 미만의 OCR 결과는 무시 |
| `CLICK_DELAY_MIN/MAX` | `0.3` / `0.8` s | 클릭 간 랜덤 딜레이 범위 |
| `CLICKS_PER_ROUND` | `26` | 한 라운드 클릭 횟수 |
| `STARTUP_DELAY` | `3` s | 시작 전 대기 시간 |

---

## 문제 해결

| 증상 | 해결책 |
|------|--------|
| `PermissionError` / 클릭 안 됨 | 손쉬운 사용 권한 확인 |
| 화면 캡처 실패 | 화면 기록 권한 확인 |
| OCR 정확도 낮음 | `CAPTURE_REGION` 재조정, 게임 창을 최대화 |
| 단어는 읽히나 클릭 안 됨 | `coord_map.json` 확인, 단어 철자 일치 여부 확인 |
| EasyOCR 첫 실행 느림 | 모델 다운로드 중 (정상, 한 번만 발생) |

---

## 주의사항

- 이 봇은 개인 학습 및 테스트 목적으로 제작되었습니다.
- 게임 서비스 약관을 확인하고 사용하세요.
