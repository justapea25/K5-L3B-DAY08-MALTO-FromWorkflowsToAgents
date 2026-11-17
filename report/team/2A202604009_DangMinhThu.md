# Báo cáo cá nhân — 2A202604009_DangMinhThu

## 1. Thông tin thành viên

- Họ tên: Đặng Minh Thu
- MSSV: 2A202604009
- Email: 26ai.thudm@vinuni.edu.vn
- GitHub: minhthu27

## 2. Phần việc phụ trách

Công việc C: **shape C `orchestrator`** (`src/lab8/shapes/orchestrator.py`) và phần handoff đi kèm (`lab8.handoff.make_handoff`, danh sách tool chỉ đọc cho investigator). Test của shape nằm ở `src/tests/test_group_orchestrator.py`.

## 3. Đóng góp cụ thể

- **Luồng orchestrator:** orchestrator đọc claim bằng `get_claim_view` (allowlist cột, không `SELECT *`), rồi tạo handoff, chạy investigator, tính quote và gọi host. Trả sớm đúng trạng thái: `failed` khi claim không tồn tại, `needs_info` khi thiếu `order_id`, `escalated` khi investigator không thấy được order. Cả ba nhánh đều không ghi ledger.
- **Handoff có allowlist:** `make_handoff(..., facts={}, allowed_tools=["lookup_order", "lookup_refund_history", "compute_compensation"])`. Tôi chủ động để `facts` rỗng, nên parent context (`parent_secret`, raw headers, chữ trong ticket, phone/address) không có đường đi sang investigator. Cách này không dựa vào việc nhờ LLM tóm tắt rồi coi là đã làm sạch. Handoff chỉ chứa tool đọc, và `make_handoff` từ chối `issue_refund` hay `append_audit`.
- **Trace:** chỉ ghi handoff đã làm sạch (`trace.add("handoff", safe_dump(handoff))`), view order qua `safe_dump`, số tiền đã hoàn và quote của investigator. Trace không ghi parent context.
- **Ranh giới tiền:** investigator chỉ đọc. Orchestrator tự gọi `compute_compensation` bằng code từ `order_view["order"]`, rồi gọi `settle()`. `settle()` truyền **quote đầy đủ** vào `durability.issue_refund`, không tự trừ phần đã hoàn, vì host đã trừ phần hoàn trước đó trên cùng order. Quote bằng 0 thì `denied` và không gọi `issue_refund`. Số ngày trễ ghi trong ticket không ảnh hưởng quote.
- **Crash:** `crash_at` được chuyển thẳng xuống `settle()`. Khi gặp `InjectedCrash`, trace vẫn được ghi trước khi ném lại lỗi, nên run bị crash vẫn kiểm tra được.
- **Test (shape C):** `test_orchestrator_traces_only_sanitized_readonly_handoff` kiểm tra đúng một event handoff, field nằm trong `ALLOWED_FIELDS`, tool nằm trong `READONLY_TOOLS`, không có `issue_refund`, và `facts == {}`. `test_handoff_refuses_write_tool` kiểm tra handoff từ chối tool ghi. `test_handoff_drops_parent_context_from_facts` kiểm tra `phone` và `ticket` bị loại khỏi `facts`.
- **Số đo của shape C** (14 claim × 5 seed, `src/reports/benchmark.json`): pass rate 1.000, pass^5 1.000, variance 0, cost/success 57.01 VND, trung bình 2.71 model call và 5.5 tool call mỗi trial. Orchestrator đắt hơn workflow (28.66) gần gấp đôi mà không pass hơn, nên nhóm chọn workflow. Phần này nằm trong `decision_adr.md`.
- **Commit chính:** `830a54c`

## 4. Bằng chứng

- File: `src/lab8/shapes/orchestrator.py`, `src/tests/test_group_orchestrator.py`.
- `python -m lab8.check_submission`: shape `orchestrator` format đúng, 12/12 claim public pass ở seed 11.
- `src/reports/benchmark.json`: `by_shape.orchestrator` có pass_rate 1.0, pass_5 1.0, seed_variance 0.0, cost_per_success_vnd 57.01.
- `src/reports/crash.json`: crash suite 20/20.
- Run id mẫu: `R-orchestrator-C-001-s11`.

## 5. Công cụ AI đã dùng

Claude Code (VS Code). Tôi dùng nó để đọc cấu trúc repo, đối chiếu phần việc C với README và CHECKPOINTS. Tôi tự kiểm tra bằng cách đối chiếu từng số trong báo cáo với `benchmark.json`, và đối chiếu mô tả luồng với code trong `orchestrator.py` và với test `test_group_orchestrator.py`. Tôi cũng chạy `python -m lab8.check_submission`. Ban đầu `python -m pytest -q` lỗi import `tests.conftest` khi collect, vì Python hệ thống có một gói `tests` lạ trong `site-packages` che mất thư mục `tests/` của repo (`src/.venv` có sẵn lại là venv macOS/Linux nên không dùng được trên Windows). Tôi tạo venv Windows sạch (`src/.venv-win`), cài `requirements.txt` và chạy lại: `python -m pytest -q` cho 82 passed, `pytest -m student` cho 248 passed, `lab8.smoke` pass.

## 6. Tự đánh giá

- **Làm tốt:** giữ đúng ranh giới an toàn (investigator chỉ đọc, handoff allowlist, host là nơi duy nhất ghi tiền), và dùng số đo thay vì mặc định "multi-agent tốt hơn".
- **Hạn chế:** MockLLM tất định theo seed, nên variance 0 không chứng minh được độ ổn định với model thật. Với `facts={}`, investigator không nhận dữ kiện nào từ orchestrator; thiết kế này an toàn nhưng chưa tận dụng các field `FACT_KEYS`.
