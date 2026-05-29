# Python Code Style

worship-support의 Python 코드 컨벤션. 모든 Python 파일에 적용.

---

## 파일 구조

**모듈 docstring 작성하지 않는다.** 파일명, `# #` 섹션, 최상위 함수가 의도를 드러낸다.

**절차 순서 = 읽기 순서.** 호출자가 위, 피호출자가 아래. 최상위 함수가 파일 맨 위. 타입(`@dataclass` 등)은 그 단계 섹션 안에 동거. 전방 참조용 `from __future__ import annotations` 사용.

**모듈 수준 상수 블록(`MAX_X = ...`)은 피한다.** 별도 `config.py`로 분리 (`ABC` + `@property @abstractmethod` + 환경별 서브클래스 + 팩토리 함수). 단일 파일 lab/script의 `# config` 섹션은 fallback이지 권장 아님.

**CLI 섹션 최대한 간결**:
- `argparse.ArgumentParser()` 빈 생성자 (description은 필요할 때만)
- `_main` = parse → side-effect → delegate
- 단발 입력은 kwarg에 인라인 (중간 변수 X)
- 위임 결과는 직접 `return await ...`
- 섹션 내 순서: `_parse_args` → `_main` → `if __name__`
- **`# cli` 섹션 내부는 함수 사이 빈 줄 1줄** (모듈 기본 2줄의 예외 — CLI 진입부는 시각적으로 한 단락)
- 리소스 셋업(session 등)은 wrapper 함수 분리하지 말고 `_main` 안에 `async with`로 인라인

```python
from __future__ import annotations

import argparse
import asyncio


# #
# orchestrate

async def generate(*, ...) -> list[ScoredSong]:
    # fetch
    metadatas = await fetch_all_metadata(...)
    # score
    scored = [score(...) for m in metadatas]
    # select
    generated = select(scored=scored, size=size)

    return generated


# #
# fetch
# (SongMetadata 타입, fetch 관련 함수들)

# #
# score
# (ScoredSong 타입, score 관련 함수들)

# #
# select
# (select 관련 함수들)

# #
# cli

def _parse_args() -> argparse.Namespace:
    return argparse.ArgumentParser().parse_args()

async def _main():
    _parse_args()
    async with transactional_session(db_client.SessionLocal) as session:
        print(start_oauth(
            db=db_client,
            session=session,
            input=Input.new(),
        ))

if __name__ == "__main__":
    asyncio.run(_main())
```

---

## 섹션 마커

**`# #` 시그니처**로 파일/클래스 내부 논리 영역 구분.

```python
# #
# factory

@classmethod
def new(cls, ...): ...
```

라벨 예:
- 모듈: `# route`, `# run`, `# cli`, `# client`, `# model`, `# repository`, `# orchestrate`, `# fetch`, `# score`, `# select`
- 클래스 내부: `# factory`, `# query`, `# command`, `# create`, `# read`, `# update`, `# delete`

**인라인 라벨(`# label`, 단일 `#`)** 로 메서드 내부 단계 표기.

```python
# type
if not isinstance(value, str):
    raise  # InvalidError

# format
if not re.match(...):
    raise  # InvalidFormatError
```

라벨 예: `# type`, `# format`, `# value`, `# length`, `# hint`, `# cap`, `# normalize`, `# components`, `# weighted sum`, `# fan-out`, `# filter`, `# backoff retry`, `# rank`, `# fallback`.

---

## 네이밍

**식별자에 폴더/파일 컨텍스트를 중복하지 않는다.** 호출부 `from foo.bar import X`에서 경로 `foo.bar`가 이미 컨텍스트를 제공함. `X` 안에 `foo`나 `bar`를 다시 담으면 import 라인이 `bar의 BarX`처럼 stutter.

**폴더 컨텍스트 중복 금지** (폴더명을 접두로 반복하지 않음):

