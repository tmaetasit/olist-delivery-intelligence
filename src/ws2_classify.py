"""WS2 step 2: classify review comments with a local LLM (LM Studio).

Start LM Studio, load an instruction model (e.g. a 7–8B Qwen or Llama), and start the
local server (default http://localhost:1234). Then:

  python src/ws2_classify.py --input data/processed/ws2/label_sample.csv     # validate first
  python src/ws2_classify.py --input data/processed/ws2/low_reviews_all.csv  # then everything
  python src/ws2_classify.py --dry-run                                        # print one prompt

Output: same file name with _llm.csv, adding an llm_label column. Resumes if stopped.
Data never leaves the machine: the model runs locally.
"""
import argparse
import json
import os
import time
import urllib.request

import pandas as pd

LABELS = ["not_delivered", "late", "partial_or_missing", "wrong_item",
          "damaged_defective", "quality_not_as_described", "seller_service", "other"]

SYSTEM = """You classify Brazilian Portuguese e-commerce reviews by the MAIN reason the customer is unhappy.
Answer with exactly one label from this list and nothing else:
not_delivered - product never arrived ("não chegou", "não recebi", "ainda não recebi")
late - arrived or still coming later than promised ("atraso", "demorou", "prazo")
partial_or_missing - only part of the order arrived or an item is missing ("faltou", "veio só", "apenas um", "incompleto")
wrong_item - different product, model, colour or size ("errado", "diferente do pedido", "outro produto")
damaged_defective - broken, damaged or not working ("quebrado", "defeito", "não funciona")
quality_not_as_described - works but poor quality or unlike the listing ("qualidade", "diferente do anúncio")
seller_service - seller/store contact, refund or cancellation problems ("atendimento", "reembolso", "cancelar")
other - no clear complaint or none of the above
Rules: "still not received" is not_delivered. "Received only one of the products" is partial_or_missing.
If two reasons are equally strong, choose the one earlier in the list."""


def ask(url, model, text, timeout=120):
    body = {"model": model, "temperature": 0, "max_tokens": 12,
            "messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": f"Review: {text}\nLabel:"}]}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        answer = json.load(r)["choices"][0]["message"]["content"].strip().lower()
    for label in LABELS:                       # tolerate extra words around the label
        if label in answer:
            return label
    return "other"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="data/processed/ws2/label_sample.csv")
    p.add_argument("--url", default="http://localhost:1234/v1/chat/completions")
    p.add_argument("--model", default="local-model", help="model id shown in LM Studio")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    df = pd.read_csv(a.input)
    if a.dry_run:
        print(SYSTEM, "\n\nReview:", df.comment.iloc[0], "\nLabel:")
        return
    out = a.input.replace(".csv", "_llm.csv")
    if os.path.exists(out):                     # resume
        done = pd.read_csv(out)
        df = df.merge(done[["order_id", "llm_label"]], on="order_id", how="left")
    else:
        df["llm_label"] = None

    start = time.time()
    todo = df.index[df.llm_label.isna()]
    for n, i in enumerate(todo, 1):
        try:
            df.at[i, "llm_label"] = ask(a.url, a.model, str(df.at[i, "comment"]))
        except Exception as e:                   # keep going; failed rows stay empty for the next run
            print(f"row {i}: {e}")
        if n % 50 == 0 or n == len(todo):
            df.to_csv(out, index=False)
            rate = n / (time.time() - start)
            print(f"{n}/{len(todo)} done, {rate:.1f} reviews/s")
    df.to_csv(out, index=False)
    print(df.llm_label.value_counts().to_string())


if __name__ == "__main__":
    main()
