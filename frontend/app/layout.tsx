import type { Metadata } from "next";
import "./globals.css";

import { Providers } from "@/lib/providers";
import { Toaster } from "sonner";

export const metadata: Metadata = {
  title: "Prelude",
  description: "Understand documents before you commit to reading them.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-background text-foreground antialiased">
        <Providers>
          {children}
          <Toaster richColors />
        </Providers>
      </body>
    </html>
  );
}
