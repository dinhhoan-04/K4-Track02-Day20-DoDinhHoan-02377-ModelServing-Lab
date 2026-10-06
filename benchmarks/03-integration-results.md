# 03 - Integrate: RAG pipeline run

Host `Windows-AMD64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.0 | 2706.0 | 2706.0 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.0 | 2674.9 | 2674.9 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.0 | 2662.9 | 2663.0 |

Mean per stage (ms): embed **0.0** · retrieve **0.0** ·
llm **2681.3** · total **2681.3**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Goodput@SLO counts only the requests per second that met the TTFT and TPOT targets.

**What problem does PagedAttention actually solve?**

> PagedAttention stores the KV cache in non-contiguous pages, which removes the internal fragmentation that wasted most GPU memory.

**When does splitting prefill and decode help?**

> Splitting prefill and decode helps because prefill is compute-bound and decode is memory-bandwidth-bound.


## Pipeline Component Declaration & Reflection

- **Component Status**:
  - N16 (Cloud/IaC): stub
  - N17 (Data pipeline): stub
  - N18 (Lakehouse): stub
  - N19 (Vector + features): stub (in-memory toy collection with keyword fallback)
  - N20 (Model Serving): **real** (llama-server on port 8080)

- **Dominant Stage Analysis**: The LLM stage is overwhelmingly dominant at **2681.3 ms (100% of total pipeline latency)**, whereas embedding and retrieval are ~0.0 ms. This perfectly matches expectations because in-memory keyword matching on small text corpora takes sub-millisecond time, while autoregressive transformer decoding consumes virtually all latency.
- **Optimization Strategy**: To cut pipeline latency in half (2x speedup), I would attack the **LLM stage** directly:
  1. Enable **prefix/prompt caching** so the repetitive system prompt and static context blocks skip the compute-heavy prefill phase across consecutive queries.
  2. Use a smaller/faster quantization (e.g. UD-Q2_K_XL or speculative decoding) to accelerate per-token generation speed during the decode phase.
