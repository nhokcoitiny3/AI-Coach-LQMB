const PUBLIC_API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API = typeof window === "undefined" ? (process.env.BACKEND_API_URL || PUBLIC_API) : PUBLIC_API;
export type Player = { id: string; name: string; created_at: string };
export type Job = { id: string; image_id: string; status: string; parsed_payload?: Record<string, unknown>; error?: string };
export async function getPlayers(): Promise<Player[]> { const r = await fetch(`${API}/api/v1/players`, { cache: "no-store" }); if (!r.ok) throw new Error("Không thể tải người chơi"); return r.json(); }
export async function getScout(id: string) { const r = await fetch(`${API}/api/v1/players/${id}/scout`, { cache: "no-store" }); if (!r.ok) throw new Error("Không thể tải hồ sơ Scout"); return r.json(); }
export { API };
