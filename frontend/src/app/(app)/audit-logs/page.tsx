"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<{ id: string; action: string; resource_type: string; severity: string; created_at: string; details: Record<string, unknown> }[]>([]);

  useEffect(() => {
    api<typeof logs>("/audit-logs").then(setLogs).catch(() => []);
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Audit Logs</h1>
        <p className="text-slate-400">Structured audit trail for compliance and forensics</p>
      </div>
      <Card>
        <CardHeader><CardTitle>Recent Activity</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {logs.map((l) => (
              <div key={l.id} className="flex items-center justify-between rounded-lg bg-white/5 px-4 py-3 font-mono text-xs">
                <div>
                  <span className="text-cyan-400">{l.action}</span>
                  <span className="mx-2 text-slate-600">·</span>
                  <span className="text-slate-400">{l.resource_type}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`uppercase ${l.severity === "critical" ? "text-red-400" : "text-slate-500"}`}>{l.severity}</span>
                  <span className="text-slate-600">{new Date(l.created_at).toLocaleString()}</span>
                </div>
              </div>
            ))}
            {logs.length === 0 && <p className="text-slate-500">No audit logs yet. Actions will appear as you use the platform.</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
