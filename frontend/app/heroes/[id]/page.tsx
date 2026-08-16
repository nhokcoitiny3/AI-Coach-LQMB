import Link from "next/link";
import { notFound } from "next/navigation";
import { getHero } from "@/lib/api";

const formatRate = (value?: number | null) => value == null ? "—" : `${Math.round(value * 100)}%`;
const roleLabel = (role: string) => role === "unknown" ? "Chưa xác định" : role;

export default async function HeroDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let hero: Awaited<ReturnType<typeof getHero>>;
  try { hero = await getHero(id); } catch { return notFound(); }
  return <main>
    <Link href="/heroes" className="text-sm text-cyan-400 hover:text-cyan-300">← Quay lại Meta tướng</Link>
    <div className="mt-5 flex flex-wrap items-end justify-between gap-4">
      <div><p className="text-cyan-400">Hồ sơ tướng trong AI Coach</p><h1 className="mt-1 text-4xl font-bold">{hero.name}</h1><p className="mt-2 text-slate-400">Dữ liệu meta đang lưu trong hệ thống của bạn, theo region và patch của nguồn.</p></div>
      <span className="rounded-lg bg-cyan-500/15 px-4 py-2 text-xl font-bold text-cyan-300">Tier {hero.tier || "—"}</span>
    </div>
    <div className="mt-6 h-64 rounded-xl border border-slate-700 bg-slate-900 bg-cover bg-center" role="img" aria-label={`Ảnh tướng ${hero.name}`} style={hero.image_url ? { backgroundImage: `linear-gradient(90deg, rgba(2,6,23,.25), rgba(2,6,23,.7)), url(${hero.image_url})` } : undefined}/>
    <section className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div className="card"><p className="text-slate-400">Vai trò</p><p className="mt-2 text-xl font-semibold capitalize">{roleLabel(hero.role)}</p></div>
      <div className="card"><p className="text-slate-400">Win rate</p><p className="mt-2 text-xl font-semibold">{formatRate(hero.win_rate)}</p></div>
      <div className="card"><p className="text-slate-400">Pick rate</p><p className="mt-2 text-xl font-semibold">{formatRate(hero.pick_rate)}</p></div>
      <div className="card"><p className="text-slate-400">Ban rate</p><p className="mt-2 text-xl font-semibold">{formatRate(hero.ban_rate)}</p></div>
    </section>
    <section className="card mt-6"><h2 className="text-xl font-semibold">Nguồn và phạm vi dữ liệu</h2><dl className="mt-4 grid gap-4 text-sm sm:grid-cols-2"><div><dt className="text-slate-400">Patch</dt><dd className="mt-1 font-medium">{hero.patch_version || "Chưa có"}</dd></div><div><dt className="text-slate-400">Region</dt><dd className="mt-1 font-medium uppercase">{hero.region}</dd></div><div><dt className="text-slate-400">Nguồn crawl</dt><dd className="mt-1 font-medium">{hero.source}</dd></div><div><dt className="text-slate-400">Cập nhật</dt><dd className="mt-1 font-medium">{new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(hero.captured_at))}</dd></div></dl>
      {hero.aliases.length > 1 && <p className="mt-5 text-sm text-slate-400">Tên đối chiếu: <span className="text-slate-200">{hero.aliases.join(", ")}</span></p>}
      <a className="mt-6 inline-block text-sm text-cyan-400 hover:text-cyan-300" href={hero.source_url} target="_blank" rel="noreferrer">Xem trang nguồn ROVMeta ↗</a>
    </section>
  </main>;
}
