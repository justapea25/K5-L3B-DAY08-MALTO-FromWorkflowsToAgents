# src/reports/

Mọi lệnh dưới đây chạy trong thư mục `src/`, nên file JSON được ghi vào `src/reports/`.

Nhóm **commit** các file do công cụ của lab sinh ra. Đây là bằng chứng nộp bài:

| File | Lệnh tạo | Bắt buộc |
| --- | --- | --- |
| `benchmark.json` | `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` | Có |
| `crash.json` | `python -m lab8.crash_test --count 20 --out reports/crash.json` | Có |
| `hidden_selfcheck.json` | benchmark trên `student_drop/` (xem `src/README.md`, mục Tự kiểm trên bộ hidden) | Không |
| `bonus_*.json` | script bonus của nhóm | Chỉ khi làm bonus |
| `security.json` | `python -m bonus.security_eval --out reports/security.json` | Bằng chứng 15 ca riêng của phần security/eval |
| `ablation_verification.json` | `python -m lab8.benchmark --shapes swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_verification.json` | Thí nghiệm R2 trong research card |

Không sửa tay file JSON. Giảng viên chạy lại đúng các lệnh trên trên máy chấm. Số không khớp thì mục Reproducibility mất điểm. `hidden_grade.json` chỉ giảng viên tạo và bị gitignore.

Nếu chưa activate môi trường ở gốc repo, thay `python` bằng
`../.venv/Scripts/python.exe` khi chạy trong `src/`.

`security_eval` chạy pytest thật và trả mã khác 0 nếu có ca thất bại.
Không đổi failure thành passed hay skip shape chưa hoàn tất. `security.json`
chỉ lưu tên ca/trạng thái, không chép traceback chứa giá trị fixture.
Sau khi gộp orchestrator từ đội, bộ riêng đạt 15/15. Bộ 15 ca bổ sung của
nhánh đội được giữ trong `tests/test_group_security_regressions.py` và cùng
chạy trong cổng host (104 passed). Ma trận student đạt 248/248. Trước khi
chốt hash merge, kiểm lại `lab8.check_submission`.

`ablation_verification.json` phục vụ research card; không thay kết quả của
shape swarm chính thức trong `benchmark.json`. Mô tả biến can thiệp và giới
hạn nằm trong `report/team/research_card.md` ở gốc repo.
