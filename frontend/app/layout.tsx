import "./globals.css";
import Link from "next/link";
export const metadata = { title: "Liên Quân AI Coach", description: "Player Scout" };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <><header className="border-b border-slate-800"><nav className="mx-auto flex max-w-6xl items-center gap-6 px-5 py-4"><Link href="/" className="font-bold text-cyan-400">Liên Quân AI Coach</Link><Link href="/heroes">Meta tướng</Link><Link href="/players">Người chơi</Link></nav></header>{children}</>;
}
