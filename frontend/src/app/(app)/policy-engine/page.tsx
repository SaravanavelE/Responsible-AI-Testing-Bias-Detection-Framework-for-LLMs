"use client";

import { useEffect, useState } from "react";
import { Shield, Zap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";

export default function PolicyEnginePage() {
  const [policies, setPolicies] = useState<{ id: string; name: string; pii_policy: string; default_action: string }[]>([]);
  const [firewallPrompt, setFirewallPrompt] = useState("");
  const [firewallResult, setFirewallResult] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    api<typeof policies>("/policies").then(setPolicies).catch(() => {});
  }, []);

  async function testFirewall() {
    const result = await api<Record<string, unknown>>("/policies/firewall/intercept", {
      method: "POST",
      body: JSON.stringify({ prompt: firewallPrompt }),
    });
    setFirewallResult(result);
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Policy Engine</h1>
        <p className="text-slate-400">Per-tenant policies with Allow · Warn · Quarantine · Redact · Block</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center gap-2"><Shield className="h-5 w-5 text-cyan-400" /><CardTitle>Active Policies</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {policies.map((p) => (
              <div key={p.id} className="rounded-lg border border-white/10 bg-white/5 p-4">
                <p className="font-medium text-white">{p.name}</p>
                <p className="text-xs text-slate-500">PII: {p.pii_policy} · Default: {p.default_action}</p>
              </div>
            ))}
            {policies.length === 0 && <p className="text-slate-500">Default security policy active.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center gap-2"><Zap className="h-5 w-5 text-amber-400" /><CardTitle>Live Prompt Firewall</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <Label htmlFor="firewall-prompt">Test prompt</Label>
            <Textarea
              id="firewall-prompt"
              value={firewallPrompt}
              onChange={(e) => setFirewallPrompt(e.target.value)}
              placeholder="Enter prompt to intercept..."
              className="min-h-32 font-mono text-emerald-300"
            />
            <Button onClick={testFirewall} className="w-full">Intercept Prompt</Button>
            {firewallResult && (
              <div className="rounded-lg bg-black/40 p-4 font-mono text-xs">
                <p className={firewallResult.allowed ? "text-emerald-400" : "text-red-400"}>
                  Decision: {String(firewallResult.decision)} | Allowed: {String(firewallResult.allowed)}
                </p>
                <p className="mt-2 text-slate-400">PII matches: {String(firewallResult.pii_matches)}</p>
                <p className="text-slate-400">Latency: {String(firewallResult.latency_ms)}ms</p>
                {firewallResult.redacted_prompt && (
                  <p className="mt-2 text-amber-300">Redacted: {String(firewallResult.redacted_prompt).slice(0, 200)}</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Policy Controls</CardTitle></CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {["Allowed tools", "Forbidden phrases", "Allowed domains", "Max token budget", "PII policy", "Prompt length limit", "Compliance mode"].map((label) => (
              <div key={label} className="rounded-lg border border-white/10 p-3">
                <p className="text-xs text-slate-500">{label}</p>
                <p className="mt-1 text-sm text-white">Configured per tenant</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
