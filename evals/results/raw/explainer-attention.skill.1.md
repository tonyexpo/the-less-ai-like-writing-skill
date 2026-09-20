Attention is the mechanism behind how large language models write, search, and generate code. It draws on linear algebra you likely already know, and understanding it is worth the time.

## Vectors in Conversation

Attention represents every token in a sequence as three vectors: a **query**, a **key**, and a **value**. Each is a linear projection — a matrix multiplication — of the token's embedding. Instead of treating a sentence as a fixed, ordered list, this lets every word "ask a question" (its query) that other words can "answer" (their keys).

## Not All Tokens Are Created Equal

Taking the dot product of a query and a key gives a similarity score between two tokens. Scale these scores and pass them through a softmax, and they become a probability distribution — weights that sum to one. Attention isn't applying fixed rules; it's deciding, token by token, what to weight most heavily. Relevant context gets amplified, irrelevant context fades, and a word can draw on another word many positions away just as easily as one right next to it.

The output is a weighted sum of the value vectors, using those softmax weights — a blend of what the model has chosen to draw on for that token.

## Many Heads, Many Perspectives

Transformers typically run several of these query-key-value operations in parallel — multi-head attention. Where one head might pick up on one kind of pattern, several heads running at once can pick up on several.

## Where This Leaves Us

The math is linear algebra: vectors, projections, weighted sums. That's what makes attention worth learning — the same handful of operations explain a mechanism now running across most of the software people use every day.
