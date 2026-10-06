# 01 - Tune: thread-count sweep

Model `gemma-4-E2B-it-UD-Q4_K_XL.gguf` · host `Windows-AMD64` · llama.cpp `b10488`
CPU: **24 physical · 32 logical** cores · `ngl=99` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 117.7 | 100% |
| 12 | 118.0 | 100% |
| 24 | 117.9 | 100% |
| 32 | 114.6 | 97% |
| 64 | 117.9 | 100% |

**Best**: `-t 12` at 118.0 tok/s
**Slowest tested**: `-t 32` at 114.6 tok/s (1.03x spread)
**Against the physical-core default** (`-t 24`, 117.9 tok/s): 1.00x

Use this in your run:

```bash
LAB_N_THREADS=12 make bench
```

## Observation & Mechanism Explanation

- **Flat Curve Observation**: Across all thread counts (-t 1 to -t 64), throughput remains almost perfectly flat at **~117.7 – 118.0 tok/s** (with a negligible spread of 1.03x). -t 12 yields 118.0 tok/s while -t 1 yields 117.7 tok/s.
- **Architectural Cause (GPU Offload)**: Because 
gl=99 is active, all model layers are offloaded to the NVIDIA GeForce RTX 4060 GPU VRAM. During the decode phase, tensor operations and memory access are executed by CUDA kernels on the GPU's dedicated GDDR6 VRAM channels.
- **Why CPU Threads Do Not Bottleneck**: The host CPU is only responsible for queuing CUDA kernel launches via the NVIDIA driver stream. Increasing CPU thread count from 1 to 64 neither increases GPU memory bandwidth nor parallelizes GPU execution further. A single CPU thread is sufficient to keep the GPU pipeline saturated without CPU context-switching overhead.
