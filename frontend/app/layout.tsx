import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import { Suspense } from "react";
import { Header } from "@/components/header";
import { SystemStatusBar } from "@/components/SystemStatusBar";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MIMIC | Surgical Cinematic Synthesis",
  description:
    "An advanced AI editor that replicates the visual pacing and intent of any reference video.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} antialiased text-foreground selection:bg-indigo-500 selection:text-white`}
      >
        <div className="bg-mesh" />
        <Header />
        <main className="relative z-10">
          <Suspense fallback={<div className="min-h-screen bg-black" />}>
            {children}
          </Suspense>
        </main>
        <Toaster position="bottom-right" theme="dark" />
      </body>
    </html>
  );
}
