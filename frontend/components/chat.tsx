"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { useUser } from "@/lib/user-context";
import { api, ChatContextRow } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

type Message = {
  role: "user" | "assistant";
  content: string;
  contextRows?: ChatContextRow[];
};

const SUGGESTIONS = [
  "How much have I spent on food overall?",
  "What transactions look suspicious or unusual?",
  "What's my average monthly spend on rent?",
];

function formatCurrency(n: number) {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

export function Chat() {
  const { selectedUserId } = useUser();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

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
      <ScrollArea className="flex-1 px-6">
        <div className="flex flex-col gap-4 py-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
              <p className="text-muted-foreground text-sm">
                Ask about this user&apos;s spending, or try:
              </p>
              <div className="flex flex-col gap-2 w-full max-w-sm">
                {SUGGESTIONS.map((s) => (
                  <Button key={s} variant="outline" size="sm" onClick={() => send(s)}>
                    {s}
                  </Button>
                ))}
              </div>
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
              <span className="animate-pulse">Thinking…</span>
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
        <Button type="submit" disabled={!selectedUserId || loading || !input.trim()}>
          Send
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
