Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
$base = "A:\SecureMaint AI 2.0\frontend\app\dashboard"

$routes = @(
  @{ path="analytics";     title="Fleet Analytics";           color="#00d4ff"; desc="Fleet-wide performance analytics, OEE metrics, and trend reports." }
  @{ path="predictive";    title="Predictive Maintenance";    color="#a855f7"; desc="XGBoost, LightGBM, BiLSTM, Isolation Forest, LSTM Autoencoder and Random Forest predictions." }
  @{ path="cyber";         title="Cyber Security Console";    color="#ff4444"; desc="Real-time threat detection: sensor spoofing, data injection, and gradual drift attacks." }
  @{ path="cybersecurity"; title="Cyber Security Console";    color="#ff4444"; desc="HMAC-signed telemetry validation and Isolation Forest boundary networks." }
  @{ path="twin";          title="Digital Twin";              color="#00ff88"; desc="Three.js 3D real-time digital twins for every machine in your fleet." }
  @{ path="copilot";       title="AI Copilot";                color="#6366f1"; desc="Natural language interface - ask anything about machines, maintenance, or anomalies." }
  @{ path="alerts";        title="Alerts Center";             color="#ff9500"; desc="All active alerts, warnings, and notifications sorted by severity." }
  @{ path="scheduler";     title="Maintenance Scheduler";     color="#00d4ff"; desc="AI-optimised scheduling with technician allocation and spare parts management." }
  @{ path="sustainability";title="Sustainability Dashboard";  color="#00ff88"; desc="Energy savings, CO2 avoided, efficiency scores, and green ratings." }
  @{ path="graph";         title="Knowledge Graph";           color="#a855f7"; desc="Neo4j relationship graph between machines, sensors, faults, and maintenance events." }
  @{ path="reports";       title="Reports";                   color="#00d4ff"; desc="Auto-generated PDF and Excel reports for fleet health and compliance." }
  @{ path="settings";      title="Settings";                  color="#64748b"; desc="Platform configuration, Kafka topics, database connections, and notifications." }
  @{ path="admin";         title="Admin Panel";               color="#ff6b35"; desc="User management, role-based access control, audit logs, and system health." }
  @{ path="profile";       title="Profile";                   color="#64748b"; desc="Your account details and preferences." }
  @{ path="assets";        title="Asset Registry";            color="#00d4ff"; desc="Full registry of all industrial assets, specifications, and maintenance history." }
)

foreach ($r in $routes) {
  $dir = Join-Path $base $r.path
  if (!(Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  $file = Join-Path $dir "page.tsx"
  $c = @"
export default function Page() {
  return (
    <div style={{ minHeight: "100vh", background: "linear-gradient(135deg,#0a0e1a 0%,#0d1b2e 50%,#0a0e1a 100%)", color: "#e2e8f0", fontFamily: "Inter,system-ui,sans-serif", display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 16, padding: "40px 20px" }}>
      <div style={{ width: 64, height: 64, borderRadius: 16, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28 }}>+</div>
      <h1 style={{ fontSize: 28, fontWeight: 800, color: "$($r.color)", letterSpacing: "-0.5px", margin: 0, textAlign: "center" }}>$($r.title)</h1>
      <p style={{ fontSize: 14, color: "#64748b", maxWidth: 480, textAlign: "center", lineHeight: 1.6, margin: 0 }}>$($r.desc)</p>
      <a href="/dashboard" style={{ background: "rgba(0,212,255,0.1)", border: "1px solid rgba(0,212,255,0.25)", color: "#00d4ff", fontSize: 12, padding: "10px 24px", borderRadius: 20, textDecoration: "none", fontWeight: 600, marginTop: 8 }}>Back to Dashboard</a>
    </div>
  );
}
"@
  Set-Content -Path $file -Value $c -Encoding UTF8
  Write-Host "Created: $($r.path)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "All routes created! Now run: npm run dev" -ForegroundColor Green
