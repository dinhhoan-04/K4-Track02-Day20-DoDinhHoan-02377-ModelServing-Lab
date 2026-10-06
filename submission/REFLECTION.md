# Reflection — Day 20 Lab (Personal Report)

> **Đây là báo cáo cá nhân.** Số liệu của bạn **không** so sánh được với bạn cùng lớp
> — chỉ so **before vs after trên chính máy bạn**. Rubric chấm độ rõ ràng của setup,
> đo lường và **lập luận**, không chấm tốc độ tuyệt đối.

**Họ Tên:** Đỗ Đình Hoàn
**MSSV:** 02377
**Cohort:** AICB-P2T2
**Ngày submit:** 2026-10-06

---

## 1. Hardware & runtime  *(rubric 1, 2 — 10 điểm)*

- **OS:** Windows 11 (AMD64)
- **CPU:** 13th Gen Intel(R) Core(TM) i9-13900HX
- **Cores:** 24 physical / 32 logical
- **CPU extensions:** AVX2
- **RAM:** 15.7 GB
- **Accelerator:** NVIDIA GeForce RTX 4060 Laptop GPU (8188 MiB)
- **llama.cpp asset đã tải:** llama-b10488-bin-win-cuda-12.4-x64.zip
- **Model đã dùng:** Gemma 4 E2B (`LAB_MODEL=gemma4-e2b`)
- **Quantization:** UD-Q4_K_XL + UD-Q2_K_XL

**Chạy ở đâu:** laptop của tôi

**Setup story**: Lần đầu tiên khởi chạy script `detect-hardware.py` gặp lỗi encoding `charmap` do console Windows mặc định. Thêm `$env:PYTHONIOENCODING='utf-8'` đã khắc phục hoàn toàn. Tiến trình bootstrap tự động tải prebuilt release `b10488` có hỗ trợ CUDA và tải 5.2 GB weights Gemma 4 E2B vô cùng mượt mà.

---

## 2. Đo lường  *(rubric 3, 4, 5 — 20 điểm)*

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 3675 | 183 / 434 | 9.2 / 9.3 | 754 / 1020 / 1020 | 109.3 |
| UD-Q2_K_XL | 2.24 | 2962 | 175 / 318 | 8.0 / 8.2 | 677 / 821 / 821 | 124.7 |

**Quan sát**: Bản 2-bit (`UD-Q2_K_XL`) giải mã nhanh hơn **1.14x** (124.7 tok/s so với 109.3 tok/s), giảm 0.73 GB VRAM và tải model nhanh hơn ~700 ms. Tuy nhiên, khi hỏi cùng câu hỏi phức tạp trên 2 server (`make serve` vs `serve.py --compare`), bản 4-bit (`UD-Q4_K_XL`) duy trì ngữ pháp và khả năng suy luận tốt hơn rõ rệt. Vì GPU RTX 4060 có 8 GB VRAM, bản 4-bit (2.97 GB) nằm gọn trong VRAM nên `UD-Q4_K_XL` là lựa chọn tối ưu cho sản phẩm thực tế.

---

## 3. Serving under load  *(rubric 8, 9, 10 — 20 điểm)*

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|
| 10 | 4.07 | 1500 | 2900 | 4100 | 6.5 | 0.0% |
| 50 | 4.29 | 10000 | 11000 | 13000 | 42.3 | 0.0% |

- **Offered load tăng 5×, throughput thực tăng:** 1.05×
- **P95 tăng:** 3.79×
- **Effective concurrency ở 50 users:** 42.3 so với `--parallel` = 4 slots

**Peak `llamacpp:n_busy_slots_per_decode`**: 3.96 / 4 slots

**Saturation reading**: Server bão hoà ngay tại mức 10 users (4.07 RPS). Khi tăng tải gấp 5 lần (50 users), throughput chỉ tăng 1.05x (đạt trần bão hoà 4.29 RPS), trong khi P95 phồng lên 3.79x (từ 2.9s lên 11s). Theo Little's Law, effective concurrency đạt 42.3 requests, vượt xa 4 hardware slots (`--parallel 4`). Phần latency tăng thêm 8.1s chính là **queue time** (`requests_deferred` đạt 42). Để tăng goodput@SLO (ví dụ SLO P95 ≤ 3s), knob đầu tiên cần đổi là tăng `--parallel` lên 8 slot vì VRAM còn dư nhiều.

---

## 4. Integration  *(rubric 12, 13 — 15 điểm)*

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | Cloud Infrastructure | stub |
| N17 Data pipeline | Data ingestion | stub |
| N18 Lakehouse | Storage lake | stub |
| N19 Vector + features | Vector search | stub |
| N20 Serving | `llama-server` | real |

**Latency split**:

- embed: 0.0 ms
- retrieve: 0.0 ms
- llm: 2681.3 ms
- **stage chiếm nhiều nhất:** llm (100% của total)

