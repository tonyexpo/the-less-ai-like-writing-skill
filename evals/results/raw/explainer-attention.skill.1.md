In an era where large language models are reshaping how we write, search, and build software, understanding the mechanism at their core has never been more valuable. That mechanism is **attention**, and while the math behind it draws on ideas you already know from linear algebra, its impact reaches far beyond the classroom.

Actually, let me just write the revised draft directly rather than narrate my edits.

## The Core Idea: Vectors in Conversation

Large language models are changing how we write, search, and build software, and at the core of nearly all of them is one mechanism: **attention**. The math behind it draws on linear algebra you likely already know — vectors, projections, weighted sums.

At its heart, attention represents every token in a sequence as three vectors: a **query**, a **key**, and a **value**. In practice these are linear projections — matrix multiplications — of the token's embedding. This is a subtle but important design choice: instead of treating a sentence as a rigid, ordered list, attention lets every word ask a question (its query) and every other word offer an answer (its key).

## Not All Tokens Are Created Equal

Once queries and keys exist, their dot products give a similarity score between every pair of tokens. Scaling these scores and passing them through a softmax turns them into a probability distribution — weights that sum to one. Attention isn't applying fixed rules; it's deciding, for each token, what matters most, and that decision changes with every input:

- **Relevant context gets amplified**, while irrelevant context fades.
- **Long-range relationships** become as accessible as nearby ones.
- **The same architecture** adapts across languages, domains, and tasks.

The weighted sum of value vectors, using those softmax weights, produces the output — a blend of what the model has chosen to attend to.

## Many Heads, Many Perspectives

Rather than relying on a single attention computation, transformers typically use **multi-head attention**: several query-key-value operations running in parallel. Where a single head might capture one kind of pattern, multiple heads can capture several at once.

## The Foundation Holds

Attention has proven to be a flexible building block, and it keeps getting adapted into new variants. What doesn't change is the linear-algebra intuition underneath it — vectors, projections, weighted sums — which is what makes it possible to follow how any of those variants actually work.
