# Nhóm MALTO

## Thông tin nhóm

- Tên nhóm: MALTO
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-MALTO-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo: https://github.com/justapea25/K5-L3B-DAY08-MALTO-FromWorkflowsToAgents
- Nhánh làm việc hiện tại: `main`; nhánh nộp và commit chốt: nhóm xác nhận sau khi tích hợp.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Xuân Khánh Linh | 2A202603801 | nxklinh@gmail.com | [linkiewinkie](https://github.com/linkiewinkie) | workflow + integration |
|   2 |        |      |       |        |         |
|   3 |        |      |       |        |         |
|   4 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Xuân Khánh Linh | workflow + integration | | `src/tests/test_group_workflow.py`: injection, claim không tồn tại, thiếu order_id, T14 top-up, T14 retry (5 test) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603801_NguyenXuanKhanhLinh

### Phần việc phụ trách

- Workflow và tích hợp; báo cáo cá nhân: [2A202603801_NguyenXuanKhanhLinh.md](report/team/2A202603801_NguyenXuanKhanhLinh.md).

### Đóng góp cụ thể

- Triển khai `src/lab8/shapes/workflow.py`, thêm 5 test riêng, chạy kiểm thử và sinh bằng chứng public bằng công cụ có sẵn.

### Bằng chứng

- Test riêng: 5/5; ma trận student workflow: 62/62; cổng host: 59/59.
- `src/reports/benchmark.json`: workflow 70/70 trial public trên 5 seed.
- `src/reports/crash.json`: bộ crash host 20/20; kiểm trực tiếp workflow qua 3 điểm crash/resume.
- `report/team/decision_adr.md`: quyết định tạm thời, chờ tích hợp hai shape còn lại.
