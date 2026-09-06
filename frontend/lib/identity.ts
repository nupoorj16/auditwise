// Three curated demo profiles, hand-picked from the dataset for genuinely
// distinct, demonstrable patterns (see the analysis behind these choices in
// project history) - not a generic per-user name generator. Each backstory
// is grounded in real numbers from that user's actual transaction history.

export type Persona = {
  userId: string;
  name: string;
  initials: string;
  colorVar: string;
  tagline: string;
  backstory: string;
};

export const PERSONAS: Persona[] = [
  {
    userId: "A_U036",
    name: "Ananya Rao",
    initials: "AR",
    colorVar: "--chart-1",
    tagline: "The balanced professional",
    backstory:
      "A mid-career professional splitting time between Pune, Delhi, and Bangalore. Her income is genuinely diversified across salary, bonus, freelance work, and investments, so her finances are mostly steady, with just a handful of flagged outliers.",
  },
  {
    userId: "A_U117",
    name: "Arjun Mehta",
    initials: "AM",
    colorVar: "--avatar-teal",
    tagline: "The freelancer",
    backstory:
      "An independent consultant whose freelance income ($785K) dwarfs every other source combined. Freelance payments arrive in irregular, lumpy amounts rather than a predictable paycheck, which is exactly why his transaction history has noticeably more flagged anomalies than a salaried profile.",
  },
  {
    userId: "A_U113",
    name: "Neha Kapoor",
    initials: "NK",
    colorVar: "--avatar-rose",
    tagline: "The volatile one",
    backstory:
      "Higher cost of living, mixed and irregular income streams, and the most flagged transactions of anyone in the dataset (18). Her rent alone runs well above every other profile's, and her income comes mostly from an ambiguous mix of bonuses and side income rather than one steady source.",
  },
];

export function getPersona(userId: string): Persona {
  return PERSONAS.find((p) => p.userId === userId) ?? PERSONAS[0];
}
