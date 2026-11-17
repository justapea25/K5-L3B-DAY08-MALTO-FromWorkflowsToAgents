# Báo cáo nhóm — MALTO, Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Lớp: L3B; repo: `K5-L3B-DAY08-MALTO-FromWorkflowsToAgents`.
- Thành viên, vai trò và commit đóng góp: xem `TEAM.md`.
- Nhánh làm việc: `dev`.
- Commit chốt: chưa có; bản đang đánh giá có thay đổi chưa commit và chưa đủ điều kiện nộp.
- Trạng thái ngày 17/11/2026: workflow/single chạy được; orchestrator còn stub.

## 2. Mục tiêu và cách tiếp cận

Xử lý claim hoàn phí vận chuyển bằng bốn kiến trúc trên cùng dữ liệu và
chọn mức tự chủ phù hợp. Code quyết định số tiền, quyền truy cập và quyền
ghi; ticket là đầu vào không đáng tin cậy. Nhóm phân công workflow/integration,
single, orchestrator/handoff và durability/security/evaluation.

## 3. Giải pháp hiện có

Workflow đọc claim qua allowlist, kiểm principal khi tra đơn, tính quote từ
order và policy hiện hành, rồi gửi quote đầy đủ cho host. MockLLM chỉ soạn
câu trả lời sau khi tính quote. Single dùng vòng ReAct tối đa 8 bước để gọi
công cụ đọc; model không được gọi tool ghi. Sau vòng lặp, code lấy quote từ
`compute_compensation` và gọi helper `settle` của workflow.

Orchestrator hiện chưa triển khai; chưa có bằng chứng handoff của shape này.
Swarm tham chiếu tạo handoff cho investigator chỉ đọc. Nó có lỗi cố ý ở seed
chia hết cho 5: tin số ngày trễ trong ticket thay vì DB. Không sửa bản tham
chiếu; biến thể tắt nhánh lỗi chỉ dùng cho thí nghiệm research card.

Host kiểm approval gắn đúng claim và trần theo đơn, tự trừ refund trước đó.
Ledger cùng audit committed dùng một transaction. Checkpoint hỗ trợ resume;
ledger và idempotency key `refund:{claim_id}` mới chặn ghi trùng. Shape
truyền `crash_at` và cho `InjectedCrash` truyền ra ngoài để kiểm thử có thật.

Trace chỉ chứa quyết định, quote, tool view đã qua allowlist và trạng thái
host. Không ghi ticket thô, parent secret, headers, phone, address, item hay
internal note. Test security quét kết quả, trace/file phụ cùng run_id và cả
stdout/stderr; kiểm run_id và việc thay trace cũ ở các nhánh trả sớm.

## 4. Kết quả

Nguồn: `src/reports/benchmark.json`, 14 claim × 5 seed
(11,22,33,44,55), DB mới cho mỗi trial. Cost là VND mô phỏng; latency `unavailable`.
Steps đếm event trace nên phụ thuộc mức chi tiết logging, không phải latency.

| Shape | Trial đạt | Pass rate | pass^5 | Seed min–max | Variance | Cost/success | Mean/p95 steps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| workflow | 70/70 | 1.000000 | 1.000000 | 1.000000–1.000000 | 0.000000000 | 28.66 | 4.43/5 |
| single | 70/70 | 1.000000 | 1.000000 | 1.000000–1.000000 | 0.000000000 | 39.30 | 8.86/10 |
| orchestrator | 0/70 | 0.000000 | 0.000000 | 0.000000–0.000000 | 0.000000000 | — | 1.00/1 |
| swarm | 69/70 | 0.985714 | 0.928571 | 0.928571–1.000000 | 0.000816327 | 49.57 | 2.80/3 |

Số 0 của orchestrator phản ánh stub, không chứng minh kiến trúc orchestrator
kém hơn. Trước khi chốt so sánh phải hoàn tất shape này và chạy lại.

