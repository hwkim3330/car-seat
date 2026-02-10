# KETI Smart Seat Sensor Monitoring System

**Three.js 기반 차량 시트 센서 실시간 3D 시각화 시스템**

> 한국전자기술연구원(KETI) 스마트 시트 프로젝트 — 4종 센서(체압, 온도, 포지션, 모션) 실시간 모니터링 및 3D 시각화

## Live Demo

| 버전 | 링크 | 설명 |
|------|------|------|
| **Desktop** (Apple Style) | [index.html](https://hwkim3330.github.io/car-seat/) | 메인 대시보드 — 3패널 레이아웃, 프로스티드 글래스 UI |
| **Mobile** | [mobile.html](https://hwkim3330.github.io/car-seat/mobile.html) | 모바일 최적화 — 다크 테마, 바텀 시트, 터치 제스처 |
| **Tablet** (Hyundai Pleos) | [tablet.html](https://hwkim3330.github.io/car-seat/tablet.html) | 태블릿용 — 현대 Pleos 브랜딩, 시안 악센트 다크 테마 |
| **Cockpit** (Cyberpunk HUD) | [cockpit.html](https://hwkim3330.github.io/car-seat/cockpit.html) | 디지털 콕핏 — 사이버펑크 HUD 스타일, 스캔라인 오버레이 |
| **Tesla Style** | [tesla.html](https://hwkim3330.github.io/car-seat/tesla.html) | 테슬라 스타일 — 미니멀 화이트 디자인 |
| **Technical Report** | [report.html](https://hwkim3330.github.io/car-seat/report.html) | 기술 보고서 — 스마트 시트 생태계 R&D 전략 문서 |
| **App Prototype** | [prototype.html](https://hwkim3330.github.io/car-seat/prototype.html) | 앱 프로토타입 — 로그인, MON/ACT/APP 전체 기능, 3D+생체 |
| **Mobile Prototype** | [prototype-mobile.html](https://hwkim3330.github.io/car-seat/prototype-mobile.html) | 모바일 앱 프로토타입 — 4탭, 원격제어, 프리셋 |
| **GLB Seat Viewer** | [seat-viewer.html](https://hwkim3330.github.io/car-seat/seat-viewer.html) | GLB 3D 모델 기반 — 4좌석 배치, 풀 모니터링+제어 |

## 주요 기능

### 센서 시뮬레이션 (4종)
- **체압 센서 (Pressure)** — 16×16 매트릭스 체압 분포 히트맵, 좌석 쿠션 + 등받이 오버레이
- **온도 센서 (Temperature)** — 6존 독립 제어(L/R 쿠션, L/R 등받이, L/R 볼스터), 열선/쿨링 토글
- **포지션 센서 (Position)** — 전후/높이/리클라인/헤드레스트 4축 조절, 프리셋(Drive/Sport/Relax/Entry) 애니메이션
- **모션 센서 (Motion)** — 3축 가속도(X/Y/Z), 진동 게이지, 실시간 파형, 피크 추적

### 3D 시각화
- **Three.js** 기반 프로시저럴 시트 모델 (쿠션, 등받이, 볼스터, 헤드레스트)
- 백레스트 피벗 시스템 — 리클라인 시 등받이+볼스터+헤드레스트 연동 회전
- 체압 히트맵 캔버스 텍스처 오버레이 (쿠션 + 등받이)
- 모션 화살표(ArrowHelper) 시각화
- OrbitControls — 마우스/터치 줌/회전/팬

### 시뮬레이션 제어
- 탑승자 체중 (30~130 kg)
- 차량 속도 (0~200 km/h)
- 노면 타입 (Smooth / Normal / Rough / Cobble)
- 탑승 상태 (Seated / Empty / Child / Heavy)
- 임계값 설정 (체압, 온도 과열, 진동)

### 데이터 내보내기
- **JSON** — 전체 센서 스냅샷 (체압 그리드 포함)
- **CSV** — 테이블 형식 타임스탬프 데이터

## 기술 스택

| 기술 | 용도 |
|------|------|
| Three.js r152 | 3D 렌더링 엔진 |
| OrbitControls | 카메라 인터랙션 |
| Canvas 2D API | 히트맵, 게이지, 파형 렌더링 |
| Font Awesome 6 | 아이콘 |
| CSS3 Backdrop Filter | 프로스티드 글래스 효과 |
| Vanilla JavaScript | 서버 의존성 없는 클라이언트사이드 |

## 프로젝트 구조

```
car-seat/
├── index.html          # 메인 데스크톱 버전 (Apple Style)
├── mobile.html         # 모바일 최적화 버전
├── tablet.html         # 태블릿 버전 (Hyundai Pleos)
├── cockpit.html        # 사이버펑크 HUD 버전
├── tesla.html          # 테슬라 스타일 버전
├── report.html         # 기술 보고서
├── prototype.html      # 앱 프로토타입 (데스크톱)
├── prototype-mobile.html # 앱 프로토타입 (모바일)
├── keti.png            # KETI 로고
├── favicon.ico         # 파비콘
├── libs/
│   ├── three.min.js    # Three.js 코어
│   ├── OrbitControls.js # 카메라 컨트롤
│   └── GLTFLoader.js   # GLTF 모델 로더
└── .github/
    └── workflows/
        └── deploy.yml  # GitHub Pages 자동 배포
```

## 버전별 특징

### Desktop — Apple Style (`index.html`)
- 라이트 테마 (`#f5f5f7` 배경)
- 3컬럼 레이아웃: 좌측 제어 패널 | 중앙 3D 캔버스 | 우측 데이터 대시보드
- 프로스티드 글래스 (`backdrop-filter: blur(20px)`) UI
- 실시간 경고 시스템

### Mobile (`mobile.html`)
- 다크 테마 (`#000000` 배경)
- 풀스크린 3D 캔버스 + 플로팅 센서 탭
- 스와이프 가능한 바텀 시트
- 안전 영역(노치) 대응

### Tablet — Hyundai Pleos (`tablet.html`)
- 다크 테마 + 시안 악센트 (`#00AAD2`)
- 2패널: 사이드바 + 하단 대시보드 (탭 네비게이션)
- 현대 Pleos 브랜딩
- 가로 모드 최적화

### Cockpit — Cyberpunk HUD (`cockpit.html`)
- 심층 다크 테마 (`#0a0a14`)
- 스캔라인 오버레이 효과
- JetBrains Mono 모노스페이스 폰트
- 사이버네틱 글로우 악센트

### Tesla Style (`tesla.html`)
- 미니멀 화이트 디자인 (`#fafafa`)
- 클린 타이포그래피 기반
- 간결한 데이터 카드 레이아웃

### App Prototype (`prototype.html`)
- 풀스택 앱 프로토타입 — 로그인 → 대시보드
- **MON-01~07**: 점유감지, 승객분류, 자세점수(게이지), 비대칭(L/R 바), 심박(BPM+파형), 호흡(RPM+파형), 상태추론(배지+리스크바)
- **ACT-01~06**: 열선 3단, 통풍 3단, 공압 7채널, 마사지 4프로그램, 드라이브모드, 안전제약(속도>5 포지션 잠금)
- **APP-01~06**: 차량 페어링, 원격 프리셋 시동, 프리셋 CRUD, 멀티시트 상태, 알림 센터, 프로필 로밍
- Three.js 3D 시트 + 체압 히트맵 + 다크 테마

### Mobile App Prototype (`prototype-mobile.html`)
- 모바일 네이티브 앱 프로토타입 (PWA 스타일)
- 4탭: Status / Remote / Presets / Settings
- 원격 시트 제어 (열선/통풍/마사지/드라이브모드)
- 실시간 생체 데이터 + 심박 파형
- 프리셋/프로필 관리
- 다크 테마, 터치 최적화

## 로컬 실행

별도 서버 불필요 — HTML 파일을 직접 브라우저에서 열면 됩니다.

```bash
# 방법 1: 파일 직접 열기
open index.html        # macOS
xdg-open index.html    # Linux

# 방법 2: 간단한 HTTP 서버 사용
python3 -m http.server 8080
# → http://localhost:8080 접속
```

## 라이선스

KETI (한국전자기술연구원) 내부 프로젝트

---

**KETI — Korea Electronics Technology Institute**
