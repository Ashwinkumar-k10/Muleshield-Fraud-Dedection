"use client";
import { useRouter, usePathname } from "next/navigation";

const TABS = [
  { id: "dashboard",      label: "Dashboard",     href: "/dashboard" },
  { id: "fleet",          label: "Fleet",          href: "/dashboard/analytics" },
  { id: "predictive",     label: "Predictive",     href: "/dashboard/predictive" },
  { id: "cyber",          label: "Cyber",          href: "/dashboard/cyber" },
  { id: "twin",           label: "Digital Twin",   href: "/dashboard/twin" },
  { id: "copilot",        label: "Copilot",        href: "/dashboard/copilot" },
  { id: "alerts",         label: "Alerts",         href: "/dashboard/alerts" },
  { id: "scheduler",      label: "Scheduler",      href: "/dashboard/scheduler" },
  { id: "analytics",      label: "Analytics",      href: "/dashboard/analytics" },
  { id: "sustainability", label: "Sustainability",  href: "/dashboard/sustainability" },
  { id: "graph",          label: "Graph",          href: "/dashboard/graph" },
  { id: "reports",        label: "Reports",        href: "/dashboard/reports" },
  { id: "settings",       label: "Settings",       href: "/dashboard/settings" },
  { id: "admin",          label: "Admin",          href: "/dashboard/admin" },
];

export default function DashNav() {
  const router = useRouter();
  const pathname = usePathname();
  return (
    <nav style={{ background: "rgba(10,14,26,0.97)", borderBottom: "1px solid rgba(0,212,255,0.15)", padding: "0 20px", display: "flex", alignItems: "center", height: 52, overflowX: "auto", position: "sticky", top: 0, zIndex: 100 }}>
      <div style={{ fontSize: 15, fontWeight: 800, color: "#00d4ff", whiteSpace: "nowrap", marginRight: 20, letterSpacing: "2px", cursor: "pointer" }} onClick={() => router.push("/dashboard")}>
        SECURE<span style={{ color: "#ff6b35" }}>MAINT</span> <span style={{ fontSize: 10, color: "#475569", fontWeight: 400 }}>AI 2.0</span>
      </div>
      {TABS.map(t => (
        <button key={t.id}
          onClick={() => router.push(t.href)}
          style={{ padding: "0 13px", height: 52, background: "none", border: "none", borderBottom: pathname === t.href ? "2px solid #00d4ff" : "2px solid transparent", cursor: "pointer", fontSize: 11, fontWeight: 600, color: pathname === t.href ? "#00d4ff" : "#64748b", whiteSpace: "nowrap", textTransform: "uppercase", letterSpacing: "0.6px" }}>
          {t.label}
        </button>
      ))}
    </nav>
  );
}