```
infrastructure/cafe24/cache.py
  class Cafe24OAuthStateCache  ❌  →  class OAuthStateCache  ✓
  def cafe24_token_cache()     ❌  →  def token_cache()      ✓

usecase/cafe24/start_oauth.py
  class StartCafe24OAuth       ❌  →  class StartOAuth       ✓
```

**파일 컨텍스트 중복 금지** (파일명을 접미/접두로 반복하지 않음):

```
setlist_generator.py
  def generate_setlist()       ❌  →  def generate()         ✓

domain/user/email.py
  def from_email_str()         ❌  →  def from_str()         ✓
```

**예외 — 파일 안에 동종 다중 식별자가 있어 분별 단어가 필요한 경우**:

```
infrastructure/cafe24/cache.py
  class OAuthStateCache, class OAuthTokenCache    # "Cache" 보존 (둘 다 캐시), "OAuth" 일관 부여

domain/brand/brand_repository.py
  class BrandModel, class BrandRepository         # "Model"/"Repository" 보존
```

이 경우엔 분별 단어(`Cache`, `Model`, `Repository`)는 유지하되 폴더 prefix(`Brand`, `Cafe24`)는 유지/생략 모두 가능. 베이스 ABC가 일반 이름(`Repository`, `Entity`)일 때만 서브에 도메인 prefix 부여로 충돌 회피 (예: `BrandRepository extends Repository`).

| 대상 | 형태 | 예 |
|------|------|-----|
| 클래스 | PascalCase | `User`, `RegisterUser` |
| 함수/메서드/변수 | snake_case | `from_str`, `user_repository` |
| 비공개 (모듈/필드) | `_` 접두 | `_value`, `_fetch_metadata` |
| Config 프로퍼티 | UPPER_CASE | `POSTGRES_USER` |
| 힌트 클래스 필드 | `_` + `# hint` | `_format: str = "%Y-%m-%d"` |

---

## 반환값

**Happy path는 named variable에 담은 뒤 return.** 함수의 정상 출력을 함수 이름을 만족하는 변수에 담고 반환.

```python
metadata = SongMetadata(...)
return metadata
```

**예외**:
- 가드/에러 early return: inline (`return None`, `return 0.0` 등)
- 순수 위임(passthrough): `return await delegate(...)` inline 허용 (CLI 진입점 등)

| 함수 | 변수명 |
|------|--------|
| `fetch_all_metadata` | `metadatas` |
| `_fetch_metadata` | `metadata` |
| `_fetch_with_retry` | `response` |
| `score` | `scored` |
| `_score_freshness` | `freshness` |
| `select` | `selected` |
| `generate` | `generated` |

규칙: intermediate 변수는 **생산 함수** 출력 의미, 최종 return 변수는 **enclosing 함수** 출력 의미.

---

## 호출 스타일

**인자 표기는 all-or-nothing.** 한 호출 안에서 keyword/positional 혼용 금지.

```python
# ✓ 전부 positional
asyncio.wait_for(coro, FETCH_TIMEOUT_SEC)
random.sample(["a", "b", "c"], 2)

# ✓ 전부 keyword
score(metadata=m, target_topics=topics, congregation_low=lo, congregation_high=hi)

# ❌ 혼용
asyncio.wait_for(coro, timeout=FETCH_TIMEOUT_SEC)
random.sample(["a", "b"], k=2)
```

stdlib 강제 혼용 예외:
- `sorted(iterable, /, *, key, reverse)`
- `argparse.add_argument(*name_or_flags, **kwargs)`

**키워드 전용 강제.** 도메인 함수는 `*` 로 모든 인자 키워드 전용화. 다인자 시그니처는 파라미터마다 줄바꿈 + trailing comma.

```python
def new(
    cls,
    *,
    name: Name,
    birth: Birth,
    email: Email,
    password: Password,
) -> "User":
```

---

## DDD 도메인 (worship_support/api/)

