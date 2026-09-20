# First run: Colab and Hugging Face

Start with `notebooks/colab_basics.ipynb`. It uses the public
[Qwen2.5-0.5B-Instruct model](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)
to learn inference: generating answers from an already trained model.

## Open the local notebook now

1. Open [Google Colab](https://colab.research.google.com/) and sign in to Google.
2. Choose **File > Upload notebook** (or the **Upload** tab in the opening dialog).
3. Select `C:\Projects\RSIorML\notebooks\colab_basics.ipynb`.
4. Choose **Runtime > Change runtime type > T4 GPU**, if available, and save.
5. Run the cells from top to bottom, one at a time. Wait for each to finish.
6. Success means cell 3 prints the loaded model, cell 4 prints an answer, cell 5
   prints a follow-up, and cell 7 downloads a JSON file.

No local Python installation, Hugging Face account, API key, paid inference endpoint,
repository clone, or Drive mount is required for this first notebook. A free GPU
is not guaranteed; the default model also has a slower CPU fallback.

Once this notebook is committed and pushed to GitHub's `main` branch, you can use
[Open in Colab](https://colab.research.google.com/github/Meeka89/RSIorML/blob/main/notebooks/colab_basics.ipynb).
That link reads GitHub, so it cannot see unpushed local changes. Upload works immediately.

## What runs where

| Piece | Purpose |
|---|---|
| This Git repository | Stores notebook source, documentation, and eventually research code. |
| Notebook (`.ipynb`) | Contains text explanations and runnable code cells. |
| Colab runtime | A temporary remote computer running Python, with CPU or GPU. |
| Hugging Face Hub | Supplies downloaded model weights, tokenizer, and configuration. |
| Transformers / PyTorch | Load the model and perform computation inside Colab. |
| Tokenizer / chat template | Turn role-labeled messages into the model's expected input. |

Opening the notebook does not clone this repo. Installing packages installs them on
Colab, not your Windows machine. Generating answers does not update model weights.
Conversation context works because the notebook resends the message history.

## Save your work

Use **File > Save a copy in Drive** to keep an editable notebook, or download an
`.ipynb` from the File menu. Saving the notebook does not preserve the runtime's
installed packages, downloaded model cache, or arbitrary files. Download the JSON
test record before ending the session. In a new runtime, run the setup cells again.

Neither a Drive copy nor an uploaded notebook automatically syncs back to this repo.
Keep exploratory output separate from the benchmark's `results/raw/` records.
For repo edits, change `notebooks/build_colab_basics.py`, then regenerate with:

```bash
python notebooks/build_colab_basics.py
```

The notebook contains troubleshooting steps and exercises. Learn those first; the
existing `colab_smoke_test.ipynb` is a later exploration of benchmark prompts.
The benchmark harness currently uses an HTTP model endpoint; loading a model in
Colab alone does not connect it to that harness.

References: [Colab FAQ](https://research.google.com/colaboratory/faq.html) and
[Hugging Face chat templates](https://huggingface.co/docs/transformers/chat_templating).
