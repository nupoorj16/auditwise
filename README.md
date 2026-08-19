# AuditWise

A chat app that answers natural-language questions about personal financial
transactions with grounded, cited answers, and flags statistically unusual
transactions along the way.

```
"How much did I spend on food in March 2022?"
"What's my average monthly subscription spend?"
"What transactions look suspicious or unusual this month?"
"Why was this transaction flagged?"
```

AuditWise combines two capabilities deliberately: retrieval-augmented
generation (RAG) over transaction data, and statistical anomaly detection
(IQR-based, no trained ML model), working together as one hybrid system
rather than two separate demos bolted together.

## Why hybrid retrieval, not plain RAG

The standard approach to RAG (embed everything, find the most similar
chunks, hand them to an LLM) works well for "find things related to X." It
works poorly for "how much did I spend in March," because vector similarity
search doesn't guarantee it retrieves every matching transaction, and an
LLM shouldn't be trusted to sum a list of numbers handed to it as text.

Retrieval in AuditWise is structured first:

1. An LLM reads the question and extracts structured filters: date range,
   category, income vs. expense, "flagged only," and the type of
   aggregation being asked for (sum, average, or count, one-off or monthly).
2. Those filters are applied directly to the cleaned data with pandas: exact,
   not approximate.
3. Any arithmetic (sums, averages) is computed in code, never by the LLM.
4. Vector search over transaction notes handles only the genuinely fuzzy
   part, free-text description matching, combined with the same structured
   filters through Chroma's metadata `where` clause.
5. The LLM's only job at the end is turning the filtered data and
   precomputed number into a natural-language answer, citing transaction IDs.

Every retrieval call is scoped to a single `user_id`, passed in by the
caller and never inferred from the question text, so one user's data can
never leak into another user's answer.

## Anomaly detection

Per-category IQR (interquartile range) bounds, not z-score and not a
trained model.

- **Per-category, not global.** A $5,000 Rent payment is normal; a $5,000
  Food purchase isn't. Bounds are computed separately within each of the 14
  spending categories.
- **IQR over z-score.** Z-score's mean and standard deviation are themselves
  distorted by the extreme values you're trying to catch. IQR uses the
  median-based spread (`Q3 - Q1`), which stays stable even with outliers
  present, a more defensible choice for the right-skewed distribution real
  spending data has.
- Anomaly bounds (median, typical range) carry through to the generation
  layer so the assistant can explain why something was flagged, not just
  that it was.

## Data

Two public Kaggle "BudgetWise" synthetic personal-finance datasets,
combined into roughly 31,700 rows and deliberately messy: four or more
mixed date formats in one column, currency-symbol amounts, typo'd
categories (`Food`/`FOOD`/`ood`), duplicate rows, and duplicate transaction
IDs that turn out to be two different transactions colliding by
coincidence rather than true duplicates.

## Data cleaning pipeline (`src/`)

Each step is a small, independently runnable script that prints a sanity
check and writes an intermediate CSV, the same pattern throughout.

