"use client";

import { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import { Plus, Plug, CheckCircle, XCircle, Zap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { StatCard } from "@/components/dashboard/stat-card";
import { api } from "@/lib/api";
import { PROVIDER_LIST, getProviderPreset, PROVIDER_DEFAULTS } from "@/lib/provider-presets";

interface Connection {
  id: string;
  name: string;
  provider: string;
  model_name: string;
  health_status: string;
  environment: string;
  token_usage_total: number;
}

type FormState = {
  name: string;
  provider: string;
  api_key: string;
  api_base_url: string;
  model_name: string;
  temperature: number;
  max_tokens: number;
};

function buildInitialForm(provider = "openai"): FormState {
  const preset = getProviderPreset(provider);
  return {
    name: "",
    provider,
    api_key: "",
    api_base_url: preset?.api_base_url ?? "",
    model_name: preset?.default_model ?? "",
    temperature: 0.7,
    max_tokens: 4096,
  };
}

export default function LLMConnectivityPage() {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [stats, setStats] = useState({ total_tenants: 0, healthy_connections: 0, failed_connections: 0, token_usage: 0 });
  const [apiPresets, setApiPresets] = useState<Record<string, { api_base_url: string; response_json_path: string; models: string[] }>>({});
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<FormState>(() => buildInitialForm("openai"));

  const modelOptions = useCallback(
    (provider: string): string[] => {
      const fromApi = apiPresets[provider]?.models;
      if (fromApi?.length) return fromApi;
      return getProviderPreset(provider)?.models ?? [];
    },
    [apiPresets]
  );

  useEffect(() => {
    load();
    api<{ provider: string; api_base_url: string; response_json_path: string; models: string[] }[]>("/llm-connections/presets")
      .then((p) => setApiPresets(Object.fromEntries(p.map((x) => [x.provider, x]))))
      .catch(() => {});
  }, []);

  async function load() {
    try {
      const [conns, s] = await Promise.all([
        api<Connection[]>("/llm-connections"),
        api<typeof stats>("/llm-connections/stats/summary"),
      ]);
      setConnections(conns);
      setStats(s);
    } catch {
      setConnections([]);
    }
  }

  function applyProviderPreset(provider: string) {
    const local = getProviderPreset(provider);
    const remote = apiPresets[provider];
    const defaultModel =
      remote?.models?.[0] ?? local?.default_model ?? "";
    const baseUrl = remote?.api_base_url ?? local?.api_base_url ?? "";

    setForm((f) => ({
      ...f,
      provider,
      api_base_url: baseUrl,
      model_name: defaultModel,
    }));
  }

  function openAddForm() {
    setForm(buildInitialForm("openai"));
    setShowForm(true);
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const preset = apiPresets[form.provider];
    const local = getProviderPreset(form.provider);
    await api("/llm-connections", {
      method: "POST",
      body: JSON.stringify({
        ...form,
        api_base_url: form.api_base_url || preset?.api_base_url || local?.api_base_url,
        model_name: form.model_name || preset?.models?.[0] || local?.default_model,
        response_json_path: preset?.response_json_path,
      }),
    });
    setShowForm(false);
    setForm(buildInitialForm());
    load();
  }

  async function testConnection(id: string) {
    await api(`/llm-connections/${id}/test`, { method: "POST" });
    load();
  }

  const models = modelOptions(form.provider);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">LLM Connectivity</h1>
          <p className="text-slate-400">Multi-tenant LLM connections with encrypted API keys</p>
        </div>
        <Button onClick={() => (showForm ? setShowForm(false) : openAddForm())}>
          <Plus className="h-4 w-4" /> Add Connection
        </Button>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <StatCard title="Total Tenants" value={stats.total_tenants} icon={Plug} />
        <StatCard title="Healthy" value={stats.healthy_connections} icon={CheckCircle} variant="success" />
        <StatCard title="Failed" value={stats.failed_connections} icon={XCircle} variant="critical" />
        <StatCard title="Token Usage" value={stats.token_usage.toLocaleString()} icon={Zap} />
      </div>

      {showForm && (
        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}>
          <Card>
            <CardHeader><CardTitle>New LLM Connection</CardTitle></CardHeader>
            <CardContent>
              <form onSubmit={handleCreate} className="grid gap-4 md:grid-cols-2">
                <div className="space-y-1.5">
                  <Label htmlFor="tenant-name">Tenant Name</Label>
                  <Input
                    id="tenant-name"
                    placeholder="e.g. Production GPT-4o"
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-1.5">
                  <Label>Provider</Label>
                  <Select value={form.provider} onValueChange={applyProviderPreset}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select provider" />
                    </SelectTrigger>
                    <SelectContent>
                      {PROVIDER_LIST.map((p) => (
                        <SelectItem key={p} value={p}>
                          {p.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="api-key">API Key</Label>
                  <Input
                    id="api-key"
                    type="password"
                    placeholder="sk-..."
                    value={form.api_key}
                    onChange={(e) => setForm({ ...form, api_key: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="api-base">API Base URL</Label>
                  <Input
                    id="api-base"
                    placeholder="https://api.example.com/v1"
                    value={form.api_base_url}
                    onChange={(e) => setForm({ ...form, api_base_url: e.target.value })}
                  />
                </div>

                <div className="space-y-1.5 md:col-span-2">
                  <Label>Model Name</Label>
                  {models.length > 0 ? (
                    <Select
                      value={form.model_name}
                      onValueChange={(v) => setForm({ ...form, model_name: v })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select model" />
                      </SelectTrigger>
                      <SelectContent>
                        {models.map((m) => (
                          <SelectItem key={m} value={m}>
                            {m}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input
                      placeholder="Model identifier"
                      value={form.model_name}
                      onChange={(e) => setForm({ ...form, model_name: e.target.value })}
                      required
                    />
                  )}
                  <p className="text-xs text-slate-500">
                    Default for {form.provider}:{" "}
                    <span className="text-cyan-400/90">
                      {getProviderPreset(form.provider)?.default_model ?? "—"}
                    </span>
                  </p>
                </div>

                <div className="flex gap-2 md:col-span-2">
                  <Button type="submit">Create Connection</Button>
                  <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {connections.map((c) => (
          <motion.div key={c.id} whileHover={{ scale: 1.01 }}>
            <Card>
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-white">{c.name}</p>
                    <p className="text-xs text-slate-400">{c.provider} · {c.model_name}</p>
                    <span className="mt-2 inline-block rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
                      {c.environment}
                    </span>
                  </div>
                  <span
                    className={`rounded-full px-2 py-1 text-xs font-medium ${
                      c.health_status === "healthy"
                        ? "bg-emerald-500/20 text-emerald-300"
                        : "bg-red-500/20 text-red-300"
                    }`}
                  >
                    {c.health_status}
                  </span>
                </div>
                <Button size="sm" variant="outline" className="mt-4 w-full" onClick={() => testConnection(c.id)}>
                  Test Connection
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
