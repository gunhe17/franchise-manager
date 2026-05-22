# Cafe24 Admin API 참조

향후 구현을 위한 Cafe24 Admin API 명세 노트.

- 공식 문서: https://developers.cafe24.com/docs/api/admin/
- Mall 기준 base URL: `https://{MALL_ID}.cafe24api.com`
- 인증: OAuth 2.0 Bearer token (운영 토큰 발급/갱신은 [`infrastructure/cafe24/client.py`](../franchise_manager/api/infrastructure/cafe24/client.py)의 `Cafe24` 클래스가 담당)
- 응답 샘플: [`cafe24-order-query-response.json`](cafe24-order-query-response.json)

---

## 공통

### 필수 헤더

| 헤더 | 값 | 비고 |
| --- | --- | --- |
| `Authorization` | `Bearer {access_token}` | `Cafe24.get_access_token(session)` 로 획득. 만료 임박 시 내부 자동 갱신 |
| `X-Cafe24-Api-Version` | `2024-09-01` 등 | 미지정 시 앱 등록 시 지정한 버전. 현재 `Cafe24Config.CAFE24_API_VERSION` |
| `Content-Type` | `application/json` | GET 에도 명시 권장 |

### 인증 scope

| Scope | 용도 |
| --- | --- |
| `mall.read_order` | 주문 조회 (현재 사용) |
| `mall.write_order` | 주문 수정·취소 (필요 시 추가) |

### Rate limit

- Leaky Bucket. 한도 약 40 req. 응답 헤더 `X-Api-Call-Limit` 으로 잔량 확인.
- 초과 시 429. 동기화 배치는 sleep + 재시도 또는 호출 빈도 조절 필요.

---

## 1. Retrieve an order — 단건 조회

> 우리가 다음으로 구현할 API.

**GET** `/api/v2/admin/orders/{order_no}`

### Path 파라미터

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `order_no` | string | ✓ | 조회할 주문 번호 |

### Query 파라미터

| 이름 | 타입 | 필수 | 기본 | 설명 |
| --- | --- | --- | --- | --- |
| `shop_no` | int | ✗ | 1 | 멀티숍 번호 |
| `embed` | string | ✗ | — | 함께 받을 sub-resource. CSV (`items,receivers,payments,shipments` 등) |
| `fields` | string | ✗ | 전체 | 응답에 포함할 필드만 지정 (CSV) |

### 응답 (주요 필드)

```jsonc
{
  "order": {
    // 핵심
    "order_no": "20260428-0000013",
    "order_date": "2026-04-28T11:34:10+09:00",
    "order_status": "...",
    "currency": "KRW",

    // 구매자
    "buyer_name": "...",
    "buyer_email": "...",
    "buyer_phone": "...",

    // 금액
    "order_total": "...",
    "payment_amount": "...",
    "shipping_fee": "...",
    // (할인 항목 다수)

    // 결제
    "payment_status": "...",
    "paid": "T",
    "payment_method": ["card"],

    // embed=items
    "items": [ /* 상품/옵션 라인 */ ],
    // embed=receivers
    "receivers": [ /* 수령자/배송지 */ ],
    // embed=payments
    "payments": [ /* 결제 트랜잭션 */ ],
    // embed=shipments
    "shipments": [ /* 배송 트래킹 */ ]
  }
}
```

전체 필드 셋은 [`cafe24-order-query-response.json`](cafe24-order-query-response.json) 참조 (실제 응답 sample — 단건이 아닌 목록이지만 단건 row 와 구조 동일).

### 구현 시 메모

- `embed` 빠뜨리면 핵심 정보(items 등) 누락. 우리 시스템에서 적립 산정에 필요한 최소: `items` (상품·금액), `payments` (결제 상태). 도입 시 정확한 필요 필드 결정.
- 주문 시각 → `order_date` (KST 포함 ISO 8601). [datamodel.md §3.7](datamodel.md) 의 `orders.ordered_at` 매핑.
- 금액 → 문자열로 옴 (`"224400.00"`). int 변환 시 `Decimal` 거쳐 원 단위 정수화.
- `order_no` 가 cafe24 측 ID. 우리 `orders.external_order_number` 컬럼에 박힘.

---

## 2. List orders — 목록 조회

**GET** `/api/v2/admin/orders`

현재 [`order.py`](../franchise_manager/api/infrastructure/cafe24/order.py) 의 `Order.fetch(start_date, end_date)` 가 호출.

### 주요 파라미터

| 이름 | 타입 | 설명 |
| --- | --- | --- |
| `start_date` | string (YYYY-MM-DD) | 검색 시작 |
| `end_date` | string (YYYY-MM-DD) | 검색 종료. range 최대 31일 제한 (공식 문서 확인 필요) |
| `shop_no` | int | 멀티숍 |
| `embed` | string | items/receivers/... |
| `limit`, `offset` | int | 페이징 |
| `order_status` | string | 상태 필터 |

배치 동기화 흐름은 [oauth2.0.html §10 - 흐름 2](oauth2.0.html) 참조.

---

## 3. Update an order — 수정 (미구현)

**PUT** `/api/v2/admin/orders/{order_no}`

scope: `mall.write_order`. 현재 우리 서비스는 읽기 전용 정책 → 미구현. 향후 가맹점 측 후처리 (예: 운영자 메모 동기화) 필요 시 검토.

---

## 4. Cancel an order — 취소 (미구현)

**POST** `/api/v2/admin/orders/{order_no}/cancellation`

scope: `mall.write_order`. Cafe24 측에서의 취소는 우리 시스템 입장에선 *외부 이벤트*. 단건 webhook 또는 polling 으로 인지 → `orders.status='canceled'` 로 UPDATE + ledger `revert_order` INSERT ([datamodel.md §4.4](datamodel.md)).

→ 우리 쪽에서 cafe24 에 취소 요청 보낼 일은 없음. **호출 API 가 아니라 인지 대상 이벤트**.

---

## 구현 우선순위 (제안)

1. ✓ List orders (`Order.fetch`) — 현재 구현됨
2. **Retrieve an order** — 단건 정합성 확인용 / webhook 후속 조회용
3. List orders 페이징 / `embed` 추가
4. 취소 인지 흐름 (webhook 또는 polling)
