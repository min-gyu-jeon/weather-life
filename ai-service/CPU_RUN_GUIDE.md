> 이 문서는 CPU 수동 실행 안내입니다. GPU 자동 갱신과 매일 실행할 명령어는 [README.md](README.md)를 참고하세요.

# Pangu CPU 실행 및 FastAPI 사용 방법

팀원이 Windows 컴퓨터에서 이 프로젝트를 받아 직접 기상자료를 다운로드하고,
Pangu로 예측한 뒤 FastAPI에서 조회하는 순서입니다. 코랩과 DB는 사용하지 않습니다.

```text
기상자료 다운로드 → CPU에서 Pangu 예측 → 결과 파일 저장 → FastAPI → Spring
```

## 1. 준비

- Windows 10/11, 64비트 Python 3.11, 인터넷 연결이 필요합니다.
- 프로젝트 폴더 전체를 전달받으세요. 폴더 경로는 각자 달라도 됩니다.
- 모델 다운로드 크기는 약 1.1GB이며, 입력·출력·패키지를 위한 디스크 여유도 필요합니다.
- CPU만으로 실행할 수 있지만, 실제 예측 성공 여부와 시간은 컴퓨터 사양에 따라 다릅니다.
  이 프로젝트에서 4GiB 제한으로 전체 Pangu 예측에 실패한 사례가 있습니다.
  함수로 감싸거나 API를 켜는 것만으로 모델 계산에 필요한 메모리가 줄어들지는 않습니다.

PowerShell에서 전달받은 프로젝트의 `ai-service` 폴더로 이동합니다.
예를 들어 프로젝트 최상위 폴더에서 열었다면:

```powershell
cd .\ai-service
```

이후 명령어는 모두 `ai-service` 폴더에서 실행하세요.

