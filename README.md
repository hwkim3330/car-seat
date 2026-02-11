# KETI Smart Seat Control System

**Three.js 기반 차량 시트 10-Bone 실시간 3D 제어 시스템**

> 한국전자기술연구원(KETI) 스마트 시트 프로젝트 — 9축 좌석 제어, 체압 시뮬레이션, 4좌석 독립 관리

---

## Live Demo

### 4좌석 시리즈 (10-Bone GLB)

| 버전 | 링크 | 설명 |
|------|------|------|
| **Desktop** | [four-seats-final.html](https://hwkim3330.github.io/car-seat/four-seats-final.html) | 3패널 레이아웃 — 좌측 차량 뷰 + 3D + 우측 제어 |
| **Mobile** | [four-seats-mobile.html](https://hwkim3330.github.io/car-seat/four-seats-mobile.html) | 바텀 시트 UI — 스와이프 터치, 3단 스냅 |
| **Tablet** | [four-seats-tablet.html](https://hwkim3330.github.io/car-seat/four-seats-tablet.html) | 접이식 우측 패널, 세로 모드 대응 |
| **Cockpit** | [four-seats-cockpit.html](https://hwkim3330.github.io/car-seat/four-seats-cockpit.html) | 차량 인포테인먼트 HUD — 시안 다크 테마, 실시간 시계 |
| **Kiosk** | [four-seats-kiosk.html](https://hwkim3330.github.io/car-seat/four-seats-kiosk.html) | 전시/쇼룸 — 풀스크린 3D, 골드 테마, 자동 데모 |
| **Dashboard** | [four-seats-dashboard.html](https://hwkim3330.github.io/car-seat/four-seats-dashboard.html) | 엔지니어링 분석 — 레이더 차트, 4석 비교 |

### 단일 좌석 / 기타

| 버전 | 링크 | 설명 |
|------|------|------|
| **Desktop** (Apple Style) | [index.html](https://hwkim3330.github.io/car-seat/) | 프로시저럴 시트 — 4센서 통합 모니터링 |
| **Mobile** | [mobile.html](https://hwkim3330.github.io/car-seat/mobile.html) | 모바일 — 다크 테마, 바텀 시트 |
| **Tablet** | [tablet.html](https://hwkim3330.github.io/car-seat/tablet.html) | 태블릿 — Hyundai Pleos 브랜딩 |
| **Cockpit** (Cyberpunk) | [cockpit.html](https://hwkim3330.github.io/car-seat/cockpit.html) | 사이버펑크 HUD — 스캔라인 오버레이 |
| **Tesla Style** | [tesla.html](https://hwkim3330.github.io/car-seat/tesla.html) | 미니멀 화이트 디자인 |
| **Technical Report** | [report.html](https://hwkim3330.github.io/car-seat/report.html) | R&D 전략 기술 보고서 |
| **App Prototype** | [prototype.html](https://hwkim3330.github.io/car-seat/prototype.html) | 풀스택 앱 — MON/ACT/APP 전체 기능 |
| **Mobile Prototype** | [prototype-mobile.html](https://hwkim3330.github.io/car-seat/prototype-mobile.html) | 모바일 앱 — 4탭 원격제어 |

---

## 10-Bone 모델 개요

`models/car-seat-rigged-v2.glb` (719 KB) — Blender에서 10개 본으로 리깅된 카시트 모델.

### 본 계층 구조

```
Root (고정: 01 Base, 02 Base rim, 03 Base controls)
└── Slide (전후 이동)
    └── Cushion (04 Bottom seat — 높이 + 틸트)
        ├── BolsterL (05 Bottom sides 좌측)
        ├── BolsterR (05 Bottom sides 우측)
        └── Backrest (06 Back seat 상부 + 08 Upper neck — 리클라인)
            ├── Lumbar (06 Back seat 하부 — weight-painted 그라데이션)
            ├── BackBolsterL (07 Seat back sides 좌측)
            ├── BackBolsterR (07 Seat back sides 우측)
            └── Headrest (09 Header — 높이 + 틸트)
```

### 9축 제어

| 축 | 범위 | 본 | 변환 | 이동량 |
|----|------|----|------|--------|
| Slide (전후) | -100 ~ +100 | Slide | position.z | ±0.5 |
| Height (높이) | 0 ~ 100 | Cushion | position.y | +0.3 |
| Tilt (기울기) | -10 ~ +10° | Cushion | rotation.x | ±10° |
| Recline (리클라인) | 0 ~ 40° | Backrest | rotation.x | +40° |
| Headrest ↕ | 0 ~ 100 | Headrest | position.y | +0.5 |
| Headrest Tilt | -15 ~ +15° | Headrest | rotation.x | ±15° |
| Bolster (좌석) | 0 ~ 100% | BolsterL/R | position.x | ±0.15 |
| Lumbar (럼바) | 0 ~ 100% | Lumbar | position.z | -0.3 |
| Back Bolster (등) | 0 ~ 100% | BackBolsterL/R | position.x | ±0.12 |

### 6개 프리셋

| 프리셋 | Slide | Height | Tilt | Recline | HrH | HrT | Bolster | Lumbar | BBolster |
|--------|-------|--------|------|---------|-----|-----|---------|--------|----------|
| **Drive** | 0 | 20 | 2° | 8° | 30 | -5° | 20% | 40% | 15% |
| **Sport** | 30 | 0 | -3° | 3° | 50 | -8° | 80% | 60% | 70% |
| **Relax** | -40 | 40 | 5° | 35° | 60 | 10° | 10% | 50% | 10% |
| **Entry** | -80 | 0 | 0° | 0° | 0 | 0° | 0% | 0% | 0% |
| **Flat** | 0 | 50 | 8° | 40° | 100 | 15° | 0% | 30% | 0% |
| **Hold** | 10 | 10 | -2° | 5° | 40 | -3° | 90% | 70% | 85% |

> 자세한 기술 문서: [TECHNICAL.md](TECHNICAL.md) | 리깅 가이드: [RIGGING_GUIDE.md](RIGGING_GUIDE.md)

---

## 4좌석 배치

```
         ▲ 전방 (Front)
    ┌─────────────┐
    │  FL    FR   │
    │  Driver Pass │
    │             │
    │  RL    RR   │
    │  Rear  Rear │
    └─────────────┘
```

| 좌석 | 위치 (x, y, z) | 기본 체중 | 색상 |
|------|----------------|-----------|------|
| FL Driver | (-0.45, 0, -0.55) | 75 kg | `#007aff` 블루 |
| FR Passenger | (0.45, 0, -0.55) | 65 kg | `#34c759` 그린 |
| RL Rear Left | (-0.45, 0, 0.55) | 55 kg | `#ff9f0a` 오렌지 |
| RR Rear Right | (0.45, 0, 0.55) | 80 kg | `#af52de` 퍼플 |

---

## 버전별 특징

### Desktop (`four-seats-final.html`, 663줄)
- 3컬럼: 좌측 패널(220px) + 3D 캔버스 + 우측 패널(300px)
- 좌측: 차량 탑뷰, 좌석 카드, 프리셋 3x2 그리드, 체중 슬라이더
- 우측: 9축 슬라이더 (Base/Back/Support), 분석 탭 (골격도/체압)
- 라이트 테마, `backdrop-filter: blur` 글래스 UI

### Mobile (`four-seats-mobile.html`, 845줄)
- 풀스크린 3D + 플로팅 좌석 선택 알약
- 바텀 시트: 3단 스냅 (56px / 45% / 75%), 터치 스와이프
- 24px 슬라이더 썸, 44px 터치 타겟
- `100dvh`, safe-area 노치 대응

### Tablet (`four-seats-tablet.html`, 712줄)
- 헤더 중앙 좌석 알약 + 접이식 우측 패널(340px)
- 미니 차량 탑뷰 오버레이, 패널 토글 버튼
- `@media (orientation: portrait)` 세로 모드 대응
- 20px 슬라이더 썸, `min-height:40px` 터치 타겟

### Cockpit (`four-seats-cockpit.html`, 685줄)
- **차량 인포테인먼트 스크린** 컨셉 (Tesla/MBUX 스타일)
- 다크 테마: `#0a0e17` 배경, `#00d4ff` 시안 악센트
- 실시간 시계(HH:MM:SS), REC 표시, CONNECTED 상태
- 글래스모피즘 카드 (`backdrop-filter: blur`)
- 시안/마젠타/그린/앰버 시트 컬러

### Kiosk (`four-seats-kiosk.html`, 716줄)
- **전시/쇼룸 대형 터치스크린** 컨셉
- 풀스크린 3D + 플로팅 오버레이 (패널 없음)
- 다크 테마: `#0c0c0c` 배경, `#c8a44e` 골드 악센트
- **자동 데모 모드**: 5초 주기 좌석/프리셋 자동 순환
- 하단 패널: 접이식 글래스 패널, 드래그 핸들
- OrbitControls autoRotate (0.3), 10초 idle 후 자동 재개

### Dashboard (`four-seats-dashboard.html`, 1,243줄)
- **엔지니어링 분석** 컨셉
- 3컬럼: 좌측 4석 카드(접이식) + 3D + 우측 분석 패널(320px)
- **레이더 차트**: 9축 오버레이로 4좌석 포지션 동시 비교
- **바 차트**: 4좌석 평균/피크 체압 시각화
- **4석 히트맵**: 2x2 격자로 4좌석 체압 분포 동시 표시
- **Apply All**: 슬라이더 변경 시 4좌석 동시 적용 토글
- **Export**: 전체 포지션/체압 데이터 클립보드 복사
- 하단 통계 바: 실시간 Avg/Peak 표시

---

## 체압 시뮬레이션

16x16 격자(256셀)에 2D 가우시안 함수로 체압 분포를 실시간 시뮬레이션.

```
G(x, y) = exp( -x²/(2σx²) - y²/(2σy²) )
```

### 가우시안 피크 좌표

| 피크 | 중심 (x, y) | 확산 (σx, σy) | 비중 |
|------|-------------|---------------|------|
| 좌측 엉덩이 | (+0.35, -0.10) | (0.28, 0.32) | 100% |
| 우측 엉덩이 | (-0.35, -0.10) | (0.28, 0.32) | 100% |
| 좌측 허벅지 | (+0.30, +0.25) | (0.22, 0.40) | 35% |
| 우측 허벅지 | (-0.30, +0.25) | (0.22, 0.40) | 35% |

- **체중 계수**: `weight / 80` (80kg 기준 정규화)
- **볼스터 효과**: 피크 x좌표 ±`(bolster/100) * 0.15` 이동
- **노이즈**: `sin(t*0.3) * 0.01` + 랜덤 `±0.005`

### 색상 그라데이션

```
0%      25%     50%     75%     100%
Blue → Cyan → Green → Yellow → Red
(저압)                         (고압)
```

---

## 프로젝트 구조

```
car-seat-review/
├── four-seats-final.html       # Desktop 기본
├── four-seats-mobile.html      # Mobile 바텀시트
├── four-seats-tablet.html      # Tablet 접이식 패널
├── four-seats-cockpit.html     # Cockpit 인포테인먼트
├── four-seats-kiosk.html       # Kiosk 전시용
├── four-seats-dashboard.html   # Dashboard 분석용
├── four-seats.html             # v1 원본
├── four-seats-v2.html          # v2 SRS 전체 기능
├── four-seats-v3.html          # v3 6축 (5-bone)
├── four-seats-v4.html          # v4 9축 (10-bone)
│
├── index.html                  # 단일좌석 Desktop
├── mobile.html                 # 단일좌석 Mobile
├── tablet.html                 # 단일좌석 Tablet
├── cockpit.html                # 단일좌석 Cyberpunk
├── tesla.html                  # 단일좌석 Tesla
├── report.html                 # 기술 보고서
├── prototype.html              # 앱 프로토타입
├── prototype-mobile.html       # 모바일 앱 프로토타입
│
├── models/
│   ├── car-seat-rigged-v2.glb  # 10-bone (719 KB) ★ 현재 사용
│   ├── car-seat-rigged.glb     # 5-bone (698 KB)
│   ├── car-seat.glb            # 비리깅 메쉬 (579 KB)
│   └── ...                     # 기타 모델
│
├── libs/
│   ├── three.min.js            # Three.js r152
│   ├── OrbitControls.js        # 카메라 컨트롤
│   └── GLTFLoader.js           # GLTF/GLB 로더
│
├── blender/
│   ├── add_armature.py         # v1 리깅 (5-bone)
│   ├── add_armature_v2.py      # v2 리깅 (10-bone)
│   └── inspect_meshes.py       # 메쉬 분석 유틸리티
│
├── TECHNICAL.md                # 기술 상세 문서
├── RIGGING_GUIDE.md            # Blender 리깅 가이드
└── README.md                   # 이 파일
```

## 기술 스택

| 기술 | 용도 |
|------|------|
| Three.js r152 | 3D 렌더링, GLB 로드, SkinnedMesh 본 제어 |
| OrbitControls | 마우스/터치 카메라 조작 |
| Canvas 2D API | 히트맵, 골격도, 레이더 차트, 바 차트 |
| CanvasTexture | 3D 모델 위 체압 오버레이 |
| CSS3 | `backdrop-filter`, CSS Variables, 미디어 쿼리 |
| Vanilla JS | 서버 의존성 없는 순수 클라이언트사이드 |

## 로컬 실행

서버 불필요 — HTML 파일을 직접 열면 됩니다.

```bash
# 방법 1: 파일 직접 열기
xdg-open four-seats-final.html    # Linux
open four-seats-final.html        # macOS

# 방법 2: 로컬 HTTP 서버
python3 -m http.server 8080
# → http://localhost:8080/four-seats-final.html
```

---

**KETI (한국전자기술연구원)** — Korea Electronics Technology Institute
