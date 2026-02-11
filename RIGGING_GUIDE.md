# Blender → GLB Rigging → Three.js 웹 애니메이션 가이드

> 카시트 3D 모델에 관절(Armature)을 넣고 GLB로 내보내서 웹에서 실시간 조작하는 전체 과정

## 전체 워크플로우 요약

```
Free3D 카시트 모델 (.blend)
    │
    ▼  Blender에서 add_armature.py 실행
5-bone 아마추어 생성 + 메쉬 스키닝 + 애니메이션 키프레임
    │
    ▼  GLB 포맷으로 Export
car-seat-rigged.glb (698 KB)
    │
    ▼  Three.js GLTFLoader로 로드
웹 브라우저에서 Bone 직접 조작 → 실시간 시트 제어
```

---

## 1단계: 원본 모델 준비

### 소스 파일
- **파일**: `/home/kim/Downloads/car_seat/20190501_Car seat complete embedded.blend` (9 MB)
- **출처**: Free3D 카시트 모델 (2019년)

### 모델 구조 (9개 메쉬 오브젝트)
| 메쉬 이름 | 설명 | 움직임 |
|-----------|------|--------|
| `01 Base` | 시트 베이스 프레임 | 고정 |
| `02 Base rim` | 베이스 테두리 | 고정 |
| `03 Base controls` | 조절 레버 | 고정 |
| `04 Bottom seat` | 쿠션 윗면 | 높이 조절 |
| `05 Bottom sides` | 쿠션 사이드 볼스터 | 높이 조절 |
| `06 Back seat` | 등받이 메인 | 리클라인 |
| `07 Seat back sides` | 등받이 볼스터 | 리클라인 |
| `08 Upper neck` | 등받이 상단 | 리클라인 |
| `09 Header` | 헤드레스트 | 상하 조절 |

---

## 2단계: Blender에서 리깅 (add_armature.py)

### 스크립트 실행 방법
```bash
# Blender를 열고 .blend 파일 로드 후:
# Edit → Preferences → File Paths 확인
# Scripting 탭에서 add_armature.py 열기 → 실행 (Alt+P)

# 또는 커맨드라인에서:
blender "20190501_Car seat complete embedded.blend" --python add_armature.py
```

스크립트 위치: `/home/kim/Downloads/car_seat/add_armature.py`

### 2-1. 아마추어(뼈대) 생성

5개 본(Bone)으로 구성된 계층 구조:

```
Root (기준점, 고정)
 └── Slide (전후 슬라이드, Y축 이동)
      └── Cushion (높이 조절, Z축 이동)
           └── Backrest (리클라인, X축 회전)
                └── Headrest (헤드레스트, Z축 이동)
```

**핵심**: 부모-자식 관계 덕분에 Slide를 움직이면 Cushion → Backrest → Headrest가 같이 따라옴.

#### 본 좌표 상세

```python
# Root: 기준점
root.head = (0, 0, 0)
root.tail = (0, 0, 0.3)

# Slide: 전후 이동용 (Root의 자식)
slide.head = (0, 0, 0.1)
slide.tail = (0, 0, 0.4)

# Cushion: 높이 조절용 (Slide의 자식)
cushion.head = (0, 0, 0.35)
cushion.tail = (0, 0, 0.65)

# Backrest: 리클라인 힌지 (Cushion의 자식)
# 쿠션과 등받이 연결부에 위치
backrest.head = (0, -0.9, 0.4)
backrest.tail = (0, -1.8, 2.0)

# Headrest: 헤드레스트 (Backrest의 자식)
headrest.head = (0, -2.0, 2.4)
headrest.tail = (0, -2.1, 3.2)
```

### 2-2. 메쉬-본 매핑 (스키닝)

각 메쉬 오브젝트를 어떤 본이 제어하는지 지정:

```python
bone_assignments = {
    '01 Base':          'Root',       # 고정 프레임
    '02 Base rim':      'Root',       # 고정 프레임
    '03 Base controls': 'Root',       # 고정 프레임
    '04 Bottom seat':   'Cushion',    # 쿠션 → 높이 따라감
    '05 Bottom sides':  'Cushion',    # 볼스터 → 높이 따라감
    '06 Back seat':     'Backrest',   # 등받이 → 리클라인 따라감
    '07 Seat back sides':'Backrest',  # 등받이 볼스터 → 리클라인 따라감
    '08 Upper neck':    'Backrest',   # 등받이 상단 → 리클라인 따라감
    '09 Header':        'Headrest',   # 헤드레스트 → 독립 상하
}
```

