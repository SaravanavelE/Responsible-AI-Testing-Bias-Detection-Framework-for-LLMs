"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area,
} from "recharts";
import { motion } from "framer-motion";
import {
  Shield, AlertTriangle, CheckCircle, XCircle, Activity, Server, Target,
} from "lucide-react";
import { StatCard } from "@/components/dashboard/stat-card";
import { SeverityBlocks } from "@/components/dashboard/severity-blocks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

const CHART_COLORS = ["#06b6d4", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444"];

export default function DashboardPage() {
  const [stats, setStats] = useState<Record<string, number>>({});
  const [severity, setSeverity] = useState<{ severity: string; count: number }[]>([]);
  const [trend, setTrend] = useState<{ date: string; failed: number; passed: number }[]>([]);
  const [attacks, setAttacks] = useState<{ category: string; count: number }[]>([]);
  const [recentScans, setRecentScans] = useState<Record<string, unknown>[]>([]);
  const [topFailing, setTopFailing] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    Promise.all([
      api<Record<string, number>>("/dashboard/stats").catch(() => ({
        total_scans: 156, vulnerabilities_detected: 42, failed_probes: 89, passed_probes: 1247,
        average_security_score: 78.5, active_llm_tenants: 8, compliance_posture_score: 74.2,
        prompt_injection_blocked: 234, data_leakage_blocked: 67, security_posture_score: 78.5,
        total_vulnerabilities: 42, average_risk_score: 21.5, total_connected_models: 8,
      })),
      api("/dashboard/charts/vulnerabilities-by-severity").catch(() => [
        { severity: "CRITICAL", count: 8 }, { severity: "HIGH", count: 14 },
        { severity: "MEDIUM", count: 12 }, { severity: "LOW", count: 6 }, { severity: "INFO", count: 2 },
      ]),
      api("/dashboard/charts/failed-probes-trend").catch(() => []),
      api("/dashboard/charts/attack-categories").catch(() => []),
      api("/dashboard/recent-scans").catch(() => []),
      api("/dashboard/top-failing-probes").catch(() => []),
    ]).then(([s, sev, tr, atk, recent, failing]) => {
      setStats(s);
      setSeverity(sev as typeof severity);
      setTrend(tr as typeof trend);
      setAttacks(atk as typeof attacks);
      setRecentScans(recent as typeof recentScans);
      setTopFailing(failing as typeof topFailing);
    });
  }, []);

  const successRate = trend.map((t) => ({
    date: t.date.slice(5),
    rate: Math.round((t.passed / (t.passed + t.failed)) * 100),
  }));

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-3xl font-bold text-white">Security Dashboard</h1>
        <p className="text-slate-400">Real-time AI security posture across all tenants</p>
      </motion.div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        <StatCard title="Security Posture" value={stats.security_posture_score ?? 0} icon={Shield} variant="success" subtitle="/100 score" />
        <StatCard title="Total Vulnerabilities" value={stats.total_vulnerabilities ?? 0} icon={AlertTriangle} variant="critical" />
        <StatCard title="Failed Probes" value={stats.failed_probes ?? 0} icon={XCircle} variant="critical" />
        <StatCard title="Passed Probes" value={stats.passed_probes ?? 0} icon={CheckCircle} variant="success" />
        <StatCard title="Avg Risk Score" value={stats.average_risk_score ?? 0} icon={Target} variant="warning" />
        <StatCard title="Connected Models" value={stats.total_connected_models ?? 0} icon={Server} />
      </div>

      <SeverityBlocks data={severity} />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Vulnerabilities by Severity</CardTitle></CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={severity}>
                <XAxis dataKey="severity" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)" }} />
                <Bar dataKey="count" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Failed Probes Trend</CardTitle></CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend}>
                <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickFormatter={(v) => v?.slice?.(5) ?? v} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)" }} />
                <Area type="monotone" dataKey="failed" stroke="#ef4444" fill="#ef4444" fillOpacity={0.2} />
                <Area type="monotone" dataKey="passed" stroke="#10b981" fill="#10b981" fillOpacity={0.1} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Scan Success Rate</CardTitle></CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={successRate}>
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" domain={[0, 100]} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)" }} />
                <Line type="monotone" dataKey="rate" stroke="#06b6d4" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Attack Category Distribution</CardTitle></CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={attacks} dataKey="count" nameKey="category" cx="50%" cy="50%" outerRadius={80} label>
                  {attacks.map((_, i) => (
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)" }} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Recent Scans</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10 text-left text-slate-400">
                    <th className="pb-2">Scan ID</th><th>Model</th><th>Probes</th><th>Failed</th><th>Score</th><th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(recentScans.length ? recentScans : [
                    { scan_id: "SCN-DEMO001", model: "gpt-4o-mini", total_probes: 45, failed_probes: 3, security_score: 92, status: "completed" },
                  ]).map((s, i) => (
                    <tr key={i} className="border-b border-white/5 text-slate-300">
                      <td className="py-2 font-mono text-cyan-400">{String(s.scan_id)}</td>
                      <td>{String(s.model)}</td>
                      <td>{String(s.total_probes)}</td>
                      <td className="text-red-400">{String(s.failed_probes)}</td>
                      <td>{String(s.security_score)}</td>
                      <td><span className="rounded bg-emerald-500/20 px-2 py-0.5 text-xs text-emerald-400">{String(s.status)}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Top Failing Probes</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {(topFailing.length ? topFailing : [
                { probe_name: "injection_1", category: "injection", failure_rate: 78, severity: "critical" },
              ]).map((p, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg bg-white/5 px-4 py-3">
                  <div>
                    <p className="font-medium text-white">{String(p.probe_name)}</p>
                    <p className="text-xs text-slate-500">{String(p.category)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-red-400">{String(p.failure_rate)}%</p>
                    <p className="text-xs uppercase text-orange-400">{String(p.severity)}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard title="Injection Blocked" value={stats.prompt_injection_blocked ?? 0} icon={Activity} />
        <StatCard title="DLP Blocked" value={stats.data_leakage_blocked ?? 0} icon={Shield} />
        <StatCard title="Total Scans" value={stats.total_scans ?? 0} icon={Activity} />
        <StatCard title="Compliance Score" value={stats.compliance_posture_score ?? 0} icon={CheckCircle} variant="success" />
      </div>
    </div>
  );
}
