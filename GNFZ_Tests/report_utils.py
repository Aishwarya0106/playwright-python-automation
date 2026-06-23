import os
import datetime

_results = []
_start   = None


def start_timer():
    global _start
    _start = datetime.datetime.now()


def add_result(module, name, start, status, log=""):
    dur = f"{(datetime.datetime.now() - start).total_seconds():.2f}s"
    _results.append({
        "module"  : module,
        "name"    : name,
        "status"  : status,
        "duration": dur,
        "log"     : log,
    })


def write_report():
    global _start
    if _start is None:
        _start = datetime.datetime.now()

    is_jenkins = "JENKINS_URL" in os.environ or "BUILD_NUMBER" in os.environ
    timestamp_str = _start.strftime("%Y%m%d_%H%M%S")
    if is_jenkins:
        build_num = os.environ.get("BUILD_NUMBER", "")
        build_suffix = f"_build{build_num}" if build_num else ""
        report_name = f"jenkins_report{build_suffix}_{timestamp_str}.html"
        report_title = "GNFZ Jenkins Automation Report"
    else:
        report_name = f"report_{timestamp_str}.html"
        report_title = "GNFZ Automation Report"

    end_time  = datetime.datetime.now()
    duration  = str(end_time - _start).split(".")[0]
    total     = len(_results)
    passed    = sum(1 for r in _results if r["status"] == "PASSED")
    failed    = total - passed
    timestamp = _start.strftime("%d %b %Y  %I:%M %p")
    pass_rate = (passed / total * 100) if total else 0

    rows = ""
    for i, r in enumerate(_results, 1):
        css  = "passed" if r["status"] == "PASSED" else "failed"
        icon = "&#10003;" if r["status"] == "PASSED" else "&#10007;"
        err  = f'<tr class="err-row"><td colspan="5"><pre>{r["log"]}</pre></td></tr>' if r["log"] else ""
        rows += f"""
        <tr class="{css}">
            <td>{i}</td>
            <td>{r["module"]}</td>
            <td>{r["name"]}</td>
            <td>{r["duration"]}</td>
            <td class="status">{icon} {r["status"]}</td>
        </tr>{err}"""

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>GNFZ Automation Report</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; color: #333; }
.header {
  background: linear-gradient(135deg, #1a1a2e, #0f3460);
  color: white; padding: 36px 40px;
  display: flex; justify-content: space-between; align-items: center;
}
.header h1 { font-size: 26px; letter-spacing: 1px; }
.header p  { font-size: 13px; opacity: .7; margin-top: 5px; }
.meta { text-align: right; font-size: 13px; opacity: .85; line-height: 2; }
.summary { display: flex; gap: 20px; padding: 28px 40px; background: #fff; border-bottom: 1px solid #e0e0e0; }
.card { flex:1; border-radius:12px; padding:20px 24px; text-align:center; color:white; }
.card.total  { background: linear-gradient(135deg,#667eea,#764ba2); }
.card.passed { background: linear-gradient(135deg,#11998e,#38ef7d); }
.card.failed { background: linear-gradient(135deg,#f7797d,#c94b4b); }
.card.time   { background: linear-gradient(135deg,#f093fb,#f5576c); }
.card .num   { font-size: 38px; font-weight: 700; }
.card .lbl   { font-size: 12px; opacity: .9; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }
.prog-wrap { padding: 0 40px 28px; background: #fff; }
.prog-lbl  { font-size: 13px; color: #666; margin-bottom: 8px; }
.prog-bar  { height: 10px; background: #eee; border-radius: 10px; overflow: hidden; }
.prog-fill { height: 100%; background: linear-gradient(90deg,#11998e,#38ef7d); border-radius: 10px; }
.table-wrap { padding: 28px 40px; }
.table-wrap h2 { font-size: 17px; margin-bottom: 14px; color: #1a1a2e; }
table { width:100%; border-collapse:collapse; background:#fff; border-radius:12px; overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,.08); }
thead { background: #1a1a2e; color: white; }
thead th { padding: 13px 18px; text-align:left; font-size:12px; text-transform:uppercase; letter-spacing:1px; }
tbody tr { border-bottom: 1px solid #f0f0f0; }
tbody tr:hover { background: #fafafa; }
tbody td { padding: 13px 18px; font-size: 14px; }
tr.passed .status { color: #11998e; font-weight: 600; }
tr.failed .status { color: #c94b4b; font-weight: 600; }
tr.err-row td { background: #fff5f5; }
tr.err-row pre { font-size:12px; color:#c94b4b; padding:12px 18px; white-space:pre-wrap; word-break:break-word; }
.footer { text-align:center; padding:18px; font-size:12px; color:#999; border-top:1px solid #e0e0e0; background:#fff; }
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>GNFZ Automation Report</h1>
    <p>Login | Create New Project</p>
  </div>
  <div class="meta">
    <div>""" + timestamp + """</div>
    <div>dev-platform.globalnetworkforzero.com</div>
    <div>Chromium Browser</div>
    <div>Aishwarya</div>
  </div>
</div>
<div class="summary">
  <div class="card total"><div class="num">""" + str(total) + """</div><div class="lbl">Total Tests</div></div>
  <div class="card passed"><div class="num">""" + str(passed) + """</div><div class="lbl">Passed</div></div>
  <div class="card failed"><div class="num">""" + str(failed) + """</div><div class="lbl">Failed</div></div>
  <div class="card time"><div class="num">""" + duration + """</div><div class="lbl">Duration</div></div>
</div>
<div class="prog-wrap">
  <div class="prog-lbl">Pass Rate - """ + f"{pass_rate:.1f}" + """%</div>
  <div class="prog-bar">
    <div class="prog-fill" style="width:""" + f"{pass_rate:.1f}" + """%;"></div>
  </div>
</div>
<div class="table-wrap">
  <h2>Test Results</h2>
  <table>
    <thead>
      <tr><th>#</th><th>Module</th><th>Test Case</th><th>Duration</th><th>Status</th></tr>
    </thead>
    <tbody>""" + rows + """</tbody>
  </table>
</div>
<div class="footer">Generated by GNFZ Automation Framework | """ + timestamp + """</div>
</body>
</html>"""

    # Dynamic title replacements
    html = html.replace("<title>GNFZ Automation Report</title>", f"<title>{report_title}</title>")
    html = html.replace("<h1>GNFZ Automation Report</h1>", f"<h1>{report_title}</h1>")

    # Save to timestamped report path
    this_dir    = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(this_dir, "reports", report_name)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n\n=== Report saved: {report_path} ===")

    # Also save a static copy representing the latest run
    latest_name = "jenkins_report.html" if is_jenkins else "report.html"
    latest_path = os.path.join(this_dir, "reports", latest_name)
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"=== Latest report updated: {latest_path} ===\n")