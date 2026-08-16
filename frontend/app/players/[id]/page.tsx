import Link from "next/link";
import { MatchHistory } from "@/components/match-history";
import { ScoutDashboard } from "@/components/scout-dashboard";
import { getScout } from "@/lib/api";

export default async function PlayerPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const data = await getScout(id);
  return <main><div className="mb-7 flex items-center justify-between"><div><p className="text-slate-400">Player Scout</p><h1 className="text-3xl font-bold">{data.player.name}</h1></div><Link className="button" href={`/players/${id}/import`}>Nhập ảnh</Link></div><ScoutDashboard data={data}/><div className="mt-6"><MatchHistory playerId={id}/></div></main>;
}
