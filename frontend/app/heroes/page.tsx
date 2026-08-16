import { HeroCatalog } from "@/components/hero-catalog";
import { getHeroCatalog } from "@/lib/api";

export default async function HeroesPage() {
  const heroes = await getHeroCatalog();
  return <main><p className="text-cyan-400">ROVMeta · region TH · patch được ghi trên từng record</p><h1 className="mt-2 text-3xl font-bold">Meta tướng</h1><p className="mb-6 mt-2 text-slate-400">Lọc theo role, tier hoặc tìm tên tướng. Dữ liệu được crawl kèm nguồn, không dùng mock data.</p><HeroCatalog heroes={heroes}/></main>;
}
