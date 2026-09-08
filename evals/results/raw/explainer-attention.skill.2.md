In an era of language models reshaping how we write, search, and build software, the mechanism at their core is attention. The math behind it draws on linear algebra you likely already know.

## The Core Idea: Vectors in Conversation

Attention represents every token in a sequence as three vectors: a query, a key, and a value. These are linear projections — matrix multiplications — of the token's embedding. Rather than treating a sentence as a rigid, ordered list, attention lets every word "ask a question" (its query) and every other word "offer an answer" (its key).

## Not All Tokens Are Created Equal

Computing the dot product between queries and keys gives a similarity score for every pair of tokens. Scaling these scores and passing them through a softmax turns them into weights that sum to one. Attention isn't about memorizing fixed rules — it decides on the fly what matters most:

- Relevant context gets amplified, while irrelevant context fades.
- Long-range relationships become as accessible as nearby ones.
- The same architecture adapts across languages, domains, and tasks.

The output is the weighted sum of the value vectors, using those softmax weights — a blend of what the model has attended to.

## Many Heads, Many Perspectives

Transformers typically use multi-head attention: several query-key-value operations run in parallel. Where a single head might capture one kind of pattern, multiple heads can capture several at once.

## A Durable Foundation

Attention is a flexible building block, and its influence continues to spread across industries. As research evolves, the underlying linear-algebra intuition — vectors, projections, weighted sums — remains a durable way to understand whatever comes next.
