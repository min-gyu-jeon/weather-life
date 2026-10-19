# Pangu GPU 자동 갱신 및 API 실행 안내

Windows 컴퓨터에서 **ECMWF 기상자료 확인 → GPU 예측 → API 결과 갱신**을 자동으로 처리합니다. 코랩과 DB는 사용하지 않습니다.

## 컴퓨터를 켰을 때 — 매번 할 일

**PowerShell 창 두 개를 열어 아래 명령어를 각각 실행하세요.** 최초 설치를 하지 않았다면 아래의 ‘처음 한 번만 준비’부터 진행합니다.

### 첫 번째 창: API 서버 실행

```powershell
cd "D:\mingyu\workspace\teamwork\weather-life\ai-service"
.\.venv\Scripts\python.exe start_local.py
```

이 창을 켜 두세요. `Uvicorn running on http://127.0.0.1:8000`이 표시되면 API 서버가 실행 중입니다.

이 명령어는 **저장된 예측을 전달하는 서버**만 켭니다. 새 예측을 만들려면 두 번째 창도 실행해야 합니다.

### 두 번째 창: 자동 GPU 예측 갱신 시작

```powershell
cd "D:\mingyu\workspace\teamwork\weather-life\ai-service"
.\.venv\Scripts\python.exe start_auto_update.py
```

이 창도 켜 두세요. 실행 직후 새 예측이 필요한지 확인하고, 이후에는 기본 **10분 간격**으로 확인합니다.

- 사용할 기준일의 예측이 이미 성공해 저장돼 있으면 GPU로 다시 계산하지 않습니다.
- 새로운 기준일의 자료가 필요하면 다운로드하고 GPU로 예측합니다.
- 성공하면 새 결과가 저장되고, 이후 API 요청부터 새 결과를 사용합니다. API 재시작은 필요 없습니다.
- 실패하면 기존 결과 파일을 유지하고 10분 후 재시도합니다. GPU를 사용할 수 없다고 CPU로 자동 전환하지 않습니다.
- 예측 실행 중에는 다른 예측을 겹쳐 실행하지 않습니다. 완료 후 즉시 기준일을 다시 확인하므로, 예측 도중 한국 날짜가 바뀌어도 다음 기준일을 확인합니다.

**다른 컴퓨터에서는 `cd` 경로를 자신이 프로젝트를 저장한 경로로 바꾸세요.** 모델, 자료, 인증키는 해당 프로젝트의 `ai-service` 안에서 관리됩니다.

### API 인증키는 그대로 사용

`start_local.py`는 기존 `local-api.key`가 있으면 그대로 사용합니다. 재부팅하거나 예측을 갱신해도 백엔드에 입력한 `X-API-Key`를 바꿀 필요가 없습니다.

## 중요: 이 프로젝트가 선택한 갱신 방식

**오늘·내일·모레 모두 오전 9시의 예측이며, 세 날짜에 같은 초기 기상자료를 사용합니다.** 이 조건을 유지하기 위해, 한국 날짜 기준 어제 또는 그 이전의 사용 가능한 **00 UTC 초기장**을 선택합니다.

예를 들어:

| 컴퓨터를 사용하는 한국 날짜 | 정상적으로 자료가 공개돼 있을 때 선택하는 기준 자료 |
| --- | --- |
| 10월 16일 | 10월 15일 00 UTC 자료 |
| 10월 17일 | 10월 16일 00 UTC 자료 |

따라서 **새 기준일마다 통상 하루 한 번** 예측합니다. 같은 자료를 사용한 성공 결과가 있어도 모델 파일이 바뀌거나 결과 파일이 손상되면 재계산할 수 있습니다.

ECMWF가 하루에 여러 번 자료를 공개하더라도, 모든 06·12·18 UTC 자료로 다시 예측하는 방식은 아닙니다. 프로그램은 해당 정책에서 사용할 수 있는 가장 새로운 자료를 확인합니다. 새 자료의 공개 시각과 이 프로그램이 기준일을 바꾸는 시각은 다릅니다.

‘오늘 오전 9시’가 이미 지났다면 그 값은 과거 시각에 대한 저장된 예측이며, 현재 관측값이 아닙니다. API의 `is_past_valid_time`으로 구분합니다.

## 처음 한 번만 준비

### 1. 필요한 환경

- Windows 10/11
- 64비트 Python 3.11
- CUDA를 지원하는 NVIDIA 그래픽카드와 호환 드라이버
- 모델을 실행할 충분한 GPU 메모리와 시스템 RAM, 디스크 여유

현재 코드는 NVIDIA CUDA GPU용입니다. AMD·Intel 그래픽카드를 같은 명령어로 사용할 수는 없습니다.

