# AI 서비스 Docker 실행 방법

이 프로젝트는 평소에는 로컬에서 실행하고, 필요할 때 Docker로 실행할 수 있도록 구성했다.
Docker에서는 우선 API 서버를 켜고, 기존에 저장한 날씨 예측 결과를 조회한다.
GPU 예측 프로그램까지 Docker에서 실행하는 방법은 문서 마지막에 정리했다.

## 1. 실행하기 전에 알아둘 내용

| 이름 | 역할 |
| --- | --- |
| Dockerfile | Python과 필요한 패키지를 설치하는 방법을 적은 파일 |
| 이미지 | Dockerfile로 만든 실행 환경. 코드를 수정하면 다시 빌드해서 반영한다 |
| 컨테이너 | 이미지를 이용해 실제로 실행 중인 프로그램 |
| compose.yaml | 사용할 이미지, 연결할 폴더, 접속 포트 등을 한 번에 설정하는 파일 |

이번 구성에서는 프로그램과 예측 결과를 다음과 같이 연결한다.

```text
기존 GPU 예측 프로그램 → 컴퓨터의 data 폴더
                              ↓
                       Docker의 API 서버
                              ↓
                         웹 또는 Spring
```

API 서버는 요청을 받으면 저장된 결과에서 해당 지역의 값을 읽는다.
지역을 바꿀 때마다 Pangu 모델을 다시 실행하지 않는다.

## 2. Docker Desktop 실행 및 폴더 이동

Docker Desktop을 켜고 엔진이 실행될 때까지 기다린다.
명령어는 Docker Desktop 화면이 아닌 **PowerShell**에서 입력한다.

아래 경로는 작성한 컴퓨터의 예시이므로, 다른 컴퓨터에서는 프로젝트를 저장한 경로로 바꾼다.

```powershell
cd C:\Users\jeonm\code\weather-life\ai-service
docker version
```

`docker version`에서 Client와 Server 정보가 모두 표시되는지 확인한다.
이후 명령어는 모두 **Dockerfile과 compose.yaml이 있는 ai-service 폴더에서** 실행한다.

관련 파일 위치는 다음과 같다.

```text
ai-service/
├─ Dockerfile
├─ DOCKER_RUN_GUIDE.md  ← 현재 문서
├─ stations.csv
├─ requirements-*.txt
├─ pangu_service/
├─ compose.yaml
└─ .dockerignore
```

## 3. 인증키와 접속 포트 설정

API 인증키는 이 서버에 요청할 때 함께 보내는 비밀번호 역할을 한다.
기존 로컬 실행에서 만든 `local-api.key`가 있으면 같은 값을 사용한다.
파일이 없을 때만 아래 명령이 새 키를 만든다.

```powershell
if (-not (Test-Path -LiteralPath .\local-api.key)) {
    [guid]::NewGuid().ToString("N") | Set-Content -LiteralPath .\local-api.key -Encoding ascii -NoNewline
}

$env:PANGU_API_KEY = (Get-Content -LiteralPath .\local-api.key -Raw).Trim()
$env:PANGU_API_PORT = "18080"
```

이 문서는 테스트 접속 포트를 `18080`으로 정했다.
별도로 지정하지 않으면 Compose 설정의 기본 포트는 `8000`이다.

`$env:`로 설정한 값은 현재 PowerShell 창에서 사용한다.
새 창을 열면 해당 창에서도 설정해야 한다.
매번 입력하는 대신 값을 저장하려면 `ai-service/.env.example`을 `.env`로 복사해 설정할 수도 있다.
같은 항목이 PowerShell과 `.env`에 모두 있으면 PowerShell 값이 우선한다.

`local-api.key`와 `.env`에는 실제 인증값이 들어가므로 GitHub에 올리지 않는다.
현재 `.gitignore`와 `.dockerignore`에서 제외하도록 설정되어 있다.

## 4. 예측 결과 폴더 연결

Docker 이미지에는 예측 결과를 넣지 않았다.
이미 만들어 둔 **data 폴더**를 연결해서 사용한다.
이 폴더 안에는 다음 파일들이 있어야 한다.

```text
data/
└─ forecasts/
   └─ 예측실행번호/
      ├─ manifest.json
      ├─ surface_24.npy
      ├─ surface_48.npy
      ├─ surface_72.npy
      └─ surface_96.npy
```

`manifest.json`에는 예측 기준 시각과 결과 파일 정보가 들어 있고,
`surface_*.npy`에는 계산된 날씨 값이 저장되어 있다.
예측 일수를 다르게 설정했다면 결과 파일 개수도 달라질 수 있다.

