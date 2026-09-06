"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { useUser } from "@/lib/user-context";
import { api, ChatContextRow } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { BookCheck, Wallet, TriangleAlert, CalendarClock, X, Send } from "lucide-react";

type Message = {
  role: "user" | "assistant";
  content: string;
  contextRows?: ChatContextRow[];
};

const WELCOME_DISMISSED_KEY = "auditwise_welcome_dismissed";

const SUGGESTIONS = [
  { icon: Wallet, text: "How much have I spent on food overall?" },
  { icon: TriangleAlert, text: "What transactions look suspicious or unusual?" },
  { icon: CalendarClock, text: "What's my average monthly spend on rent?" },
];

function formatCurrency(n: number) {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

export function Chat() {
  const { selectedUserId } = useUser();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [slowLoad, setSlowLoad] = useState(false);
  const [showWelcome, setShowWelcome] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    try {
      setShowWelcome(localStorage.getItem(WELCOME_DISMISSED_KEY) !== "1");
    } catch {
      setShowWelcome(true);
    }
  }, []);

  function dismissWelcome() {
    setShowWelcome(false);
    try {
      localStorage.setItem(WELCOME_DISMISSED_KEY, "1");
    } catch {
      // ignore - just a per-viewer convenience
    }
  }

  useEffect(() => {
    if (!loading) {
      setSlowLoad(false);
      return;
    }
    const timer = setTimeout(() => setSlowLoad(true), 5000);
    return () => clearTimeout(timer);
  }, [loading]);

  useEffect(() => {
    setMessages([]);
  }, [selectedUserId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(question: string) {
    if (!selectedUserId || !question.trim() || loading) return;
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.chat(selectedUserId, question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, contextRows: res.context_rows },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Something went wrong answering that - please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    send(input);
  }

  return (
    <div className="flex flex-col flex-1 max-w-3xl mx-auto w-full h-full">
      {showWelcome && (
        <div className="px-6 pt-4">
          <Alert className="relative pr-10">
            <BookCheck className="h-4 w-4" />
            <AlertDescription>
              <strong className="text-foreground font-medium">Welcome to AuditWise.</strong>{" "}
              This is a demo running on synthetic transaction data, not a real bank connection.
              Pick a profile in the sidebar, then ask about its spending or explore flagged anomalies below.
            </AlertDescription>
            <button
              onClick={dismissWelcome}
              aria-label="Dismiss"
              className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          </Alert>
        </div>
      )}

      <ScrollArea className="flex-1 px-6">
        <div className="flex flex-col gap-4 py-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center gap-4 py-16 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-accent text-accent-foreground">
                <Wallet className="h-6 w-6" />
              </div>
              <div>
                <p className="font-medium">Ask anything about this profile&apos;s finances</p>
                <p className="text-muted-foreground text-sm mt-1">Try one of these to get started:</p>
              </div>
              <div className="flex flex-col gap-2 w-full max-w-sm">
                {SUGGESTIONS.map(({ icon: Icon, text }) => (
                  <button
                    key={text}
                    onClick={() => send(text)}
                    className="flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3 text-left text-sm shadow-sm transition-colors hover:border-primary/40 hover:bg-accent"
                  >
                    <Icon className="h-4 w-4 shrink-0 text-primary" />
                    <span>{text}</span>
                  </button>
                ))}
              </div>
              <p className="text-xs text-muted-foreground max-w-sm">
                First question may take up to a minute if the server has been idle.
              </p>
            </div>
          )}

          {messages.map((m, i) => (
            <ChatBubble key={i} message={m} />
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-muted-foreground text-sm">
              <Avatar className="h-7 w-7">
                <AvatarFallback className="bg-primary text-primary-foreground text-xs">AI</AvatarFallback>
              </Avatar>
              <span className="animate-pulse">
                {slowLoad ? "Still working, the server may be waking up…" : "Thinking…"}
              </span>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      <form onSubmit={handleSubmit} className="border-t border-border p-4 flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your spending…"
          disabled={!selectedUserId || loading}
        />
        <Button type="submit" disabled={!selectedUserId || loading || !input.trim()} className="gap-1.5">
          <Send className="h-3.5 w-3.5" /> Send
        </Button>
      </form>
    </div>
  );
}

function ChatBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex gap-2 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <Avatar className="h-7 w-7 mt-1">
          <AvatarFallback className="bg-primary text-primary-foreground text-xs">AI</AvatarFallback>
        </Avatar>
      )}
      <div className={`flex flex-col gap-2 ${isUser ? "items-end" : "items-start"} max-w-[80%]`}>
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm shadow-sm ${
            isUser
              ? "bg-primary text-primary-foreground rounded-br-sm"
              : "bg-card border border-border rounded-bl-sm"
          }`}
        >
          {message.content}
        </div>
        {!isUser && message.contextRows && message.contextRows.length > 0 && (
          <Sources rows={message.contextRows} />
        )}
      </div>
    </div>
  );
}

function Sources({ rows }: { rows: ChatContextRow[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="w-full">
      <button
        onClick={() => setOpen((v) => !v)}
        className="text-xs text-muted-foreground hover:text-foreground underline underline-offset-2"
      >
        {open ? "Hide" : "Show"} {rows.length} cited transaction{rows.length === 1 ? "" : "s"}
      </button>
      {open && (
        <div className="mt-2 flex flex-col gap-1 rounded-lg border border-border bg-muted p-2">
          {rows.map((r) => (
            <div key={r.transaction_id_clean} className="flex justify-between gap-3 text-xs px-2 py-1">
              <span className="text-muted-foreground tabular-nums shrink-0">{r.date_clean}</span>
              <span className="truncate flex-1">{r.category_clean}</span>
              <span className={`tabular-nums shrink-0 ${r.is_anomaly ? "text-destructive font-medium" : ""}`}>
                {formatCurrency(r.amount_clean)}
              </span>
              <span className="text-muted-foreground shrink-0">[{r.transaction_id_clean}]</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
