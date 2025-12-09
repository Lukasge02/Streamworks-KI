"use client";

import Header from "./Header";
import Sidebar from "./Sidebar";

interface AppLayoutProps {
    children: React.ReactNode;
    sessionId?: string | null;
}

export default function AppLayout({ children, sessionId }: AppLayoutProps) {
    return (
        <div className="h-screen flex flex-col bg-gradient-to-br from-gray-50 via-white to-blue-50/30 overflow-hidden">
            <Header sessionId={sessionId} />

            <div className="flex-1 flex overflow-hidden">
                <Sidebar sessionId={sessionId} />

                <main className="flex-1 flex flex-col p-6 overflow-hidden">
                    {children}
                </main>
            </div>
        </div>
    );
}
