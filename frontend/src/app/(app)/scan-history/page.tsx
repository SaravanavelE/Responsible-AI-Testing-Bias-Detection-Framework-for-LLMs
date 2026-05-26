"use client";

import { useEffect, useState } from "react";
import { Search, RotateCcw, Trash2, Download } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { api } from "@/lib/api";

interface Scan {
  scan_id: string;
  model_name?: string;
  provider?: string;
  status: string;
  security_score: number;
  failed_probes: number;
  passed_probes: number;
  total_probes: number;
  duration_seconds?: number;
  created_at: string;
}

export default function ScanHistoryPage() {
  const [scans, setScans] = useState<Scan[]>([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => { load(); }, [statusFilter]);

  async function load() {
    const q = statusFilter ? `?status=${statusFilter}` : "";
    try {
      const data = await api<Scan[]>(`/scans${q}`);
      setScans(data);
    } catch { setScans([]); }
  }

  async function deleteScan(scanId: string) {
    await api(`/scans/${scanId}`, { method: "DELETE" });
    load();
  }

  const filtered = scans.filter((s) =>
    !search || s.scan_id.toLowerCase().includes(search.toLowerCase()) || s.model_name?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Scan History</h1>
        <p className="text-slate-400">Search, filter, export, re-run, and compare scans</p>
      </div>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>All Scans</CardTitle>
          <div className="flex items-end gap-3">
            <div className="relative w-56 space-y-1">
              <Label>Search</Label>
              <Search className="pointer-events-none absolute left-3 top-[2.15rem] h-4 w-4 text-slate-500" />
              <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Scan ID or model..." className="pl-9" />
            </div>
            <div className="w-40 space-y-1">
              <Label>Status</Label>
              <Select value={statusFilter || "all"} onValueChange={(v) => setStatusFilter(v === "all" ? "" : v)}>
                <SelectTrigger><SelectValue placeholder="All Status" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="running">Running</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 text-left text-slate-400">
                <th className="pb-3">Scan ID</th><th>Provider</th><th>Model</th><th>Date</th><th>Score</th><th>Failed</th><th>Duration</th><th>Status</th><th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((s) => (
                <tr key={s.scan_id} className="border-b border-white/5 text-slate-300">
                  <td className="py-3 font-mono text-cyan-400">{s.scan_id}</td>
                  <td>{s.provider}</td>
                  <td>{s.model_name}</td>
                  <td>{new Date(s.created_at).toLocaleDateString()}</td>
                  <td className={s.security_score >= 80 ? "text-emerald-400" : "text-amber-400"}>{s.security_score}</td>
                  <td className="text-red-400">{s.failed_probes}</td>
                  <td>{s.duration_seconds ? `${s.duration_seconds.toFixed(0)}s` : "—"}</td>
                  <td><span className="rounded bg-white/5 px-2 py-0.5 text-xs">{s.status}</span></td>
                  <td className="flex gap-1">
                    <Button size="sm" variant="ghost"><RotateCcw className="h-3 w-3" /></Button>
                    <Button size="sm" variant="ghost"><Download className="h-3 w-3" /></Button>
                    <Button size="sm" variant="ghost" onClick={() => deleteScan(s.scan_id)}><Trash2 className="h-3 w-3 text-red-400" /></Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
