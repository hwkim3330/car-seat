# Technical Reference — 10-Bone Seat Control System

> `four-seats-final.html` 기준 런타임 기술 문서.
> Blender 리깅 과정은 [RIGGING_GUIDE.md](RIGGING_GUIDE.md) 참조.

---

## 1. 데이터 구조

### 1.1 좌석 객체 (seats[i])

```javascript
seats[i] = {
    // 설정
    id:     0,                        // 좌석 인덱스 (0-3)
    name:   'Driver',                 // 표시 이름
    label:  'FL',                     // 약칭
    pos:    [-0.45, 0, -0.55],        // 월드 좌표
    weight: 75,                       // 탑승자 체중 (kg)

    // Three.js 참조
    model:  THREE.Group,              // GLB 씬 루트
    hl:     THREE.Mesh,               // 선택 하이라이트 링
    bones:  { Root, Slide, Cushion, Backrest, Headrest,
              BolsterL, BolsterR, Lumbar,
              BackBolsterL, BackBolsterR },
    rest:   { Root: {px,py,pz,rx,ry,rz}, ... },  // Rest Pose 저장

    // 포즈 상태
    p:      { slide:0, height:0, tilt:0, recline:0,
              hrH:0, hrT:0, bolster:0, lumbar:0, bBolster:0 },
    target: null,                     // 프리셋 애니메이션 목표 (또는 null)

    // 체압 시뮬레이션
    grid:   Float32Array(256),        // 16x16 체압 격자
    avg:    0,                        // 평균 체압 (%)
    peak:   0,                        // 피크 체압 (%)

    // 히트맵 오버레이
    hmC:    { cv, tex },              // 쿠션 캔버스 + CanvasTexture
    hmB:    { cv, tex },              // 등받이 캔버스 + CanvasTexture
};
```

### 1.2 설정 상수

```javascript
const SEATS = [
    { id:0, name:'Driver',    label:'FL', pos:[-0.45,0,-0.55], weight:75 },
    { id:1, name:'Passenger', label:'FR', pos:[ 0.45,0,-0.55], weight:65 },
    { id:2, name:'Rear Left', label:'RL', pos:[-0.45,0, 0.55], weight:55 },
    { id:3, name:'Rear Right',label:'RR', pos:[ 0.45,0, 0.55], weight:80 },
];

const AXES = ['slide','height','tilt','recline','hrH','hrT','bolster','lumbar','bBolster'];

const COL = ['#007aff','#34c759','#ff9f0a','#af52de'];

const PRESETS = {
    drive:  {slide:0,  height:20,tilt:2,  recline:8, hrH:30, hrT:-5, bolster:20, lumbar:40, bBolster:15},
    sport:  {slide:30, height:0, tilt:-3, recline:3, hrH:50, hrT:-8, bolster:80, lumbar:60, bBolster:70},
    relax:  {slide:-40,height:40,tilt:5,  recline:35,hrH:60, hrT:10, bolster:10, lumbar:50, bBolster:10},
    entry:  {slide:-80,height:0, tilt:0,  recline:0, hrH:0,  hrT:0,  bolster:0,  lumbar:0,  bBolster:0},
    flat:   {slide:0,  height:50,tilt:8,  recline:40,hrH:100,hrT:15, bolster:0,  lumbar:30, bBolster:0},
    hold:   {slide:10, height:10,tilt:-2, recline:5, hrH:40, hrT:-3, bolster:90, lumbar:70, bBolster:85},
};
const ZERO = {slide:0,height:0,tilt:0,recline:0,hrH:0,hrT:0,bolster:0,lumbar:0,bBolster:0};
```

---

## 2. 본 제어 수학

### 2.1 좌표계 변환 (Blender → GLTF)

| 동작 | Blender | GLTF/Three.js | 비고 |
|------|---------|---------------|------|
| 전후 | Y축 이동 | **-Z축** 이동 | 부호 반전 |
| 상하 | Z축 이동 | **Y축** 이동 | 축 교환 |
| 좌우 | X축 이동 | **X축** 이동 | 동일 |
| 리클라인 | X축 회전 | **X축** 회전 | 동일 |