**Dataclass + Factory 강제.** 모든 도메인 클래스 `@dataclass(frozen=True, kw_only=True)`. 베이스가 `by_factory` 플래그로 직접 생성 차단.

```python
@dataclass(frozen=True, kw_only=True)
class ValueObject:
    by_factory: InitVar[bool] = False

    def __post_init__(self, by_factory: bool):
        if not by_factory:
            raise  # Error
```

서브클래스는 `cls.new(...)` 또는 `cls.from_str(...)` 팩토리만 사용.

**팩토리 메서드**:
- `@classmethod` + `@typecheck`
- `*` 키워드 전용
- 반환 타입 = forward reference 문자열 (`"User"`)
- ValueObject = `from_str`, Entity/UseCase = `new`

**예외 처리.** 구체 예외 클래스 미구현 시 **bare `raise` + 의도 주석**으로 자리 표시.

```python
raise  # InvalidError
raise  # AlreadyExistsError
```

**Repository 패턴** — class variables 정의 + `__init_subclass__` 자동화:

```python
# (a) 순수 wiring
class BrandRepository(PostgresRepository[Brand, BrandModel]):
    model = BrandModel
    mapper = _to_brand
brand_repository = BrandRepository()  # type: ignore[call-arg]

# (b) 커스텀 finder (1줄 delegation)
class UserRepository(PostgresRepository[User, UserModel]):
    model = UserModel
    mapper = _to_user
    async def find_by_phone(self, *, session, phone: Phone) -> User | None:
        return await self._find_by(session=session, column="phone", value=phone.to_str())
user_repository = UserRepository()  # type: ignore[call-arg]

# (c) KV 패턴 (entity= 와이어)
class SettingRepository(PostgresRepository[Setting, SettingModel]):
    model = SettingModel
    mapper = _to_setting
    entity = Setting
setting_repository = SettingRepository()  # type: ignore[call-arg]
```

**도메인 repo가 가져야 할 것**:
- Class variables: `model` (필수), `mapper` (필수), `entity` (KV 패턴일 때만)
- **`__init__` 직접 구현 금지** — `__init_subclass__`가 자동 생성
- 커스텀 메서드: `(*, session, ...)` 시그니처 + `_find_by` / `_filter_by` delegation
- mapper 함수(`_to_X`)는 모듈 중간
- 모듈 끝: `# ClassName` 섹션 + 싱글톤 (`{name} = {ClassName}()` + `# type: ignore[call-arg]`)

**도메인 repo가 가지면 안 될 것**:
- `__init__` 직접 구현 / `session` 받기 — repo는 stateless
- 직접 SQL → `_find_by` / `_filter_by` 위임
- `_upsert` 등 persistence helper → domain repo 메서드로 끌어올리기

**CRUD 메서드 명명** (부모 `PostgresRepository`에서 제공):
- 생성: `add`, `add_many`
- 조회: `get_by_id`, `get_by_ids`, `exists_by_id`, `find_by_X` (delegation), `filter_by_X`
- 수정: `update`, `update_many`
- 삭제: `remove_by_id`, `remove_by_ids`

**KV 패턴** (set_by_key / set_by_keys 쓰려면):
- entity: `.new(*, key, value)` + `.with_value(value) -> Self`
- model: `key` 컬럼
- repo: `entity = Entity` 와이어

**bulk vs 단건**:
- N=1 → `set_by_key` (단순)
- N≥2 → `set_by_keys(pairs=...)` (1 SELECT IN + add_many + update_many)

**ValueObject 패턴** — 단순 값 (str, int) vs 복합 값 (dict):

