import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "People Match",
  description: "Discover mutual matches through thoughtful questions."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-muted text-foreground">{children}</body>
    </html>
  );
}