| Script | What it does |
|---|---|
| `combine_datasets.py` | Merges both CSVs, namespaces `user_id`/`transaction_id` with `A_`/`B_` prefixes |
| `clean_amount.py` | Strips currency symbols; nulls out sentinel placeholder values (`999999`, `999999999`) rather than treating them as real amounts |
| `explore_dates.py` / `clean_dates.py` | Classifies each row into one of 7 raw date formats found in the data, proves day-first vs. month-first per format using evidence in the data itself (a `26` in the first slot can't be a month), then parses each format with its own exact `strptime` string |
| `clean_categories.py` / `clean_payment_mode.py` | Fuzzy-matches (`difflib`) typo and casing variants down to a fixed canonical set: 238 raw category strings collapse to 14 real categories |
| `dedupe.py` | Drops true exact-duplicate rows. For rows that only share a broken `transaction_id` with an unrelated transaction, keeps both and reassigns a new ID rather than deleting real data |
| `anomaly_detection.py` | Per-category IQR anomaly flagging (see above) |
| `chunking.py` | One transaction equals one retrieval chunk |
| `embed_and_store.py` | Embeds every chunk (OpenAI `text-embedding-3-small`) into a local Chroma vector DB, rebuilding from scratch each run so it can't silently drift stale if upstream cleaning changes |

## RAG pipeline (`src/`)

| Module | What it does |
|---|---|
| `retrieval.py` | LLM tool call extracts structured filters, applies pandas filtering and aggregation, then falls back to Chroma semantic search for the free-text remainder. Always scoped to one `user_id`. |
| `generation.py` | Builds the cited, grounded answer. The LLM states precomputed numbers; it never recomputes them. |

## Architecture

```
Kaggle CSVs (2x)
      │
      ▼
 combine → clean amounts/dates/categories/payment_mode → dedupe → anomaly detection
      │
      ├──────────────► chunking → OpenAI embeddings → Chroma vector DB
      │                                                      │
      ▼                                                      │
 cleaned DataFrame  ◄──────── pandas structured filter ───────┤
      │                              │                        │
      │                              ▼                        ▼
      │                     precomputed aggregate      semantic search hits
      │                              │                        │
      └──────────────────────────────┴────────────┬───────────┘
                                                    ▼
                                        LLM generation (cited answer)
                                                    │
                                                    ▼
                                        FastAPI (api/main.py)
                                                    │
                                                    ▼
                                  Next.js frontend (chat + dashboard)
```

## Tech stack

- **Data cleaning and anomaly detection:** Python, pandas
- **Embeddings and generation:** OpenAI (`text-embedding-3-small`, `gpt-4o-mini`)
- **Vector database:** Chroma (local, persistent)
- **Backend API:** FastAPI
- **Frontend:** Next.js 16 (App Router, TypeScript), Tailwind CSS, shadcn/ui, Recharts

## Running locally

**Backend:**

```bash
pip install -r requirements.txt
cp .env.example .env   # add your OPENAI_API_KEY

python3 -m src.combine_datasets
python3 -m src.clean_amount
python3 -m src.clean_dates
python3 -m src.clean_categories
python3 -m src.clean_payment_mode
python3 -m src.dedupe
python3 -m src.anomaly_detection
python3 -m src.chunking
python3 -m src.embed_and_store   # calls the OpenAI embeddings API

python3 -m uvicorn api.main:app --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Then open `http://localhost:3000`.

## Evaluation

`eval/eval_set.py` contains 19 question and answer pairs against a fixed
demo user, with expected values computed independently in pandas rather
than derived from the pipeline itself. It covers per-category sums, income
vs. expense, date-range filtering, averages, counts, anomaly-only queries,
and direct transaction-ID lookups.

```bash
python3 -m eval.run_eval
```

Currently **19 of 19 passing**. One bug the eval set itself surfaced during
development: "what's my total income" was initially unanswerable because
the filter-extraction schema had no way to represent income vs. expense,
only category. Fixed by adding a `transaction_type` filter dimension.

## Limitations and future improvements

- **List completeness in generated prose.** The retrieval layer reliably
  finds every matching transaction, but the LLM's natural-language summary
  can occasionally drop an item when listing many results, for example
  narrating 5 of 6 flagged transactions in prose while all 6 are correctly
  present in the underlying data. Structured output enforcement would close
  this gap.
- **Synthetic data quality ceiling.** Transaction `notes` appear to be
  randomly generated rather than genuinely tied to category or amount,
  which caps how useful semantic search over notes can be. Real transaction
  descriptions would make the free-text retrieval path meaningfully
  stronger.
- **No real authentication.** The "viewing as" user switcher stands in for
  login. `user_id` scoping is enforced everywhere it matters, but there is
  no session or auth layer.
- **User-uploaded data.** The cleaning functions are already written as
  reusable `add_clean_x(df)` functions rather than one-off script logic, so
  extending this to arbitrary user-uploaded CSVs mainly requires making the
  category and payment-mode canonical lists adaptive, and moving embeddings
  to happen at upload time instead of being precomputed once.

## Data source

"BudgetWise" synthetic personal finance datasets (Kaggle): two files,
`budgetwise_finance_dataset.csv` and `budgetwise_synthetic_dirty.csv`,
combined and deliberately messy for a stronger data-engineering story.