### 2.2 본별 변환 공식 (applyBone)

모든 변환은 **Rest Pose 기준 델타**로 적용됩니다:

```
최종값 = RestPose + (슬라이더값 / 스케일) * 이동량
```

| 축 | 변환 타입 | 공식 | 설명 |
|----|----------|------|------|
| `slide` | Position Z | `Slide.pz = rest.pz - (val/100) * 0.5` | val=-100이면 +0.5 전진, val=+100이면 -0.5 후진 |
| `height` | Position Y | `Cushion.py = rest.py + (val/100) * 0.3` | val=100이면 0.3m 상승 |
| `tilt` | Rotation X | `Cushion.rx = rest.rx + degToRad(val)` | val=10이면 10도 전방 기울기 |
| `recline` | Rotation X | `Backrest.rx = rest.rx + degToRad(val)` | val=40이면 40도 뒤로 눕힘 |
| `hrH` | Position Y | `Headrest.py = rest.py + (val/100) * 0.5` | val=100이면 0.5m 상승 |
| `hrT` | Rotation X | `Headrest.rx = rest.rx + degToRad(val)` | val=-15이면 15도 앞으로 기울기 |
| `bolster` | Position X (대칭) | `BolsterL.px = rest.px + (val/100) * 0.15` | 좌측: +X (안쪽) |
| | | `BolsterR.px = rest.px - (val/100) * 0.15` | 우측: -X (안쪽) |
| `lumbar` | Position Z | `Lumbar.pz = rest.pz - (val/100) * 0.3` | 앞으로 밀어냄 (-Z) |
| `bBolster` | Position X (대칭) | `BackBolsterL.px = rest.px + (val/100) * 0.12` | 좌측: +X |
| | | `BackBolsterR.px = rest.px - (val/100) * 0.12` | 우측: -X |

### 2.3 본 계층과 연쇄 효과

```
Slide 이동 → Cushion, Bolsters, Backrest, Lumbar, BackBolsters, Headrest 전체 이동
Cushion 상승 → Bolsters, Backrest, Lumbar, BackBolsters, Headrest 함께 상승
Backrest 회전 → Lumbar, BackBolsters, Headrest 함께 회전
```

부모-자식 관계로 인한 자동 전파. 코드에서 명시적 처리 불필요.

### 2.4 슬라이더 범위 → 물리 단위 매핑

| 슬라이더 | 범위 | 물리 해석 |
|---------|------|----------|
| Slide | -100 ~ +100 | -50mm ~ +50mm 전후 |
| Height | 0 ~ 100 | 0 ~ 30mm 상승 |
| Tilt | -10 ~ +10 | -10° ~ +10° 쿠션 기울기 |
| Recline | 0 ~ 40 | 0° ~ 40° 등받이 뒤로 |
| Headrest ↕ | 0 ~ 100 | 0 ~ 50mm 상승 |
| Headrest Tilt | -15 ~ +15 | -15° ~ +15° |
| Bolster | 0 ~ 100 | 0% ~ 100% 조임 (0~15mm) |
| Lumbar | 0 ~ 100 | 0% ~ 100% 밀어냄 (0~30mm) |
| Back Bolster | 0 ~ 100 | 0% ~ 100% 조임 (0~12mm) |

---

## 3. 체압 시뮬레이션

### 3.1 2D 가우시안 함수

```javascript
function g2d(x, y, sx, sy) {
    return Math.exp(-(x*x)/(2*sx*sx) - (y*y)/(2*sy*sy));
}
```

### 3.2 시뮬레이션 계산

16x16 격자의 각 셀 좌표를 [-1, +1] 범위로 정규화 후 4개 가우시안 피크를 합산:

