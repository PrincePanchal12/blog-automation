import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Blog Platform",
  description: "Generate a blog draft from a simple topic.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
