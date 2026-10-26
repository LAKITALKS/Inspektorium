# Provider Contract — Phase 2 (Normalization)

Branch: `feat/provider-contract-normalization` (from `v0.6.2-output-contract`)

Phase 2 makes live provider calls observable and safe without changing scoring,
prompts, biomedical logic, or report/PDF layout. It connects real provider
output to the Phase-1 output parser (`output_contract`).

---

## Old provider contract (pre-Phase 2)

```python
class BaseProvider(ABC):
    @abstractmethod
    def send_prompt(self, task, system_prompt) -> str: ...   # raw text only, raises on error
```

- No `finish_reason`, no token usage, no per-call latency, no error typing.
- `run_agent` measured wall-clock latency, caught `Exception` → `error` string.
- Inconsistent `max_tokens`: Anthropic `4096`, OpenAI `2048`, Ollama unset.
- `OpenAIProvider` / `OllamaProvider` did not accept `temperature`/`label`, so
  the YAML path `get_provider(p, model=, temperature=, label=)` would raise
  `TypeError` for those two (latent break).

## New provider contract (Phase 2)

```python
@dataclass
class ModelResponse:
    text: str = ""
    provider: str | None = None
    model: str | None = None
    finish_reason: str | None = None   # "stop" | "length" | "error" | "unknown" | None
    usage: dict | None = None
    latency_ms: int | None = None
    error: str | None = None
    error_type: str | None = None      # normalized (see below)

class BaseProvider(ABC):
    @abstractmethod
    def send_prompt(self, task, system_prompt) -> str: ...   # unchanged primitive

    def generate(self, task, system_prompt) -> ModelResponse: ...  # NEW, never raises
```

- `generate` is the new primary, observable entry point. The default
  implementation wraps `send_prompt` (latency + error capture), so any provider
  that implements only `send_prompt` keeps working.
- Real providers (Anthropic/OpenAI/Ollama) **override `generate`** with the SDK
  call and populate `finish_reason`/`usage`; their `send_prompt` now delegates to
  `self.generate(...).text` and re-raises on error (preserving old raise-on-error
  semantics — the judge path relies on this).

## Backward compatibility

- `send_prompt(task, system_prompt) -> str` signature and raise-on-error behavior
  are preserved on every provider. The optional `judge.py` path (which calls
  `send_prompt`) is unaffected and was **not** modified.
- `AgentResult` gained three **optional, defaulted** fields (`finish_reason`,
  `usage`, `error_type`). Old run-record JSON and existing constructors still
  load/validate unchanged. No change to `AgentResponse` or `DiagnosticScores`.
- `parse_agent_output` (Phase-1 wrapper) is unchanged; `run_agent` now calls
  `parse_structured_output(text, finish_reason=...)` directly to thread the hint.
- No provider support removed. No existing test or agent YAML behavior broken
  (937 tests pass).

## finish_reason mapping

| Provider | Source field | Mapping |
|---|---|---|
| Anthropic | `message.stop_reason` | `end_turn`/`stop_sequence`/`tool_use` → `stop`; `max_tokens` → `length`; else `unknown` |
| OpenAI | `choices[0].finish_reason` | `stop`→`stop`; `length`→`length`; `content_filter`→`error`; `tool_calls`/`function_call`→`stop`; else `unknown` |
| Ollama | `done_reason` (newer versions only) | `stop`→`stop`; `length`→`length`; **absent → `None` (never fabricated)** |

If `finish_reason == "length"`, `run_agent` passes it into the Phase-1 parser,
which sets `truncation_suspected=True` on the parse diagnostics.

## usage mapping

| Provider | Normalized keys |
|---|---|
| Anthropic | `input_tokens`, `output_tokens` (from `message.usage`) |
| OpenAI | `prompt_tokens`, `completion_tokens`, `total_tokens` (from `response.usage`) |
| Ollama | `prompt_tokens` (`prompt_eval_count`), `completion_tokens` (`eval_count`) when present |

`usage` is `None` when the provider does not report it. Missing usage never
fails a call.

## Error normalization

`classify_error_type(exc)` (name/message based, no SDK import) returns:
`auth_error`, `not_found_error`, `rate_limit_error`, `timeout_error`, or
`provider_error` (default). On failure, `ModelResponse` carries `error` +
`error_type` with `finish_reason="error"` and empty `text`; `run_agent` surfaces
both into `AgentResult`. A failed call never looks like a successful empty
response.

## max_tokens notes

| Provider | Old | New | Why / risk |
|---|---|---|---|
| Anthropic | 4096 | 4096 (`DEFAULT_MAX_TOKENS`) | unchanged |
| OpenAI | **2048** | **4096** | Pre-Phase-2 audit flagged 2048 as truncation-prone. Risk: slightly higher token cost per call; low, and aligned with the audit. |
| Ollama | unset | unset | HTTP payload unchanged (no `num_predict` added) to avoid behavior risk |
| Judge | inherits provider default | inherits provider default | unchanged |

`max_tokens` is now a constructor parameter on Anthropic/OpenAI (default
`DEFAULT_MAX_TOKENS = 4096`), so it is consistent and overridable.

## Remaining limitations

- `finish_reason`/`usage` are captured but **not yet persisted into reports/PDF**
  (report layout is out of Phase-2 scope). They live on `AgentResult` for later use.
- `judge.py` still uses the `send_prompt` path and its own `_parse_judge_output`
  (which carries the same unclosed-fence fragility Phase 1 fixed for the main
  path). Harmonizing the judge parser is deferred — out of scope here.
- Ollama sampling params (`temperature`) are accepted but not wired into the HTTP
  payload yet.
- Live truncation detection depends on structural signals + `finish_reason` only
  when a provider reports it.

## Next recommended phase

`feat/provider-metadata-in-reports` (surface `finish_reason`/`usage` in run
records + reports) or harmonize the judge parser onto `output_contract`. Neither
touches scoring.