```
좌표 정규화: nx = (x/15)*2 - 1,  ny = (y/15)*2 - 1

pressure = (
    G(nx + 0.35 - bolF, ny - 0.1,  σx=0.28, σy=0.32) * 1.00   // 좌측 엉덩이
  + G(nx - 0.35 + bolF, ny - 0.1,  σx=0.28, σy=0.32) * 1.00   // 우측 엉덩이
  + G(nx + 0.30 - bolF, ny + 0.25, σx=0.22, σy=0.40) * 0.35   // 좌측 허벅지
  + G(nx - 0.30 + bolF, ny + 0.25, σx=0.22, σy=0.40) * 0.35   // 우측 허벅지
) * weightFactor

bolF = (bolster / 100) * 0.15       // 볼스터 영향 계수
weightFactor = weight / 80           // 체중 정규화 (80kg 기준)
```

### 3.3 시간 변동 + 노이즈

```
v += sin((t + seatOffset) * 0.3) * 0.01     // 호흡/미세 움직임
v += (random() - 0.5) * 0.005               // 센서 노이즈
v = clamp(v, 0, 1)                           // 0~1 범위 제한

seatOffset = seatIndex * 1.7                 // 좌석별 위상차
```

### 3.4 색상 매핑 (pRGBA)

5구간 선형 보간:

| 구간 | t 범위 | R | G | B | 투명도 |
|------|--------|---|---|---|--------|
| 1 | 0.00 ~ 0.25 | 0 | 0→255 | 255 | 0.3 ~ 0.48 |
| 2 | 0.25 ~ 0.50 | 0 | 255 | 255→0 | 0.48 ~ 0.65 |
| 3 | 0.50 ~ 0.75 | 0→255 | 255 | 0 | 0.65 ~ 0.83 |
| 4 | 0.75 ~ 1.00 | 255 | 255→0 | 0 | 0.83 ~ 1.00 |

투명도 공식: `alpha = 0.3 + t * 0.7`

### 3.5 히트맵 오버레이

체압 격자를 Canvas 2D로 그린 후 `CanvasTexture`로 3D 모델 위에 오버레이:

```
쿠션 오버레이:  128x128 캔버스 → PlaneGeometry
등받이 오버레이: 128x128 캔버스 → PlaneGeometry

각 셀 = fillRect(x*8, y*8, 8, 8, pRGBA(value))
매 프레임 tex.needsUpdate = true
```

---

## 4. Three.js 씬 구성

### 4.1 카메라

```javascript
PerspectiveCamera(fov: 42, near: 0.01, far: 100)
position: (2, 2.5, 2.8)
OrbitControls.target: (0, 0.25, 0)
minDistance: 0.5,  maxDistance: 10
maxPolarAngle: π * 0.85
enableDamping: true
```

### 4.2 조명 (4+1 구성)

| 타입 | 위치/색상 | 강도 | 역할 |
|------|----------|------|------|
| AmbientLight | 0xffffff | 1.2 | 기본 전역 조명 |
| DirectionalLight #1 | (2, 8, 3), 0xffffff | 2.2 | 메인 키라이트 + 그림자 |
| DirectionalLight #2 | (-4, 5, -2), 0xc8d0ff | 0.8 | 측면 필라이트 (블루 틴트) |
| DirectionalLight #3 | (0, 2, -6), 0xffffff | 0.5 | 후면 림라이트 |
| HemisphereLight | sky: 0xffffff, ground: 0xe8e8ea | 0.6 | 환경광 |

### 4.3 그림자 설정

```javascript
DirectionalLight #1:
  castShadow: true
  shadow.mapSize: 2048 x 2048
  shadow.camera: left:-3, right:3, top:3, bottom:-3
  shadow.near: 0.1,  shadow.far: 20
  shadow.bias: -0.001
```

### 4.4 렌더러

```javascript
WebGLRenderer({ antialias: true })
toneMapping: ACESFilmicToneMapping
toneMappingExposure: 1.8
shadowMap.enabled: true
shadowMap.type: PCFSoftShadowMap
```

### 4.5 바닥 + 격자

```javascript
GridHelper(size: 5, divisions: 24, color1: 0xccccce, color2: 0xdddddf)
PlaneGeometry(10, 10) — color: 0xe8e8ea, roughness: 0.85, receiveShadow: true
```

### 4.6 GLB 로드 프로세스

