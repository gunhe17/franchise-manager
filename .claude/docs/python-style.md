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

def _parse_args() -> argparse.Namespace: ...
async def _main(): ...

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

**함수명에 파일 컨텍스트 중복 금지.** `setlist_generator.py`의 함수는 `generate_setlist` ❌ → `generate` ✓.

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

**Repository 패턴**:
- 추상 메서드 본문 = `...` (pass 아님)
- CRUD를 `# create / # read / # update / # delete` 섹션 분리
- 명명:
  - 생성: `add`, `add_many`
  - 조회: `get_by_id`, `get_by_ids`, `exists_by_id`, `find_by_email`, `get_filtered_by_name`
  - 수정: `update`, `update_many`
  - 삭제: `remove_by_id`, `remove_by_ids`

**변환 메서드**:

| 방향 | ValueObject | Entity |
|------|-------------|--------|
| 입력 | `from_str` | `new` |
| 출력 | `to_str` | `to_dict`, `to_model` |

**Config 클래스**:
- `ABC` + `@property @abstractmethod` 인터페이스
- 프로퍼티명 = 환경변수 키와 동일한 UPPER_CASE
- 환경별 서브클래스 (`TestPostgresConfig` / `DevPostgresConfig` / `ProdPostgresConfig`)
- 모듈 수준 팩토리 함수 (`get_postgres_config()`)

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