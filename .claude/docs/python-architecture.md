# Python Architecture

`franchise_manager/api/` 레이어 구조 + 의존 방향 + 반복 패턴.

목적: "동작을 어디에 둘지 / 새 파일을 만들지" 같은 판단을 매번 새로 하지 않도록 기준 고정.

---

## 레이어

```
endpoint        ← HTTP 진입 (FastAPI route handlers)
usecase         ← 비즈니스 흐름 (deps + input → output)
domain          ← 비즈니스 모델 (Entity / ValueObject / Repository wiring)
infrastructure  ← 외부 시스템 어댑터 (HTTP 클라이언트 / DB / 캐시 + repository 일반화)
core            ← 베이스 추상 (Entity / ValueObject / UseCase / Repository / Base / typecheck)
```

## 의존 방향

- ✅ **위에서 아래로만** import (endpoint → usecase → domain → infrastructure)
- ✅ 모든 레이어 → `core` OK
- ✅ 같은 레이어 형제 모듈 import OK
- ❌ 역방향 (infrastructure → domain, domain → usecase 등) 금지

**예외 — 의도적 완화** (DDD purity vs. 코드 양 트레이드오프):
- `domain/{aggregate}/{aggregate}_repository.py`에 SQLAlchemy `Model` 동거
- domain → `infrastructure/postgresql/repository` import 허용 (`PostgresRepository` 상속)
- 사유: KV repo 한 도메인 때문에 별도 infrastructure 파일 만들 가치 없음

---

## 각 레이어 책임

### core/
ABC + 데이터클래스 베이스, 데코레이터.

| 파일 | 내용 |
|------|------|
| `entity.py` | Entity 베이스 (`id: UUID` + `by_factory` 가드) |
| `value_object.py` | ValueObject 베이스 (`by_factory` 가드) |
| `usecase.py` | UseCase 베이스 |
| `repository.py` | Generic abstract `Repository[T]` (add / get_by_id / update / remove_by_id) |
| `model.py` | SQLAlchemy `Base` |
| `validate.py` | `@typecheck` 데코레이터 |

**`by_factory` 가드 설명:**
- `Entity(id=..., by_factory=False)` ❌ 직접 생성 불가능
- `Entity.new(...)` ✓ 팩토리 메서드만 허용
- 목적: DDD Entity 생성 규칙 강제 (검증 + 불변성 보장)

거의 변화 없음. 외부 라이브러리는 SQLAlchemy `Base` 정도만.

### domain/{aggregate}/
비즈니스 모델 + 도메인-specific 데이터.

| 파일 | 내용 |
|------|------|
| `{value}.py` | ValueObject (`Key`, `Value`, `Name` 등) — frozen dataclass + factory |
| `{aggregate}.py` | Entity (`Setting`, `Brand` 등) — frozen dataclass + `new` 팩토리 + `to_dict` / `to_model` |
| `{aggregate}_repository.py` | SQLAlchemy `Model` + concrete `Repository` (**wiring만, 메서드 본문 0개가 목표**) |

**원칙**:
- Entity/VO는 frozen dataclass + factory 강제 (`by_factory`)
- Repository는 `PostgresRepository[Entity, Model]` 상속 + class variables 정의
- 도메인-specific 동작이 부모에 일반화되어 있으면 wiring만으로 사용
- 일반화 안 된 도메인 동작만 domain repository에 직접 구현

**구현 패턴**: [python-style.md](./python-style.md) "DDD 도메인" 섹션 참고

### infrastructure/{system}/
외부 시스템 어댑터. **동작 일반화의 책임처**.

| 파일 | 내용 |
|------|------|
| `client.py` | 외부 API 호출 클래스 + 모듈 레벨 싱글톤 (`cafe24 = Cafe24(...)`) |
| `cache.py` | in-memory 캐시 클래스 + 싱글톤 |
| `postgresql/repository.py` | Generic concrete `PostgresRepository[T, M]` — CRUD + KV 일반 동작 |
| `postgresql/session.py` | 트랜잭션 헬퍼 |

