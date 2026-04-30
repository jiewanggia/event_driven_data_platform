# Framework Design

## 1. Overview

This project is designed as a production-style data platform with a clear separation between:

- **Platform layer (`framework/`)**
- **Pipeline layer (`pipelines/`)**

The platform layer provides reusable capabilities such as:

- runtime context management
- logging and observability
- IO abstraction
- policies and validation

This document describes the first three foundational components:

1. JobContext (execution context)
2. Logging (observability layer)
3. PathBuilder (standardized storage path construction)

These components define the **execution contract** for all pipelines.

---

## 2. JobContext (Execution Context)

### 2.1 Purpose

`JobContext` represents the runtime context of a single pipeline job execution.

It acts as the **single source of truth** for all execution metadata.

---

### 2.2 Responsibilities

The context captures:

- pipeline identity
- job identity
- business date (data partition)
- unique run identifier (`run_id`)
- execution environment

---

### 2.3 Data Model

```python
JobContext(
    pipeline_name: str,
    job_name: str,
    business_date: str,
    run_id: str,
    env: str
)
```

---

### 2.4 Design Decisions

#### 2.4.1 Immutable Context

```python
@dataclass(frozen=True)
```

- Context is **immutable**
- Prevents accidental mutation during execution
- Ensures consistency across all components

This is critical because the context is shared across:

- IO layer
- logging
- validation
- transformations

---

#### 2.4.2 Business Date as String

```python
business_date: str
```

Instead of using `datetime`, we use:

```text
YYYY-MM-DD
```

Rationale:

- Matches S3 partitioning (`dt=YYYY-MM-DD`)
- Aligns with SQL queries
- Compatible with Airflow scheduling
- Avoids repeated conversions

---

#### 2.4.3 Run ID Design

```python
datetime.now(timezone.utc).strftime("%Y%m%d%H%M%SZ") + "_" + uuid
```

Example:

```text
20260429153000Z_ab12cd34
```

Design goals:

- globally unique
- human-readable
- time-sortable

Used for:

- log tracing
- debugging
- audit tracking

---

#### 2.4.4 Factory Method

```python
JobContext.create(...)
```

Instead of constructing directly:

```python
JobContext(...)
```

We use a factory method to:

- enforce consistent initialization
- centralize `run_id` generation
- allow future extensions without breaking callers

---

#### 2.4.5 Serialization Support

```python
context.as_dict()
```

Used for:

- structured logging
- metrics
- audit systems

---

## 3. Logging & Observability

### 3.1 Goals

The logging system is designed to be:

- **context-aware**
- **structured**
- **consistent across pipelines**

Every log should answer:

```text
Which pipeline?
Which job?
Which business date?
Which run?
Which environment?
```

---

### 3.2 Logging Architecture

```text
configure_logging()      -> global configuration
ContextLoggerAdapter     -> inject context
get_logger(context)      -> create logger per job
```

---

### 3.3 Global Logging Configuration

```python
configure_logging()
```

Responsibilities:

- define log format
- set log level
- output to stdout

Example format:

```text
timestamp level pipeline job business_date run_id env - message
```

Example output:

```text
2026-04-29 16:40:12 INFO pipeline=user_events job=ingest_to_bronze business_date=2026-04-22 run_id=... env=dev - Starting job
```

---

### 3.4 Context Injection

We use:

```python
ContextLoggerAdapter
```

It automatically injects:

```text
pipeline_name
job_name
business_date
run_id
env
```

into every log record.

---

### 3.5 Usage Pattern

```python
configure_logging()
logger = get_logger(context)

logger.info("Starting ingestion")
```

Output:

```text
INFO pipeline=user_events job=ingest_to_bronze business_date=2026-04-22 run_id=... env=dev - Starting ingestion
```

---

### 3.6 Why Not Pass Context Manually?

Without adapter:

```python
logger.info("Starting", extra={...})
```

Problems:

- repetitive
- error-prone
- inconsistent

With adapter:

```python
logger.info("Starting")
```

Benefits:

- clean
- consistent
- centralized

---

## 4. Engineering Rationale

### 4.1 Execution Context Propagation

This pattern is similar to:

- request context in backend systems
- job metadata in distributed systems

All components rely on a shared context object.

---

### 4.2 Structured Logging

Instead of free-form logs:

```text
"something happened"
```

We enforce structured logs:

```text
pipeline + job + date + run_id
```

This enables:

- debugging specific runs
- log aggregation
- monitoring and alerting

---

### 4.3 Separation of Concerns

```text
JobContext -> metadata
Logger     -> output
```

Each component has a single responsibility.

---

### 4.4 Reusability

Both components are:

- independent of any specific pipeline
- reusable across domains:
  - user_events
  - orders
  - future domains such as payments

---

## 5. Summary

- `JobContext` defines the **execution contract**
- Logging ensures **traceability and observability**
- Together they provide the foundation for:
  - debugging
  - monitoring
  - auditing
  - future extensions such as metrics and alerting

---

## 6. Path Builder

### 6.1 Purpose

`PathBuilder` centralizes S3 path construction for the platform.

It prevents individual jobs from hardcoding S3 paths and ensures consistent layout across domains and pipelines.

### 6.2 Supported Paths

The first version supports:

- raw landing paths
- Iceberg warehouse path
- Spark event logs path
- Athena query results path
- monitoring output path

### 6.3 Example

```text
s3://my-bucket/raw/user_events/dt=2026-04-22/
s3://my-bucket/raw/orders/dt=2026-04-22/
s3://my-bucket/warehouse/
```

### 6.4 Design Rationale

Path conventions are part of the platform contract.

Centralizing path construction makes it easier to:

- support multiple domains
- avoid duplicated path logic
- change storage layout safely
- keep jobs independent of infrastructure details