- `src/reports/crash.json`: bộ crash host 20/20; không coi đây là 20 ca riêng cho từng shape.
- `src/reports/security.json`: 10/15 ca đạt, 5 ca thất bại, không skip.
  Workflow và single mỗi shape đạt 5/5 (3 crash, 1 quét dữ liệu, 1 trace).
  Năm ca orchestrator thất bại vì chưa triển khai; chưa kết luận shape này an toàn.
- Cổng host hiện tại: 80 passed, 5 failed, 248 deselected; 5 lỗi đều thuộc
  orchestrator trong bộ security mới. Chưa đạt yêu cầu cổng host xanh.
- Ma trận student đầy đủ: 186 passed, 62 failed; 62 ca orchestrator chưa đạt.
- `check_submission`: 1 FAIL do orchestrator chưa triển khai, 1 WARN do chưa
  commit. Workflow/single, báo cáo benchmark/crash và research card được đọc đúng.
- Ablation: swarm 69/70 → swarm_verified 70/70; cost/success 49.57 → 48.72.
  Chi tiết kiểm soát biến và giới hạn: `research_card.md` và
  `src/reports/ablation_verification.json`.

Tạm giữ workflow làm ứng viên: cùng độ đúng public với single, chi phí mô
phỏng thấp hơn. Quyết định cuối và commit chốt phải cập nhật trong
`decision_adr.md` sau khi tích hợp đầy đủ. Chưa có kết quả hidden.

## 5. Khó khăn và cách xử lý

Bản `dev` nhận về có dấu xung đột Git trong `workflow.py` và test workflow,
gây SyntaxError và 8 lỗi lúc thu thập test. Đã gộp lại, giữ helper
`finish_status`/`settle` mà single nhập và giữ test của hai nhánh. Không xóa
kiểm thử của đồng đội. Không sửa host, evaluator, config hoặc dữ liệu chuẩn.

Máy chưa có Python trên PATH: dùng Python đi kèm ứng dụng để tạo `.venv` ở
gốc repo và cài `src/requirements.txt`. Test quét dữ liệu cần DB mới cho mỗi
claim để đúng hợp đồng evaluator; chỉ các kịch bản retry/crash dùng lại DB.

## 6. Tổng hợp đóng góp

- Dau Hoang Minh: workflow, helper dùng chung, test workflow và integration theo báo cáo cá nhân.
- Le The Anh: single, tối ưu tính quote một lần và test single theo báo cáo cá nhân.
- Nguyễn Xuân Khánh Linh: bộ 15 ca security, công cụ sinh JSON từ pytest,
  research card/ablation, báo cáo đánh giá và sửa xung đột tích hợp.
- Thành viên orchestrator: nhóm cần bổ sung danh tính và kết quả khi bàn giao.

## 7. Hạn chế và việc cần chốt

MockLLM và một lỗi swarm có chủ ý không đại diện cho hệ sản xuất. Public
100% không chứng minh đạt ngưỡng hidden. Cần hoàn tất orchestrator, đưa
security từ 10/15 lên 15/15, giữ cổng host xanh, chạy lại benchmark/crash,
kiểm `check_submission`, bổ sung thành viên còn lại và commit chốt. Báo cáo
cá nhân cần phần tự đánh giá do từng thành viên tự viết. Bản này chưa sẵn sàng nộp.

## 8. Tài liệu tham khảo

- `docs/business_rules.md`, `docs/contracts.md`, `docs/metrics.md` của bộ starter.
- [Cemri và cộng sự, NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html); dùng làm khung phân loại,
  không dùng số liệu paper thay cho kết quả lab.
- Triển khai đối chứng: `src/lab8/shapes/swarm_reference.py`; biến thể có ghi
  nguồn tại `src/bonus/swarm_verified.py`.

Các lệnh tái lập nằm trong báo cáo cá nhân và `src/reports/README.md`.