PowerShell에서 확인합니다.

```powershell
nvidia-smi
```

그래픽카드 이름과 메모리가 표시되는지 확인하세요. 이것만으로 Pangu 전체 예측 성공이 보장되지는 않습니다.

### 2. 가상환경 생성

```powershell
cd "D:\mingyu\workspace\teamwork\weather-life\ai-service"
py -3.11 -m venv .venv
```

이미 `.venv`가 있다면 다시 만들지 않아도 됩니다. 다른 컴퓨터의 가상환경은 복사하지 말고 각 컴퓨터에서 만드세요.

### 3. GPU 패키지 설치

예측과 API 서버를 종료한 상태에서 진행합니다.

```powershell
.\.venv\Scripts\python.exe -m pip uninstall -y onnxruntime onnxruntime-gpu
.\.venv\Scripts\python.exe -m pip install -r requirements-api.txt -r requirements-pipeline.txt -r requirements-gpu-cuda12.txt
```

이미 같은 가상환경에서 GPU 예측이 정상 실행됐다면 재설치하지 않아도 됩니다. GPU 환경에 CPU용 `requirements-cpu.txt`를 추가 설치하지 마세요.

프로젝트의 GPU 패키지 설정은 CUDA 12 계열·cuDNN 9용입니다. 호환성은 [ONNX Runtime 공식 안내](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html)를 확인하세요.

### 4. Pangu 24시간 모델 다운로드

```powershell
.\.venv\Scripts\python.exe -m pangu_service.download_model
```

`models/pangu_weather_24.onnx`가 이미 있으면 건너뜁니다. 모델은 약 1.1GB이며 매일 다시 다운로드하지 않습니다. 6시간 모델은 이 방식에 필요하지 않습니다.

최초 준비가 끝나면 문서 맨 위의 두 창 실행 순서대로 진행하세요. 기상자료 다운로드는 자동 갱신 프로그램이 처리하므로 매일 `fetch`나 `update`를 따로 입력할 필요가 없습니다.

## 정상 동작 확인

### 1. API 화면 열기

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

별도 PowerShell을 같은 `ai-service` 폴더에서 열어 인증키를 확인합니다.

```powershell
Get-Content .\local-api.key
```

화면의 **Authorize**에 키 값만 입력하세요. 이 키 파일은 API 서버 시작 시 자동 생성되며 공개 저장소에 올리지 않습니다.

### 2. 자동 갱신 상태 확인

`GET /v1/update-status`를 펼치고 **Try it out → Execute**를 누릅니다.

| `state` 값 | 의미 |
| --- | --- |
| `not_started` | 상태 파일이 없음. 두 번째 창에서 자동 갱신기를 실행하세요 |
| `starting` / `checking` | 시작 중이거나 새 기준 자료를 확인 중 |
| `running` | 자료 다운로드 또는 GPU 예측 중 |
| `waiting` | 다음 확인을 기다리는 중 |
| `error` | 실패 후 재시도 대기. `last_error`와 로그 확인 |
| `stopped` | 자동 갱신 프로그램이 정상 종료됨 |

`status_is_stale: true`면 상태가 오랫동안 갱신되지 않은 것이므로 두 번째 창이 살아 있는지 확인합니다. 갑자기 컴퓨터가 꺼진 경우 마지막 상태 파일만 남아 있을 수 있습니다.

`eligible_initialization_utc`는 이번에 사용할 기준 시각, `last_success_init_utc`는 확인한 마지막 성공 예측의 기준 시각입니다. 새 예측을 만들지 않고 기존 성공 결과를 재사용하는 경우에도 마지막 성공 시각을 확인할 수 있습니다.

### 3. 예측 조회

`GET /v1/availability`에서 `today_window_available: true`인지 확인합니다.

`GET /v1/forecasts`에서 다음 값을 입력하고 실행합니다.

| 입력란 | 값 |
| --- | --- |
| `latitude` | `37.5665` |
| `longitude` | `126.9780` |
| `station_id` | 비워 두기 |

관측소 번호로 조회하려면 `/v1/stations`에서 번호를 확인하고 `station_id`만 입력하세요. 좌표와 관측소 번호를 함께 입력하지 않습니다.

응답은 오늘·내일·모레 **오전 9시 시점**의 기온(℃), 풍속(m/s), 풍향(바람이 불어오는 방향, 도), 해면기압(hPa)입니다. 하루 평균·최고·최저 기온은 아닙니다.

`forecast_init_utc`는 예측에 사용한 기상자료 기준 시각이고 `published_at_utc`는 결과를 저장한 시각입니다. 예측 기준 시각은 자동 갱신 프로그램이 작동하는 동안 같은 날 그대로일 수 있습니다.

## 기존 결과를 보호하는 방식

