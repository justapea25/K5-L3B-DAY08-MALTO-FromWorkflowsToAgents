# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R4 · Evaluation confounders |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Zhang et al., *Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems*, EMNLP 2026 (main). arXiv: https://arxiv.org/abs/2609.05933 · ACL Anthology: https://aclanthology.org/2026.emnlp-main.798/. Loại: paper phương pháp đánh giá, có benchmark chẩn đoán |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Các nghiên cứu về hiệu quả của hệ multi-agent có hai điểm mù: khác biệt về thiết lập thí nghiệm không được kiểm soát, và môi trường đánh giá không thật sự đòi hỏi hành vi multi-agent. Khi giữ cố định model, agent và runtime, nhiều mức "tiết kiệm" được báo cáo phụ thuộc vào thiết lập, và có thể đến từ cấu trúc bị sụp, tool pathway bị tắt, hoặc hệ xuất phát mà cắt tỉa ngẫu nhiên vẫn giữ được độ chính xác (theo abstract) |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Kết luận gắn với các benchmark và LLM thật mà paper dùng. Lab chỉ có MockLLM tất định theo seed, 14 claim public và giá mô phỏng, nên chỉ kiểm được phần chi phí và độ ổn định, không kiểm được chất lượng suy luận |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Đổi workflow (A) → single (B) mà giữ nguyên tool, hàm tính tiền và cổng host: pass rate giữ nguyên 1.000 vì tiền do code quyết, còn cost/success tăng khoảng 50–100% vì mỗi bước ReAct tốn một model call |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, tool adapter trong `lab8.tools`, hàm `settle()` dùng chung (quote → `issue_refund`), seed 11,22,33,44,55, `data/public_claims.jsonl`, `config/pricing.yaml`, evaluator `trial_pass`. Biến thay đổi: ai chọn bước tiếp theo, code cố định (A) hay vòng ReAct do model chọn tool (B). Confounder còn lại: B gọi thêm tool đọc `lookup_refund_history` mà A không gọi. Nhóm tách chi phí thành phần tool và phần model từ các trial trong report để đo riêng confounder này |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: vòng ReAct chạm trần 8 bước và trả `failed` (`step_cap`). Đo bằng `reasons` và `p95_steps` trong report, cùng cost/success và pass^5 |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_workflow_vs_single.json`
- Run id / file report: `src/reports/ablation_workflow_vs_single.json`; ví dụ `R-workflow-C-014-s11` và `R-single-C-014-s11`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng một nửa.**
  - **Phần đúng: độ đúng không đổi.** Pass rate 1.000 → 1.000, pass^5 1.000 → 1.000, variance 0 → 0. Không trial nào chạm `step_cap`.
  - **Phần sai: độ lớn và nguyên nhân của chi phí tăng.** Cost/success tăng 28.66 → 39.30 VND (+37%), thấp hơn mức +50–100% dự đoán. Tách chi phí từ các trial: phần tool tăng 27.86 → 36.43 (+8.57 VND, do tool call 2.79 → 3.64, chủ yếu là `lookup_refund_history`), còn phần model chỉ tăng 0.80 → 2.87 (+2.07 VND, khoảng +7%), dù model call tăng 0.86 → 5.5 và p95 steps 5 → 10.
  - **Kết luận:** khoảng 80% chênh lệch chi phí đến từ confounder về tool, không đến từ topology (vòng ReAct). Điều này khớp với cảnh báo của paper rằng chênh lệch "hiệu quả" có thể đến từ khác biệt về tool pathway. Muốn quy chênh lệch cho topology thì phải cho A và B gọi cùng một tập tool.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Model call của MockLLM không ảnh hưởng quyết định, nên ablation này đo được chi phí của tự chủ, không đo được rủi ro model chọn sai tool như với LLM thật.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
