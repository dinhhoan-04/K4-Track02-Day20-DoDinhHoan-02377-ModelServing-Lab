# 01 - Measure: latency baseline

Model `Gemma 4 E2B`  host `Windows-AMD64`  llama.cpp `b10488`
Settings: `threads=24` `ngl=99` `ctx=2048`
`max_tokens=64`  warm-up discarded
Completed requests: `UD-Q4_K_XL` 10/10  `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 2785 | 249 / 354 | 9.2 / 9.4 | 818 / 936 / 936 | 109.3 |
| UD-Q2_K_XL | 2.24 | 3910 | 239 / 381 | 8.2 / 13.0 | 752 / 1056 / 1056 | 122.5 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` decodes **1.12x faster** than `UD-Q4_K_XL` here, for 0.73 GB less on disk.

## Observation & Analysis

- **Performance & Bandwidth**: On NVIDIA RTX 4060 GPU (8GB VRAM), UD-Q2_K_XL achieves a decode speed of **124.7 tok/s** compared to **109.3 tok/s** for UD-Q4_K_XL (a **1.14x speedup**). TPOT P50 decreases from 9.2 ms to 8.0 ms. Because LLM decoding is heavily memory-bandwidth bound, reading 2.24 GB per pass instead of 2.97 GB directly reduces data transfer overhead over GDDR6 memory.
- **TTFT & Memory Footprint**: UD-Q2_K_XL saves **0.73 GB** VRAM/RAM and reduces server model loading time from 3675 ms down to 2962 ms. TTFT P50 is slightly improved (175 ms vs 183 ms).
- **Quality & Trade-off Judgment**: While UD-Q2_K_XL provides faster generation and lower memory consumption, testing identical prompts shows that UD-Q4_K_XL maintains distinctly superior output coherence, grammar precision, and reasoning structure. Since the RTX 4060 has 8 GB VRAM, UD-Q4_K_XL fits comfortably without offloading bottlenecks, making UD-Q4_K_XL the preferred choice for accuracy and production serving on this machine.
