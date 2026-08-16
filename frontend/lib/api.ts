const SERVER_API = process.env.BACKEND_API_URL || "http://backend:8000";
// Browser requests stay same-origin and are proxied by Next.js, which makes the UI work through a public tunnel.
const API = typeof window === "undefined" ? SERVER_API : "";
export type Player = { id: string; name: string; created_at: string };
export type Job = { id: string; image_id: string; status: string; parsed_payload?: Record<string, unknown>; error?: string };
export async function getPlayers(): Promise<Player[]> { const r = await fetch(`${API}/api/v1/players`, { cache: "no-store" }); if (!r.ok) throw new Error("Không thể tải người chơi"); return r.json(); }
export async function getScout(id: string) { const r = await fetch(`${API}/api/v1/players/${id}/scout`, { cache: "no-store" }); if (!r.ok) throw new Error("Không thể tải hồ sơ Scout"); return r.json(); }
export { API };
