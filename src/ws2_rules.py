"""WS2 rule-based complaint classifier (no LLM needed).

Portuguese keyword rules built from docs/ws2_taxonomy.md. Checked in a fixed priority
order: specific complaints (partial, wrong item, damaged) win over the general
"not delivered", which wins over "late".

Usage:
  python src/ws2_rules.py            # evaluate on the 200 labels (dev 1-100, test 101-200), classify all reviews
"""
import re
import unicodedata
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline

WS2 = Path("data/processed/ws2")
LABELS = Path("reports/ws2/label_sample.csv")   # committed reference labels (Claude-labelled, human spot-check pending)
BAR = 0.70


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", s.replace("ñ", "nao"))


NUM = r"(um|uma|0?[1-9]|dois|duas|tres|quatro|metade)"
RULES = [
    ("partial_or_missing", [
        rf"\bso (recebi|veio|chegou|tinha|tive) {NUM}\b", rf"\bapenas {NUM}\b", rf"\bsomente {NUM}\b",
        r"recebi apenas", r"recebi somente", r"\bfalt(ou|ando|a o|a a|am)\b", r"\bo que falta\b", r"incomplet",
        r"pela metade", r"\bo restante\b", r"\bso veio\b", r"\bveio sem\b", r"\bsem o (manual|pino|cabo|controle)",
        r"vieram apenas", r"quantidade (correta|errada)", r"\ba outra\b.*(esperando|aguardando|noticia)",
        r"todos os outros .* (ja|foram) .* (entregues|chegaram)", r"(recebi|veio|chegou|entregou|enviaram) (so |apenas |somente )?(a )?metade",
        r"\bveio metade\b", r"so (entregaram|foi entregue|entregou)", r"\brecebi so\b", r"apenas recebi", r"recebid[oa]s? .{0,40} mas nao", r"(unidades?|pecas|kits?) .{0,30}(so|apenas) (recebi|veio|chegou)",
    ]),
    ("wrong_item", [
        r"\berrad[oa]s?\b(?!.*nota)", r"produto errado", r"diferente do (que )?(pedi|pedido|comprei)",
        r"outra marca", r"outro produto", r"\bcor (errada|diferente|solicitada)", r"\bvoltagem\b",
        r"\b(110|220) ?v", r"no lugar de", r"\bveio um de\b", r"produto correto", r"nada (a ver|haver)",
        r"(pedi|solicitei|comprei) .{0,40} e (recebi|veio|me (enviaram|mandaram|entregaram))",
        r"me (enviaram|mandaram) (um|uma|o pior)", r"tamanho errado", r"\bmandaram qualquer",
        r"totalmente diferente", r"divergente", r"ao inves", r"veio outr[oa]", r"encomendei .{0,40}(e veio|mas)",
        r"mas encomendei", r"nao e o mesmo produto", r"recebi (o |um |uma )?outr", r"\brecebi?e? ?outro\b", r"cor(es)? pedid", r"me (mandaram|enviaram|mandarao) (o |a )?(pior|preto|branco|azul|rosa|vermelho|outr)",
    ]),
    ("damaged_defective", [
        r"quebr", r"defeito", r"danific", r"avari", r"nao funcion", r"trincad", r"rachad", r"amassad",
        r"\bmanchas?\b", r"\bsujo\b", r"descol", r"nao (houve possibilidade|consegui) (de )?instalar", r"para o lixo",
        r"bamba", r"diferenca", r"\bmaior do que\b", r"manchad", r"vazand", r"veio aberto", r"funcionando", r"aquecend", r"rasgad", r"corroid", r"riscad", r"\busado\b",
    ]),
    ("not_delivered", [
        r"nao (recebi|recebir|recebemos|chegou|chegaram|veio|foi entregue|foram entregues|entregaram|entregou|entregue)",
        r"\bnao (rercebi|recebido)", r"\bn (chegou|recebi)\b", r"ainda nao", r"ate (agora|hoje|o momento)[ ,.!]*(nada|nao)",
        r"\bnada\.{0,3} ?$", r"nem sinal", r"extravi", r"nunca chegou", r"ainda sem receber", r"pendente de entrega",
        r"\bmas nd\b", r"estou aguardando\.?$", r"consta (como )?(produto )?entregue", r"\be nada\b", r"sala vazia",
        r"ate (agora|hoje)[ ,]+nada", r"ate a presente data",
        r"quero (o )?meu produto", r"solicito (a )?entrega", r"aguardo do produto", r"nao ocorreu", r"nao entrega\b", r"esperando o produto", r"aguar?dando o produto", r"quando chega", r"nem cheg", r"aguardando (o produto|a entrega|minha|meu)",
    ]),
    ("quality_not_as_described", [
        r"qualidade", r"pessim[oa]", r"original", r"falsific", r"autentic", r"propaganda enganosa", r"descri",
        r"anuncio", r"\bfoto\b", r"tecido", r"material", r"\bfino\b", r"mal acabad", r"acabamento",
        r"nao corresponde", r"menor", r"vagabund", r"\bruim\b", r"esperava", r"impermeavel", r"nao e adesiv",
        r"similar", r"inferior", r"\bfinas?\b", r"pequen", r"expectativa", r"nao gostei",
        r"\btamanho\b", r"difere", r"nao (realiza|vale)", r"\bcaro\b", r"transparente", r"aquem", r"ficha tecnica",
    ]),
    ("late", [
        r"atras", r"demor", r"\bprazo", r"agilidade", r"nao cumpr", r"compriu", r"\bcorreios?\b", r"lentid", r"tempo de entrega",
    ]),
    ("seller_service", [
        r"respost", r"respond", r"retorno", r"contato", r"atendimento", r"reembols", r"estorno", r"cancel",
        r"satisfacao", r"posicionamento", r"\bsac\b", r"devolu", r"\btroca\b", r"ressarc", r"devolver", r"compromisso",
    ]),
]
COMPILED = [(lab, [re.compile(p) for p in pats]) for lab, pats in RULES]


