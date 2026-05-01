# Model Rate Limits (Free Tier)

### Compatible Models for File Search
| Model | RPM | TPM | RPD |
| :--- | :---: | :---: | :---: |
| **gemini-3-flash-preview** | 5 | 250K | 20 |
| **gemini-2.5-flash-lite** | 10 | 250K | 20 |
| **gemini-3.1-flash-lite-preview** | 15 | 250K | 500 |

### Compatible Models for Non-File Search Prompts
| Model | RPM | TPM | RPD |
| :--- | :---: | :---: | :---: |
| **gemini-2.5-flash** | 5 | 250K | 20 |
| **gemma-4-31b-it** | 15 | Unlimited | 1.5K |
| **gemini-3.1-flash-lite-preview** | 15 | 250K | 500 |

> **Note:** `gemini-3.1-flash-lite-preview` can be used for both File Search and non-File Search prompts.

### Temporary High Demand

If Gemini returns `503 UNAVAILABLE` or "currently experiencing high demand", the provider is overloaded for that model. Configure comma-separated fallbacks so the backend can try another compatible model after retrying the primary model:

```bash
GEMINI_FILE_SEARCH_FALLBACK_MODELS=gemini-3-flash-preview,gemini-2.5-flash-lite
GEMINI_SYNTHESIS_FALLBACK_MODELS=gemini-2.5-flash
```

Prefer a Gemini 3 fallback first for File Search requests because structured output with File Search is documented for Gemini 3 models. Gemini 2.5 Flash-Lite can still be used as a later File Search fallback; the backend will retry without structured-output mode if a fallback model rejects that combination.
