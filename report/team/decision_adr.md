# Biên bản quyết định kiến trúc

Giữ nguyên các nhãn dưới đây để `lab8.check_submission` đọc được.
Kết quả public được chạy lại sau khi gộp đủ ba shape ngày 17/11/2026; còn chờ commit merge.

- Shape chọn: workflow
- Commit hash: Chờ commit merge giữa 9ecf01f (security/eval) và 0f5dd9f (dev của đội); cần tự điền hash bản merge sau khi commit.
- Run id dẫn chứng: R-workflow-C-014-s11; R-workflow-C-002-s55; tổng hợp tại src/reports/benchmark.json.
- Pass rate / pass^5 / seed min-max / variance: 1.0 / 1.0 / 1.0–1.0 / 0.0; 70/70 trial public, 14 claim × 5 seed (11,22,33,44,55).
- Cost per success (mô phỏng, VND): 28.65857142857143; nguồn src/reports/benchmark.json.
- Crash safety: bộ host 20/20 (src/reports/crash.json); workflow, single và orchestrator mỗi shape đạt 3/3 ca crash/resume trong src/reports/security.json; bộ security riêng đạt 15/15.
- Secret leak / approval bypass: cả ba shape qua test quét secret/PII/console, injection, principal và approval bị thu hồi trong bộ security. Không phát hiện rò dữ liệu ở các ca đã kiểm; chưa tái kiểm hidden trong lần merge này.

## Vì sao shape này

Workflow và single cùng pass 70/70 trên cùng corpus/seed; cost/success lần
lượt 28.66 và 39.30 VND mô phỏng. Swarm tham chiếu pass 69/70,
pass^5 = 0.928571, cost/success = 49.57. Quy trình nghiệp vụ hiện tại tuần tự,
code xử lý được các quyết định về order/policy/approval mà không cần vòng
chọn tool, nên workflow là ứng viên phù hợp ở mức tự chủ thấp hơn.

Orchestrator của Đặng Minh Thu đã được tích hợp và đạt 70/70 public,
pass^5 = 1.0, variance = 0; cost/success = 57.01 VND mô phỏng. Workflow
vẫn có chi phí thấp nhất trong các shape đạt đủ public. Bộ host hiện đạt
104/104, ma trận student 248/248. Số liệu hidden do đội đưa vào báo cáo nhóm
được giữ kèm nguồn commit nhưng chưa có artifact tại máy này để tái kiểm.

## Có đáng đổi lấy multi-agent không

Chưa có bằng chứng public trong bản hiện tại để đổi từ workflow. Cân nhắc
đổi nếu shape khác giữ các điều kiện an toàn, cải thiện độ đúng trên các
trường hợp workflow không xử lý được và có chi phí/dao động chấp nhận được.
Ablation ở research card cho thấy sửa bước kiểm chứng dữ kiện đã đủ loại
lỗi T02 của swarm; không cần thay topology để sửa đúng lỗi này.

## Trace và bằng chứng

Workflow ghi claim có tồn tại/mã đơn, order view đã allowlist, quote, kết quả
host và quyết định cuối. Single bổ sung event quan sát tool và kết thúc
ReAct. `finish` ghi trace ở các nhánh trả sớm; khi crash, helper ghi trace
rồi ném lại InjectedCrash. Orchestrator ghi thêm handoff đã sanitize bằng
make_handoff, facts rỗng và chỉ cấp tool đọc cho investigator. Trace dùng run_id do make_run_id tạo, đặt trong
thư mục traces, không có log phụ ngoài phạm vi scanner.

Không ghi ticket thô, parent_secret, headers, phone, address, internal_note
hoặc item_name. Bộ security dùng giá trị fixture thật để quét kết quả,
file trace/file phụ cùng run_id và console; kiểm file mới và run_id cả ở
claim lạ, thiếu order_id, sai principal, denied và resolved.

## Giới hạn

MockLLM không phải model sản xuất; latency `unavailable`. Chi phí là mô
phỏng; số event trace không phải thời gian thực. Không sửa JSON bằng tay.
Bộ host đạt 104/104 và security riêng 15/15 sau gộp. Cần check_submission
đạt 0 FAIL, bổ sung hash merge và xác nhận bằng chứng hidden trước khi nộp.
Chưa tự tạo commit merge hoặc push. Trace/SQLite/.venv không đưa vào Git.
