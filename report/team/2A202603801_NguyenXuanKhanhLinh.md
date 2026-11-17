# Báo cáo cá nhân — Nguyễn Xuân Khánh Linh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Xuân Khánh Linh
- MSSV: 2A202603801
- Email: nxklinh@gmail.com
- GitHub: [linkiewinkie](https://github.com/linkiewinkie)
- Nhóm: MALTO, lớp L3B

## 2. Phần việc phụ trách

Workflow và tích hợp: triển khai `src/lab8/shapes/workflow.py`, thêm test riêng,
cập nhật bảng đóng góp và chuẩn bị ADR cùng bằng chứng public. Các shape
single/orchestrator và nghiên cứu ablation do các thành viên còn lại hoàn tất.

## 3. Đóng góp cụ thể

- Giữ nguyên chữ ký `run_claim`; đọc claim bằng `get_claim_view`, kiểm quyền
  qua `lookup_order`, tính quote bằng `compute_compensation` từ order/policy.
- Không dùng ticket để chọn đơn, số ngày trễ, policy hay số tiền. Workflow
  không cần gọi model, nên số model call bằng 0.
- Truyền quote đầy đủ cho `durability.issue_refund`, để host tự kiểm approval
  và trừ khoản đã hoàn. T14 có proposal 150000 VND và refund mới 120000 VND.
- Dùng `finish` lấy effect/audit thật từ database, ghi trace ở các nhánh trả
  sớm; chỉ ghi các field cần thiết. Đóng kết nối bằng `finally`.
- Truyền `crash_at`, không chặn `InjectedCrash`; ghi trace khi crash truyền ra.
- Thêm 5 test trong `src/tests/test_group_workflow.py`:
  `test_injection_cannot_override_order_or_leak_context`,
  `test_unknown_claim_returns_failed_with_trace_and_no_write`,
  `test_missing_order_id_does_not_use_order_from_ticket`,
  `test_t14_passes_full_quote_and_pays_only_the_difference`,
  `test_t14_retry_keeps_one_refund_and_one_committed_audit`.

## 4. Bằng chứng

Các lệnh dưới chạy trong `src/`, sử dụng môi trường `.venv` ở gốc repo:

```powershell
& ../.venv/Scripts/python.exe -m lab8.smoke
& ../.venv/Scripts/python.exe -m pytest -q tests/test_group_workflow.py
& ../.venv/Scripts/python.exe -m pytest -q -m student -o addopts= -k workflow
& ../.venv/Scripts/python.exe -m pytest -q
& ../.venv/Scripts/python.exe -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
& ../.venv/Scripts/python.exe -m lab8.crash_test --count 20 --out reports/crash.json
```

Kết quả kiểm tự động ngày 17/11/2026:

| Hạng mục | Kết quả |
| --- | --- |
| Smoke | Pass |
| Test riêng | 5 passed |
| Ma trận student workflow | 62 passed, 245 deselected |
| Cổng host | 59 passed, 248 deselected |
| Benchmark workflow | 70/70 trial public; pass rate = pass^5 = 1.0 |
| Seed min–max / variance | 1.0–1.0 / 0.0 |
| Cost/success | 34.285714285714285 VND mô phỏng |
| Bộ crash host | 20/20 |
| Kiểm trực tiếp workflow crash/resume | 3/3 điểm; mỗi claim một refund và một audit committed |

Nguồn số liệu benchmark: `src/reports/benchmark.json`; crash host:
`src/reports/crash.json`. Run dẫn chứng: `R-workflow-C-014-s11`.
Không đưa trace hoặc SQLite vào Git. Bộ crash 20/20 chủ yếu kiểm host;
không trình bày nó như 20 ca crash riêng cho workflow.

Hai shape single/orchestrator vẫn là stub, nên báo cáo so sánh hiện tại chỉ
là mốc tích hợp ban đầu. Cần chạy lại sau khi các thành viên hoàn tất.

Kiểm tra tích hợp đã chạy:

```powershell
& ../.venv/Scripts/python.exe -m lab8.check_submission
```

Kết quả: workflow pass 12/12 claim kiểm format ở seed 11; báo cáo benchmark,
crash, nhãn ADR và bảng đóng góp được đọc đúng. Còn 3 FAIL của phần nhóm:
`single` chưa triển khai, `orchestrator` chưa triển khai và `research_card.md`
chưa điền. Có 1 WARN vì chưa commit, đúng yêu cầu hiện tại của thành viên.
Sau khi nhận phần việc còn lại, chạy lại kiểm tra này và cập nhật báo cáo,
ADR cùng hash trước khi nộp.

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc cấu trúc repo, viết workflow và 5 test, chạy các lệnh kiểm
tự động, sinh bằng chứng bằng công cụ của lab và soạn tài liệu tiếng Việt.
Các số liệu ở trên lấy từ lần chạy thật, không sửa tay JSON. Máy chưa có
Python trên PATH nên dùng Python 3.12.14 đi kèm ứng dụng để tạo `.venv`,
cài đúng `src/requirements.txt` và chạy kiểm thử.

## 6. Tự đánh giá

