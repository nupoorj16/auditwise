"use client";

import { createContext, useContext, useState, ReactNode } from "react";
import { PERSONAS } from "./identity";

type UserContextValue = {
  selectedUserId: string;
  setSelectedUserId: (id: string) => void;
};

const UserContext = createContext<UserContextValue | null>(null);

export function UserProvider({ children }: { children: ReactNode }) {
  const [selectedUserId, setSelectedUserId] = useState<string>(PERSONAS[0].userId);

  return (
    <UserContext.Provider value={{ selectedUserId, setSelectedUserId }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used within a UserProvider");
  return ctx;
}
