# Bonus - GPU offload sweep

Host `Windows-AMD64` · backend(s) `nvidia_cuda, vulkan` ·
llama.cpp `b10488` · `threads=24` · metric `tg128`

| -ngl | tg128 (tok/s) | vs -ngl 0 | vs best |
|:--|--:|--:|--:|
| 0 | 33.4 | 1.00x | 29% |
| 8 | 42.5 | 1.27x | 36% |
| 16 | 53.4 | 1.60x | 46% |
| 24 | 73.7 | 2.21x | 63% |
| 32 | 93.7 | 2.81x | 80% |
| 99 | 116.6 | 3.49x | 100% |

Best: `-ngl 99` at 116.6 tok/s
-- 3.49x faster than CPU-only.

Where the curve flattens tells you the model ran out of layers to move. Where it
*peaks below* full offload tells you something did not fit and the accelerator
started paying to fetch weights it could not hold.

## Finding & Hardware Explanation

- **Full Offload Dominance**: Full GPU offload (-ngl 99) achieves the highest generation throughput of **116.6 tok/s**, yielding a **3.49x speedup** over CPU-only execution (-ngl 0, 33.4 tok/s).
- **Linear Partial Offload Scaling**: As layers are offloaded incrementally from -ngl 0 to 32, performance scales predictably: 8 layers (42.5 tok/s, 1.27x), 16 layers (53.4 tok/s, 1.60x), 24 layers (73.7 tok/s, 2.21x), 32 layers (93.7 tok/s, 2.81x). Each offloaded layer reduces CPU system RAM bandwidth requests and transfers layer execution to high-bandwidth GDDR6 GPU VRAM.
- **VRAM Headroom**: Because Gemma 4 E2B Q4 weights occupy ~2.97 GB, the entire model fits comfortably within the RTX 4060's 8 GB VRAM. There is zero host-to-device memory thrashing over PCIe during decode steps, allowing full offload to reach maximum throughput.
