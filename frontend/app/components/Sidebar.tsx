"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
    MessageCircle,
    Sparkles,
    LayoutDashboard,
    ChevronLeft,
    ChevronRight,
    FileText
} from "lucide-react";
import { cn } from "@/app/utils/cn";

interface SidebarProps {
    sessionId?: string | null;
}

const NAV_ITEMS = [
    { href: "/editor", label: "Stream Editor", icon: Sparkles, description: "Wizard + KI-Chat" },
    { href: "/streams", label: "Meine Streams", icon: LayoutDashboard, description: "Gespeicherte Jobs" },
    { href: "/documents", label: "Dokumente", icon: FileText, description: "RAG Wissensbasis" },
    { href: "/chat", label: "Dokumenten-Chat", icon: MessageCircle, description: "Fragen an Dokumente" },
];

export default function Sidebar({ sessionId }: SidebarProps) {
    const pathname = usePathname();
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <motion.aside
            initial={false}
            animate={{ width: isCollapsed ? 72 : 220 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            className="relative bg-white border-r border-gray-100 flex flex-col flex-shrink-0 h-full"
        >
            {/* Toggle Button */}
            <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="absolute -right-3 top-6 z-10 w-6 h-6 bg-white border border-gray-200 rounded-full shadow-sm flex items-center justify-center hover:bg-gray-50 transition-colors"
            >
                {isCollapsed ? (
                    <ChevronRight className="w-3.5 h-3.5 text-gray-500" />
                ) : (
                    <ChevronLeft className="w-3.5 h-3.5 text-gray-500" />
                )}
            </button>

            {/* Navigation */}
            <nav className="flex-1 p-3 space-y-1 pt-4">
                <AnimatePresence>
                    {!isCollapsed && (
                        <motion.h3
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-3 px-2"
                        >
                            Navigation
                        </motion.h3>
                    )}
                </AnimatePresence>

                {NAV_ITEMS.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;
                    const href = item.href;

                    return (
                        <Link
                            key={item.href}
                            href={href}
                            className={cn(
                                "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative",
                                isActive && "bg-[#0082D9] text-white shadow-lg shadow-[#0082D9]/20",
                                !isActive && "text-gray-600 hover:bg-gray-50 hover:text-gray-900",
                                isCollapsed && "justify-center px-0"
                            )}
                        >
                            <div className={cn(
                                "w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors",
                                isActive ? "bg-white/20" : "bg-gray-100 group-hover:bg-gray-200"
                            )}>
                                <Icon className={cn(
                                    "w-4.5 h-4.5",
                                    isActive ? "text-white" : "text-gray-500 group-hover:text-gray-700"
                                )} />
                            </div>

                            <AnimatePresence>
                                {!isCollapsed && (
                                    <motion.div
                                        initial={{ opacity: 0, width: 0 }}
                                        animate={{ opacity: 1, width: "auto" }}
                                        exit={{ opacity: 0, width: 0 }}
                                        className="flex-1 min-w-0 overflow-hidden"
                                    >
                                        <span className={cn(
                                            "text-sm font-medium block whitespace-nowrap",
                                            isActive && "text-white"
                                        )}>
                                            {item.label}
                                        </span>
                                        <span className={cn(
                                            "text-[11px] whitespace-nowrap",
                                            isActive ? "text-white/70" : "text-gray-400"
                                        )}>
                                            {item.description}
                                        </span>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            {/* Tooltip when collapsed */}
                            {isCollapsed && (
                                <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded-md opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 transition-opacity">
                                    {item.label}
                                </div>
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer */}
            <div className="p-3 border-t border-gray-100">
                <AnimatePresence>
                    {!isCollapsed && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="text-[10px] text-gray-400 text-center"
                        >
                            v2.0.0
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </motion.aside>
    );
}
