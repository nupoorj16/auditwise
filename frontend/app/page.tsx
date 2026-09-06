"use client";

import { Sidebar } from "@/components/sidebar";
import { Chat } from "@/components/chat";
import { Dashboard } from "@/components/dashboard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MessageCircle, LayoutDashboard } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-1 h-full min-h-0">
      <Sidebar />
      <main className="flex flex-col flex-1 min-h-0">
        <Tabs defaultValue="chat" className="flex flex-col flex-1 min-h-0">
          <div className="border-b border-border px-6 pt-4">
            <TabsList>
              <TabsTrigger value="chat" className="gap-1.5">
                <MessageCircle className="h-4 w-4" /> Chat
              </TabsTrigger>
              <TabsTrigger value="dashboard" className="gap-1.5">
                <LayoutDashboard className="h-4 w-4" /> Dashboard
              </TabsTrigger>
            </TabsList>
          </div>
          <TabsContent value="chat" className="flex flex-col flex-1 min-h-0 mt-0">
            <Chat />
          </TabsContent>
          <TabsContent value="dashboard" className="flex-1 min-h-0 overflow-y-auto mt-0">
            <Dashboard />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
