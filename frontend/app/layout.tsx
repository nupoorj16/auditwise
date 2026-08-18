import type { Metadata } from "next";
import { UserProvider } from "@/lib/user-context";
import "./globals.css";

export const metadata: Metadata = {
  title: "Personal Finance Assistant",
  description: "RAG + anomaly detection over personal finance transactions",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full h-full flex flex-col">
        <UserProvider>{children}</UserProvider>
      </body>
    </html>
  );
}
