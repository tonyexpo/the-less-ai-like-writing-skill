In modern language models, everything runs on **attention** — and the math behind it comes straight from linear algebra you already know.

## Vectors in Conversation

Attention represents every token as three vectors: a **query**, a **key**, and a **value** — each just a linear projection of the token's embedding. Rather than treating a sentence as a rigid, ordered list, attention lets every word "ask a question" (its query) and every other word "offer an answer" (its key).

## Not All Tokens Are Created Equal

Taking the dot product of queries and keys gives a similarity score between every pair of tokens. Scaling these scores and passing them through a softmax turns them into weights that sum to one. So attention isn't a fixed rule — it's a distribution recomputed for each input, deciding on the fly what matters most. Relevant context gets amplified, irrelevant context fades, and a word at the start of a sequence is just as reachable as one right next to it.

The output is the weighted sum of value vectors, using those softmax weights: a blend of what the model has chosen to attend to.

## Many Heads, Many Perspectives

Transformers usually run several of these query-key-value computations in parallel — multi-head attention. One head might catch one kind of pattern; several heads, run together, can catch more than one at once.

## Why It's Worth Understanding

Vectors, projections, weighted sums: that's the whole mechanism, and it's what's underneath most of the language models built today.
