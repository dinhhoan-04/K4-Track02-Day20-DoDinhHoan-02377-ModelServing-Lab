# 02 - Continuous batching under load (u50)

Host `Windows-AMD64` · `--parallel 4` · 15 samples over
60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.96 of 4 slots (99%) |
| `requests_processing` | 4 |
| `requests_deferred` | 42 |
| `kv_cache_usage_ratio` | n/a  not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 28950 |

Highest sampled value was **3.96 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.

## Observation & Batching Analysis

- **Continuous Batching Proof**: The peak 
_busy_slots_per_decode reached **3.96 of 4 slots (99% utilization)**. This proves that llama-server is actively interleaving and packing up to 4 concurrent requests into shared decode steps on the GPU.
- **Slot Capacity & Deferred Queue**: 
equests_processing reached the maximum hard limit of 4 slots, while 
equests_deferred peaked at 42 requests. Because 50 users were concurrently sending prompts, incoming traffic exceeded the 4 available slots, forcing remaining requests into the server queue.
- **Queueing vs Compute**: The deferred queue directly explains the inflation of P95/P99 latencies during heavy load. While active slots remain compute/memory-bound during decode steps, the additional latency experienced by users beyond 4 concurrent requests is pure queue wait time.