**Reflection**: Giai đoạn LLM chiếm 100% latency đúng như kỳ vọng vì truy vấn keyword trên tập tài liệu nhỏ cực nhanh (dưới 1ms), trong khi quá trình sinh token của transformer tiêu tốn toàn bộ thời gian. Để giảm 2x latency của pipeline này, tôi sẽ tấn công vào giai đoạn LLM bằng cách bật **prompt prefix caching** (tránh re-prefill hệ thống prompt) và dùng quantization nhẹ hơn hoặc speculative decoding.

---

## 5. The single change that mattered most  *(rubric 11 — 10 điểm)*

**Change:** Offload toàn bộ layer của model lên GPU (`-ngl 0` → `-ngl 99`)

```
before:  33.4 tok/s (-ngl 0, CPU-only execution)
after:   116.6 tok/s (-ngl 99, full CUDA offload to RTX 4060)
speedup: 3.49x
```

**Tại sao nó work**:
Việc chuyển toàn bộ layer của model từ CPU sang GPU offload mang lại mức tăng tốc 3.49x nhờ giải quyết nghẽn **memory bandwidth**. Trong quá trình decode autoregressive, mỗi bước sinh token phải đọc lại toàn bộ weights của model từ bộ nhớ. Khi chạy thuần CPU (`-ngl 0`), tốc độ bị chặn bởi băng thông bộ nhớ RAM hệ thống (DDR5 ~40-60 GB/s). Khi offload lên GPU RTX 4060 (`-ngl 99`), toàn bộ 2.97 GB weights nằm trực tiếp trên VRAM GDDR6 có băng thông tới 272 GB/s, đồng thời các phép tính ma trận được thực thi song song trên hàng nghìn nhân CUDA, loại bỏ hoàn toàn cổ chai truyền dữ liệu qua bus PCIe trong giai đoạn decode.

---

## 6. Bonus  *(optional — tối đa 10 điểm)*

**Đã làm:** B2 (GPU offload sweep `-ngl 0..99`), B3 (3.49x speedup performance report), B4 & B5 (C8 Semantic Cache Offline demo & threshold sweep)

**Numbers:**

```
before:  33.4 tok/s (-ngl 0)
after:   116.6 tok/s (-ngl 99)
speedup: 3.49x
```

**Điều này nói lên gì mà deck chưa nói:**
1. GPU offload không phải lựa chọn nhị phân (bật/tắt) mà tăng trưởng tuyến tính theo số layer được chuyển lên GPU (`-ngl 8` = 42.5 tok/s, `-ngl 16` = 53.4 tok/s, `-ngl 32` = 93.7 tok/s) giúp tối ưu cho các hệ thống GPU bộ nhớ hạn chế (partial offloading).
2. Semantic Cache (tầng cache đầu tiên đứng trước KV Cache) giúp loại bỏ 100% chi phí compute (cả prefill lẫn decode) cho các câu hỏi paraphrase (đạt 38% hit rate trên demo stream, tiết kiệm 750ms). Tầng cache này bắt buộc phải được "salt" theo tenant để tránh rủi ro bảo mật side-channel leak thông tin giữa các user.

---

## 7. Điều làm bạn ngạc nhiên nhất

Sự hiệu quả của continuous batching trong `llama-server`: dưới tải nặng 50 users, gauge `n_busy_slots_per_decode` đạt đỉnh 3.96/4 slots (99% slot capacity), tự động gộp các request đồng thời vào chung bước decode trên GPU mà không có bất kỳ request nào bị lỗi HTTP failure (0.0% error rate).

---

## 8. Self-check trước khi push

- [x] `hardware.json` committed
- [x] `models/active.json` committed
- [x] `benchmarks/01-quickstart-results.md` committed (`make bench`)
- [x] `benchmarks/01-tuning-tg128.md` committed (`make tune`)
- [x] `benchmarks/02-server-results.md` committed (`make load-report`)
- [x] `benchmarks/02-server-batching-u50.md` hoặc `-metrics-u50.csv` committed (`make metrics`)
- [x] `benchmarks/locust-10_stats.csv` + `locust-50_stats.csv` committed (`make load-10` / `load-50`)
- [x] `benchmarks/03-integration-results.md` committed (`make pipeline`)
- [x] Mọi section **"required — replace this line"** trong các file `benchmarks/*.md`
      đã được thay bằng nhận xét của bạn
- [x] 5 screenshots trong `submission/screenshots/`
- [x] `make verify` → **exit 0**
- [x] Repo tên đúng mẫu `K4-L3-DAY20-HoVaTen-MSSV-ModelServing` (xem `docs/SUBMISSION.md`)
- [x] Repo GitHub ở chế độ **public**
- [x] Đã push và paste public URL vào VinUni LMS **trước 23:59 (UTC+7) ngày làm lab**
- [x] **Không** commit `models/*.gguf`, `runtime/` hay `.env` (đã có trong `.gitignore`)

---

## 9. Khai báo sử dụng AI  *(xem `docs/RULES.md` §3)*

Antigravity AI (Gemini 3.6 Flash) được sử dụng để hỗ trợ chạy thử nghiệm, thu thập metrics tự động, kiểm tra định dạng báo cáo markdown và tạo ảnh minh họa cho submission.