def classify(text: str) -> str:
    t = norm(text)
    if not t.strip() or t == "nan":
        return "other"
    for lab, pats in COMPILED:
        if any(p.search(t) for p in pats):
            return lab
    return "other"


def report(name, y, yhat):
    f1 = f1_score(y, yhat, average="macro", zero_division=0)
    acc = accuracy_score(y, yhat)
    print(f"{name:<28} accuracy {acc:.3f}  macro-F1 {f1:.3f}  -> {'PASS' if f1 >= BAR else 'below bar'}")
    return acc, f1


def main():
    lab = pd.read_csv(LABELS)
    lab["rule_label"] = lab.comment.map(classify)
    dev, test = lab.iloc[:100], lab.iloc[100:]

    print("Rules")
    report("  dev (reviews 1-100)", dev.human_label, dev.rule_label)
    acc, f1 = report("  test (reviews 101-200)", test.human_label, test.rule_label)
    report("  all 200", lab.human_label, lab.rule_label)

    tfidf = make_pipeline(TfidfVectorizer(preprocessor=norm, ngram_range=(1, 2), min_df=1, sublinear_tf=True),
                          LogisticRegression(max_iter=2000, class_weight="balanced"))
    tfidf.fit(dev.comment.fillna(""), dev.human_label)
    print("TF-IDF + logistic regression (trained on 1-100)")
    report("  test (reviews 101-200)", test.human_label, tfidf.predict(test.comment.fillna("")))

    print("\nRules on all 200, per class:")
    print(classification_report(lab.human_label, lab.rule_label, zero_division=0))
    labels = [l for l, _ in RULES] + ["other"]
    cm = pd.DataFrame(confusion_matrix(lab.human_label, lab.rule_label, labels=labels), index=labels, columns=labels)
    print(cm.to_string())
    lab.to_csv(WS2 / "label_sample_rules.csv", index=False)

    allr = pd.read_csv(WS2 / "low_reviews_all.csv")
    allr["complaint"] = allr.comment.map(classify)
    allr.to_csv(WS2 / "low_reviews_classified.csv", index=False)
    names = {"not_delivered": "Not delivered", "late": "Late", "partial_or_missing": "Partial / missing item",
             "wrong_item": "Wrong item", "damaged_defective": "Damaged / defective",
             "quality_not_as_described": "Quality / not as described", "seller_service": "Seller service",
             "other": "Other / unclear"}
    group = {"partial_or_missing": "Product & fulfilment", "wrong_item": "Product & fulfilment",
             "damaged_defective": "Product & fulfilment", "quality_not_as_described": "Product & fulfilment",
             "not_delivered": "Delivery", "late": "Delivery", "seller_service": "Service", "other": "Other"}
    pd.DataFrame({"review_id": range(1, len(allr) + 1), "order_id": allr.order_id,
                  "complaint": allr.complaint.map(names), "complaint_group": allr.complaint.map(group),
                  "delivery_status": allr.is_late.map({0: "On time", 1: "Late"}),
                  "seller_count": allr.n_sellers.map(lambda n: "Multi-seller" if n > 1 else "Single seller"),
                  "review_score": allr.review_score}).to_csv("data/processed/mart/fact_complaints.csv", index=False)
    pd.DataFrame({"set": ["test 101-200"], "accuracy": [acc], "macro_f1": [f1]}).to_csv(WS2 / "rules_eval.csv", index=False)
    print(f"\nClassified {len(allr):,} reviews -> {WS2/'low_reviews_classified.csv'}")
    print((allr.complaint.value_counts(normalize=True) * 100).round(1).to_string())


if __name__ == "__main__":
    main()
