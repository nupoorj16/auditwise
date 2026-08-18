"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api, UserListItem } from "./api";

type UserContextValue = {
  users: UserListItem[];
  selectedUserId: string | null;
  setSelectedUserId: (id: string) => void;
  loading: boolean;
};

const UserContext = createContext<UserContextValue | null>(null);

export function UserProvider({ children }: { children: ReactNode }) {
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listUsers()
      .then((list) => {
        setUsers(list);
        if (list.length > 0) setSelectedUserId(list[0].user_id);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <UserContext.Provider value={{ users, selectedUserId, setSelectedUserId, loading }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used within a UserProvider");
  return ctx;
}
