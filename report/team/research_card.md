# Research card — R2: kiểm chứng dữ kiện trong swarm

## Phiếu của nhóm

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 — Failure taxonomy |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng | Cemri và cộng sự, *Why Do Multi-Agent LLM Systems Fail?*, NeurIPS 2025, Datasets and Benchmarks; [bài gốc](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html). Bằng chứng: phân tích trace và taxonomy MAST, không phải benchmark LogiX-VN. |
| CLAIM | Một kết luận gốc của nguồn | MAST phân loại lỗi của hệ multi-agent thành ba nhóm: thiết kế hệ thống, lệch phối hợp giữa agent và kiểm chứng nhiệm vụ. Một số lỗi cần thay đổi cấu trúc hệ thống, không chỉ sửa prompt. |
| BOUNDARY | Giới hạn kết luận | Nghiên cứu dựa trên các framework, model và nhiệm vụ trong MAST-Data. Paper không chứng minh biện pháp sửa lỗi cụ thể trong lab này. Việc xếp T02 vào nhóm kiểm chứng là diễn giải của nhóm. |
| HYPOTHESIS | Hướng và mức thay đổi dự kiến | Tắt nhánh swarm cho ticket ghi đè delay_days sẽ sửa T02 seed 55: số trial đạt dự kiến từ 69/70 lên 70/70; pass^5 từ 13/14 lên 14/14; cost/success không tăng. Giả thuyết được đặt theo lỗi đã công bố trong starter, không phải dự đoán mù. |
| METHOD | Biến giữ cố định và biến duy nhất thay đổi | Giữ MockLLM, cấu trúc prompt, host, policy, corpus 14 claim, seed 11/22/33/44/55, bảng giá và evaluator. Biến can thiệp duy nhất: cho phép hay ngăn nhánh REFERENCE_WEAKNESS ghi đè dữ kiện DB từ ticket. Đổi shape/run_id chỉ để tách trace. |
| FAILURE / METRIC | Lỗi dự kiến và phép đo | Lỗi kiểm chứng dữ kiện T02: ticket ghi trễ 5 ngày, DB ghi 2. Đo pass rate, pass^5, seed variance và cost/success; kiểm tra cặp kết quả khác nhau theo claim/seed. |

## Kết quả ablation

Chạy trong `src/` (dùng `../.venv/Scripts/python.exe` thay `python` nếu chưa activate):

```powershell
python -m lab8.benchmark --shapes swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_verification.json
```

Nguồn triển khai: `src/bonus/swarm_verified.py`, phái sinh có ghi nguồn từ
`lab8/shapes/swarm_reference.py`. Không sửa shape tham chiếu, host, dữ liệu hay evaluator.
Đây là thí nghiệm research card, chưa đăng ký bài bonus lấy điểm.

| Biến thể | Trial đạt | Pass rate | pass^5 | Variance | Cost/success (VND mô phỏng) |
| --- | --- | --- | --- | --- | --- |
| swarm tham chiếu | 69/70 | 0.985714 | 0.928571 | 0.000816327 | 49.566957 |
| swarm_verified | 70/70 | 1.000000 | 1.000000 | 0 | 48.715714 |

- File: `src/reports/ablation_verification.json`.
- Run đối chứng: `R-swarm-C-002-s55` và `R-swarm_verified-C-002-s55`.
- Giả thuyết đúng trên bộ public: pass rate tăng 1.428571 điểm phần trăm;
  pass^5 tăng 7.142857 điểm phần trăm; cost/success giảm khoảng 0.851242 VND.
- Chênh lệch chi phí là kết quả của can thiệp: bỏ lần tính lại quote từ dữ
  kiện ticket ở trial lỗi và tăng số trial thành công. Hai biến thể vẫn trung
  bình 3 model call/trial; không thay bảng giá để tạo lợi thế.
- Đây là lỗi được cài có chủ ý và chỉ một trial đổi kết quả. Không suy rộng
  thành kết luận mọi swarm hoặc model thật đều có cùng lỗi. Corpus nhỏ,
  MockLLM theo seed; không có hidden, latency là `unavailable`.