```python
# 단순 값 — from_str / to_str
@dataclass(frozen=True, kw_only=True)
class Name(ValueObject):
    _value: str
    @classmethod
    def from_str(cls, value) -> "Name":
        if not isinstance(value, str) or not value.strip():
            raise InvalidFormatError("Name")
        return cls(_value=value, by_factory=True)
    def to_str(self) -> str:
        return self._value

# 복합 값 — from_dict / to_dict
@dataclass(frozen=True, kw_only=True)
class Address(ValueObject):
    _text: str
    _latitude: float
    _longitude: float
    @classmethod
    def from_dict(cls, value) -> "Address":
        if not isinstance(value, dict):
            raise InvalidError("Address")
        text = value.get("text")
        if not isinstance(text, str) or not text.strip():
            raise InvalidFormatError("Address.text")
        latitude = float(value.get("latitude"))
        if not (-90.0 <= latitude <= 90.0):
            raise InvalidFormatError("Address.latitude")
        return cls(_text=text, _latitude=latitude, _longitude=float(value.get("longitude")), by_factory=True)
    def to_dict(self) -> dict:
        return {"text": self._text, "latitude": self._latitude, "longitude": self._longitude}
```

**ValueObject 원칙**:
- **frozen dataclass + kw_only** 강제
- **필드명 `_` 접두** (private)
- **팩토리**: `from_str` (단순) 또는 `from_dict` (복합)
- **변환**: `to_str` 또는 `to_dict`
- **검증 순서**: type (InvalidError) → format (InvalidFormatError) → range/규칙

**Entity 패턴**:

```python
@dataclass(frozen=True, kw_only=True)
class Brand(Entity):
    name: Name
    business_number: BusinessNumber | None = None
    
    @classmethod
    @typecheck
    def new(cls, *, name: Name, business_number: BusinessNumber | None = None) -> "Brand":
        return cls(name=name, business_number=business_number, by_factory=True)
    
    def to_dict(self):
        return {"id": str(self.id), "name": self.name.to_str(), "business_number": self.business_number.to_str() if self.business_number else None}
    
    def to_model(self):
        return {"id": self.id, "name": self.name.to_str(), "business_number": self.business_number.to_str() if self.business_number else None}
```

**Entity 원칙**:
- **Entity 상속 필수** → `by_factory=True` 가드, UUID id 자동
- **팩토리**: `@classmethod @typecheck def new(...)`
- **`to_dict()`**: API 응답용 (id 포함, UUID → str)
- **`to_model()`**: DB 저장용 (mapper가 id 처리)
- **`with_X()`**: immutable evolve (필요시)

**변환 메서드 요약**:

| 방향 | ValueObject | Entity |
|------|-------------|--------|
| 입력 | `from_str` / `from_dict` | `new` |
| 출력 | `to_str` / `to_dict` | `to_dict`, `to_model` |

**Config 클래스**:
- `ABC` + `@property @abstractmethod` 인터페이스
- 프로퍼티명 = 환경변수 키와 동일한 UPPER_CASE
- 환경별 서브클래스 (`TestPostgresConfig` / `DevPostgresConfig` / `ProdPostgresConfig`)
- 모듈 수준 팩토리 함수 (`get_postgres_config()`) — Dev/Test/Prod 분기 때문에 factory 정당함

---

## Infrastructure 싱글톤

**모듈 수준 직접 인스턴스화.** factory 함수 wrapper 금지 — 호출 시 `()` 깜빡 버그 제거.

```python
# #
# Cafe24
cafe24 = Cafe24(config=get_cafe24_config())

# 호출
from franchise_manager.api.infrastructure.cafe24.client import cafe24
cafe24.method(...)
```

**섹션 마커는 PascalCase 클래스명** — "이 블록은 해당 클래스의 default 인스턴스"임을 표시. 일반 라벨(`# client`, `# cli` 등 lowercase 카테고리)의 예외 케이스.

여러 싱글톤이 같은 파일에 있으면 각각 별도 섹션:

```python
# #
# OAuthStateCache

oauth_state_cache = OAuthStateCache(config=get_cafe24_config())


# #
# OAuthTokenCache

oauth_token_cache = OAuthTokenCache(config=get_cafe24_config())
```