## 2. 최초 설치

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-cpu.txt
```

다른 컴퓨터의 `.venv` 폴더는 복사하지 말고 각자 새로 만드세요.
가상환경 활성화는 하지 않아도 됩니다. 위처럼 파이썬 경로를 직접 지정합니다.

## 3. Pangu 모델 다운로드 — 최초 한 번

```powershell
.\.venv\Scripts\python.exe -m pangu_service.download_model
```

`models/pangu_weather_24.onnx`가 생성됩니다. 이미 존재하면 다시 받지 않습니다.
다운로드 서비스 제한 등으로 실패하면 [공식 저장소의 24시간 모델 링크](https://github.com/198808xc/Pangu-Weather#downloading-trained-models)로 받아 같은 경로에 놓으세요.
공식 모델 가중치는 CC BY-NC-SA 4.0 조건이므로 사용 조건을 확인하세요.

## 4. 입력 기상자료 다운로드

```powershell
.\.venv\Scripts\python.exe -m pangu_service.pipeline fetch --source ecmwf --data-dir data
```

오늘 09시를 양의 리드타임 예측에 포함하기 위해, 한국 날짜 기준 어제 또는 그 이전의
사용 가능한 00 UTC 초기장을 선택합니다. 오늘 날짜의 최신 초기장과는 다를 수 있습니다.
실제 선택된 시각은 실행 로그와 `data/inputs/.../metadata.json`에서 확인합니다.

## 5. 메모리 제한을 적용해 CPU 예측 실행

```powershell
.\.venv\Scripts\python.exe run_cpu_limited.py --max-memory-gb 4 --timeout-seconds 120 --days 4
```

- Windows Job Object로 예측 작업 전체의 커밋 메모리를 최대 4GiB로 제한합니다.
  이 값은 컴퓨터 전체 RAM 사용량이 아닙니다.
- 시작 시 여유 물리 메모리와 커밋 여유가 각각 제한값 + 2GiB 이상이어야 합니다.
- 실행 중 시스템 여유가 부족해지거나 120초가 지나면 작업을 중단합니다.
- 이 설정은 실행 가능성을 확인하는 짧은 시도입니다. 120초 안에 전체 CPU 예측이 끝난다는 뜻은 아닙니다.
- 시간만 부족하고 메모리가 충분하다고 확인한 경우, 같은 메모리 제한을 유지하며
  `--timeout-seconds 1800`처럼 시간만 늘릴 수 있습니다. 완료는 보장되지 않습니다.
- 4GiB보다 높은 제한값은 거부하며, 제한 설정 실패 시 무제한 실행으로 넘어가지 않습니다.
- 보호 장치가 시스템의 멈춤을 완전히 방지한다고 보장하지는 않습니다.

다음과 같은 **두 조건을 함께** 확인해야 예측 성공입니다.

1. 로그에 `Published run ...`이 있고 마지막에 `Worker finished: exited; exit=0`이 표시됨.
2. `data/forecasts/<run_id>/`에 `manifest.json`과 예측 표면 파일이 저장됨.

`bad allocation`, `timeout`, `low_system_headroom`, `exit=1`은 예측 성공이 아닙니다.
새 결과를 대신하는 임의 데이터는 생성하지 않습니다. 예전 결과가 있더라도 새 예측 성공으로 해석하지 마세요.
메모리 부족이면 같은 명령을 반복하거나 제한을 해제하지 말고, 충분한 메모리의 컴퓨터에서 실행하세요.

`--days 4`는 24시간 모델을 네 번 순차 실행한다는 의미입니다.
API는 그중 한국 시간 오늘·내일·모레의 오전 9시 예측 세 개를 반환합니다.
날짜가 바뀌면 저장된 예측이 세 날짜를 계속 포함하는지 확인해야 합니다.

예측 갱신 시에는 **4번 자료 다운로드 → 5번 예측**을 다시 실행합니다.
이 CPU 수동 실행 경로에는 자동 갱신 스케줄이 없으며, API 호출 자체가 모델을 실행하거나 자료를 갱신하지 않습니다.

> `pipeline predict --device cpu`를 직접 실행하면 이 복사본에서는 메모리 보호를 우회하게 됩니다.
> CPU 예측에는 위의 `run_cpu_limited.py` 또는 `python -m pangu_service.guarded_run`을 사용하세요.

## 6. FastAPI 실행

예측이 성공한 뒤 실행합니다.

```powershell
.\.venv\Scripts\python.exe start_local.py
```

서버 창을 열어 둔 상태에서 브라우저로 <http://127.0.0.1:8000/docs>에 접속합니다.
다른 PowerShell 창을 `ai-service`에서 열고 인증키를 확인합니다.

```powershell
Get-Content .\local-api.key
```

Swagger 화면의 **Authorize**에 키 값만 입력합니다. 키는 컴퓨터마다 자동 생성됩니다.
인증키를 공유 문서나 공개 저장소에 올리지 마세요.

| 경로 | 확인할 내용 |
| --- | --- |
| `GET /v1/stations` | 관측소 번호·위도·경도. 예측이 없어도 조회 가능 |
| `GET /v1/availability` | 저장된 예측과 오늘부터 3일의 제공 가능 여부 |
| `GET /v1/forecasts` | 위도·경도 또는 관측소 번호로 3일 예측 조회 |
| `GET /health` | 오늘부터 3일의 결과 파일 준비 상태. 인증 불필요 |

예측 조회에서는 `latitude=37.5665`, `longitude=126.9780`을 함께 입력하거나,
관측소 목록에 있는 `station_id`만 입력합니다. 두 방식을 섞지 않습니다.
응답 값은 09:00 KST의 기온(℃), 풍속(m/s), 풍향(바람이 불어오는 방향, 도),
해면기압(hPa)입니다. 하루 평균·최고·최저 기온이나 현재 관측값이 아닙니다.
무풍일 때 풍향은 `null`일 수 있습니다.

예측 파일이 없으면 예측 API는 503을, 오늘부터 세 날짜를 포함하는 실행 결과가 없으면
예측 API는 404를 반환할 수 있습니다. `/health`는 준비되지 않은 경우 503입니다.
이 상태에서도 `/docs`가 열릴 수 있습니다.

종료는 서버 창에서 `Ctrl+C`입니다.

## 7. Spring에서 호출

Spring과 FastAPI를 **같은 컴퓨터**에서 실행하면 기본 주소는 `http://127.0.0.1:8000`입니다.
요청에 `X-API-Key` 헤더로 이 컴퓨터의 `local-api.key` 값을 보냅니다.

```http
GET /v1/forecasts?latitude=37.5665&longitude=126.9780
X-API-Key: <local-api.key의 값>
```

서로 다른 컴퓨터라면 `127.0.0.1`은 각자 자기 컴퓨터를 가리키므로 그대로 연결되지 않습니다.
현재 시작 파일은 같은 컴퓨터에서 사용하는 설정입니다.

## 전달할 파일과 각자 생성할 파일

- 전달: 이 프로젝트의 소스, README, `requirements-*.txt`, `stations.csv`, `run_cpu_limited.py`, `pangu_service/guarded_run.py`.
- 각자 생성/다운로드: `.venv`, `models`, `data`, `local-api.key`.
- DB는 필요하지 않습니다. API 요청은 저장된 예측 파일만 읽으며 ONNX 모델을 불러오지 않습니다.
- 파일을 추가했다고 실제 예측 성공이 검증되는 것은 아닙니다. 팀원 컴퓨터에서 5번의 성공 조건을 확인하세요.

