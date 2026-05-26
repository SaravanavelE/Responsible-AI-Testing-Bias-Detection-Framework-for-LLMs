"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        <p className="text-slate-400">Platform configuration, API keys, and notifications</p>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Security</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {["Enable MFA", "Session timeout (60 min)", "IP allowlist", "Webhook notifications"].map((s) => (
              <label key={s} className="flex items-center justify-between">
                <span className="text-sm text-slate-300">{s}</span>
                <input type="checkbox" defaultChecked className="rounded" />
              </label>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Observability</CardTitle></CardHeader>
          <CardContent className="space-y-3 text-sm text-slate-400">
            <p>Prometheus: http://localhost:9090</p>
            <p>OpenTelemetry: OTLP endpoint configured</p>
            <p>Structured JSON audit logs enabled</p>
            <Button variant="outline" size="sm">Export Configuration</Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Innovative Features</CardTitle></CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-slate-300">
              {[
                "Red Team Mode (continuous scanning)",
                "Shadow Testing",
                "AI Attack Replay",
                "Honey Prompts",
                "Threat Intelligence Feed",
                "Model Behavior Diff",
                "Auto Policy Generator",
              ].map((f) => (
                <li key={f} className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
                  {f}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>API Configuration</CardTitle></CardHeader>
          <CardContent>
            <p className="text-xs text-slate-500">API URL</p>
            <code className="mt-1 block rounded bg-black/30 p-2 text-xs text-cyan-400">
              {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}
            </code>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
