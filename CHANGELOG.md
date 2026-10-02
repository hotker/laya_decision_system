# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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