```
1. GLTFLoader.load('models/car-seat-rigged-v2.glb')
2. model.traverse() → SkinnedMesh 찾기
3. skeleton.bones → 이름으로 bones{} 매핑
4. Rest Pose 저장 (position.x/y/z, rotation.x/y/z)
5. 머티리얼 교체:
   - 프레임 (01,02,03): color:0x1a1a1c, metalness:0.6, roughness:0.25
   - 볼스터 (05,07):    color:0x383838, metalness:0.05, roughness:0.45
   - 가죽 (기타):       color:0x2c2c2e, metalness:0.04, roughness:0.52
6. 스케일링: 0.8 / max(bbox.size) → setScalar
7. 위치 배치: SEATS[i].pos 기준
8. 하이라이트 링 생성 (TorusGeometry)
9. 체압 오버레이 생성 (mkOv)
```

---

## 5. 프리셋 애니메이션

### 5.1 보간 방식

매 프레임 선형 보간 (lerp):

```javascript
function animTargets(dt) {
    seats.forEach(s => {
        if (!s.target) return;
        let done = true;
        AXES.forEach(k => {
            const diff = s.target[k] - s.p[k];
            if (Math.abs(diff) > 0.3) {
                s.p[k] += diff * dt * 5;    // 보간 속도 = 5/s
                applyBone(s, k, s.p[k]);
                done = false;
            } else {
                s.p[k] = s.target[k];
                applyBone(s, k, s.p[k]);
            }
        });
        if (done) { s.target = null; syncSliders(); }
    });
}
```

### 5.2 프리셋 적용 흐름

```
goPreset('sport') 호출
→ seats[cur].target = {...PRESETS.sport} 설정
→ animate() 루프에서 animTargets(dt) 매 프레임 호출
→ 각 축이 목표값에 수렴할 때까지 보간
→ 모든 축 도달 시 target = null, syncSliders() 호출
```

---

## 6. 골격 다이어그램 (drawBoneDiagram)

Canvas 2D로 현재 포즈의 2D 단면도를 실시간 렌더링.

### 6.1 사이드 뷰 (왼쪽 절반)

```
표시 요소:
- 쿠션 경사선 (tilt 반영)
- 등받이 기울기선 (recline 반영)
- 럼바 서포트 포인트 (lumbar 반영)
- 헤드레스트 위치/기울기 (hrH, hrT 반영)
- 높이 표시선 (height 반영)
- 슬라이드 오프셋 (slide 반영)

색상:
- 쿠션: #007aff (blue)
- 등받이: #af52de (purple)
- 럼바: #ff3b30 (red)
- 헤드레스트: #ff6482 (pink)
- 기준선: #aeaeb2 (dim gray)
```

### 6.2 프론트 뷰 (오른쪽 절반)

```
표시 요소:
- 좌석 볼스터 좌/우 조임 (bolster 반영)
- 등 볼스터 좌/우 조임 (bBolster 반영)
- 럼바 중앙 돌출 (lumbar 반영)
- 좌석 폭 표시

색상:
- 볼스터: #30b0c7 (teal)
- 백볼스터: #30b0c7 (teal)
- 럼바: #ff3b30 (red)
```

### 6.3 업데이트 주기

```javascript
// animate() 루프 내
if (elapsedTime - lastUI > 0.2) {   // 200ms 간격
    updStats();
    drawBoneDiagram();
    lastUI = elapsedTime;
}
```

---

## 7. 버전별 차이점

### 7.1 테마/컬러 비교

| 버전 | Background | Accent | COL 배열 | Scene BG |
|------|-----------|--------|----------|----------|
| Desktop | `#f5f5f7` | `#007aff` | blue,green,orange,purple | `0xf0f0f2` |
| Mobile | `#f5f5f7` | `#007aff` | blue,green,orange,purple | `0xf0f0f2` |
| Tablet | `#f5f5f7` | `#007aff` | blue,green,orange,purple | `0xf0f0f2` |
| Cockpit | `#0a0e17` | `#00d4ff` | cyan,green,amber,magenta | `0x0a0e17` |
| Kiosk | `#0c0c0c` | `#c8a44e` | gold tones (4 variants) | `0x111111` |
| Dashboard | `#f0f2f5` | `#2563eb` | blue,green,orange,purple | `0xf0f2f5` |

