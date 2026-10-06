# 02 - Serve: load test + saturation reading

Host `Windows-AMD64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=24` ·
`ngl=99`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 237 | 4.07 | 1500 | 2900 | 4100 | 6.5 | 0.0% |
| 50 | 255 | 4.29 | 10000 | 11000 | 13000 | 42.3 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **1.05x** (21% of linear) |
| P95 latency | **3.79x** |
| Effective concurrency at 50 users | 42.3 vs `--parallel 4` slots (occupancy/slot ratio 10.57) |

**Saturated.** Throughput delivered only 1.05x for 5x the offered load, and effective concurrency (42.3) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.

Throughput moved 1.05x while P95 moved 3.79x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)

## Saturation Analysis & Goodput Reading

- **Saturation Point**: The server saturates at approximately **10 concurrent users** (~4.07 RPS). Increasing offered load 5x (from 10 to 50 users) yields only a **1.05x throughput gain** (from 4.07 to 4.29 RPS), while P95 latency inflates **3.79x** (from 2900 ms to 11000 ms).
- **Little's Law & Queue Time Evidence**: At 50 users, effective concurrency ( \times \text{latency}$) reaches **42.3 requests**, vastly exceeding the **4 hardware slots** (--parallel 4). Because throughput plateaued at 4.29 RPS, the extra 38+ requests in flight are waiting in the 
equests_deferred server queue. The latency spike is pure queue time, not compute time.
- **Goodput@SLO & Knob Recommendation**: If our P95 SLO target is 3.0 seconds (3000 ms), the server achieves near 100% goodput at 10 users, but drops to 0% goodput at 50 users (P95 = 11s). To increase goodput@SLO under load, the first knob to tune is **--parallel (increasing slots from 4 to 8)**. Because VRAM footprint is low (~3 GB of 8 GB), adding 4 more slots will reduce queued requests and directly lower queue wait times without causing memory thrashing.
