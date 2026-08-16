import Link from "next/link";
import type { MetaHero } from "@/lib/api";

const formatRate = (value?: number | null) => value == null ? "—" : `${Math.round(value * 100)}%`;

export function MetaTable({ heroes }: { heroes: MetaHero[] }) {
  return <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="border-b border-slate-700 text-slate-400"><tr><th className="pb-3">Tướng</th><th className="pb-3">Role</th><th className="pb-3">Tier</th><th className="pb-3">Win</th><th className="pb-3">Pick</th><th className="pb-3">Ban</th><th className="pb-3">Patch</th></tr></thead><tbody>{heroes.map(hero => <tr className="border-b border-slate-800" key={hero.id}><td className="py-3 font-semibold"><Link className="hover:text-cyan-300" href={`/heroes/${hero.id}`}>{hero.name}</Link></td><td className="py-3">{hero.role}</td><td className="py-3"><span className="rounded bg-cyan-500/15 px-2 py-1 text-cyan-300">{hero.tier || "—"}</span></td><td className="py-3">{formatRate(hero.win_rate)}</td><td className="py-3">{formatRate(hero.pick_rate)}</td><td className="py-3">{formatRate(hero.ban_rate)}</td><td className="py-3 text-slate-400">{hero.patch_version || "—"}</td></tr>)}</tbody></table></div>;
}
