# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.1] - 2026-10-02

### Fixed
- Fixed Plugin auto-registration system — true automatic discovery via `register_scenarios()`, no manual `main.py` mapping needed
- Fixed Async HTTP client — persistent connection pooling (was creating/closing client per request)
- Fixed Async HTTP client — added exponential backoff retry for 429/5xx errors (was missing retry logic)
- Fixed Batch processing recursion — iterative chunking instead of recursive calls (stack overflow risk for large batches)
- Fixed ProgressBar infinite loop — corrected recursive `line.format(bar=line)` causing terminal corruption
- Fixed Batch processing hardcoded to sentiment — now dynamically displays all answer keys from response
- Fixed Risk scenario missing `--data` support — now supports external data source like other scenarios
- Fixed Empty results `IndexError` in `_print_stats` helpers across all scenario modules
- Fixed CSV output nested JSON flattening — `_flatten_value()` now safely serializes dicts/lists to strings
- Fixed Output file accumulation — added `fmt` parameter to `save_results()` for CSV/JSON selection
- Fixed `validate_state` tight coupling to `DecisionRequest` — extracted independent validation logic
- Fixed Plugin state reset — `reset()` API instead of direct `_scenarios.clear()` access
- Fixed Configuration system — removed legacy `LAYA_CONFIG` dict, unified access via `get_config()`
- Fixed CLI scenario routing — dynamic `_run_scenario()` via plugin registry instead of hardcoded imports

### Changed
- Scenario auto-discovery now extracts clean names: `run_xxx_example` → `xxx`, `run_xxx_assessment` → `xxx`, etc.
- All scenario modules share common `_print_stats()` pattern with safety checks
- `save_results()` and `save_single_result()` now accept `fmt` parameter for format selection
- Async HTTP client now uses persistent `httpx.AsyncClient` with connection pooling
- Batch retry uses iterative loop instead of recursive function calls

### Added
- `plugin.reset()` API for clean test isolation
- Plugin alias system for CLI flag mapping (`--recommend` → `product_recommendation` scenario)
- `_flatten_value()` helper in output module for safe CSV export
- Async HTTP client retry count override via `max_retries` parameter

## [2.0.0] - 2026-10-02

### Added
- HTTP retry with `requests.Retry` (auto-retry on 429/5xx with exponential backoff)
- Async HTTP client via `httpx` for high-concurrency batch processing
- Structured JSON logging via `structlog` with trace IDs
- Input validation with `pydantic` request parameter validation
- Environment variable configuration with `pydantic-settings` (`.env` support)
- External data source support (`--data file.json/.csv/-`)
- Unified output format (`{"metadata": {...}, "results": [...]}`)
- Real-time progress bar during batch processing
- Risk assessment scenario
- Plugin architecture with automatic scene registration
- CSV output format (`--format csv`)
- Complete test suite with `pytest` and coverage
- Docker support
- GitHub Actions CI (tests on Python 3.10–3.12)
- Issue and Pull Request templates

### Changed
- Internationalized all user-facing text to English
- Refactored configuration into structured `pydantic-settings` models

### Removed
- Hardcoded configuration values (replaced by environment variables)

[2.0.0]: https://github.com/hotker/laya_decision_system/releases/tag/v2.0.0