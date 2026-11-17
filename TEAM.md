# Nhóm MALTO

## Thông tin nhóm

- Tên nhóm: MALTO
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-MALTO-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo: https://github.com/justapea25/K5-L3B-DAY08-MALTO-FromWorkflowsToAgents
- Nhánh làm việc hiện tại: `main`; nhánh nộp và commit chốt: nhóm xác nhận sau khi tích hợp.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Đặng Minh Thu | 2A202604009 | 26ai.thudm@vinuni.edu.vn | minhthu27 | Orchestrator + handoff (shape C) |
|   2 | Nguyễn Xuân Khánh Linh | 2A202603801 | nxklinh@gmail.com | [linkiewinkie](https://github.com/linkiewinkie) | Durability, security + eval |
|   3 | Đậu Hoàng Minh | 2A202604011 | 26ai.minhdh4@vinuni.edu.vn | [justapea25](https://github.com/justapea25) | Workflow (shape A) + tích hợp repo |
|   4 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Đặng Minh Thu | Orchestrator + handoff (shape C) | `830a54c`: orchestrator.py, handoff allowlist, trace handoff đã làm sạch | `tests/test_group_orchestrator.py`: `test_orchestrator_traces_only_sanitized_readonly_handoff`, `test_handoff_refuses_write_tool`, `test_handoff_drops_parent_context_from_facts` |
| Nguyễn Xuân Khánh Linh | Durability, security + eval | `b4076c8`: test ledger/idempotency/injection, sinh `src/reports/benchmark.json` và `crash.json` bằng công cụ có sẵn | `src/tests/test_group_workflow.py`: `test_injection_cannot_override_order_or_leak_context`, `test_unknown_claim_returns_failed_with_trace_and_no_write`, `test_missing_order_id_does_not_use_order_from_ticket`, `test_t14_passes_full_quote_and_pays_only_the_difference`, `test_t14_retry_keeps_one_refund_and_one_committed_audit` |
| Đậu Hoàng Minh | Workflow (shape A) + tích hợp repo | `aa39dd7`: `workflow.py` và hàm dùng chung `settle()` / `finish_status()`; `28f72f0`, `099e004`: gộp nhánh thành viên vào `dev`, xử lý conflict | `src/tests/test_group_workflow.py` (`c0b7841`): `test_workflow_ignores_injection_and_lying_delay_in_ticket`, `test_workflow_unknown_claim_fails_without_exception`, `test_workflow_retry_is_idempotent_and_proposal_stays_full_quote`, `test_workflow_missing_order_id_needs_info_without_ledger` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603801_NguyenXuanKhanhLinh

### Phần việc phụ trách

- Durability, security và eval; báo cáo cá nhân: [2A202603801_NguyenXuanKhanhLinh.md](report/team/2A202603801_NguyenXuanKhanhLinh.md).

### Đóng góp cụ thể

- Thêm 5 test kiểm ledger và idempotency (T14 chỉ hoàn phần chênh, gọi lại vẫn một refund và một audit), chống injection và không lộ marker trong kết quả, trace, stdout.
- Chạy kiểm thử và sinh bằng chứng public (`benchmark.json`, `crash.json`) bằng công cụ có sẵn; kiểm trực tiếp crash/resume ở 3 điểm crash.
- Viết một bản workflow riêng trong `b4076c8`. Khi tích hợp, nhóm giữ bản `workflow.py` có `settle()` vì single và orchestrator cần import hàm này.

### Bằng chứng

- Commit `b4076c8`; 5 test riêng trong `src/tests/test_group_workflow.py` đều pass.
- `src/reports/crash.json`: bộ crash host 20/20.

## 2A202604011_DauHoangMinh

### Phần việc phụ trách

- Workflow (shape A) và tích hợp repo; báo cáo cá nhân: [2A202604011_DauHoangMinh.md](report/team/2A202604011_DauHoangMinh.md).

### Đóng góp cụ thể

- Viết `src/lab8/shapes/workflow.py` theo các bước cố định: claim view → kiểm `order_id` → `lookup_order` → `compute_compensation` → `issue_refund` với quote đầy đủ.
- Viết hàm dùng chung `settle()` / `finish_status()` trong `workflow.py`, được single và orchestrator import. Đặt trong file shape vì grader chỉ chép 3 file shape.
- Thêm 4 test workflow: injection và ticket ghi sai số ngày trễ, claim không tồn tại, gọi lại T14, thiếu `order_id`.
- Tạo repo nhóm, gộp nhánh của các thành viên vào `dev` và xử lý conflict (`single.py`, `TEAM.md`, ADR, file bị commit kèm dấu conflict).

### Bằng chứng

- Commit: `aa39dd7` (workflow), `c0b7841` (test), `28f72f0` và `099e004` (gộp nhánh).
- Ma trận student workflow: 62/62; cổng host sau khi gộp: 89 passed.
- `src/reports/benchmark.json`: workflow pass rate 1.000, pass^5 1.000, cost/success 28.66 VND mô phỏng.
