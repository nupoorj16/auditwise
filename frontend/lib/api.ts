const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type UserListItem = {
  user_id: string;
  transaction_count: number;
};

export type UserSummary = {
  total_transactions: number;
  total_spend: number;
  total_income: number;
  anomalies_count: number;
  date_range_start: string | null;
  date_range_end: string | null;
};

export type CategorySpend = {
  category: string;
  total: number;
};

export type AnomalyRow = {
  transaction_id_clean: string;
  date_clean: string;
  category_clean: string;
  amount_clean: number;
  lower_bound: number;
  upper_bound: number;
  category_median: number;
  notes: string;
};

export type ChatContextRow = {
  transaction_id_clean: string;
  date_clean: string;
  category_clean: string;
  amount_clean: number;
  is_anomaly?: boolean;
  chunk_text: string;
};

export type ChatResponse = {
  answer: string;
  matched_count: number;
  aggregate: number | null;
  context_rows: ChatContextRow[];
};

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, init);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json();
}

export const api = {
  listUsers: () => fetchJson<UserListItem[]>("/api/users"),
  getSummary: (userId: string) => fetchJson<UserSummary>(`/api/users/${userId}/summary`),
  getSpendByCategory: (userId: string) => fetchJson<CategorySpend[]>(`/api/users/${userId}/spend-by-category`),
  getAnomalies: (userId: string) => fetchJson<AnomalyRow[]>(`/api/users/${userId}/anomalies`),
  chat: (userId: string, question: string) =>
    fetchJson<ChatResponse>("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, question }),
    }),
};
