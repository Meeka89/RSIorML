"""Generate model_screening.ipynb: python notebooks/build_model_screening.py."""
import json
from pathlib import Path
from build_colab_basics import md, code

cells = [
md('''# Quick model screening in Colab
Choose a Transformers instruction checkpoint, run the repo's development items,
and download responses for manual review. This is inference only: no training,
automatic scoring, or claim of final benchmark performance.

Select **Runtime > Change runtime type > T4 GPU**. Run sections 1–7 in order.
For another model, download your results first, change section 2, and rerun sections
2–7. Section 4 releases the previous model. A fresh runtime is safest if memory or
library errors occur. GGUF files need a different loader and are not supported here.
Reasoning-model raw output is preserved; review its final answer separately.'''),
md('''## 1. Install
Pinned for this notebook; do not reuse the GPT-2 training notebook's dependency cell.
If asked to restart, restart the session and continue with section 2.'''),
code('''%pip install -q "transformers==5.13.0" "accelerate==1.10.1" "bitsandbytes==0.48.1"'''),
md('''## 2. Change models here
Gemma access requires accepting its conditions on Hugging Face, then logging in.
Examples: `google/gemma-2-9b-it`, `google/gemma-2-2b-it`,
`Qwen/Qwen2.5-7B-Instruct`, `Qwen/Qwen2.5-1.5B-Instruct`.
Choose a safetensors/Transformers checkpoint, not a GGUF repository.
Keep settings matched between models and record any differences. A reasoning model
may need a larger answer budget; capped generations are flagged, not scored.
`MODEL_REVISION=None` resolves the current default revision and records it.
For the Gemma rerun, the revision below is pinned to the first run. **When switching
models, change MODEL_ID and reset MODEL_REVISION to None.**
The repo revision is resolved to a commit so both dataset files come from one snapshot.'''),
code('''MODEL_ID = "google/gemma-2-9b-it"
MODEL_REVISION = "11c9b309abf73637e4b6f9a3fa1e92e615547819"  # Gemma 9B first-run revision; set None when changing models
LOAD_IN_4BIT = True
LOGIN_TO_HF = True  # Gemma: accept conditions on its model page first
MAX_NEW_TOKENS = 1024  # raised after the first Gemma run hit 256 on every response
MAX_INPUT_TOKENS = 2048  # overlong items fail visibly, never silently truncate
LIMIT_SINGLE = None  # None = all active items; 3 = quick initial check
LIMIT_CONVERSATIONS = None
REPO_ID = "Meeka89/RSIorML"
REPO_REF = "7d1080675a76f4aa829f3551625c48840ca6834c"  # same dataset snapshot as first Gemma run
# Optional model-specific chat-template options, recorded in results.
# Example for models that support it: {"enable_thinking": False}
CHAT_TEMPLATE_KWARGS = {}
SEED = 42'''),
md('''## 3. Imports, GPU check, optional login
Login interactively or through Colab's secret prompt; never put a token into code.
Public ungated models do not require login. This notebook requires a CUDA GPU.'''),
code('''import gc, csv, hashlib, io, json, platform, time, urllib.request, zipfile
from datetime import datetime, timezone
from pathlib import Path
import torch, transformers, accelerate, bitsandbytes
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from google.colab import files
assert torch.cuda.is_available(), "Select a GPU runtime before continuing."
if LOGIN_TO_HF:
    login()
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
print("GPU:", torch.cuda.get_device_name(0))
print("Transformers:", transformers.__version__, "PyTorch:", torch.__version__)'''),
md('''## 4. Release the previous model and load the new one
T4 uses float16 computation. Four-bit quantization reduces weight memory, not parameter
count. Device placement is explicit so CPU offloading cannot silently change timing.
If loading fails, verify access/architecture support and available memory.
Model-defined remote Python code is disabled.'''),
code('''for name in ("model", "tokenizer"):
    globals().pop(name, None)
gc.collect()
torch.cuda.empty_cache()
torch.cuda.reset_peak_memory_stats()
compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
load_kwargs = {"revision": MODEL_REVISION, "dtype": compute_dtype,
               "device_map": {"": 0}, "trust_remote_code": False}
if LOAD_IN_4BIT:
    load_kwargs["quantization_config"] = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=compute_dtype, bnb_4bit_use_double_quant=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION, trust_remote_code=False)
assert tokenizer.chat_template, "Choose a chat checkpoint with a documented chat template."
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, **load_kwargs).eval()
resolved_revision = getattr(model.config, "_commit_hash", None)
print("Loaded:", MODEL_ID, "revision:", resolved_revision)
print("Allocated GPU GiB:", round(torch.cuda.memory_allocated() / 2**30, 2))'''),
md('''## 5. Fetch the repo's development dataset
Downloads only the two JSONL files, not the whole repo. Records their SHA256 hashes
and source commit. The current expected labels are provisional rubric judgments.
They are saved for reviewers and are never passed to the model.'''),
code('''def fetch_bytes(url):
    req = urllib.request.Request(url, headers={"User-Agent": "RSIorML-Colab"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()

commit_info = json.loads(fetch_bytes(f"https://api.github.com/repos/{REPO_ID}/commits/{REPO_REF}"))
repo_commit = commit_info["sha"]
dataset_hashes = {}
def read_items(path):
    payload = fetch_bytes(f"https://raw.githubusercontent.com/{REPO_ID}/{repo_commit}/{path}")
    dataset_hashes[path] = hashlib.sha256(payload).hexdigest()
    items = [json.loads(line) for line in payload.decode("utf-8").splitlines() if line.strip()]
    return [item for item in items if item.get("status", "active") == "active"]

single_items = read_items("data/prompts/prompts.jsonl")
conversation_items = read_items("data/conversations/conversations.jsonl")
single_items = single_items[:LIMIT_SINGLE]
conversation_items = conversation_items[:LIMIT_CONVERSATIONS]
print("Dataset commit:", repo_commit)
print("Single items:", len(single_items), "Conversations:", len(conversation_items))'''),
md('''## 6. Run and save each response immediately
Every single-turn item starts fresh. Each conversation includes the model's actual
previous replies. No system prompt is used, allowing templates such as Gemma's.
Greedy decoding reduces sampling variation; hardware/version reproducibility is not
guaranteed. Errors are recorded; a failed conversation stops rather than fabricating
an assistant turn. Re-running creates a new run folder.

If interrupted, already written records remain on disk. Download them with section 7
before deleting the runtime. An output that consumes its entire token budget is flagged
conservatively; inspect whether it ended naturally before treating it as truncated.'''),
code('''run_time = datetime.now(timezone.utc)
RUN_DIR = Path("/content/model-screening") / f"{MODEL_ID.replace('/', '__')}__{run_time:%Y%m%dT%H%M%S%fZ}"
RUN_DIR.mkdir(parents=True, exist_ok=False)
manifest = {
    "purpose": "development-model-screening", "created_at": run_time.isoformat(),
    "model_id": MODEL_ID, "model_revision": resolved_revision,
    "repo_id": REPO_ID, "repo_commit": repo_commit, "dataset_sha256": dataset_hashes,
    "quantization": "nf4-double-quant" if LOAD_IN_4BIT else "none",
    "compute_dtype": str(compute_dtype), "gpu": torch.cuda.get_device_name(0),
    "versions": {"python": platform.python_version(), "torch": torch.__version__,
        "transformers": transformers.__version__, "accelerate": accelerate.__version__,
        "bitsandbytes": bitsandbytes.__version__},
    "generation": {"do_sample": False, "max_new_tokens": MAX_NEW_TOKENS},
    "max_input_tokens": MAX_INPUT_TOKENS, "seed": SEED,
    "system_prompt": None, "chat_template_kwargs": CHAT_TEMPLATE_KWARGS,
    "chat_template": tokenizer.chat_template,
    "single_ids": [x["id"] for x in single_items],
    "conversation_ids": [x["id"] for x in conversation_items],
}
(RUN_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
records = []

@torch.inference_mode()
def generate_reply(messages):
    inputs = tokenizer.apply_chat_template(messages, tokenize=True,
        add_generation_prompt=True, return_dict=True, return_tensors="pt",
        **CHAT_TEMPLATE_KWARGS).to("cuda")
    n_input = inputs["input_ids"].shape[-1]
    context_limit = getattr(model.config, "max_position_embeddings", None)
    if n_input > MAX_INPUT_TOKENS:
        raise ValueError(f"Input has {n_input} tokens, above cap {MAX_INPUT_TOKENS}; no truncation applied")
    if isinstance(context_limit, int) and n_input + MAX_NEW_TOKENS > context_limit:
        raise ValueError("Input plus output budget exceeds model context window")
    torch.cuda.synchronize()
    started = time.perf_counter()
    output = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
                           pad_token_id=(tokenizer.pad_token_id if tokenizer.pad_token_id is not None
                                         else tokenizer.eos_token_id))
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - started
    generated = output[0, n_input:]
    return {"response": tokenizer.decode(generated, skip_special_tokens=True).strip(),
            "input_tokens": n_input, "generated_tokens": len(generated),
            "hit_output_cap": len(generated) >= MAX_NEW_TOKENS,
            "seconds": elapsed, "error": None}

def run_turn(item, messages, turn, expected):
    row = {"item_id": item["id"], "turn": turn, "category": item["category"],
           "topic": item["topic"], "expected_response": expected,
           "messages": [dict(message) for message in messages]}
    try:
        row.update(generate_reply(messages))
    except Exception as exc:
        row.update(response=None, error=f"{type(exc).__name__}: {exc}")
        gc.collect()
        torch.cuda.empty_cache()
    records.append(row)
    with (RUN_DIR / "responses.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\\n")
    print(f"\\n{row['item_id']} turn {turn} | expected: {expected}")
    print(row["error"] or row["response"])
    if row.get("hit_output_cap"):
        print("[Output budget reached: inspect for truncation]")
    return row

for item in single_items:
    run_turn(item, [{"role": "user", "content": item["prompt"]}], 1, item["expected_response"])
for item in conversation_items:
    history = []
    for index, message in enumerate(item["turns"]):
        history.append(dict(message))
        row = run_turn(item, history, index + 1, item["expected_response"][index])
        if row["error"]:
            break
        history.append({"role": "assistant", "content": row["response"]})
print("\\nSaved:", RUN_DIR)
print("Peak GPU allocated GiB:", round(torch.cuda.max_memory_allocated() / 2**30, 2))'''),
md('''## 7. Download results for manual review
ZIP includes the manifest, all raw response records, and a CSV with blank review
columns. Mark actual response as normal/clarify/redirect/refuse after reading it;
record relevant conditional answers, technical errors, and truncation in notes.
Expected labels are hypotheses for rubric review, not automatic truth. Do not score
errored or incomplete generations as behavioral failures.

Repeat sections 2–7 for the next model. Keep the same repo commit and generation
settings for a comparison. This notebook does not save model weights or credentials.'''),
code('''rows = [json.loads(line) for line in (RUN_DIR / "responses.jsonl").read_text(encoding="utf-8").splitlines()]
columns = ["item_id", "turn", "category", "expected_response", "response",
           "hit_output_cap", "error", "actual_response", "review_notes"]
with (RUN_DIR / "manual_review.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
with zipfile.ZipFile(str(RUN_DIR) + ".zip", "w", zipfile.ZIP_DEFLATED) as archive:
    for path in RUN_DIR.iterdir():
        if path.is_file():
            archive.write(path, arcname=path.name)
print("Records:", len(rows), "Errors:", sum(bool(row.get("error")) for row in rows))
files.download(str(RUN_DIR) + ".zip")'''),
]
if __name__ == "__main__":
    nb = {"nbformat": 4, "nbformat_minor": 5,
          "metadata": {"colab": {"provenance": [], "gpuType": "T4"},
                       "kernelspec": {"name": "python3", "display_name": "Python 3"},
                       "language_info": {"name": "python"}, "accelerator": "GPU"},
          "cells": [dict(cell, id=f"screen-{i:02d}") for i, cell in enumerate(cells)]}
    Path(__file__).with_name("model_screening.ipynb").write_text(
        json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
