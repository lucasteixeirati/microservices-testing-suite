#!/usr/bin/env python3
"""Build a portable visual dashboard from JUnit and coverage artifacts."""

from __future__ import annotations

import html
import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "testing-suite" / "reports"
OUTPUT = ROOT / "docs" / "evidence"


def junit_results() -> list[dict[str, int | str]]:
    results = []
    for path in sorted(REPORTS.glob("junit-*.xml")):
        root = ET.parse(path).getroot()
        suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
        totals = {
            key: sum(int(float(suite.attrib.get(key, 0))) for suite in suites)
            for key in ("tests", "failures", "errors", "skipped")
        }
        totals["name"] = path.stem.removeprefix("junit-").title()
        results.append(totals)
    jest_path = ROOT / "services" / "order-service" / "coverage" / "test-results.json"
    if jest_path.exists():
        data = json.loads(jest_path.read_text(encoding="utf-8"))
        results.append(
            {
                "name": "Node.js unit",
                "tests": int(data.get("numTotalTests", 0)),
                "failures": int(data.get("numFailedTests", 0)),
                "errors": 0,
                "skipped": int(data.get("numPendingTests", 0)),
            }
        )

    go_path = ROOT / "services" / "payment-service" / "test-results.json"
    if go_path.exists():
        actions = []
        raw = go_path.read_bytes()
        encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8"
        for line in raw.decode(encoding).splitlines():
            event = json.loads(line)
            if event.get("Test") and event.get("Action") in {"pass", "fail", "skip"}:
                actions.append(event["Action"])
        results.append(
            {
                "name": "Go unit",
                "tests": len(actions),
                "failures": actions.count("fail"),
                "errors": 0,
                "skipped": actions.count("skip"),
            }
        )
    return results


def coverage_results() -> dict[str, float | None]:
    coverage: dict[str, float | None] = {"Python": None, "Node.js": None, "Go": None}
    path = REPORTS / "coverage.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        coverage["Python"] = round(float(data.get("totals", {}).get("percent_covered", 0)), 1)

    node_path = ROOT / "services" / "order-service" / "coverage" / "coverage-summary.json"
    if node_path.exists():
        data = json.loads(node_path.read_text(encoding="utf-8"))
        coverage["Node.js"] = round(float(data["total"]["lines"]["pct"]), 1)

    go_path = ROOT / "services" / "payment-service" / "coverage.out"
    if go_path.exists():
        total = covered = 0
        for line in go_path.read_text(encoding="utf-8").splitlines()[1:]:
            fields = line.split()
            statements, count = int(fields[-2]), int(fields[-1])
            total += statements
            covered += statements if count else 0
        coverage["Go"] = round(covered / total * 100, 1) if total else 0.0
    return coverage


def render(results: list[dict[str, int | str]], coverage: dict[str, float | None]) -> tuple[str, str]:
    total = sum(int(item["tests"]) for item in results)
    failed = sum(int(item["failures"]) + int(item["errors"]) for item in results)
    skipped = sum(int(item["skipped"]) for item in results)
    passed = total - failed - skipped
    pass_rate = round((passed / total * 100) if total else 0, 1)
    coverage_text = " · ".join(
        f"{name} {value:.1f}%" if value is not None else f"{name} N/D"
        for name, value in coverage.items()
    )
    status = "APROVADO" if total and failed == 0 else "ATENÇÃO"

    rows = "".join(
        f"<tr><td>{html.escape(str(item['name']))}</td><td>{item['tests']}</td>"
        f"<td class='ok'>{int(item['tests']) - int(item['failures']) - int(item['errors']) - int(item['skipped'])}</td>"
        f"<td class='bad'>{int(item['failures']) + int(item['errors'])}</td><td>{item['skipped']}</td></tr>"
        for item in results
    ) or "<tr><td colspan='5'>Execute a suíte para preencher o dashboard.</td></tr>"

    document = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Evidências dos testes</title><style>
:root{{--bg:#07111f;--panel:#101d31;--ink:#ecf3ff;--muted:#9bb0ca;--green:#35d07f;--red:#ff6b7a;--blue:#60a5fa}}
*{{box-sizing:border-box}}body{{margin:0;background:linear-gradient(135deg,#07111f,#10264a);color:var(--ink);font:16px system-ui,sans-serif}}
main{{max-width:1100px;margin:auto;padding:48px 24px}}h1{{font-size:clamp(2rem,5vw,4rem);margin:.2em 0}}p{{color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin:32px 0}}.card{{background:var(--panel);border:1px solid #29405f;border-radius:16px;padding:22px}}
.value{{font-size:2.2rem;font-weight:800}}.label{{color:var(--muted);font-size:.85rem;text-transform:uppercase;letter-spacing:.08em}}
.bar{{height:12px;background:#26384f;border-radius:99px;overflow:hidden}}.bar span{{display:block;height:100%;background:linear-gradient(90deg,var(--blue),var(--green));width:{pass_rate}%}}
table{{width:100%;border-collapse:collapse;background:var(--panel);border-radius:16px;overflow:hidden}}th,td{{padding:14px;text-align:left;border-bottom:1px solid #26384f}}th{{color:var(--muted)}}.ok{{color:var(--green)}}.bad{{color:var(--red)}}
</style></head><body><main><p>MICROSERVICES TESTING SUITE</p><h1>Evidências dos testes</h1><p>Resumo portátil gerado automaticamente a partir dos relatórios JUnit e de cobertura.</p>
<section class="grid"><div class="card"><div class="label">Status</div><div class="value">{status}</div></div><div class="card"><div class="label">Testes</div><div class="value">{total}</div></div><div class="card"><div class="label">Taxa de sucesso</div><div class="value">{pass_rate}%</div></div><div class="card"><div class="label">Cobertura</div><div>{coverage_text}</div></div></section>
<section class="card"><div class="label">Progresso geral</div><p>{passed} aprovados · {failed} falhas · {skipped} ignorados</p><div class="bar"><span></span></div></section><br>
<table><thead><tr><th>Categoria</th><th>Total</th><th>Aprovados</th><th>Falhas</th><th>Ignorados</th></tr></thead><tbody>{rows}</tbody></table>
</main></body></html>"""

    markdown = (
        "## Resultado automatizado\n\n"
        f"- Status: **{status}**\n"
        f"- Testes coletados: **{total}**\n"
        f"- Aprovados: **{passed}**\n"
        f"- Falhas/erros: **{failed}**\n"
        f"- Ignorados: **{skipped}**\n"
        f"- Taxa de sucesso: **{pass_rate}%**\n"
        f"- Cobertura: **{coverage_text}**\n"
    )
    return document, markdown


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    dashboard, summary = render(junit_results(), coverage_results())
    (OUTPUT / "latest-test-dashboard.html").write_text(dashboard, encoding="utf-8")
    (OUTPUT / "latest-test-summary.md").write_text(summary, encoding="utf-8")
    print(f"Dashboard: {OUTPUT / 'latest-test-dashboard.html'}")


if __name__ == "__main__":
    main()
