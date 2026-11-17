# Nhóm MALTO

## Thông tin nhóm

- Tên nhóm: MALTO
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-MALTO-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo: https://github.com/justapea25/K5-L3B-DAY08-MALTO-FromWorkflowsToAgents
- Nhánh làm việc hiện tại: `dev`; commit chốt: nhóm xác nhận sau khi tích hợp và kiểm thử xanh.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Xuân Khánh Linh | 2A202603801 | nxklinh@gmail.com | [linkiewinkie](https://github.com/linkiewinkie) | durability, security + eval |
|   2 | Dau Hoang Minh | 2A202604011 | 26ai.minhdh4@vinuni.edu.vn | [justapea25](https://github.com/justapea25) | workflow + integration |
|   3 | Le The Anh | 2A202603983 | 26ai.anhlt5@vinuni.edu.vn | [LETHESHIYING](https://github.com/LETHESHIYING) | single agent |
|   4 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Xuân Khánh Linh | durability, security + eval | Chưa commit phần security/eval; thành viên tự điền hash sau khi xem thay đổi | `src/tests/test_group_security.py`: 15 ca, gồm 9 crash/resume, 3 quét secret/PII, 3 trace; báo cáo và ablation trong `src/reports/` |
| Dau Hoang Minh | workflow + integration | `aa39dd7`, `c0b7841` | Workflow, helper `settle`/`finish_status` và test workflow theo báo cáo cá nhân |
| Le The Anh | single agent | `7390aaa`, `1adafcb` | Single agent và test single theo báo cáo cá nhân |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603801_NguyenXuanKhanhLinh

### Phần việc phụ trách

- Durability, security và evaluation; báo cáo cá nhân: [2A202603801_NguyenXuanKhanhLinh.md](report/team/2A202603801_NguyenXuanKhanhLinh.md).

### Đóng góp cụ thể

- Viết 15 ca security, công cụ xuất kết quả pytest thành JSON, research card R2 và báo cáo nhóm; chạy lại benchmark/crash sau tích hợp.
- Sửa dấu xung đột bị commit trong workflow và test workflow, giữ helper mà single sử dụng và giữ các test của cả hai nhánh.

### Bằng chứng

- `src/reports/security.json`: kết quả 15 ca, không bỏ qua shape chưa triển khai.
- `src/reports/benchmark.json`, `src/reports/crash.json`: bằng chứng do CLI của lab sinh ra.
- `src/reports/ablation_verification.json`: đối chứng swarm với biến thể chỉ tắt nhánh ghi đè dữ kiện DB từ ticket.
- `report/team/research_card.md`, `group_report.md`: phương pháp, số liệu và giới hạn; ADR vẫn chờ hoàn tất orchestrator.