**factory 함수 wrapper는 금지** — 단, 예외:
- 환경별 인스턴스 선택 필요 (Config의 `get_postgres_config()` 같이 Dev/Test/Prod 분기)
- lazy 초기화 비용이 큰 인스턴스

```python
# ❌ 불필요한 wrapper
_cafe24 = Cafe24(...)

def cafe24() -> Cafe24:
    return _cafe24

# 호출: cafe24().method(...)  ← () 빠뜨리면 AttributeError silent
```

적용 예: `db_client`, `cafe24`, `oauth_state_cache`, `oauth_token_cache`, `setting_repository`, `brand_repository`, `user_repository`, `store_repository`.

도메인 repository도 같은 패턴 — `__init__()` 무인자, session은 메서드 인자로. 상세는 [python-architecture.md](./python-architecture.md) "패턴 1. Repository" + "패턴 4. Session = Transaction" 참고.

---

## UseCase 파일 구조

`usecase/{aggregate}/{action}.py` — Input + 함수 + CLI 3섹션.

```python
from __future__ import annotations
import argparse, asyncio
from pydantic import BaseModel
from franchise_manager.api.core.validate import typecheck
from franchise_manager.api.infrastructure.cafe24.client import cafe24
from franchise_manager.api.infrastructure.postgresql.client import db_client
from franchise_manager.api.infrastructure.postgresql.session import transactional_session

# #
# input
class Input(BaseModel):
    code: str

# #
# usecase
@typecheck
async def start_oauth(*, db, session, input: Input) -> Result:
    ...

# #
# cli
def _parse_args():
    return argparse.ArgumentParser().parse_args()
async def _main():
    args = _parse_args()
    async with transactional_session(db_client.SessionLocal) as session:
        print(await start_oauth(db=db_client, session=session, input=Input(code=args.code)))
if __name__ == "__main__":
    asyncio.run(_main())
```

### Input 모델

- **pydantic `BaseModel`** (도메인 ValueObject와 달리 `by_factory` 가드 없음 — Input은 boundary 입력 검증용, 도메인 객체 아님)
- 입력 필드 없어도 **항상 정의**: `class Input(BaseModel): pass`. 호출 시그니처를 일관되게 유지 (`input=Input()`).
- 클래스명은 `Input` 고정 — 파일명(`{action}`)이 컨텍스트 제공 → 폴더/파일 컨텍스트 중복 금지 규칙 따름

### usecase 함수 시그니처

```python
@typecheck
async def {action}(*, db, session, input: Input) -> Result:
```

- `@typecheck` 필수
- **kwarg-only** (`*` 강제) — db/session/input 순서 고정
- `db = db_client` 싱글톤, `session = AsyncSession`, `input = Input 인스턴스` — 함수가 직접 사용 안 해도 자리는 둔다 (CLI 일관 시그니처)
- repository도 싱글톤으로 import — `from ... import setting_repository`. 호출 시 `session=session`을 첫 kwarg로 명시
- 외부 시스템 싱글톤(`cafe24`, `oauth_*_cache`)은 모듈 import로 직접 참조
- sync/async는 IO 유무에 따라 — 순수 in-memory 조작뿐이면 sync 가능 (`start_oauth`는 sync, `complete_oauth`는 async)

### 본문 내 컨벤션

- 단계별 `# label` 인라인 마커: `# state`, `# exchange`, `# persist`, `# cache` 등
- persistence helper(`_upsert` 같은 거) 함수 안에 두지 말 것 — domain repo의 메서드(`set_by_key`)로 끌어올림 → [python-architecture.md](./python-architecture.md) 의사결정 체크리스트 참고

### CLI 섹션

- `_parse_args` — argparse, input 모델 필드와 1:1 매핑되는 `--flag` 추가
- `_main` — **항상 async** (session이 async라서). usecase가 sync여도 `_main`은 async + `async with transactional_session(...)`로 session 열기
- 결과 출력: usecase가 의미 있는 값 반환하면 `print(result)`, `None` 반환이면 생략 가능 (현 lab은 일관성 위해 `print(await ...)` 사용 — `None`이 찍혀도 무방)
- `# cli` 섹션 내부는 함수 사이 빈 줄 1줄 (파일 구조 섹션 참고)

