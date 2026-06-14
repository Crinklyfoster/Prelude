import type { Metadata } from "next";
import "./globals.css";

import Navbar from "@/components/layout/Navbar";
import { Providers } from "@/lib/providers";
import { Toaster } from "sonner";

export const metadata: Metadata = {
  title: "Enterprise RAG Assistant",
  description: "Enterprise Retrieval-Augmented Generation Assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>
          <Navbar />
          {children}
          <Toaster richColors />
        </Providers>
      </body>
    </html>
  );
}