현재 프로젝트의 `ai-service/data`를 사용한다면 별도 설정 없이 실행할 수 있다.
기존 로컬 결과가 다른 폴더에 있다면 아래 경로를 **실제 data 폴더 경로로 바꿔서** 입력한다.

```powershell
# 아래 경로는 예시이다. 실제 예측 결과가 저장된 data 폴더로 변경한다.
$env:PANGU_HOST_DATA_DIR = "C:/weather-results/data"

# manifest.json 파일이 보이는지 확인한다.
Get-ChildItem -Path "$env:PANGU_HOST_DATA_DIR/forecasts/*/manifest.json" -ErrorAction Stop
```

연결할 위치는 `forecasts` 폴더나 개별 예측 폴더가 아니라 **그 위의 data 폴더**다.
예측 결과가 아직 없다면 먼저 기존 로컬 GPU 프로그램으로 결과를 생성한다.
API 서버만 켜도 예측 파일이 자동으로 만들어지는 것은 아니다.

## 5. Docker API 실행

앞에서 설정한 **같은 PowerShell 창**에서 실행한다.

```powershell
docker compose up -d --build ai-api
```

| 옵션 | 의미 |
| --- | --- |
| `up` | 컨테이너를 만들거나 실행한다 |
| `-d` | PowerShell 입력창을 계속 사용할 수 있도록 뒤에서 실행한다 |
| `--build` | 현재 코드와 Dockerfile을 기준으로 이미지를 빌드한다 |
| `ai-api` | Compose에 등록된 API 서버 이름 |

처음 실행할 때는 Python 이미지와 패키지를 내려받으므로 시간이 걸릴 수 있다.
실행 상태와 로그는 아래 명령으로 확인한다.

```powershell
docker compose ps
docker compose logs --tail 30 ai-api
```

`healthy`는 API 서버가 응답하고 있다는 뜻이다.
날씨 결과까지 준비됐는지는 다음 단계의 `/health`에서 확인한다.

## 6. 실제 예측값 조회

먼저 PowerShell에서 결과 준비 상태를 확인한다.

```powershell
Invoke-RestMethod http://localhost:18080/health
```

`status`가 `ready`이면 현재 날짜에 필요한 결과 파일을 읽을 수 있는 상태다.
그다음 브라우저에서 아래 주소를 연다.