#### 스키닝 방식
- **Vertex Group** 생성 → 해당 본 이름으로
- 모든 버텍스를 **weight 1.0**으로 할당 (리지드 스키닝)
- **Armature Modifier** 적용

```python
# 핵심 코드
vg = mesh_obj.vertex_groups.new(name=bone_name)
vg.add(list(range(len(mesh_obj.data.vertices))), 1.0, 'REPLACE')

mod = mesh_obj.modifiers.new(name='Armature', type='ARMATURE')
mod.object = armature_obj
```

> **리지드 스키닝**: 각 메쉬의 모든 버텍스가 하나의 본에 100% 귀속. 카시트 부품은 단단한 부품이므로 블렌드 웨이트 불필요.

### 2-3. 애니메이션 액션 생성

4개 Named Action을 키프레임으로 정의:

| 액션 이름 | 조작 대상 | 프레임 | 내용 |
|-----------|----------|--------|------|
| `Recline` | Backrest.rotation_euler.x | 0→30→60 | 0° → 30° → 0° |
| `HeadrestAdjust` | Headrest.location.z | 0→30→60 | 0 → +0.4 → 0 |
| `SlideForAft` | Slide.location.y | 0→30→60→90 | 0 → +0.5 → -0.5 → 0 |
| `HeightAdjust` | Cushion.location.z | 0→30→60 | 0 → +0.2 → 0 |

> **참고**: 이 액션들은 GLB에 포함되지만, 웹에서는 AnimationMixer로 재생하지 않고 **본을 직접 조작**하는 방식을 사용함.

### 2-4. GLB 내보내기

```python
bpy.ops.export_scene.gltf(
    filepath='car_seat_rigged.glb',
    export_format='GLB',           # 단일 바이너리 파일
    export_animations=True,        # 애니메이션 포함
    export_skins=True,             # 스켈레톤/본 포함
    use_selection=True,            # 선택된 오브젝트만
    export_apply=False,            # 모디파이어 유지 (적용X)
)
```

출력: `car_seat_rigged.glb` (698 KB) — 원본 579KB에서 +119KB (본+스킨 데이터)

---

## 3단계: Three.js에서 GLB 로드 및 본 제어

### 사용 파일
- **four-seats.html** — 4좌석 풀 모니터링 (메인)
- **bone-test.html** — 본 제어 테스트/디버깅

### 3-1. GLB 로드 + 본 추출

```javascript
import { GLTFLoader } from './libs/GLTFLoader.js';

const loader = new GLTFLoader();

loader.load('models/car-seat-rigged.glb', (gltf) => {
    const model = gltf.scene;

    // 본 레퍼런스 수집
    const bones = {};
    model.traverse(child => {
        // 방법 1: SkinnedMesh의 skeleton에서
        if (child.isSkinnedMesh && child.skeleton) {
            child.skeleton.bones.forEach(bone => {
                bones[bone.name] = bone;
            });
        }
        // 방법 2: 직접 Bone 노드 탐색
        if (child.isBone) {
            bones[child.name] = child;
        }
    });

    // bones = { Root, Slide, Cushion, Backrest, Headrest }
});
```

### 3-2. Rest Pose 저장

본을 조작하기 전에 **초기 상태(Rest Pose)**를 저장해둬야 함:

```javascript
const boneRest = {};
Object.entries(bones).forEach(([name, bone]) => {
    boneRest[name] = {
        px: bone.position.x, py: bone.position.y, pz: bone.position.z,
        rx: bone.rotation.x, ry: bone.rotation.y, rz: bone.rotation.z,
    };
});
```

### 3-3. 실시간 본 조작

Rest Pose 기준으로 **델타값**을 더해서 제어:

