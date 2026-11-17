# Báo cáo cá nhân — Nguyễn Xuân Khánh Linh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Xuân Khánh Linh
- MSSV: 2A202603801
- Email: nxklinh@gmail.com
- GitHub: [linkiewinkie](https://github.com/linkiewinkie)
- Nhóm: MALTO, lớp L3B

## 2. Phần việc phụ trách

Vai trò số 4: durability, security và evaluation. Phụ trách test bảo mật/
crash, bằng chứng JSON, research card và tổng hợp báo cáo nhóm.
Workflow/integration thuộc Dau Hoang Minh; single thuộc Le The Anh.

## 3. Đóng góp cụ thể

- Viết `src/tests/test_group_security.py` với 15 ca pytest sau tham số hóa:
  9 ca crash/resume (3 điểm × 3 shape), 3 ca quét secret/PII và 3 ca trace.
- Crash phải thật sự ném InjectedCrash; kiểm trạng thái effect/checkpoint
  đúng cửa sổ crash, resume và replay bằng seed khác vẫn chỉ một refund,
  một audit committed và có checkpoint.
- Quét secret/PII lấy từ fixture, kết quả, trace/file phụ cùng run_id và
  stdout/stderr. Các nhánh kiểm gồm resolved, sai principal, injection và
  approval bị thu hồi. Mỗi trial dùng DB riêng, không sửa dữ liệu chuẩn.
- Kiểm trace thay file cũ, đúng run_id/shape/claim, có events; phủ cả các
  nhánh trả sớm. Không skip orchestrator chưa triển khai.
- Viết `src/bonus/security_eval.py` xuất JSON từ kết quả pytest/JUnit thật;
  báo cáo không chép traceback hoặc giá trị nhạy cảm.
- Chuẩn bị ablation R2 tại `src/bonus/swarm_verified.py`, phái sinh có ghi
  nguồn từ swarm tham chiếu; chỉ tắt nhánh ticket ghi đè delay_days.
- Điền research card, báo cáo nhóm và cập nhật ADR bằng số liệu mới.
- Sửa xung đột Git đã bị commit trong workflow/test workflow. Giữ helper
  finish_status/settle mà single dùng và giữ test cả hai nhánh; không nhận
  tác giả implementation workflow/single của đồng đội.

Commit phần security/eval: `9ecf01f`. Commit `b4076c8` là phần kiểm thử
ledger/injection trước đó. Lần merge hiện tại gộp thêm `0f5dd9f` của đội,
giữ orchestrator mới, bộ test security bổ sung và research card R4 của đội.
Chưa tạo commit merge; cần tự điền hash bản merge vào ADR sau khi hoàn tất.

## 4. Bằng chứng

Ngày chạy: 17/11/2026. Lệnh chạy trong `src/`:

```powershell
& ../.venv/Scripts/python.exe -m bonus.security_eval --out reports/security.json
& ../.venv/Scripts/python.exe -m pytest -q --tb=no
& ../.venv/Scripts/python.exe -m pytest -q tests/test_public_matrix.py -m student -o addopts= --tb=no -rN
& ../.venv/Scripts/python.exe -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
& ../.venv/Scripts/python.exe -m lab8.crash_test --count 20 --out reports/crash.json
& ../.venv/Scripts/python.exe -m lab8.benchmark --shapes swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_verification.json
& ../.venv/Scripts/python.exe -m lab8.check_submission
& ../.venv/Scripts/python.exe -m lab8.smoke
```

| Hạng mục | Kết quả hiện tại |
| --- | --- |
| Security riêng | 15 passed, 0 failed, 0 skipped |
| Cổng host | 104 passed, 248 deselected; gồm cả 15 ca bổ sung từ đội |
| Ma trận student đầy đủ | 248 passed |
| Kiểm format bài nộp | 0 FAIL, 1 WARN do còn chờ commit merge |
| Smoke | Pass |
| Workflow / single benchmark | Mỗi shape 70/70 trial public |
| Orchestrator benchmark | 70/70 sau tích hợp |
| Crash host | 20/20 |
| Crash riêng ba shape | Mỗi shape 3/3 cửa sổ crash/resume |
| Ablation swarm → swarm_verified | 69/70 → 70/70; cost/success 49.57 → 48.72 |

Ở mốc `9ecf01f`, security đạt 10/15 vì orchestrator còn stub. Sau khi
gộp code orchestrator của đội và chạy lại thật, bộ này đạt 15/15; không sửa
kết quả JSON bằng tay. Mức 20/20 của bộ crash host không thay cho bằng chứng
crash từng shape. Bảng so sánh đầy đủ và giới hạn nằm trong group_report.md;
phương pháp và nguồn nghiên cứu nằm trong research_card.md.

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc repo, phát hiện/gỡ xung đột, viết test và công cụ xuất báo
cáo, chạy lệnh, tra bài gốc MAST và soạn tài liệu. Số liệu lấy từ lần chạy
thật; JSON do CLI sinh, không chỉnh tay. Không sửa host/evaluator/config/data.
Thành viên cần tự đọc và chạy lại để giải thích được ranh giới code/model,
quote đầy đủ, ledger so với checkpoint và phạm vi quét trace trước khi nộp.
Không khẳng định đã hoàn tất việc tự kiểm tra thủ công của thành viên.

## 6. Tự đánh giá

Thành viên tự điền trải nghiệm và mức độ hiểu sau khi xem code/chạy lại.
Không viết thay nhận xét cá nhân hoặc khẳng định hiểu phần chưa tự kiểm tra.