**원칙**:
- 도메인이 wiring만 하도록 충분히 유연한 부모 클래스 설계 책임이 여기 있음
- 싱글톤은 직접 모듈 변수 (factory 함수 wrapper X) — [python-style.md](./python-style.md) "Infrastructure 싱글톤" 참고

### usecase/{aggregate}/
비즈니스 흐름 — deps + input → output.

| 파일 | 내용 |
|------|------|
| `{action}.py` | `Input` pydantic 모델 + `@typecheck async def {action}(...)` 함수 + `# cli` 섹션 |

**원칙**:
- 함수 시그니처: `(*, db, session, input: Input) -> Result`
- repository는 싱글톤 — 모듈 import로 직접 사용 (`from ... import setting_repository`)
- 모든 repo 호출에 `session=session`을 명시적으로 주입 (같은 session = atomic transaction)
- 싱글톤(`cafe24`, `oauth_*_cache`, `*_repository` 등)은 모듈 import로 직접 사용
- 도메인 동작은 repository 메서드 호출 — **usecase에 persistence helper(`_upsert` 등) 두지 말 것** (domain repo로 끌어올리기)

### endpoint/
FastAPI route handlers. usecase 호출 + HTTP 응답 변환. 비즈니스 로직 0.

---

## 반복 패턴

### 패턴 1. Repository (싱글톤 + session-per-method)

모든 도메인 repository는 **stateless 싱글톤**. session은 모든 메서드 호출의 `session=` kwarg로 받음.

**구조**: class variables (`model`, `mapper`, `entity`) 정의 + `__init_subclass__` 자동 생성 + 커스텀 메서드는 `_find_by` / `_filter_by` delegation

**판정 기준 — 부모 vs 자식**:
- entity 1개에만 쓰이고 일반화 어려움 → domain repository 메서드로
- 2개 이상 entity에 패턴 반복 → `PostgresRepository`에 끌어올리기 + entity 컨벤션 합의

**상세 구현**: [python-style.md](./python-style.md) "DDD 도메인 / Repository 패턴" 섹션 참고

### 패턴 2. UseCase (함수 + Input)

`usecase/{aggregate}/{action}.py` — Input 모델 + 함수 + CLI

**시그니처**: `async def {action}(*, db, session, input: Input) -> Result`

**원칙**:
- repository는 싱글톤으로 import — 호출 시 `session=session` 명시
- persistence helper는 domain repository 메서드로 끌어올리기

**상세 구현**: [python-style.md](./python-style.md) "UseCase 파일 구조" 섹션 참고

### 패턴 3. Infrastructure 싱글톤

모듈 수준 직접 인스턴스화 — factory 함수 wrapper 금지.

**상세 구현**: [python-style.md](./python-style.md) "Infrastructure 싱글톤" 섹션 참고

### 패턴 4. Session = Transaction 경계 (usecase 1개 = 1 트랜잭션)

Repository는 **stateless 싱글톤**. session은 **모든 호출의 첫 kwarg**. 같은 session을 모든 repo 호출에 주입하면 같은 transaction.

```
transactional_session(SessionLocal)
   │ BEGIN
   ├─ session 생성
   ├─ yield session                                  ← usecase 실행 구간
   │     ├─ setting_repository.set_by_key(session=session, ...)
   │     ├─ brand_repository.add(session=session, ...)
   │     └─ 같은 session 주입한 모든 쿼리 = 같은 transaction
   │ COMMIT (정상) / ROLLBACK (예외)
   │ session close
```

**usecase에서 지킬 contract**:
- `session`을 인자로 받음 — usecase 안에서 새로 만들지 말 것
- 모든 repo 메서드 호출에 **같은 session 주입**:
  ```python
  async def some_usecase(*, db, session, input):
      await setting_repository.set_by_key(session=session, key=..., value=...)
      await brand_repository.add(session=session, entity=brand)
      # → 두 호출 atomic
  ```
- usecase 내부에서 `session.commit()` / `session.begin()` 명시적 호출 금지 — outer `transactional_session`이 관리

**session 생성 위치**:
- FastAPI endpoint: `Depends(transactional_session_helper)`
- CLI `_main`: `async with transactional_session(db_client.SessionLocal) as session:`

