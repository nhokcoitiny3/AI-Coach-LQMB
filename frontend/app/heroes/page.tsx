import { MetaTable } from "@/components/meta-table";
import { getHeroCatalog } from "@/lib/api";

export default async function HeroesPage(){const heroes=await getHeroCatalog();return <main><p className="text-cyan-400">ROVMeta · region TH · patch được ghi trên từng record</p><h1 className="mt-2 text-3xl font-bold">Meta tướng</h1><p className="mb-6 mt-2 text-slate-400">Dữ liệu được gắn link nguồn, không phải dữ liệu mock. Tỷ lệ meta phụ thuộc region và patch.</p><section className="card"><MetaTable heroes={heroes}/></section></main>}
