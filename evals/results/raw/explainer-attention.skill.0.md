Attention is the mechanism behind how large language models write, search, and help build software. The math draws on ideas from ordinary linear algebra, but the effect reaches far beyond the classroom.

## Vectors in Conversation

Attention represents every token in a sequence as three vectors: a **query**, a **key**, and a **value**. Each is just a linear projection — a matrix multiplication — of the token's embedding. That framing matters: instead of treating a sentence as a fixed, ordered list, attention lets every word ask a question (its query) and every other word offer an answer (its key). Context becomes something the model can search, not just a sequence it has to move through in order.

## Not All Tokens Matter Equally

Taking the dot product of a query and a key gives a similarity score between two tokens. Scale those scores and pass them through a softmax, and they become a probability distribution — weights that sum to one. So attention isn't applying fixed rules; it's deciding, for each token, what else in the sequence is worth weighing. That has a few consequences:

- Relevant context gets amplified; irrelevant context fades.
- A word ten tokens back is as reachable as the word right before it.
- The same mechanism works across languages, domains, and tasks without modification.

The output is the weighted sum of the value vectors, using those softmax weights — a blend of what the model judged worth attending to.

## Multi-Head Attention

Transformers rarely run just one attention computation. Multi-head attention runs several query-key-value operations in parallel, each free to pick up on a different kind of pattern — one head might track syntactic relationships, another something more semantic.

## Why It Holds Up

Attention has become a standard building block precisely because it's simple at its core: vectors, projections, weighted sums. That's also why it's worth understanding in the first place — the underlying operations don't change even as the architectures built on top of them do.
