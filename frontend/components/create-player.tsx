"use client";
import { useState } from "react";
import { API } from "@/lib/api";
export function CreatePlayer({ onCreated }: { onCreated: () => void }) {
 const [name, setName] = useState(""); const [error, setError] = useState("");
 async function create(e: React.FormEvent) { e.preventDefault(); setError(""); const r = await fetch(`${API}/api/v1/players`, {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name})}); if (!r.ok) setError(await r.text()); else { setName(""); onCreated(); } }
 return <form onSubmit={create} className="flex gap-2"><input className="input flex-1" placeholder="Tên người chơi" value={name} onChange={e=>setName(e.target.value)} required/><button className="button">Tạo người chơi</button>{error && <small className="text-red-400">{error}</small>}</form>
}