```javascript
function applyBonePose(bones, boneRest, axis, value) {
    switch (axis) {
        case 'recline':
            // 등받이 리클라인: X축 회전 (0~40도)
            bones.Backrest.rotation.x =
                boneRest.Backrest.rx + THREE.MathUtils.degToRad(value);
            break;

        case 'headrest':
            // 헤드레스트 상하: Y축 이동 (0~0.5)
            bones.Headrest.position.y =
                boneRest.Headrest.py + (value / 100) * 0.5;
            break;

        case 'slide':
            // 전후 슬라이드: Z축 이동 (-0.5~+0.5)
            bones.Slide.position.z =
                boneRest.Slide.pz - (value / 100) * 0.5;
            break;

        case 'height':
            // 높이 조절: Y축 이동 (0~0.3)
            bones.Cushion.position.y =
                boneRest.Cushion.py + (value / 100) * 0.3;
            break;
    }
}
```

### 3-4. 좌표계 변환 주의

Blender와 Three.js(GLTF)의 좌표계가 다름:

| 동작 | Blender 축 | GLTF/Three.js 축 |
|------|-----------|-------------------|
| 전후 슬라이드 | Y (forward) | -Z |
| 높이 | Z (up) | Y |
| 헤드레스트 상하 | Z (up) | Y |
| 리클라인 회전 | X (동일) | X |

> GLTF 내보내기 시 Blender가 자동 변환하지만, 코드에서 방향 부호는 직접 확인 필요.

### 3-5. 프리셋 포즈 + 스무스 애니메이션

```javascript
const POSE_PRESETS = {
    drive:  { recline: 8,  headrest: 30, slide: 0,   height: 20 },
    sport:  { recline: 3,  headrest: 50, slide: 30,  height: 0  },
    relax:  { recline: 35, headrest: 60, slide: -40, height: 40 },
    entry:  { recline: 0,  headrest: 0,  slide: -80, height: 0  },
};

// 매 프레임 보간으로 부드럽게 전환
function animatePoses(dt) {
    seats.forEach(seat => {
        if (!seat.poseTarget) return;
        let done = true;
        ['recline', 'headrest', 'slide', 'height'].forEach(axis => {
            const diff = seat.poseTarget[axis] - seat.pose[axis];
            if (Math.abs(diff) > 0.5) {
                seat.pose[axis] += diff * dt * 4;  // 부드러운 보간
                done = false;
            } else {
                seat.pose[axis] = seat.poseTarget[axis];
            }
            applyBonePose(seat, axis, seat.pose[axis]);
        });
        if (done) seat.poseTarget = null;
    });
}
```

---

## 4단계: 머티리얼 설정

GLB 로드 후 메쉬 이름으로 재질 교체:

```javascript
// 프레임 부품 (메탈릭)
const frameNames = new Set(['01 Base', '02 Base rim', '03 Base controls']);

// 악센트 부품 (약간 다른 가죽)
const accentNames = new Set(['05 Bottom sides', '07 Seat back sides']);

model.traverse(child => {
    if (child.isMesh) {
        if (frameNames.has(child.name)) {
            child.material = new THREE.MeshStandardMaterial({
                color: 0x1a1a1c, roughness: 0.25, metalness: 0.6
            });
        } else if (accentNames.has(child.name)) {
            child.material = new THREE.MeshStandardMaterial({
                color: 0x383838, roughness: 0.45, metalness: 0.05
            });
        } else {
            // 가죽 (기본)
            child.material = new THREE.MeshStandardMaterial({
                color: 0x2c2c2e, roughness: 0.52, metalness: 0.04
            });
        }
    }
});
```

---

## 5단계: 4좌석 시스템

같은 GLB를 4번 독립 로드 → 각각 다른 위치에 배치:

```javascript
const SEAT_CONFIG = [
    { id: 0, name: 'Driver',     pos: [-0.42, 0,  0.35], weight: 75 },
    { id: 1, name: 'Passenger',  pos: [ 0.42, 0,  0.35], weight: 65 },
    { id: 2, name: 'Rear Left',  pos: [-0.42, 0, -0.55], weight: 55 },
    { id: 3, name: 'Rear Right', pos: [ 0.42, 0, -0.55], weight: 80 },
];

// 각 좌석별로 독립된 bones, boneRest, pose 상태 관리
SEAT_CONFIG.forEach(config => {
    loader.load('models/car-seat-rigged.glb', (gltf) => {
        const model = gltf.scene.clone();
        model.position.set(...config.pos);
        scene.add(model);
        // 본 추출 & rest pose 저장 (좌석별 독립)
    });
});
```

