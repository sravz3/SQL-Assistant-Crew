# Changelog

## [Unreleased]

### Added
- Support for local Ollama models.
- `requirements.txt` file for easier dependency management.

### Changed
- `crew_setup.py` to dynamically load models based on the provider specified in `agents.yaml`.
- `config/agents.yaml` to use `ollama/llama2` for the `query_generator_agent`.
