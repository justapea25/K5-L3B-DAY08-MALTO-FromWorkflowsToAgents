"""Chạy 15 test security và sinh JSON từ kết quả pytest thật.

Chạy trong src/: python -m bonus.security_eval --out reports/security.json
Không bỏ qua test lỗi, không sửa các file thước đo của lab.
"""

import argparse
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Chạy bộ security/eval của nhóm")
    parser.add_argument("--out", default="reports/security.json")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="lab8-security-") as directory:
        junit = Path(directory) / "security.xml"
        command = [sys.executable, "-m", "pytest", "-q", "--tb=short", "tests/test_group_security.py",
                   "-o", "addopts=", f"--junitxml={junit}"]
        result = subprocess.run(command, check=False)
        cases = []
        if junit.exists():
            for case in ET.parse(junit).getroot().iter("testcase"):
                status = "passed"
                for candidate in ("failure", "error", "skipped"):
                    if case.find(candidate) is not None:
                        status = candidate
                        break
                # Không chép traceback/giá trị fixture nhạy cảm vào báo cáo.
                cases.append({"name": case.get("name"), "status": status})
        report = {
            "command": "python -m pytest -q --tb=short tests/test_group_security.py -o addopts=",
            "expected_cases": 15,
            "count": len(cases),
            "passed": sum(case["status"] == "passed" for case in cases),
            "failed": sum(case["status"] in ("failure", "error") for case in cases),
            "skipped": sum(case["status"] == "skipped" for case in cases),
            "pytest_exit_code": result.returncode,
            "cases": cases,
        }
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"security: {report['passed']}/{report['count']}; {output}")
        complete = report["count"] == 15 and report["passed"] == 15
        return result.returncode or (0 if complete else 1)


if __name__ == "__main__":
    raise SystemExit(main())
