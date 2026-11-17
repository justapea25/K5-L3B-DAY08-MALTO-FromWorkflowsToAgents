# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: MALTO
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): `5972259`

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
| B single | Vòng `run_react` tối đa 8 bước; `decide` (một MockLLM call mỗi bước) chọn lần lượt `get_claim_view`, `lookup_order`, `lookup_refund_history`, `compute_compensation` | Model chỉ chọn tool đọc; quote lấy từ kết quả tool `compute_compensation` (code tính, chỉ gọi một lần), không lấy số nào do model đưa ra | `settle()` |
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
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 39.30 | 8.86 / 10 | 5.50 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 57.01 | 4.36 / 5 | 2.71 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.00 |

- Trial fail duy nhất là `R-swarm-C-002-s55`: swarm tin ticket "trễ 5 ngày" thay vì `delay_days = 2`, trả `resolved` thay vì `denied`.
- Crash safety: `20/20` (`src/reports/crash.json`). Crash suite chủ yếu kiểm host và swarm, nên nhóm thêm `test_crash_then_resume_pays_exactly_once` cho ba shape × ba điểm crash; sau khi resume vẫn đúng một refund 35.000 và một audit `refund_committed`.
- Cổng host sau lần gộp hiện tại: **104 passed, 248 deselected**. Ma trận student: **248/248**.
- Bộ security riêng của Khánh Linh: **15/15**, không skip, nguồn `src/reports/security.json`.
  Gồm 9 crash/resume, 3 quét secret/PII/console, 3 kiểm trace ở các nhánh trả sớm.
- Bộ 15 ca security từ nhánh đội được giữ riêng tại `src/tests/test_group_security_regressions.py`;
  vẫn chạy trong cổng host, không bị thay thế khi gộp. Ba shape đều qua cả ba điểm crash.
- Research card chính là R2: swarm tham chiếu 69/70 → swarm_verified 70/70,
  cost/success 49.57 → 48.72 VND mô phỏng (`ablation_verification.json`).
  Bản R4 của đội và báo cáo workflow/single được giữ tại `research_card_r4.md` và
  `ablation_workflow_vs_single.json`.

Tự kiểm trên `student_drop/` (`src/reports/hidden_selfcheck.json`): 3 shape × 200 trial, 0 trial lỗi, 0 trial nghi lộ secret.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- Hai phía cùng sửa 6 file nên Git chặn merge. Đã giữ bộ test của cả hai phía,
  research card R2 chính và R4 bổ sung, thông tin đủ 4 thành viên. Test host,
  student và báo cáo được chạy lại trên tổ hợp code sau gộp; chưa tự commit/push.

- **Không tách được module helper.** Grader hidden chỉ lấy ba file shape, nên một module mới trong `lab8/shapes/` sẽ bị bỏ qua và làm lỗi import. Cách xử lý: đặt `settle()` và `finish_status()` trong `workflow.py`, hai shape kia import từ đó.
- **`run_react` chỉ đưa cho `decide` kết quả của tool gần nhất.** `decide` giữ scratchpad (`memory`) theo tên tool; sau vòng lặp, code lấy quote đã tính một lần từ tool `compute_compensation`. Model không đưa ra số tiền.
- **Crash suite 20 điểm không chạy shape của nhóm.** Cách xử lý: thêm test crash và resume riêng cho cả ba điểm crash, để ADR có bằng chứng cho đúng shape được chọn.
- **Nguy cơ lộ PII khi debug.** Cách xử lý: không ghi ticket hay row thô vào trace, và có test quét trace của cả 14 claim để tìm `CANARY_*`, `Bearer`, SĐT, địa chỉ và tên hàng.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

- MockLLM không phải model sản xuất; latency là `unavailable`. MockLLM tất định theo seed và không ảnh hưởng quyết định, nên variance 0 của single và orchestrator không nói lên độ ổn định với LLM thật.
- Kết luận dựa trên 14 claim public. Bộ hidden của đề có thêm homoglyph, principal lẫn, approval mượn của claim khác…; nhóm xử lý các trường hợp này nhờ host và allowlist của tool. Public pass không chứng minh đã đạt hidden; điểm hidden do grader của giảng viên chấm.
- So sánh workflow → single trong R4 bổ sung cho thấy khoảng 80% chênh lệch chi phí được hạch toán vào số tool call. Đây là phân rã chi phí, chưa cô lập tác động nhân quả của topology vì hai implementation gọi khác tập tool. R2 chính chỉ thay nhánh swarm ghi đè dữ kiện DB từ ticket.
- Hướng cải thiện: mở rộng test ngoài public và thử model thật với ngân sách kiểm soát. Biến thể swarm_verified hiện chỉ tắt lỗi có chủ ý; không chứng minh một verifier tổng quát đã giải quyết được mọi lỗi multi-agent.
- Quyết định chọn workflow sẽ đổi nếu ticket chứa dữ kiện phi cấu trúc mà code không đọc được (xem ADR).

## 8. Tài liệu tham khảo

- Cemri và cộng sự, [Why Do Multi-Agent LLM Systems Fail?](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html), NeurIPS 2025; nguồn của R2 chính.
- `docs/business_rules.md`, `docs/contracts.md`, `docs/metrics.md`, `docs/architecture.md` của repo lab.
- Zhang et al., *Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems*, EMNLP 2026. https://arxiv.org/abs/2609.05933 · https://aclanthology.org/2026.emnlp-main.798/. Dùng cho `research_card_r4.md` bổ sung; kết quả có confounder về tập tool.
