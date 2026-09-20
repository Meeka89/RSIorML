"""Generate the standalone beginner notebook: python notebooks/build_colab_basics.py."""
import json
from pathlib import Path


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.strip()}


def code(source):
    return {"cell_type": "code", "metadata": {}, "source": source.strip(),
            "execution_count": None, "outputs": []}


cells = [
    md("""
# Your first Hugging Face model in Colab

Goal: load a model, ask it questions, understand conversation history, and download
an output. This is inference (using existing weights), not training or a research run.

**The pieces:** this repo stores the notebook; Colab provides a temporary computer;
Hugging Face hosts the model files; Transformers loads and runs them using PyTorch.
The model runs inside your Colab runtime, not on a Hugging Face inference API.

Choose **Runtime > Change runtime type > T4 GPU** if available, then run each code
cell in order with its play button or Shift+Enter. A CPU also works for this small
model, but is slower. GPU availability and session limits vary.
You need a Google account for Colab; this public model needs no Hugging Face token.
No repo clone or Drive mount is needed for this walkthrough.
"""),
    md("""## 1. Install the model-loading library
`%pip` installs into this runtime. Run again when Colab gives you a new runtime.
We pin Transformers to keep this tutorial's API stable; Colab supplies PyTorch.
If Colab requests a session restart, restart and continue from cell 2."""),
    code('%pip install -q "transformers==5.13.0"'),
    md("## 2. Check the computer\nCUDA means PyTorch can use the NVIDIA GPU. CPU mode is a valid fallback."),
    code('''import platform
import torch
import transformers

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32
print("Python:", platform.python_version())
print("Transformers:", transformers.__version__)
print("PyTorch:", torch.__version__)
print("Device:", DEVICE, "| dtype:", DTYPE)
if DEVICE == "cuda":
    print("GPU:", torch.cuda.get_device_name(0))
    print("GPU memory (GiB):", round(torch.cuda.get_device_properties(0).total_memory / 2**30, 1))'''),
    md("""## 3. Download and load a model
`MODEL_ID` is a Hugging Face repository name. `0.5B` means roughly half a billion
parameters (learned numbers). `Instruct` means it was adapted to follow instructions.
This small model is for learning the mechanics; its answers can be wrong.

The **tokenizer** converts text to token IDs and back. The **model** predicts new
tokens. Download progress bars on the first run are normal. GPU memory includes
weights plus working memory. Loading once lets us reuse the model for many prompts.
"""),
    code('''from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=DTYPE).to(DEVICE)
model.eval()
print("Loaded:", MODEL_ID, "on", model.device)'''),
    md("""## 4. Send one message
A chat template inserts the role markers expected by this model. Tokenization then
turns the formatted conversation into numbers. We pass an attention mask too.
`generate` returns the prompt plus new tokens; we decode only the new part.

`max_new_tokens` caps the answer length in tokens, not words. `do_sample=False`
chooses the most likely next token each step. This reduces randomness but does not
guarantee identical answers across hardware or library versions.
"""),
    code('''@torch.inference_mode()
def chat(messages, max_new_tokens=128):
    inputs = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True,
        return_dict=True, return_tensors="pt",
    ).to(DEVICE)
    output = model.generate(
        **inputs, max_new_tokens=max_new_tokens, do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
    )
    new_tokens = output[0, inputs["input_ids"].shape[-1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

prompt = "Explain what a GPU does in two short sentences."
messages = [{"role": "user", "content": prompt}]
reply = chat(messages)
print(reply)'''),
    md("""## 5. Give it a follow-up
The model does not keep a chat history for you. We send the earlier user message,
the model's actual reply, and the new question together. Rerunning this cell starts
from the single answer above, so it does not silently accumulate extra turns.
"""),
    code('''history = messages + [
    {"role": "assistant", "content": reply},
    {"role": "user", "content": "Explain that again using a kitchen analogy."},
]
follow_up = chat(history)
print(follow_up)'''),
    md("""## 6. Try it yourself
Change the question below and rerun this cell. This creates a fresh conversation.
Try changing the answer cap from 96 to 32 to see how truncation affects the answer.
You do not need to reinstall or reload the model for each prompt.
"""),
    code('''my_question = "What is the difference between training and inference?"
print(chat([{"role": "user", "content": my_question}], max_new_tokens=96))'''),
    md("""## 7. Save the first conversation
Runtime files disappear when the runtime is deleted. This cell writes a JSON record
and downloads it to your computer. It saves the conversation from cells 4–5, not
the independent exercise in cell 6. This is a learning artifact, not benchmark data.
"""),
    code('''import json
from datetime import datetime, timezone
from pathlib import Path
from google.colab import files

now = datetime.now(timezone.utc)
record = {
    "purpose": "learning-only",
    "created_at": now.isoformat(),
    "model_id": MODEL_ID,
    "model_revision": getattr(model.config, "_commit_hash", None),
    "transformers_version": transformers.__version__,
    "torch_version": torch.__version__,
    "device": DEVICE,
    "dtype": str(DTYPE),
    "generation": {"max_new_tokens": 128, "do_sample": False},
    "messages": history + [{"role": "assistant", "content": follow_up}],
}
output_path = Path("/content") / f"colab-learning-{now:%Y%m%dT%H%M%S%fZ}.json"
output_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
files.download(str(output_path))'''),
    md("""## What to do next
- Edit the prompt and explain each step of `chat()` in your own words.
- Compare a fresh question with a follow-up that includes earlier messages.
- Once comfortable, restart the session, change `MODEL_ID` to
  `Qwen/Qwen2.5-1.5B-Instruct`, and run from cell 2. Prefer a GPU for this step.
  Restarting first releases the old model's memory.
- Save your notebook with **File > Save a copy in Drive**, or download the `.ipynb`.
  Drive copies and this repo do not automatically synchronize. The repo's notebook
  is generated from `notebooks/build_colab_basics.py`; bring edits back there.
- When finished, use **Runtime > Disconnect and delete runtime** to release it.

### If something goes wrong
| Symptom | What to do |
|---|---|
| No GPU available | Use CPU with the default 0.5B model, or try a GPU later. |
| `NameError` | Run earlier cells again; a restart clears variables. |
| CUDA out of memory | Restart the session and use the default small model and short prompts. |
| Missing `HF_TOKEN` warning | Public model downloads can run without a token. |
| Download fails / HTTP 429 | Wait and retry; check connectivity and Hub availability. |
| 401/403 for a different model | Check its access requirements, accept its terms if needed, and use `huggingface_hub.login()` interactively. Never paste tokens into notebook code. |
| Import error after installing | Restart the session and rerun from cell 2; if unresolved, preserve the full error and version output. |
| Answer ends abruptly | Raise `max_new_tokens` modestly. |

Changing the model ID is not universal compatibility: other models may require more
memory, different dependencies, or different message roles. Start with these two Qwen models.
This notebook does not connect the model to `src/run_eval.py`; that integration comes later.

Sources: [model card](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct),
[chat templates](https://huggingface.co/docs/transformers/chat_templating),
[Colab FAQ](https://research.google.com/colaboratory/faq.html).
"""),
]

if __name__ == "__main__":
    notebook = {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {
            "colab": {"provenance": [], "gpuType": "T4"},
            "kernelspec": {"name": "python3", "display_name": "Python 3"},
            "language_info": {"name": "python"}, "accelerator": "GPU",
        },
        "cells": [dict(cell, id=f"basics-{i:02d}") for i, cell in enumerate(cells)],
    }
    Path(__file__).with_name("colab_basics.ipynb").write_text(
        json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