[API 테스트 화면 열기](http://localhost:18080/docs)

1. PowerShell에서 `Get-Content .\local-api.key`로 인증키를 확인한다.
2. API 화면의 **Authorize**를 누르고 키를 입력한다.
3. **GET /v1/forecasts → Try it out**을 누른다.
4. `latitude`, `longitude`는 비우고 `station_id`에 `400`을 입력한다.
5. **Execute**를 누른다.
6. **Server response**의 코드가 `200`이고 실제 기온이 나오는지 확인한다.

좌표로 조회할 때는 `latitude`, `longitude` 두 값만 입력하고 `station_id`는 비운다.
400번 관측소의 좌표는 위도 `37.4982`, 경도 `127.0816`이다.

조회 결과는 오늘·내일·모레 **오전 9시(KST)**의 예측값이다.
오전 9시가 지난 뒤 조회한 오늘 값도 그날 오전 9시를 대상으로 만든 예측이다.
화면 아래 `Example Value`의 `string`, `0` 등은 응답 형식 예시이므로 실제 결과는 **Server response → Response body**에서 확인한다.

Spring이 같은 컴퓨터에서 실행된다면 AI 서버 주소를 `http://localhost:18080`으로 설정한다.
Spring에서 보내는 `X-API-Key`도 위에서 사용한 키와 같아야 한다.
현재 설정은 같은 컴퓨터에서 접속하는 용도이며, 다른 컴퓨터에서 접근하려면 연결 설정을 별도로 변경해야 한다.

## 7. 종료하고 로컬 실행으로 돌아가기

확인이 끝나면 아래 명령으로 Docker 서비스를 종료한다.

```powershell
docker compose --profile gpu down
```

연결했던 컴퓨터의 예측 파일과 인증키는 그대로 남는다.
평소에는 기존에 로컬 환경을 준비해 둔 `ai-service` 폴더에서 기존 명령을 사용하면 된다.

```powershell
# 첫 번째 PowerShell: 로컬 API 서버
.\.venv\Scripts\python.exe start_local.py
```

```powershell
# 두 번째 PowerShell: 로컬 GPU 예측 갱신
.\.venv\Scripts\python.exe start_auto_update.py
```

로컬 API의 기본 접속 주소는 `http://localhost:8000/docs`다.
로컬 프로그램은 그 프로젝트의 `data` 폴더를 사용한다.
Docker에서 다른 폴더를 연결했다면, 로컬에서도 해당 결과를 관리하던 원래 프로젝트를 실행하면 된다.

## 8. 실행 중 문제가 생겼을 때

| 증상 | 먼저 확인할 내용 |
| --- | --- |
| Docker 엔진에 연결할 수 없음 | Docker Desktop이 실행 중인지, `docker version`에 Server 정보가 나오는지 확인 |
| `PANGU_API_KEY`가 없다는 오류 | 현재 PowerShell 창에서 3번의 인증키 설정을 했는지 확인 |
| `401` | Authorize에 입력한 키와 컨테이너에 설정한 키가 같은지 확인 |
| `503`, `No published forecast files` | 연결한 data 폴더 안에 읽을 수 있는 `forecasts/예측실행번호/manifest.json`이 있는지 확인 |
| `404`, `TODAY_WINDOW_NOT_AVAILABLE` | 저장된 예측이 오늘·내일·모레를 모두 포함하는지 확인. 오래된 결과라면 새 예측 생성 |
| `422` | 위도·경도와 station_id를 동시에 입력했는지, 숫자 범위가 올바른지 확인 |
| 포트가 사용 중이라는 오류 | 다른 포트로 `PANGU_API_PORT`를 설정한 뒤 `docker compose up -d ai-api` 실행 |
| `/v1/update-status`가 `not_started` | 연결한 data 폴더에 갱신 상태 기록이 없음. 이 값과 별도로 `/health`에서 예측 파일 준비 상태 확인 |

실제로 어떤 폴더가 연결되었는지 확인하려면 다음 명령을 사용한다.

```powershell
docker inspect (docker compose ps -q ai-api) --format '{{json .Mounts}}'
docker compose exec ai-api ls -laR /app/data/forecasts
```

`Source`가 컴퓨터의 data 경로이고 `Destination`이 컨테이너의 `/app/data` 경로다.
`Permission denied`가 나오면 해당 결과 폴더를 읽을 권한이 없는 것이다.
이 경우 경로를 계속 바꾸거나 예측 파일을 삭제하기보다, 오류에 나온 폴더의 Windows 읽기 권한을 먼저 확인한다.

키·포트·결과 경로를 변경한 뒤에는 `docker compose up -d ai-api`로 설정을 반영한다.
실행 중인 컨테이너의 설정은 `restart`만으로 바뀌지 않는다.

## 9. 선택 사항: GPU 예측도 Docker에서 실행

이 부분은 API 서버 실행과 별도다.
실제 모델을 계산하므로 NVIDIA GPU와 충분한 메모리가 필요하다.
Windows Docker Desktop에서는 WSL 2 기반의 GPU 사용 환경을 준비해야 한다.
설치 조건은 [Docker 공식 GPU 안내](https://docs.docker.com/desktop/features/gpu/)에서 확인할 수 있다.

기존 모델이 있다면 `ai-service/models/pangu_weather_24.onnx`에 준비하거나,
`PANGU_HOST_MODELS_DIR`에 모델이 들어 있는 폴더를 지정한다.
모델을 처음 받는 경우에는 다음 명령을 사용한다. GPU 실행 환경이 먼저 준비되어 있어야 한다.

```powershell
docker compose --profile gpu run --rm --build ai-updater python -m pangu_service.download_model
```

모델 준비가 끝나면 API와 GPU 자동 갱신기를 함께 실행한다.

```powershell
docker compose --profile gpu up -d --build
docker compose logs --tail 40 ai-updater
```

`ai-updater`가 새 기상자료를 확인하고 GPU로 예측한 뒤 결과를 저장한다.
`ai-api`는 같은 결과 폴더를 읽는다. Docker 안의 API는 결과 폴더를 읽기 전용으로 연결한다.
같은 결과 폴더를 사용하는 **로컬 갱신기와 Docker 갱신기 중 하나만 실행**한다.

GPU를 Docker에서 사용하는 설정을 넣었다고 해서 모델의 메모리 사용량이 줄어들지는 않는다.
API 실행 확인과 GPU 모델 추론 성공은 각각 확인해야 한다.

## 참고 파일

- [Dockerfile](Dockerfile): 이미지 구성
- [compose.yaml](compose.yaml): 실행 설정
- [기존 로컬 GPU 실행 안내](README.md)
- [CPU 실행 안내](CPU_RUN_GUIDE.md)
