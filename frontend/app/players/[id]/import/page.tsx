import { ImportReview } from "@/components/import-review";
export default async function Import({params}:{params:Promise<{id:string}>}){const {id}=await params;return <main><h1 className="mb-2 text-3xl font-bold">Nhập và duyệt ảnh</h1><p className="mb-6 text-slate-400">Ảnh có confidence thấp sẽ chờ bạn xác nhận.</p><ImportReview playerId={id}/></main>}
