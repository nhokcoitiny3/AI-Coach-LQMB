"use client";

import { useMemo, useState } from "react";
import { MetaTable } from "@/components/meta-table";
import type { MetaHero } from "@/lib/api";

type SortKey = "tier" | "name" | "role";
const tierOrder: Record<string, number> = { S: 0, A: 1, B: 2, C: 3, D: 4, F: 5 };

export function HeroCatalog({ heroes }: { heroes: MetaHero[] }) {
  const [query, setQuery] = useState("");
  const [role, setRole] = useState("all");
  const [tier, setTier] = useState("all");
  const [sort, setSort] = useState<SortKey>("tier");
  const roles = useMemo(() => [...new Set(heroes.map(hero => hero.role))].sort(), [heroes]);
  const filtered = useMemo(() => heroes.filter(hero => {
    const haystack = `${hero.name} ${hero.aliases.join(" ")}`.toLocaleLowerCase();
    return haystack.includes(query.trim().toLocaleLowerCase()) && (role === "all" || hero.role === role) && (tier === "all" || hero.tier === tier);
  }).sort((left, right) => {
    if (sort === "tier") return (tierOrder[left.tier || "F"] ?? 99) - (tierOrder[right.tier || "F"] ?? 99) || left.name.localeCompare(right.name);
    return left[sort].localeCompare(right[sort]);
  }), [heroes, query, role, sort, tier]);
  return <section className="card"><div className="mb-5 grid gap-3 md:grid-cols-4"><input aria-label="Tìm tướng" className="input" value={query} onChange={event => setQuery(event.target.value)} placeholder="Tìm tướng..."/><select aria-label="Lọc role" className="input" value={role} onChange={event => setRole(event.target.value)}><option value="all">Tất cả role</option>{roles.map(value => <option key={value} value={value}>{value}</option>)}</select><select aria-label="Lọc tier" className="input" value={tier} onChange={event => setTier(event.target.value)}><option value="all">Tất cả tier</option>{["S", "A", "B", "C"].map(value => <option key={value} value={value}>Tier {value}</option>)}</select><select aria-label="Sắp xếp" className="input" value={sort} onChange={event => setSort(event.target.value as SortKey)}><option value="tier">Sắp xếp: Tier cao</option><option value="name">Sắp xếp: Tên A–Z</option><option value="role">Sắp xếp: Role</option></select></div><p className="mb-4 text-sm text-slate-400">Hiển thị {filtered.length}/{heroes.length} tướng</p><MetaTable heroes={filtered}/></section>;
}
