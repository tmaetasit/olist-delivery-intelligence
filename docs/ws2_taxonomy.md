# WS2 Complaint Taxonomy

Used by humans (200-review validation sample) and by the LLM. One label per review: the **main** reason the customer is unhappy. Reviews are in Portuguese; the cue words help human labellers.

| Label | Meaning | Portuguese cues |
|---|---|---|
| `not_delivered` | Customer says the product never arrived | não chegou, não recebi, ainda não recebi |
| `late` | Arrived, or still waiting, later than promised | atraso, atrasou, demorou, prazo |
| `partial_or_missing` | Only part of the order arrived, or an item is missing | faltou, veio só, apenas um, incompleto, falta |
| `wrong_item` | Different product, model, colour or size from the one ordered | errado, diferente do pedido, cor errada, outro produto |
| `damaged_defective` | Broken, damaged or does not work | quebrado, defeito, danificado, não funciona, avariado |
| `quality_not_as_described` | Works, but quality is poor or differs from the listing | qualidade, péssimo, diferente do anúncio, material |
| `seller_service` | Problems with seller or store contact, refund, cancellation | atendimento, sem resposta, reembolso, cancelar, estorno |
| `other` | No clear complaint, positive text, or none of the above | — |

## Rules
1. Pick the reason that would have to be fixed for the customer to be happy.
2. "Ainda não recebi" (still not received) → `not_delivered`, even if the order is late too.
3. "Recebi só um dos produtos" (received only one) → `partial_or_missing`.
4. If two reasons are equally strong, prefer the one earlier in the table.

## Quality bar
Macro-F1 of the LLM against the 200 human labels must reach **0.70** before the labels are used for KPI 15. If it does not, refine the prompt with the confusion matrix (most errors usually sit between `late` and `not_delivered`).
