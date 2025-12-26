# Python Logging Pattern: get_logger + LoggerMixin

This document explains:

- `get_logger()` with `@lru_cache`
- `LoggerMixin`
- `@property`
- how `self.logger.info(...)` works
- the full call flow

---

## Example Code

```python
from functools import lru_cache
import logging

@lru_cache
def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class LoggerMixin:
    @property
    def logger(self) -> logging.Logger:
        return get_logger(self.__class__.__name__)


class PaymentService(LoggerMixin):
    def process(self) -> None:
        self.logger.info("Processing payment")
```

---

## High-Level Idea

This pattern separates logging into two responsibilities:

| Responsibility | Component |
| --- | --- |
| Logging configuration | `setup_logging()` (elsewhere) |
| Logger access | `LoggerMixin` + `get_logger()` |

Goals:

- centralized logging configuration
- consistent logger access
- minimal boilerplate in classes

---

## What `get_logger()` Does

```python
@lru_cache
def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
```

Key points:

- `logging.getLogger(name)` returns a singleton logger per name
- `@lru_cache` reuses the same logger object
- this function does not configure logging
- it only retrieves a named logger

Example:

```python
get_logger("PaymentService") is get_logger("PaymentService")
# True
```

---

## What `LoggerMixin` Provides

A mixin is a helper class that provides reusable behavior via inheritance.

```python
class LoggerMixin:
    @property
    def logger(self) -> logging.Logger:
        return get_logger(self.__class__.__name__)
```

This mixin:

- adds a `logger` attribute to any class that inherits it
- ensures one logger per class
- removes repeated `logging.getLogger(...)` calls

---

## Why `@property` Is Used

The `@property` decorator turns a method into a computed attribute.

It allows:

```python
self.logger.info("message")
```

Instead of:

```python
self.get_logger().info("message")
```

Note: `self.logger` is not a stored variable. It is a method that runs on access.

---

## How `self.logger.info(...)` Works

Line to expand:

```python
self.logger.info("Processing payment")
```

Step-by-step:

1. Python evaluates `self.logger`.
2. `logger` is not found on the instance.
3. Python checks base classes and finds the `logger` property in `LoggerMixin`.
4. The property executes: `get_logger(self.__class__.__name__)`.
5. `get_logger("PaymentService")` returns a `logging.Logger`.
6. `.info("Processing payment")` runs on that logger.

---

## Fully Expanded Version

This:

```python
self.logger.info("Processing payment")
```

Is equivalent to:

```python
get_logger(self.__class__.__name__).info("Processing payment")
```

Which is equivalent to:

```python
logging.getLogger("PaymentService").info("Processing payment")
```

---

## Why `@lru_cache` Is Optional

Logging already caches loggers internally:

```python
logging.getLogger("X") is logging.getLogger("X")
# True
```

`@lru_cache` adds:

- explicit caching
- minor performance savings
- clear intent that loggers are shared

It does not change behavior.

---

## Why Use `LoggerMixin` At All?

Without `LoggerMixin`:

```python
import logging

class PaymentService:
    def process(self) -> None:
        logger = logging.getLogger(__name__)
        logger.info("Processing payment")
```

With `LoggerMixin`:

```python
class PaymentService(LoggerMixin):
    def process(self) -> None:
        self.logger.info("Processing payment")
```

Benefits:

- no repeated imports
- no naming decisions per class
- cleaner code
- enforced consistency
- easy to enhance later

---

## Future-Proofing (Why This Pattern Exists)

If you want to attach context (request IDs, trace IDs, etc.), change it once:

```python
class LoggerMixin:
    @property
    def logger(self) -> logging.Logger:
        base = get_logger(self.__class__.__name__)
        return logging.LoggerAdapter(base, {"request_id": get_request_id()})
```

Every class automatically gets enriched logs.

---

## When This Pattern Is Worth Using

| Scenario | Recommended |
| --- | --- |
| scripts or notebooks | no |
| small apps | no |
| medium apps | optional |
| large apps | yes |
| microservices | yes |
| agent systems | yes |

---

## Final Mental Model

```text
self.logger
  -> LoggerMixin.logger property
  -> get_logger("ClassName")
  -> logging.getLogger("ClassName")
  -> Logger instance
  -> .info(...)
```

---

## One-Line Summary

`LoggerMixin` provides a class-specific logger via a property that calls a cached `get_logger()` function, which returns a standard `logging.Logger`.
