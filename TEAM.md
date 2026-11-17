# Nhóm MALTO

## Thông tin nhóm

- Tên nhóm: MALTO
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-MALTO-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo: https://github.com/justapea25/K5-L3B-DAY08-MALTO-FromWorkflowsToAgents
- Nhánh làm việc hiện tại: `dev`; commit chốt: chờ thành viên hoàn tất merge sau khi kiểm thử.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Đặng Minh Thu | 2A202604009 | 26ai.thudm@vinuni.edu.vn | minhthu27 | Orchestrator + handoff (shape C) |
|   2 | Nguyễn Xuân Khánh Linh | 2A202603801 | nxklinh@gmail.com | [linkiewinkie](https://github.com/linkiewinkie) | Durability, security + eval |
|   3 | Đậu Hoàng Minh | 2A202604011 | 26ai.minhdh4@vinuni.edu.vn | [justapea25](https://github.com/justapea25) | Workflow (shape A) + tích hợp repo |
|   4 | Le The Anh | 2A202603983 | 26ai.anhlt5@vinuni.edu.vn | [LETHESHIYING](https://github.com/LETHESHIYING) | Single agent (shape B) |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Đặng Minh Thu | Orchestrator + handoff (shape C) | `830a54c`: orchestrator.py, handoff allowlist, trace handoff đã làm sạch | `tests/test_group_orchestrator.py`: `test_orchestrator_traces_only_sanitized_readonly_handoff`, `test_handoff_refuses_write_tool`, `test_handoff_drops_parent_context_from_facts` |
| Nguyễn Xuân Khánh Linh | Durability, security + eval | `9ecf01f`: bộ 15 ca security, công cụ xuất JSON, research card R2 và báo cáo; `b4076c8`: kiểm ledger/injection/T14 trước đó | `src/tests/test_group_security.py`: 9 ca crash/resume, 3 quét secret/PII/stdout, 3 trace; giữ bộ test security từ dev trong `test_group_security_regressions.py` |
| Đậu Hoàng Minh | Workflow (shape A) + tích hợp repo | `aa39dd7`: `workflow.py` và hàm dùng chung `settle()` / `finish_status()`; `28f72f0`, `099e004`: gộp nhánh thành viên vào `dev`, xử lý conflict | `src/tests/test_group_workflow.py` (`c0b7841`): `test_workflow_ignores_injection_and_lying_delay_in_ticket`, `test_workflow_unknown_claim_fails_without_exception`, `test_workflow_retry_is_idempotent_and_proposal_stays_full_quote`, `test_workflow_missing_order_id_needs_info_without_ledger` |
| Le The Anh | Single agent (shape B) | `7390aaa`: cùng Codex hoàn thiện single agent, tính quote một lần và chuyển quote đầy đủ cho host; `1adafcb`: bổ sung test | `src/tests/test_group_single.py`: `test_single_computes_compensation_once` (resolved và denied), thực hiện cùng Codex |

## Cá nhân

Mỗi thành viên có báo cáo riêng trong `report/team/`:

| Thành viên | Báo cáo cá nhân |
| --- | --- |
| Đặng Minh Thu | [2A202604009_DangMinhThu.md](report/team/2A202604009_DangMinhThu.md) |
| Nguyễn Xuân Khánh Linh | [2A202603801_NguyenXuanKhanhLinh.md](report/team/2A202603801_NguyenXuanKhanhLinh.md) |
| Đậu Hoàng Minh | [2A202604011_DauHoangMinh.md](report/team/2A202604011_DauHoangMinh.md) |
| Le The Anh | [2A202603983_LeTheAnh.md](report/team/2A202603983_LeTheAnh.md) |
