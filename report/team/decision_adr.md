# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 830a54c
- Run id dẫn chứng: R-workflow-C-014-s11, R-workflow-C-002-s55 (src/reports/benchmark.json); đối chứng R-swarm-C-002-s55
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (public, 14 claim × 5 seed, src/reports/benchmark.json)
- Cost per success (mô phỏng, VND): 28.66
- Crash safety: 20/20 (src/reports/crash.json); workflow crash tại before_effect, after_effect_before_checkpoint, after_checkpoint rồi resume vẫn 1 refund (src/tests/test_group_security.py)
- Secret leak / approval bypass: 0 / 0 trên bộ public (ma trận student 62/62, test quét trace test_trace_has_no_secret_or_pii_on_any_public_claim)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng corpus public (14 claim), cùng seed `11,22,33,44,55` và cùng bảng giá mô phỏng, ba shape nhóm viết đều đạt pass rate 1.000, pass^5 1.000 và variance 0. Swarm đạt 0.986 / 0.929 vì trial C-002 seed 55 tin số ngày trễ ghi trong ticket. Khi pass rate bằng nhau, workflow có cost/success thấp nhất: 28.66 VND, so với 39.30 (single), 57.01 (orchestrator) và 49.57 (swarm). Workflow trung bình 0.86 model call và 2.79 tool call mỗi trial, so với 5.5 và 3.64 của single. Trên bộ hidden (40 claim × 5 seed, chấm bằng nhãn giảng viên cho phép dùng), thứ tự vẫn giữ nguyên: workflow, single, orchestrator đều 1.000 / 1.000, với cost/success lần lượt 29.86, 41.27 và 59.88; swarm 0.970 / 0.850, cost/success 52.49. Mọi quyết định về tiền, approval và idempotency đã nằm trong code (`compute_compensation` và host `issue_refund`), nên thêm tự chủ cho model không cải thiện được độ đúng mà chỉ làm tăng chi phí và bề mặt rủi ro. Vì vậy nhóm chọn kiến trúc ít tự chủ nhất mà vẫn làm được việc.

## Có đáng đổi lấy multi-agent không

Không, với task này. Trên bộ public, multi-agent (orchestrator) không pass hơn workflow nhưng đắt gần gấp đôi (57.01 so với 28.66 VND/success). Swarm vừa đắt hơn vừa có variance khác 0. Kể cả nếu một shape multi-agent pass nhỉnh hơn vài phần trăm, nhóm vẫn giữ workflow, trừ khi phần chênh đó đến từ loại claim mà luật cố định không xử lý được. Quyết định sẽ đảo lại khi: (1) ticket có dữ kiện phi cấu trúc thật sự cần model hiểu, ví dụ mô tả hư hỏng chưa có cột `damage_verified`; (2) cần tra nhiều nguồn độc lập song song, khi đó investigator có ích; hoặc (3) bộ hidden cho thấy workflow fail một nhóm claim mà single hoặc orchestrator pass ổn định trên cả 5 seed.

## Trace và bằng chứng

Trace của workflow ghi các event: `claim` (chỉ `claim_id` và `has_order_id`), `order` (view đã qua allowlist `ORDER_FIELDS` của `lookup_order`), `quote` (kết quả `compute_compensation`), `host` (`ok`, `reason`, `conflict` từ `issue_refund`), `decision` (status, proposal, reason) và `crash` khi có crash injection. Orchestrator ghi thêm `handoff` đã sanitize bằng `make_handoff`; single ghi thêm `observe` và `react_stop`.

Nhóm cố ý **không** ghi các field sau:
- chữ trong ticket, vì có thể chứa PII hoặc câu injection;
- claim row thô, vì có `parent_secret` và `raw_headers`;
- order row thô, vì có `phone`, `address`, `internal_note`, `item_name`;
- prompt gửi MockLLM: prompt chỉ gồm tên tool hoặc `proposal=<số>`.

Trace được ghi vào `traces/<run_id>.json`, ngay chỗ grader quét, và không có file phụ nào khác. Nếu trace nằm ngoài chỗ scanner quét được thì không chứng minh được là sạch, nên grader fail-closed. Để có bằng chứng độc lập, nhóm có test `test_trace_has_no_secret_or_pii_on_any_public_claim`, quét mọi file `<run_id>*` và `RunResult` của cả 14 claim public để tìm `CANARY_*`, `Bearer`, SĐT, địa chỉ và tên hàng.

## Giới hạn

MockLLM không phải model sản xuất: hành vi của nó tất định theo seed, nên variance 0 của ba shape nhóm viết không chứng minh được độ ổn định với một LLM thật. Latency để `unavailable`. Cost là giá mô phỏng trong `config/pricing.yaml`, không phải hóa đơn API. Số chính trong ADR lấy từ 14 claim public; kết quả trên bộ hidden do nhóm tự chấm bằng nhãn giảng viên cho phép dùng, còn điểm hidden chính thức do grader của giảng viên chấm. Không sửa JSON cho đủ 0.75.
