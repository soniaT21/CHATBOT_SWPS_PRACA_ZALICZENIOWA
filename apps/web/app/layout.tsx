import "bootstrap/dist/css/bootstrap.min.css";
import "./globals.css";

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Asystent SWPS",
  description: "Chatbot SWPS — pytaj o publikacje i badania uczelni.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pl">
      <body>{children}</body>
    </html>
  );
}
