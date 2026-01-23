"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Zap } from "lucide-react";

const navItems = [
    { label: "Studio", href: "/" },
    { label: "Assets", href: "/gallery" },
    { label: "Projects", href: "/vault" },
];

export function Header() {
    const pathname = usePathname();

    return (
        <header className="w-full z-50 py-8 px-6 md:px-12 bg-transparent">
            <div className="max-w-[1400px] mx-auto flex items-center justify-between">
                {/* Brand */}
                <Link href="/" className="flex items-center gap-4 group">
                    <div className="h-10 w-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(79,70,229,0.4)] transition-all duration-500 group-hover:rotate-12 group-hover:scale-110">
                        <Zap className="h-5 w-5 text-white fill-current" />
                    </div>
                    <div className="flex flex-col">
                        <span className="text-lg font-black tracking-[0.1em] uppercase text-white leading-none">Mimic</span>
                        <span className="text-[9px] font-bold tracking-[0.4em] uppercase text-indigo-400/80 mt-1.5 ml-0.5">V3.3</span>
                    </div>
                </Link>

                {/* Navigation */}
                <nav className="flex items-center gap-10">
                    {navItems.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "relative text-[11px] font-black uppercase tracking-[0.3em] transition-all duration-300 group py-2",
                                    isActive ? "text-white" : "text-slate-500 hover:text-indigo-400"
                                )}
                            >
                                {item.label}
                                <span className={cn(
                                    "absolute bottom-0 left-0 h-[2px] bg-indigo-500 transition-all duration-500",
                                    isActive ? "w-full opacity-100 shadow-[0_0_10px_rgba(99,102,241,1)]" : "w-0 opacity-0 group-hover:w-full group-hover:opacity-50"
                                )} />
                            </Link>
                        );
                    })}
                </nav>

                {/* System Status */}
                <div className="hidden lg:flex items-center gap-6 pl-10 border-l border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="h-2 w-2 rounded-full bg-cyan-500 animate-pulse shadow-[0_0_10px_rgba(34,211,238,0.5)]" />
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Neural Link Active</span>
                    </div>
                </div>
            </div>
        </header>
    );
}
