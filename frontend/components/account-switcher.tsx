"use client";

import { useState } from "react";
import { useUser } from "@/lib/user-context";
import { PERSONAS, getPersona } from "@/lib/identity";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { ChevronsUpDown, Check } from "lucide-react";

function AvatarCircle({ colorVar, initials, size = "h-9 w-9" }: { colorVar: string; initials: string; size?: string }) {
  return (
    <div
      className={`flex ${size} shrink-0 items-center justify-center rounded-full text-xs font-semibold text-white`}
      style={{ background: `var(${colorVar})` }}
    >
      {initials}
    </div>
  );
}

export function AccountSwitcher() {
  const { selectedUserId, setSelectedUserId } = useUser();
  const [open, setOpen] = useState(false);
  const current = getPersona(selectedUserId);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger className="flex w-full items-center gap-3 rounded-xl border border-border bg-card px-3 py-2.5 text-left shadow-sm transition-colors hover:bg-accent">
        <AvatarCircle colorVar={current.colorVar} initials={current.initials} />
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium truncate">{current.name}</p>
          <p className="text-xs text-muted-foreground truncate">{current.tagline}</p>
        </div>
        <ChevronsUpDown className="h-4 w-4 shrink-0 text-muted-foreground" />
      </PopoverTrigger>
      <PopoverContent align="start" className="w-72 p-1.5">
        <p className="px-2 py-1.5 text-xs text-muted-foreground">Switch profile</p>
        <div className="flex flex-col gap-0.5">
          {PERSONAS.map((p) => {
            const isSelected = p.userId === selectedUserId;
            return (
              <button
                key={p.userId}
                onClick={() => {
                  setSelectedUserId(p.userId);
                  setOpen(false);
                }}
                className={`flex items-center gap-3 rounded-lg px-2 py-2 text-left transition-colors hover:bg-accent ${
                  isSelected ? "bg-accent" : ""
                }`}
              >
                <AvatarCircle colorVar={p.colorVar} initials={p.initials} size="h-8 w-8" />
                <div className="min-w-0 flex-1">
                  <p className="text-sm truncate">{p.name}</p>
                  <p className="text-xs text-muted-foreground truncate">{p.tagline}</p>
                </div>
                {isSelected && <Check className="h-4 w-4 shrink-0 text-primary" />}
              </button>
            );
          })}
        </div>
      </PopoverContent>
    </Popover>
  );
}
