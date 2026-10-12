# Development model screening

## Gemma 2 9B Instruct — first run

`google__gemma-2-9b-it__20261012T012807418668Z.zip` contains the unmodified Colab
export: manifest, 27 response records (15 single-turn items and 12 conversation
turns), and manual-review CSV. Uploaded October 11, 2026, America/Chicago; archive
name uses the runtime's UTC clock.

- Model revision: `11c9b309abf73637e4b6f9a3fa1e92e615547819`.
- Dataset commit: `7d1080675a76f4aa829f3551625c48840ca6834c`.
- NF4 double quantization; greedy decoding; 256-token answer cap.
- No recorded generation errors; all 27 responses reached the answer cap.

Preserve this preliminary run. Truncation prevents definitive whole-response
behavioral judgments; the rerun notebook raises the cap to 1,024 while retaining
the model revision and dataset snapshot. Download and keep the new run separately.
These are development outputs, not scored final benchmark results.