### 7.2 레이아웃 비교

| 버전 | 좌측 패널 | 3D 캔버스 | 우측 패널 | 특수 UI |
|------|----------|----------|----------|---------|
| Desktop | 220px (차량뷰+카드+프리셋) | flex | 300px (슬라이더+분석) | - |
| Mobile | - | fullscreen | - | 바텀시트 (스와이프) |
| Tablet | - | flex | 340px (접이식) | 미니카 오버레이 |
| Cockpit | 200px | flex | 300px | 시계, REC |
| Kiosk | - | fullscreen | - | 하단 글래스 패널 |
| Dashboard | 280px (4석 카드) | flex | 320px (차트) | 바/레이더/히트맵 |

### 7.3 고유 기능

| 버전 | 고유 기능 |
|------|----------|
| Cockpit | 실시간 시계 (1초 갱신), REC 인디케이터, CONNECTED 상태 |
| Kiosk | 자동 데모 모드, OrbitControls autoRotate, idle 감지 |
| Dashboard | 레이더 차트 (9축 4석 오버레이), 바 차트, 4석 히트맵, Apply All, Export |

---

## 8. 함수 레퍼런스

### 8.1 초기화

| 함수 | 역할 |
|------|------|
| `initScene()` | Three.js 씬, 카메라, 렌더러, 조명, 바닥, 격자 생성. GLB 4회 로드 |
| `buildCar()` | 프로시저럴 차량 외형 (탑뷰 Shape) + 전방 화살표 생성 |
| `loadGLB(i)` | i번째 좌석 GLB 로드 → 본 추출 → 머티리얼 → 오버레이 → hilite |
| `drawLeg()` | 체압 컬러 범례 캔버스 (130px 그라데이션) |

### 8.2 본 제어

| 함수 | 역할 |
|------|------|
| `applyBone(s, axis, val)` | 개별 본 position/rotation 설정 (9 case switch) |
| `setPose(axis, val)` | 현재 좌석의 포즈 업데이트 + applyBone + syncSliders |
| `goPreset(name)` | 프리셋 목표 설정 → 애니메이션 시작 |
| `resetPose()` | ZERO 포즈로 애니메이션 리셋 |
| `animTargets(dt)` | 프리셋 보간 (매 프레임) |
| `syncSliders()` | DOM 슬라이더 값 ← 현재 포즈 동기화 |

### 8.3 체압

| 함수 | 역할 |
|------|------|
| `g2d(x, y, sx, sy)` | 2D 가우시안 함수 |
| `simPress(s, t)` | 16x16 격자 체압 시뮬레이션 |
| `updOv(s)` | 쿠션/등받이 히트맵 캔버스 업데이트 |
| `pRGBA(t)` | 체압값 → RGBA 색상 변환 |
| `updStats()` | Avg/Peak 통계 + 미니 히트맵 갱신 |

### 8.4 UI

| 함수 | 역할 |
|------|------|
| `sel(i)` | i번째 좌석 선택 → hilite + syncSliders |
| `hilite()` | 선택된 좌석 하이라이트 링 토글 |
| `renderCards()` | 좌측 패널 좌석 카드 HTML 생성 |
| `switchTab(name)` | 분석 탭 전환 (Diagram/Pressure) |
| `setWt(w)` | 탑승자 체중 설정 |
| `toast(msg)` | 알림 토스트 표시 (2초 자동 숨김) |
| `drawBoneDiagram()` | 골격 2D 단면도 렌더링 |
| `mkOv(parent, w, h, pos)` | 캔버스 텍스처 오버레이 메쉬 생성 |

### 8.5 메인 루프

```javascript
function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.1);   // 프레임 델타 (100ms 캡)
    const t = clock.getElapsedTime();

    seats.forEach(s => { simPress(s, t); updOv(s); });   // 체압 매 프레임
    animTargets(dt);                                      // 프리셋 보간

    if (t - lastUI > 0.2) {                              // 200ms UI 갱신
        updStats();
        drawBoneDiagram();
        lastUI = t;
    }

    controls.update();
    renderer.render(scene, camera);
}
```

