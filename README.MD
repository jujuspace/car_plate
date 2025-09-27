# Car Plate AI - 뺑소니 범인 찾기

이 프로젝트는 뺑소니 사고 범인을 찾기 위한 차량 번호판 인식 AI 시스템입니다.

## 프로젝트 구조

```
car_plate_AI/
├── data/
│   ├── 2_useful_images/          # 유용한 이미지 데이터
│   │   ├── segment_1/           # 첫 번째 세그먼트 이미지들
│   │   ├── segment_2/           # 두 번째 세그먼트 이미지들
│   │   └── segment_3/           # 세 번째 세그먼트 이미지들
│   ├── plate_results/           # 번호판 크롭 결과물
│   └── cropped_plates/          # 크롭된 번호판 이미지들
├── jujuspace/                   # 개발 작업공간
├── advanced_plate_cropper.py    # 고급 번호판 크롭 도구
├── simple_plate_cropper.py      # 간단한 번호판 크롭 도구
├── plate_cropper.py             # 기본 번호판 크롭 도구
├── car_inform.py                # 차량 정보 관련 코드
└── point_data.json              # 점 데이터 저장 파일
```

## 번호판 크롭 도구 사용법

### Advanced Plate Cropper (권장)

최신 기능이 포함된 고급 번호판 크롭 도구입니다.

```bash
python advanced_plate_cropper.py
```

**주요 기능:**
- 🔹 이미지 경로 입력으로 이미지 로드
- 🔹 4개 점 클릭으로 번호판 영역 선택
- 🔹 **드래그로 점 위치 미세 조정**
- 🔹 **자동 JSON 저장** (point_data.json)
- 🔹 **실시간 perspective transform** (880x440)
- 🔹 **마스크 이미지 생성** (선택 영역 외부 어둡게)
- 🔹 다중 결과 저장 (perspective + masked + annotated)

**사용 방법:**
1. 웹 인터페이스에서 이미지 경로 입력 (예: `data/2_useful_images/segment_1/frame_002317.jpg`)
2. "Load Image" 클릭
3. 번호판 4개 모서리를 순서대로 클릭
4. 점을 드래그해서 위치 미세 조정
5. "Save Results"로 모든 결과물 저장

**출력 파일:**
- `{이미지명}_perspective.jpg`: 880x440 크롭된 번호판
- `{이미지명}_masked.jpg`: 마스크 적용된 원본 이미지
- `{이미지명}_annotated.jpg`: 점과 선이 표시된 이미지
- `{이미지명}_data.json`: 상세 데이터 (점 좌표, 타임스탬프 등)

## 데이터 관리

### 자동 저장 시스템
- 점을 찍을 때마다 `point_data.json`에 자동 저장
- 이미지 재로드 시 기존 점 정보 자동 복원
- "Export All Points"로 전체 데이터 내보내기

### 데이터 다운로드
프로젝트에 필요한 데이터는 Google Drive를 통해 다운로드해야 합니다.

## 개발 가이드라인

### 코드 구조
- **각자 새로운 폴더를 만들어서 개발하세요**
- 개인별 작업 공간을 유지하여 코드 충돌을 방지합니다

### 추가 데이터
- 추가할 데이터가 있다면 Google Drive에 업로드하고 링크를 공유해주세요

## 프로젝트 목적

- 뺑소니 사고 영상에서 차량 번호판 자동 인식
- 범인 차량 식별을 위한 AI 기반 분석 시스템
- 정확한 번호판 영역 추출을 위한 수동 어노테이션 도구 제공

##
차량번호판 사이즈 출처 
https://ko.wikipedia.org/wiki/%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EC%B0%A8%EB%9F%89_%EB%B2%88%ED%98%B8%ED%8C%90

## 참고 유튜브 영상
트럭 뒷모습 https://youtu.be/LXjmRBoMhT8?si=yClVXfKH1elZ1V2N&t=632


big_plate_size=(880, 440) # (width, height) ㅐorigin size=(440mm, 220mm)