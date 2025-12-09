import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "Streamworks Self Service",
    description: "Self Service Portal für Streamworks XML-Generierung",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="de" suppressHydrationWarning>
            <head>
                <link rel="preconnect" href="https://fonts.googleapis.com" />
                <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
                <link
                    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@400;500;600&display=swap"
                    rel="stylesheet"
                />
            </head>
            <body className="font-sans min-h-screen bg-white" suppressHydrationWarning>{children}</body>
        </html>
    );
}
