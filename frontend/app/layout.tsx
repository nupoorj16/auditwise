import type { Metadata } from "next";
import { UserProvider } from "@/lib/user-context";
import { TooltipProvider } from "@/components/ui/tooltip";
import "./globals.css";

export const metadata: Metadata = {
  title: "AuditWise",
  description: "RAG + anomaly detection over personal finance transactions",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full h-full flex flex-col">
        <TooltipProvider delayDuration={200}>
          <UserProvider>{children}</UserProvider>
        </TooltipProvider>
      </body>
    </html>
  );
}
