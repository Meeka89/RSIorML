# Learning artifacts

These are exploratory training artifacts, separate from benchmark results in `raw/`.

## distillation-20261012-004343.zip

Uploaded October 11, 2026 (America/Chicago); the filename uses the Colab runtime clock.
GPT-2 teacher → existing DistilGPT-2 student, 50 additional distillation updates using
LoRA on WikiText. The archive contains adapter safetensors/configuration, tokenizer,
exact base revision in `metadata.json`, training log, and before/after measurements.
It does not contain full base weights or an optimizer checkpoint.

| Validation metric | Before | After |
|---|---:|---:|
| Next-token cross-entropy | 4.932719 | 4.462851 |
| Perplexity | 138.756265 | 86.734454 |
| Temperature-scaled token KL | 0.587338 | 0.462708 |

Samples remain repetitive and inaccurate. This learning run does not establish improved
instruction following or benchmark behavior. Fresh-runtime reload is not yet confirmed.

To use it, download the ZIP and upload it in section 10 of `distillation_today.ipynb`.
Alternatively, extract it and load `distilbert/distilgpt2` at revision
`2290a62682d06624634c1f46a6ad5be0f47f38aa`, then load the `adapter/` directory with
`PeftModel.from_pretrained`. The teacher is not needed for inference.