---

## 9. 원본 메쉬 데이터

### 9.1 버텍스 분포 (Blender 좌표계)

| 메쉬 | 버텍스 | X 범위 | Y 범위 | Z 범위 |
|------|--------|--------|--------|--------|
| 01 Base | 882 | -1.11 ~ 1.11 | -1.35 ~ 1.31 | -0.36 ~ 0.36 |
| 02 Base rim | 128 | -9.11 ~ 9.11 | -0.82 ~ 1.00 | 0.17 ~ 0.87 |
| 03 Base controls | 1,306 | -30.06 ~ 30.06 | -1.02 ~ 1.88 | 0.14 ~ 1.10 |
| 04 Bottom seat | 283 | -0.65 ~ 0.65 | -1.34 ~ 1.14 | -0.54 ~ 0.24 |
| 05 Bottom sides | 302 | -0.89 ~ 0.89 | -1.18 ~ 1.03 | -0.18 ~ 0.56 |
| 06 Back seat | 115 | -0.71 ~ 0.71 | -2.09 ~ -0.92 | 0.06 ~ 2.13 |
| 07 Seat back sides | 337 | -1.10 ~ 1.10 | -2.31 ~ -0.81 | -0.23 ~ 2.01 |
| 08 Upper neck | 427 | -0.88 ~ 0.88 | -0.35 ~ 0.46 | -0.42 ~ 0.41 |
| 09 Header | 158 | -0.58 ~ 0.58 | -2.32 ~ -1.75 | 2.47 ~ 3.22 |

### 9.2 볼스터 분할 대칭성

| 메쉬 | 좌측 | 중앙 | 우측 | 분할 방식 |
|------|------|------|------|----------|
| 05 Bottom sides | 151 | 0 | 151 | X축, 완벽 대칭 |
| 07 Seat back sides | 162 | 15 | 160 | X축, 중앙 15개 블렌드 |
| 06 Back seat | 50 | 15 | 50 | Z축 (높이), 럼바 그라데이션 |

---

## 10. DOM ID 맵

### 10.1 3D 관련

| ID | 용도 |
|----|------|
| `#c3d` | Three.js 렌더러 컨테이너 |
| `#legCv` | 체압 컬러 범례 캔버스 |
| `#boneCv` | 골격 다이어그램 캔버스 |
| `#miniHeat` | 미니 히트맵 캔버스 |

### 10.2 좌석 선택

| ID | 용도 |
|----|------|
| `#d0` ~ `#d3` | 탑뷰 좌석 도트 (FL/FR/RL/RR) |
| `#cards` | 좌석 카드 컨테이너 |
| `#posLabel` | 현재 좌석 라벨 |

### 10.3 슬라이더 (입력 / 표시값)

| 슬라이더 ID | 표시값 ID | 축 |
|------------|----------|-----|
| `#sSlide` | `#vSlide` | slide |
| `#sHeight` | `#vHeight` | height |
| `#sTilt` | `#vTilt` | tilt |
| `#sRecline` | `#vRecline` | recline |
| `#sHrH` | `#vHrH` | hrH |
| `#sHrT` | `#vHrT` | hrT |
| `#sBol` | `#vBol` | bolster |
| `#sLum` | `#vLum` | lumbar |
| `#sBBol` | `#vBBol` | bBolster |
| `#wSl` | `#wVal` | weight |

### 10.4 분석/통계

| ID | 용도 |
|----|------|
| `#pAvg` | 평균 체압 표시 |
| `#pPeak` | 피크 체압 표시 |
| `#boneInfo` | 골격 정보 텍스트 |
| `#tab-diagram` | 다이어그램 탭 콘텐츠 |
| `#tab-pressure` | 체압 탭 콘텐츠 |

### 10.5 기타

| ID | 용도 |
|----|------|
| `#loader` | 로딩 오버레이 |
| `#lmsg` | 로딩 메시지 |
| `#toast` | 토스트 알림 |
| `#presetBtns` | 프리셋 버튼 그룹 |
