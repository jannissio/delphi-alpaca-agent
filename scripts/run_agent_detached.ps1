# Start the live paper loop as a detached, hidden process with logs on disk (Windows).
#   powershell -ExecutionPolicy Bypass -File scripts/run_agent_detached.ps1
# Prints the PID; stop it with `Stop-Process -Id <pid>` (after `python scripts/kill.py` if orders are open).
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root
New-Item -ItemType Directory -Force -Path "$root\logs" | Out-Null
$env:PYTHONIOENCODING = "utf-8"
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$out = "$root\logs\agent_detached_$stamp.log"
$err = "$root\logs\agent_detached_$stamp.err"
$p = Start-Process -FilePath "$root\.venv\Scripts\python.exe" -ArgumentList "-m", "agent.main" `
        -WorkingDirectory $root -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $out -RedirectStandardError $err
"agent started: pid $($p.Id) -> $out"
