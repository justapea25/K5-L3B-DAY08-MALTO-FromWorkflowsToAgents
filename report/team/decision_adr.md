# Biên bản quyết định kiến trúc

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: Chưa commit theo yêu cầu của thành viên; cần điền hash chứa triển khai workflow sau khi tự commit, trước khi nộp.
- Run id dẫn chứng: R-workflow-C-014-s11 (proposal 150000 VND, refund mới 120000 VND); tổng hợp tại src/reports/benchmark.json.
- Pass rate / pass^5 / seed min-max / variance: 1.0 / 1.0 / 1.0–1.0 / 0.0; 70/70 trial public, 14 claim × 5 seed (11,22,33,44,55).
- Cost per success (mô phỏng, VND): 34.285714285714285 (src/reports/benchmark.json); không phải chi phí API thật.
- Crash safety: 20/20 theo src/reports/crash.json (bộ host); workflow đã kiểm trực tiếp crash/resume ở cả before_effect, after_effect_before_checkpoint và after_checkpoint, mỗi lần vẫn một refund và một audit committed; T12 của ma trận workflow cũng pass.
- Secret leak / approval bypass: Không phát hiện trên các ca public của workflow và 5 test riêng; host từ chối các ca approval không hợp lệ. Chưa có kết quả hidden; không suy rộng thành bảo đảm cho mọi đầu vào.

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Đây là quyết định tạm thời cho phần workflow, chưa phải kết luận cuối của cả nhóm.
Trên cùng 14 claim public và 5 seed, workflow pass 70/70, pass^5 = 1.0,
variance = 0.0 và cost/success ≈ 34.29 VND mô phỏng. Swarm tham chiếu pass
69/70, pass^5 ≈ 0.928571 và cost/success ≈ 49.57 VND. Workflow bỏ qua ticket
khi tính tiền và chỉ dùng order cùng policy hiện hành, nên tránh được lỗi T02
ở seed 55 của swarm. Các quyết định nghiệp vụ theo chuỗi cố định phù hợp với
workflow, không cần gọi model để chọn tool hay số tiền.

`single` và `orchestrator` hiện vẫn là stub, mỗi shape pass 0/70 trong báo cáo
nền hiện tại. Không dùng các số 0 này để kết luận kiến trúc đó kém hơn; phải
chạy lại cùng lệnh sau khi hai thành viên hoàn tất triển khai, rồi chốt ADR.

## Có đáng đổi lấy multi-agent không

Ở trạng thái hiện tại, chưa có bằng chứng để đổi từ workflow sang multi-agent.
Chỉ cân nhắc đổi sau khi các shape còn lại hoàn tất và được đo trên cùng
corpus, seed, bảng giá và evaluator. Một shape khác phải giữ được các điều kiện
an toàn, cải thiện độ đúng hoặc giải quyết được trường hợp workflow chưa xử lý,
và có mức chi phí/dao động mà nhóm chấp nhận. Cần bổ sung kết quả hidden tự kiểm
khi được phát dữ liệu; public pass 100% không thay thế điểm hidden.

## Trace và bằng chứng

Workflow ghi `claim_lookup` (found), `order_lookup` (visible, reason), `quote`
(amount_vnd, reason, clause_ids, parts), `refund_request` (proposal_amount),
`refund_result` (ok, reason) và `decision` (status, reason). Các nhánh trả sớm
cũng dùng `finish()` để ghi file trace với `run_id` khớp kết quả. Trước khi
`InjectedCrash` truyền ra ngoài, khối `finally` ghi trace; kết nối được đóng
bởi `finally` của `run_claim`.

Không ghi raw ticket, parent_secret, headers, phone, address, item_name,
internal_note hoặc toàn bộ claim/order row. Không tạo log phụ hay in dữ liệu
nhạy cảm ra stdout. File trace nằm trong `src/traces/`, tên bắt đầu bằng
`run_id`, đúng phạm vi scanner. Trace và SQLite được gitignore.

Test injection còn đối chiếu toàn bộ ledger trước/sau và quét kết quả, trace,
stdout/stderr để bảo đảm chỉ thị trong ticket không gây ghi tiền hoặc lộ marker.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.

Workflow hiện không gọi MockLLM (0 model call); cost là chi phí tool mô phỏng.
Báo cáo benchmark được sinh bằng `lab8.benchmark`, báo cáo crash bằng
`lab8.crash_test`; không sửa tay JSON. Báo cáo này chưa có kết quả hidden,
commit chốt, hoặc so sánh với single/orchestrator đã triển khai. Người phụ
trách tích hợp cần cập nhật các mục đó trước khi nộp.
