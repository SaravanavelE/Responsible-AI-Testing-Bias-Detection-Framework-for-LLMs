"use client";

import { useEffect, useState } from "react";
import { Building2, Globe } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function TenantsPage() {
  const [tenants, setTenants] = useState<{ id: string; name: string; slug: string; plan: string; region: string; compliance_mode: string }[]>([]);

  useEffect(() => {
    api<typeof tenants>("/tenants").then(setTenants).catch(() => setTenants([
      { id: "1", name: "Acme Enterprise", slug: "acme", plan: "enterprise", region: "us-east-1", compliance_mode: "standard" },
    ]));
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Tenant Management</h1>
        <p className="text-slate-400">Multi-region tenant governance and isolation</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {tenants.map((t) => (
          <Card key={t.id}>
            <CardContent className="p-5">
              <div className="flex items-center gap-3">
                <Building2 className="h-8 w-8 text-cyan-400" />
                <div>
                  <p className="font-semibold text-white">{t.name}</p>
                  <p className="text-xs text-slate-500">{t.slug} · {t.plan}</p>
                </div>
              </div>
              <div className="mt-4 flex gap-4 text-xs text-slate-400">
                <span className="flex items-center gap-1"><Globe className="h-3 w-3" />{t.region}</span>
                <span>{t.compliance_mode}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
