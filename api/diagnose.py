"""
Temporary diagnostic entrypoint. A segfault bypasses Python's exception
handling, so we can't catch it - but we can print a marker after each
import/step, flushed immediately, so the LAST line in the logs before the
crash tells us exactly which step actually kills the process.
"""
import os
import sys

print("STEP 1: process started", flush=True)

import pandas  # noqa: E402
print("STEP 2: pandas imported", flush=True)

import fastapi  # noqa: E402
print("STEP 3: fastapi imported", flush=True)

from pydantic import BaseModel  # noqa: E402
print("STEP 4: pydantic imported", flush=True)

from openai import OpenAI  # noqa: E402
print("STEP 5: openai imported", flush=True)

from src.retrieval import load_data  # noqa: E402
print("STEP 6: src.retrieval imported", flush=True)

from src.generation import answer_question  # noqa: E402
print("STEP 7: src.generation imported", flush=True)

df = load_data()
print(f"STEP 8: data loaded, {len(df)} rows", flush=True)

from api.main import app  # noqa: E402
print("STEP 9: api.main app object built", flush=True)

import uvicorn  # noqa: E402
print("STEP 10: uvicorn imported, about to call uvicorn.run()", flush=True)

port = int(os.environ.get("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port, loop="asyncio", http="h11")

print("STEP 11: uvicorn.run() returned (should not happen while serving)", flush=True)
