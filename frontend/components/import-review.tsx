"use client";

import { useCallback, useEffect, useState } from "react";
import { API, Job } from "@/lib/api";

type ReviewData = { hero: string; role: string; result: string; kills: string; deaths: string; assists: string };

function ReviewCard({ job, onDone }: { job: Job; onDone: () => void }) {
  const parsed = job.parsed_payload || {};
  const [data, setData] = useState<ReviewData>({ hero: String(parsed.hero || ""), role: String(parsed.role || "dragon"), result: String(parsed.result || "win"), kills: String(parsed.kills ?? 0), deaths: String(parsed.deaths ?? 0), assists: String(parsed.assists ?? 0) });
  const [error, setError] = useState(""); const [saving, setSaving] = useState(false);
  const update = (key: keyof ReviewData, value: string) => setData(current => ({ ...current, [key]: value }));
  async function save() { setSaving(true); setError(""); const response = await fetch(`${API}/api/v1/jobs/${job.id}/manual-review`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...data, kills: Number(data.kills), deaths: Number(data.deaths), assists: Number(data.assists) }) }); if (!response.ok) { const body = await response.json().catch(() => ({})); setError(body.detail || "Không thể lưu trận."); setSaving(false); return; } onDone(); }
  return <div className="card"><div className="flex justify-between"><b>{job.status === "review" ? "Cần duyệt AI" : "Chờ AI / nhập thủ công"}</b><span className="text-slate-400">{job.id.slice(0, 8)}</span></div>{parsed.confidence != null && <p className="mt-2 text-sm text-slate-400">Độ tin cậy AI: {Math.round(Number(parsed.confidence) * 100)}%</p>}<div className="mt-4 grid gap-3 md:grid-cols-3"><input className="input" value={data.hero} onChange={event => update("hero", event.target.value)} placeholder="Tên tướng"/><select className="input" value={data.role} onChange={event => update("role", event.target.value)}>{["dragon", "jungle", "mid", "slayer", "support"].map(role => <option key={role}>{role}</option>)}</select><select className="input" value={data.result} onChange={event => update("result", event.target.value)}><option value="win">Thắng</option><option value="loss">Thua</option></select><input className="input" type="number" min="0" value={data.kills} onChange={event => update("kills", event.target.value)} placeholder="Kills"/><input className="input" type="number" min="0" value={data.deaths} onChange={event => update("deaths", event.target.value)} placeholder="Deaths"/><input className="input" type="number" min="0" value={data.assists} onChange={event => update("assists", event.target.value)} placeholder="Assists"/></div><button className="button mt-4" disabled={saving || !data.hero.trim()} onClick={save}>{saving ? "Đang lưu…" : "Lưu trận đã duyệt"}</button>{error && <p className="mt-3 text-sm text-rose-400">{error}</p>}</div>;
}

export function ImportReview({ playerId }: { playerId: string }) {
  const [files, setFiles] = useState<FileList | null>(null); const [jobs, setJobs] = useState<Job[]>([]); const [loading, setLoading] = useState(false);
  const load = useCallback(() => fetch(`${API}/api/v1/players/${playerId}/jobs`).then(response => response.ok ? response.json() : []).then(setJobs), [playerId]);
  useEffect(() => { void load(); const timer = setInterval(load, 2500); return () => clearInterval(timer); }, [load]);
  async function submit(event: React.FormEvent) { event.preventDefault(); if (!files) return; setLoading(true); const form = new FormData(); Array.from(files).forEach(file => form.append("files", file)); await fetch(`${API}/api/v1/players/${playerId}/screenshots`, { method: "POST", body: form }); setLoading(false); void load(); }
  return <div className="space-y-5"><form onSubmit={submit} className="card"><h2 className="mb-2 font-semibold">Nhập ảnh kết quả</h2><p className="mb-3 text-sm text-slate-400">AI sẽ đề xuất tướng/KDA khi Gemini được cấu hình. Bạn luôn có thể sửa hoặc nhập thủ công trước khi lưu.</p><input type="file" accept="image/jpeg,image/png,image/webp" multiple onChange={event => setFiles(event.target.files)}/><button className="button ml-3" disabled={!files || loading}>{loading ? "Đang tải…" : "Tải ảnh lên"}</button></form><section className="space-y-3">{jobs.length === 0 && <div className="card text-slate-400">Chưa có ảnh nào. Tải ảnh kết quả trận để bắt đầu.</div>}{jobs.map(job => job.status === "completed" ? <div className="card" key={job.id}><b>Đã lưu</b><span className="ml-3 text-slate-400">{job.id.slice(0, 8)}</span></div> : <ReviewCard key={job.id} job={job} onDone={load}/>)}</section></div>;
}
