"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { CreatePlayer } from "./create-player";
import { getPlayers, Player } from "@/lib/api";
export function PlayerList() { const [players,setPlayers]=useState<Player[]>([]); const load=()=>getPlayers().then(setPlayers).catch(()=>setPlayers([])); useEffect(load,[]); return <><CreatePlayer onCreated={load}/><div className="mt-6 grid gap-3 md:grid-cols-2">{players.map(p=><Link className="card hover:border-cyan-400" href={`/players/${p.id}`} key={p.id}><p className="text-lg font-semibold">{p.name}</p><p className="text-sm text-slate-400">Mở Player Scout →</p></Link>)}</div></> }
