"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Play, Terminal } from "lucide-react";
import * as Progress from "@radix-ui/react-progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { api } from "@/lib/api";

interface Suite { id: string; name: string; probe_count: number; severity: string; description: string }
interface Connection { id: string; name: string; model_name: string }

export default function ScanPage() {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [suites, setSuites] = useState<Suite[]>([]);
  const [dynamicSuites, setDynamicSuites] = useState<{ id: string; name: string }[]>([]);
  const [selectedConn, setSelectedConn] = useState("");
  const [selectedSuites, setSelectedSuites] = useState<string[]>([]);
  const [selectedDynamic, setSelectedDynamic] = useState<string[]>([]);
  const [parallelism, setParallelism] = useState(4);
  const [scanDepth, setScanDepth] = useState("standard");
  const [severityThreshold, setSeverityThreshold] = useState("low");
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [securityScore, setSecurityScore] = useState(0);

  useEffect(() => {
    api<Connection[]>("/llm-connections").then(setConnections).catch(() => {});
    api<Suite[]>("/scans/suites").then(setSuites).catch(() => {});
    api<{ id: string; name: string }[]>("/scans/dynamic-suites").then(setDynamicSuites).catch(() => {});
  }, []);

  function toggleSuite(id: string) {
    setSelectedSuites((prev) => prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]);
  }

  function toggleDynamic(id: string) {
    setSelectedDynamic((prev) => prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]);
  }

  async function startScan() {
    if (!selectedConn) return;
    setScanning(true);
    setLogs([]);
    setProgress(0);
    setLogs((l) => [...l, `[${new Date().toISOString()}] Initializing scan...`]);
    try {
      const scan = await api<{ scan_id: string }>("/scans", {
        method: "POST",
        body: JSON.stringify({
          llm_connection_id: selectedConn,
          suites: selectedSuites,
          dynamic_suites: selectedDynamic,
          severity_threshold: severityThreshold,
          parallelism,
          scan_depth: scanDepth,
        }),
      });
      setLogs((l) => [...l, `[SCAN] Started ${scan.scan_id}`]);
      let pct = 0;
      const interval = setInterval(async () => {
        try {
          const detail = await api<{ status: string; security_score: number; total_probes: number; failed_probes: number }>(`/scans/${scan.scan_id}`);
          pct = Math.min(95, pct + 5);
          setProgress(pct);
          setSecurityScore(detail.security_score);
          setLogs((l) => [...l, `[PROBE] Status: ${detail.status} | Score: ${detail.security_score}`]);
          if (detail.status === "completed" || detail.status === "failed") {
            setProgress(100);
            setScanning(false);
            clearInterval(interval);
            setLogs((l) => [...l, `[COMPLETE] Security score: ${detail.security_score}/100`]);
          }
        } catch { /* polling */ }
      }, 3000);
    } catch (e) {
      setLogs((l) => [...l, `[ERROR] ${e}`]);
      setScanning(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Vulnerability Scan</h1>
        <p className="text-slate-400">Static suites + dynamic adversarial probes with live scoring</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Scan Configuration</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <Label>LLM Tenant</Label>
              <Select value={selectedConn || undefined} onValueChange={setSelectedConn}>
                <SelectTrigger>
                  <SelectValue placeholder="Select connection..." />
                </SelectTrigger>
                <SelectContent>
                  {connections.map((c) => (
                    <SelectItem key={c.id} value={c.id}>
                      {c.name} ({c.model_name})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="parallelism">Parallelism</Label>
                <Input id="parallelism" type="number" min={1} max={16} value={parallelism} onChange={(e) => setParallelism(+e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label>Scan Depth</Label>
                <Select value={scanDepth} onValueChange={setScanDepth}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="quick">Quick</SelectItem>
                    <SelectItem value="standard">Standard</SelectItem>
                    <SelectItem value="deep">Deep</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>Severity Threshold</Label>
                <Select value={severityThreshold} onValueChange={setSeverityThreshold}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {["info", "low", "medium", "high", "critical"].map((s) => (
                      <SelectItem key={s} value={s}>{s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <p className="mb-2 text-sm font-medium text-white">Static Scan Suites</p>
              <div className="grid gap-2 md:grid-cols-2">
                {suites.map((s) => (
                  <label key={s.id} className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition ${selectedSuites.includes(s.id) ? "border-cyan-500/50 bg-cyan-500/10" : "border-white/10 bg-white/5"}`}>
                    <input type="checkbox" checked={selectedSuites.includes(s.id)} onChange={() => toggleSuite(s.id)} className="mt-1 h-4 w-4 accent-cyan-500" />
                    <div>
                      <p className="text-sm font-medium text-white">{s.name}</p>
                      <p className="text-xs text-slate-400">{s.probe_count} probes · {s.severity}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
            <div>
              <p className="mb-2 text-sm font-medium text-white">Dynamic AI Probes (20 per suite)</p>
              <div className="flex flex-wrap gap-2">
                {dynamicSuites.map((s) => (
                  <button key={s.id} type="button" onClick={() => toggleDynamic(s.id)}
                    className={`rounded-full px-3 py-1 text-xs ${selectedDynamic.includes(s.id) ? "bg-purple-600/30 text-purple-300 border border-purple-500/50" : "bg-white/5 text-slate-400 border border-white/10"}`}>
                    {s.name}
                  </button>
                ))}
              </div>
            </div>
            <Button onClick={startScan} disabled={scanning || !selectedConn} className="w-full">
              <Play className="h-4 w-4" /> {scanning ? "Scan Running..." : "Start Scan"}
            </Button>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader><CardTitle>Live Progress</CardTitle></CardHeader>
            <CardContent>
              <div className="text-center">
                <p className="text-5xl font-bold text-cyan-400">{securityScore}</p>
                <p className="text-xs text-slate-500">Security Score</p>
              </div>
              <Progress.Root value={progress} className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
                <Progress.Indicator className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all" style={{ width: `${progress}%` }} />
              </Progress.Root>
              <p className="mt-2 text-center text-xs text-slate-500">{progress}% complete</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center gap-2"><Terminal className="h-4 w-4" /><CardTitle>Scan Logs</CardTitle></CardHeader>
            <CardContent>
              <div className="terminal-log h-64 overflow-y-auto rounded-lg bg-black/40 p-3 text-green-400/90">
                {logs.map((l, i) => <div key={i}>{l}</div>)}
                {scanning && <motion.span animate={{ opacity: [1, 0] }} transition={{ repeat: Infinity, duration: 0.8 }}>▌</motion.span>}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
