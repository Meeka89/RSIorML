# Reference material

Third-party code kept for study. **Nothing here is part of the benchmark pipeline** —
it is not imported by `src/`, not run by any experiment, and not covered by
`python -m src.validate`.

---

## `arik_poznanski_code.py`

Knowledge distillation in PyTorch: a ResNet50 teacher distilled into a ResNet18
student on CIFAR-10, with a from-scratch ResNet18 as the baseline.

- **Author:** Arik Poznanski
- **Source:** _(add the original URL here — this copy arrived without one)_
- **License:** _(unverified — check the source before reusing or redistributing any
  of it, and especially before this repository is made public)_
- **Retrieved:** September 2026

Originally a notebook; the section comments (`# Basic Setup`, `# Load Dataset`, …) are
flattened markdown cells.

### What to read, and what to skip

The concept is about fifteen lines. `distillation_loss` is the whole of Hinton et al.
(2015):

```python
soft_targets = F.kl_div(
    F.log_softmax(student_logits / T, dim=1),   # student's distribution
    F.softmax(teacher_logits / T, dim=1),        # teacher's soft labels
    reduction='batchmean'
) * (T * T)                                      # gradient rescale

hard_loss = F.cross_entropy(student_logits, targets)
return alpha * soft_targets + (1 - alpha) * hard_loss
```

Note `alpha`: training blends the teacher's soft targets with ordinary cross-entropy on
the true labels, here 70/30. Everything else in the file — model setup, data loading,
accuracy and latency helpers — is scaffolding.

**Two techniques are layered here without being distinguished.** The loss above is
Hinton et al. The projection layers (`FeatureProjector`, `StudentWrapper`, and the MSE
over intermediate feature maps) are a separate, later idea — feature distillation, from
FitNets (Romero et al.). Don't attribute the second to the first in the paper.

### Known problems

Recorded so this file isn't mistaken for a model to copy from:

| Where | Problem |
|---|---|
| `measure_latency` | Never calls `torch.cuda.synchronize()`. CUDA kernels are asynchronous, so on a GPU this times how fast work was *queued*, not how long it took. **Do not copy this timing pattern.** |
| `setup_models` | Uses torchvision's ImageNet stem (7×7 stride-2 conv + stride-2 maxpool) on 32×32 CIFAR images: 32 → 16 → 8 before `layer1` runs, and `layer4` ends up 1×1. Runs, but caps accuracy and makes the deepest feature-distillation term nearly spatial-free. CIFAR fix is a 3×3 stride-1 conv1 with `maxpool = nn.Identity()`. |
| `train_student` | `scheduler.step(loss)` passes the final *batch's* loss, not the epoch mean, so `ReduceLROnPlateau` reacts to batch noise. |
| `train_teacher` | The `lr` argument is ignored; line 228 hardcodes `1e-3`. |
| `train_teacher` | Returns early if the checkpoint exists. Change the architecture without deleting the `.pth` and you get a stale model or a load error. |
| line 27 | `CIFAR10(root='./data', ...)` would download into this repo's benchmark `data/` directory. Point it at a gitignored path before running. |

### Running it

Needs `torchvision`, which is not in `requirements.txt` (the benchmark pipeline has no
PyTorch dependency). It also trains three networks for 25 epochs each — a job for a GPU,
not a CPU-only install. Colab is the natural home for it.
