# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: MALTO
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Bài toán là xử lý claim hoàn phí vận chuyển theo bốn kiến trúc có mức tự chủ tăng dần (workflow → single → orchestrator → swarm), rồi chọn kiến trúc ít tự chủ nhất mà vẫn đúng. Ranh giới nhóm giữ xuyên suốt: số tiền, approval và chống ghi trùng do **code** quyết (`compute_compensation` cùng cổng host `durability.issue_refund`); model chỉ chọn tool đọc hoặc soạn chữ.

Thứ tự làm:
1. Viết workflow trước làm chuẩn đúng, gồm hàm dùng chung `settle()` (ánh xạ quote và kết quả của host sang `RunResult`).
2. Viết single và orchestrator dùng lại `settle()`, nên ba shape chỉ khác nhau ở **ai thu thập dữ kiện**.
3. Viết test riêng của nhóm, chạy crash suite và benchmark, rồi viết ADR và research card.

Hàm dùng chung đặt trong `workflow.py` chứ không tách module riêng, vì grader hidden chỉ chép ba file shape từ repo nhóm.

## 3. Giải pháp

| Shape | Đọc gì | Ai quyết định | Gọi host |
| --- | --- | --- | --- |
| A workflow | `get_claim_view` → `lookup_order` → `compute_compensation` theo thứ tự cố định | Code | `settle()` truyền quote đầy đủ vào `issue_refund(..., crash_at=crash_at)` |
| B single | Vòng `run_react` tối đa 8 bước; `decide` (một MockLLM call mỗi bước) chọn lần lượt `get_claim_view`, `lookup_order`, `lookup_refund_history`, `compute_compensation` | Model chọn tool đọc; sau vòng lặp, code tính lại quote từ order view đã qua allowlist, bỏ qua mọi output của model | `settle()` |
| C orchestrator | Orchestrator đọc claim view; investigator nhận handoff có tool `lookup_order`, `lookup_refund_history`, `compute_compensation` | Orchestrator tính quote bằng code từ order view của investigator | `settle()` |

Các luật chung:
- Thiếu `order_id` → `needs_info`. Không lấy mã đơn từ chữ trong ticket.
- Đơn không thấy, hoặc principal không sở hữu đơn → `escalated`.
- Quote 0 → `denied`, không gọi host.
- Quote > 0 → gọi host. Host từ chối thì trả `denied` với `proposal_amount` là quote đầy đủ, và host ghi audit `policy_denied`. Amount conflict → `failed`.
- `InjectedCrash` không bị bắt: trace được flush rồi exception được ném tiếp.

**Handoff:** dựng bằng `make_handoff`, `facts={}`, chỉ có tool đọc. Hàm `sanitize` chặn `parent_secret`, `raw_headers` và `CANARY_SECRET_`. Trace chỉ ghi handoff đã sanitize, không ghi parent context.

**Trace:** ghi các event `claim`, `order` (allowlist), `quote`, `host`, `decision` và `crash`; orchestrator thêm `handoff`, single thêm `observe` và `react_stop`. Trace không ghi chữ trong ticket, claim row thô hay order row thô.

## 4. Kết quả

Bộ public gồm 14 claim × 5 seed (`11,22,33,44,55`), giá mô phỏng, lấy từ `src/reports/benchmark.json`:

| Shape | Pass rate | pass^5 | Seed min–max | Variance | Cost/success (VND) | Mean / p95 steps | Model calls TB |
| --- | ---: | ---: | --- | ---: | ---: | --- | ---: |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | **28.66** | 4.43 / 5 | 0.86 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 47.87 | 8.86 / 10 | 5.50 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 57.01 | 4.36 / 5 | 2.71 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.00 |

- Trial fail duy nhất là `R-swarm-C-002-s55`: swarm tin ticket "trễ 5 ngày" thay vì `delay_days = 2`, trả `resolved` thay vì `denied`.
- Crash safety: `20/20` (`src/reports/crash.json`). Crash suite chủ yếu kiểm host và swarm, nên nhóm thêm `test_crash_then_resume_pays_exactly_once` cho ba shape × ba điểm crash; sau khi resume vẫn đúng một refund 35.000 và một audit `refund_committed`.
- Cổng host `python -m pytest -q`: 82 passed (54 test có sẵn và 28 test của nhóm trong `tests/test_group_{workflow,single,orchestrator,security}.py`). Ma trận student: 248/248.
- Tự kiểm trên `student_drop/`: TODO, chạy sau khi giảng viên phát bộ hidden.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- **Không tách được module helper.** Grader hidden chỉ lấy ba file shape, nên một module mới trong `lab8/shapes/` sẽ bị bỏ qua và làm lỗi import. Cách xử lý: đặt `settle()` và `finish_status()` trong `workflow.py`, hai shape kia import từ đó.
- **`run_react` chỉ đưa cho `decide` kết quả của tool gần nhất.** Cách xử lý: `decide` giữ một scratchpad (`memory`) theo tên tool, và sau vòng lặp code đọc order view từ scratchpad để tính lại quote. Model không bao giờ đưa ra số tiền.
- **Crash suite 20 điểm không chạy shape của nhóm.** Cách xử lý: thêm test crash và resume riêng cho cả ba điểm crash, để ADR có bằng chứng cho đúng shape được chọn.
- **Nguy cơ lộ PII khi debug.** Cách xử lý: không ghi ticket hay row thô vào trace, và có test quét trace của cả 14 claim để tìm `CANARY_*`, `Bearer`, SĐT, địa chỉ và tên hàng.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

- MockLLM không phải model sản xuất; latency là `unavailable`. MockLLM tất định theo seed và không ảnh hưởng quyết định, nên variance 0 của single và orchestrator không nói lên độ ổn định với LLM thật.
- Kết luận chỉ dựa trên 14 claim public. Bộ hidden có thêm homoglyph, principal lẫn, approval mượn của claim khác…; nhóm dựa vào host và allowlist của tool cho các trường hợp này, chưa tự kiểm từng loại.
- Hướng cải thiện: test thêm các claim kiểu hidden, như approval hết hạn hoặc bị thu hồi, đơn `in_transit`/`cancelled`, policy tương lai; làm bonus "swarm có verifier" để đo xem verifier kéo pass^5 của swarm lên được bao nhiêu và tốn thêm bao nhiêu.
- Quyết định chọn workflow sẽ đổi nếu ticket chứa dữ kiện phi cấu trúc mà code không đọc được (xem ADR).

## 8. Tài liệu tham khảo

- `docs/business_rules.md`, `docs/contracts.md`, `docs/metrics.md`, `docs/architecture.md` của repo lab.
- EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* (thư viện tham khảo slide 68–69), dùng cho research card R4.
