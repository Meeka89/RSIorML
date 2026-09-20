# Notebooks

Exploratory work that runs on a GPU. Nothing here is part of the reproducible
pipeline — results that go in the paper come from `src/run_eval.py` and
`src/score.py`, not from a notebook.

## `colab_smoke_test.ipynb`

Loads a Hugging Face instruct model on a Colab GPU and runs a handful of real
benchmark items through it, including the `shift-imitation-001` / `shift-control-001`
pair. Standalone: it does not need this repo cloned, since the prompts are inlined.

Open it in Colab by uploading the file, or once this is on `main`:

```
https://colab.research.google.com/github/Meeka89/RSIorML/blob/main/notebooks/colab_smoke_test.ipynb
```

Set Runtime → Change runtime type → **T4 GPU** first.

**Editing it.** The notebook is generated. Edit `build_smoke_test.py` — where the cell
sources are plain Python strings — and regenerate:

```bash
python notebooks/build_smoke_test.py
```

That keeps the cells reviewable in a diff instead of buried in escaped JSON. If you
edit the notebook directly in Colab, copy the changes back into the build script or
they will be overwritten.
