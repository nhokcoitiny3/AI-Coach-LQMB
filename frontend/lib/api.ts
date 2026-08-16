const SERVER_API = process.env.BACKEND_API_URL || "http://backend:8000";
// Browser requests stay same-origin and are proxied by Next.js, which makes the UI work through a public tunnel.
const API = typeof window === "undefined" ? SERVER_API : "";
export type Player = { id: string; name: string; created_at: string };
export type Job = { id: string; image_id: string; status: string; parsed_payload?: Record<string, unknown>; error?: string };
export type MetaHero = { id: string; name: string; role: string; aliases: string[]; image_url?: string | null; tier?: string | null; pick_rate?: number | null; ban_rate?: number | null; win_rate?: number | null; patch_version?: string | null; region: string; source: string; source_url: string; captured_at: string };
export type MetaSource = { key: string; name: string; region: string; base_url: string; enabled: boolean; last_run?: { status: string; records_written: number; finished_at?: string | null } | null };
export type MetaDashboard = { hero_count: number; tier_distribution: Record<string, number>; role_distribution: Record<string, number>; top_meta: MetaHero[]; sources: MetaSource[] };
export async function getPlayers(): Promise<Player[]> { const r = await fetch(`${API}/api/v1/players`, { cache: "no-store" }); if (!r.ok) throw new Error("Không thể tải người chơi"); return r.json(); }
export async function getScout(id: string) { const r = await fetch(`${API}/api/v1/players/${id}/scout`, { cache: "no-store" }); if (!r.ok) throw new Error("Không thể tải hồ sơ Scout"); return r.json(); }
export async function getMetaDashboard(): Promise<MetaDashboard> { const r = await fetch(`${API}/api/v1/meta/dashboard`, { cache: "no-store" }); if (!r.ok) throw new Error("Không thể tải dữ liệu meta"); return r.json(); }
export async function getHeroCatalog(): Promise<MetaHero[]> { const r = await fetch(`${API}/api/v1/catalog/heroes`, { cache: "no-store" }); if (!r.ok) throw new Error("Không thể tải catalog tướng"); return r.json(); }
export async function getHero(id: string): Promise<MetaHero> { const r = await fetch(`${API}/api/v1/catalog/heroes/${id}`, { cache: "no-store" }); if (!r.ok) throw new Error("Không thể tải chi tiết tướng"); return r.json(); }
export { API };