**transaction에 포함 안 되는 것** (별도 commit 흐름 따로 고려):
- 외부 HTTP (`cafe24.exchange_code` 등) — 이미 발생한 호출은 rollback 불가. usecase 내 ordering: HTTP → DB 순서로 두면 DB 실패 시 outer state 일관 유지 가능
- in-memory cache (`oauth_token_cache.set` 등) — DB commit 이후 시점이 안전하지만 현재는 commit이 usecase return 후이라 cache가 commit 전 갱신될 여지 있음. admin tool 수준에서는 허용

**왜 session을 메서드 인자로 받는가** (싱글톤 가능하게 하는 핵심):
- repo가 session-바인딩 인스턴스면 매 요청마다 `Repo(session=...)` 생성 필요 → 싱글톤 불가
- session-per-method로 받으면 repo는 stateless → cafe24/cache처럼 모듈 레벨 싱글톤 가능
- 호출 시 `session=` 명시가 noise 같지만 **transaction boundary가 호출부에서 보이는** 이점
- 인프라 싱글톤(cafe24, oauth_*_cache, *_repository) 전체가 동일 형태로 일관성

---

## 의사결정 체크리스트

새 기능 추가 / 기존 동작 이동 시 순서대로 점검:

1. **이 동작은 entity 1개에만 쓰이나?**
   - YES → domain repository 메서드로
   - NO → infrastructure 부모(`PostgresRepository`)로 끌어올리기 + entity 컨벤션(`with_X`, `new(*, key, value)`) 갖추기

2. **이 helper는 usecase 안 흐름 조립인가, 도메인 모델의 동작인가?**
   - 흐름 조립 → usecase 함수 안 인라인 또는 모듈 레벨 `_helper`
   - 도메인 모델 동작 → domain repository / entity 메서드로 끌어올리기

3. **이 싱글톤은 환경별 분기가 필요한가?**
   - YES → factory 함수 (`get_postgres_config()` 같이)
   - NO → 직접 모듈 변수 (`cafe24 = Cafe24(...)`)

4. **이 import는 레이어 방향 맞나?**
   - 위에서 아래만 OK. 의심되면 의존 그래프 그려보기

5. **새 파일을 만들기 전: 기존 파일에 동거 가능한가?**
   - 도메인 repo concrete impl은 `infrastructure/postgresql/{aggregate}_repository.py` 같은 중간 파일 만들지 말고 `domain/{aggregate}/{aggregate}_repository.py`에 동거
   - 싱글톤 여러 개도 한 파일에 (e.g. `cache.py`의 `OAuthStateCache` + `OAuthTokenCache`)

---

## 안티패턴

- ❌ usecase에 `_upsert` 같은 persistence helper → domain repo 공개 메서드(`set_by_key`)로
- ❌ domain repo에 `find_by_X` 직접 SQL (`select(...).where(...)`) → `PostgresRepository._find_by` / `_filter_by`로 delegate
- ❌ domain repo `__init__` 직접 구현 — `__init_subclass__`가 class variables에서 자동 생성
- ❌ domain repo `__init__`에 `session` 받기 — repo는 stateless 싱글톤. session은 메서드 인자
- ❌ usecase에 `repo = SettingRepository(session=session)` 같이 인스턴스화 — 싱글톤 import해서 바로 호출
- ❌ domain repo가 추상(`abstractmethod`) 메서드만 갖고 concrete impl이 별도 파일 — `PostgresRepository` 직접 상속해서 한 파일로
- ❌ `infrastructure/postgresql/{aggregate}_repository.py` 중간 파일 — domain repo가 직접 상속
- ❌ factory 함수 wrapper로 싱글톤 노출 → 직접 모듈 변수
- ❌ Entity에 `.update_value(value)` 같은 mutating 메서드 — frozen이므로 `.with_value(value)` evolve
- ❌ repo 메서드 호출 시 `session=` 빠뜨림 — 모든 호출에 명시 (transaction boundary 가시화)

---

## 참조

- [python-style.md](./python-style.md) — 코드 컨벤션 (네이밍 / 섹션 마커 / CLI / Import 등)
- [system.md](./system.md) — 공통 워크플로우 (MCP 의존성 확인)
