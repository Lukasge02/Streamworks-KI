"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
    const router = useRouter();

    useEffect(() => {
        router.replace("/editor");
    }, [router]);

    return (
        <div className="h-screen flex items-center justify-center bg-gray-50">
            <div className="w-10 h-10 border-4 border-gray-200 border-t-[#0082D9] rounded-full animate-spin" />
        </div>
    );
}