---

## 체압 히트맵 오버레이

시트 위에 Canvas 텍스처 기반 히트맵 표시:

```javascript
// 16×16 그리드 체압 시뮬레이션
const pressureGrid = new Float32Array(256);

// 2-피크 가우시안 (왼/오른 엉덩이 압력 분포)
function simulatePressure(weight, time) {
    const wF = weight / 80;
    for (let y = 0; y < 16; y++) {
        for (let x = 0; x < 16; x++) {
            const nx = (x/15)*2-1, ny = (y/15)*2-1;
            const leftPeak  = gaussian2D(nx+0.35, ny-0.1, 0.28, 0.32);
            const rightPeak = gaussian2D(nx-0.35, ny-0.1, 0.28, 0.32);
            pressureGrid[y*16+x] = (leftPeak + rightPeak) * wF;
        }
    }
}

// 색상 매핑: 파랑(저) → 시안 → 초록 → 노랑 → 빨강(고)
```

---

## 파일 위치 정리

```
/home/kim/Downloads/car_seat/
├── 20190501_Car seat complete embedded.blend   ← 원본 블렌더 파일
├── add_armature.py                             ← 리깅 자동화 스크립트
├── car_seat.glb                                ← 리깅 전 메쉬만
└── car_seat_rigged.glb                         ← 리깅 완료 (→ 웹에서 사용)

/home/kim/car-seat-review/
├── models/
│   ├── car-seat.glb                            ← 기본 메쉬 (복사본)
│   └── car-seat-rigged.glb                     ← 리깅된 모델 (복사본)
├── libs/
│   ├── three.min.js                            ← Three.js r152
│   ├── GLTFLoader.js                           ← GLTF/GLB 로더
│   └── OrbitControls.js                        ← 카메라 컨트롤
├── four-seats.html                             ← 메인: 4좌석 본 제어
├── bone-test.html                              ← 본 테스트/디버깅
├── seat-viewer.html                            ← 기본 메쉬 뷰어
└── index.html (외 5개)                          ← 프로시저럴 방식 (참고)
```

---

## 요약: 같은 작업 다시 하려면

### 1. 블렌더 모델 준비
- `.blend` 파일에서 메쉬 이름 확인 (Outliner 패널)
- 각 메쉬가 어떤 움직임을 해야 하는지 정리

### 2. 본 계층 설계
- 물리적 관절 구조 기반으로 부모-자식 관계 설정
- 이동(position)과 회전(rotation) 중 뭘 쓸지 결정

### 3. add_armature.py 수정 후 실행
- `bone_assignments` 딕셔너리에서 메쉬↔본 매핑 수정
- 본 좌표를 모델 바운딩박스에 맞게 조정
- Blender Scripting 탭에서 실행

### 4. GLB 내보내기
- `export_skins=True`, `export_animations=True` 필수
- `export_apply=False`로 모디파이어 유지

### 5. Three.js에서 로드
- `GLTFLoader`로 로드
- `traverse()`로 본 레퍼런스 수집
- Rest Pose 저장
- 슬라이더/프리셋으로 본 position/rotation 직접 조작

---

## 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| 모델 로드 안됨 | CORS 정책 | `python3 -m http.server`로 로컬 서버 실행 |
| 본이 안 보임 | SkinnedMesh에서 추출 안함 | `child.isSkinnedMesh && child.skeleton` 체크 |
| 방향이 이상함 | Blender↔GLTF 좌표계 차이 | Y↔Z 축 변환 확인, 부호 조정 |
| 메쉬가 안 움직임 | Vertex Group 이름 불일치 | 본 이름과 Vertex Group 이름 정확히 일치 확인 |
| 애니메이션 안 됨 | AnimationMixer 사용 안함 | 본 직접 조작 방식 사용 (위 코드 참고) |
| 모델이 검게 보임 | 라이트 부족 | DirectionalLight + AmbientLight 추가 |