### 실제 예시

- [usecase/cafe24/start_oauth.py](../../franchise_manager/api/usecase/cafe24/start_oauth.py) — 입력 없음 (`Input(BaseModel): pass`) + sync 함수
- [usecase/cafe24/complete_oauth.py](../../franchise_manager/api/usecase/cafe24/complete_oauth.py) — 입력 있음 (`code`, `state`) + async 함수 + 다중 저장소 갱신

---

## Import

순서: 표준 → 서드파티 → 로컬. 그룹마다 한 줄 공백. 로컬은 `from api.xxx` (패키지 루트 `worship_support` 생략). 도메인 클래스는 **한 줄에 하나씩** 별도 import.

```python
import re
from dataclasses import dataclass

from api.core.value_object import ValueObject

from api.domain.user.name import Name
from api.domain.user.birth import Birth
from api.domain.user.email import Email
```

### 라우터/registry — 모듈 namespace import

여러 핸들러를 한 모듈에서 등록할 때는 **`from package import module`** 형태로 import하고 `module.func`로 접근. alias 노이즈 제거 + namespace 의도 명확.

```python
# ✓ 모듈 namespace — 한 모듈에서 N개 함수 등록
from franchise_manager.api.endpoint import cafe24

server.router(Router(path="/auth/cafe24/start",    methods=["GET"], endpoint=cafe24.start))
server.router(Router(path="/auth/cafe24/callback", methods=["GET"], endpoint=cafe24.callback))
```

```python
# ❌ alias 패턴 — endpoint 추가마다 import 늘어남
from franchise_manager.api.endpoint.cafe24 import start as cafe24_start
from franchise_manager.api.endpoint.cafe24 import callback as cafe24_callback
```

**적용 기준**:
- 한 모듈에서 **2개 이상** 함수 import → 모듈 namespace (`from pkg import mod`)
- 한 모듈에서 **1개**만 import → 함수 직접 (`from pkg.mod import func`)

적용 위치 예: FastAPI router 등록 (`bin/server.py`), CLI dispatcher, MCP tool registry 등 "여러 핸들러를 외부 시스템에 등록"하는 파일.

도메인/usecase/repository 호출처에는 적용 안 함 — 그쪽은 도메인 클래스 한 줄당 import 규칙 그대로.

---

## 비동기

- DB 접근 메서드는 `async`
- 트랜잭션은 `@asynccontextmanager` 헬퍼로 래핑
- 추상 비동기 메서드 본문도 `...`

```python
@asynccontextmanager
async def transactional_session(session_factory):
    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
```

---

## 포맷팅

- 들여쓰기 4칸
- import 블록 후 두 줄 공백
- 모듈 함수 사이 두 줄 공백 (`# cli` 섹션 내부는 한 줄 예외 — 파일 구조 섹션 참고)
- 메서드 사이 한 줄 공백
- 긴 함수 시그니처: 파라미터마다 줄바꿈 + trailing comma
- `if __name__ == "__main__":` 는 파일 하단 `# cli` 또는 `# run` 섹션

---

## 주석 언어

- 코드 라벨/섹션 마커: **영어** (`# factory`, `# query`)
- 도메인 의미가 강한 docstring (MCP tool 설명 등): **한국어 허용**

---

## 핵심 철학

> **DDD 레이어 분리 + 팩토리 강제 + 시각적 섹션 마커(`# #`) + 자명한 파일 구조**

코드의 의도가 라벨 주석과 파일 구조로 시각적으로 드러난다. 도메인 객체는 검증된 팩토리로만 생성. 단일 파일은 호출 순서 = 읽기 순서로 배치되어 파일을 열었을 때 1초 안에 의도가 파악되어야 한다.