예측이 모두 성공한 경우에만 새 결과 폴더를 공개합니다. 다운로드나 GPU 실행이 실패하면 기존 예측 결과를 삭제하지 않습니다. 모델은 별도 작업으로 실행되므로 API가 모델을 직접 불러오지 않습니다.

기존 예측이 오늘부터 3일을 포함하는 동안은 계속 조회할 수 있습니다. 실패가 오래 지속돼 날짜 범위를 벗어나면 API는 404 또는 준비 안 됨 상태를 알립니다. 파일이 없거나 손상된 경우에는 503일 수 있습니다. 과거 결과를 오늘 예측인 것처럼 날짜만 바꿔 반환하지 않습니다.

자동 갱신기를 두 번 실행하면 두 번째 실행은 거부됩니다. 수동 `fetch`/`predict`/`update` 명령도 같은 자료 폴더의 작업 잠금을 사용하므로 동시에 자료를 바꾸거나 GPU 예측을 겹쳐 실행하지 않습니다. 이 잠금은 현재 프로그램의 CLI 경로에 적용됩니다.

## 오류 확인

갱신 프로그램 로그:

```powershell
Get-Content .\data\auto_update.log -Tail 40
```

기상자료 다운로드 및 GPU 예측 상세 로그:

```powershell
Get-Content .\data\gpu_worker.log -Tail 60
```

- `CUDAExecutionProvider unavailable` / DLL 오류: GPU 패키지·드라이버·CUDA·cuDNN 호환성을 확인합니다.
- `bad allocation` / GPU 메모리 부족: GPU 메모리와 시스템 RAM을 확인합니다. 임의의 성공 결과는 생성되지 않습니다.
- 모델 없음: 최초 준비의 모델 다운로드를 진행합니다.
- 다른 작업 실행 중: 다른 자동 갱신기나 수동 예측이 실행 중인지 확인합니다. 잠금 파일을 삭제해서 우회하지 마세요.
- 최초 실행 중 `/health`나 예측 API의 503: 아직 성공한 예측 파일이 없을 수 있습니다. GPU 작업 완료 여부를 확인하세요.

기본 GPU 작업 제한 시간은 **2시간**입니다. 다운로드와 예측에 합쳐서 2시간이 넘으면 해당 작업만 종료하고 재시도합니다. CPU 실행기의 4GiB 메모리 제한은 GPU 작업에는 적용되지 않습니다.

## 종료와 재부팅

- 각 PowerShell 창에서 `Ctrl+C`를 눌러 종료합니다.
- 자동 갱신기를 종료하면 자신이 실행 중이던 예측 작업도 종료합니다.
- 컴퓨터가 꺼지거나 절전 상태면 API와 자동 갱신이 작동하지 않습니다.
- 다시 켰을 때 문서 맨 위의 두 명령어를 실행하면 됩니다. 부팅 시 자동 실행 등록은 하지 않았습니다.
- 기존 인증키와 완성된 예측 파일은 유지됩니다. 같은 자료로 이미 성공했다면 불필요하게 다시 예측하지 않습니다.

## 선택 옵션

기본값 그대로 시작하는 명령어:

```powershell
.\.venv\Scripts\python.exe start_auto_update.py
```

5분마다 확인하고, GPU 작업 제한 시간을 3시간으로 설정하려면:

```powershell
.\.venv\Scripts\python.exe start_auto_update.py --check-interval-seconds 300 --worker-timeout-seconds 10800
```

확인 주기를 짧게 해도 하루 중 모든 ECMWF 자료를 사용하는 정책으로 바뀌지는 않습니다.

한 번만 확인하고, 필요하면 예측한 뒤 종료하려면:

```powershell
.\.venv\Scripts\python.exe start_auto_update.py --once
```

Spring과 FastAPI가 같은 컴퓨터에 있으면 `http://127.0.0.1:8000`으로 연결합니다. 서로 다른 컴퓨터라면 현재의 로컬 전용 바인딩과 백엔드 주소를 별도로 설정해야 합니다.

CPU 실행 방법은 [기존 CPU 안내](CPU_RUN_GUIDE.md)를 참고하세요. GPU 자동 갱신과 CPU 수동 예측을 동시에 실행하지 마세요.

## 검증 범위

자동 확인·중복 방지·실패 후 재시도·기존 파일 유지·API에서 새 결과 읽기·작업 잠금·시간 초과 종료는 가상 입력과 작은 작업으로 테스트합니다. 이 변경 작업에서 실제 Pangu GPU 추론이나 기상자료 다운로드를 실행한 것은 아닙니다. 실제 GPU 예측 성공은 사용 컴퓨터에서 로그와 API 준비 상태로 확인해야 합니다.
