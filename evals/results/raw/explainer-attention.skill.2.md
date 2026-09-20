In an era where large language models are reshaping how we write, search, and build software, understanding the mechanism at their core has never been more valuable. That mechanism is **attention**, and the math behind it comes from linear algebra you've probably already seen.

## Queries, Keys, and Values

Attention represents every token in a sequence as three vectors: a **query**, a **key**, and a **value**. In practice these are just linear projections — matrix multiplications — of the token's embedding. Rather than treating a sentence as a rigid, ordered list, this lets every word "ask a question" (its query) that every other word can "answer" (its key).

## Weighing What Matters

Once queries and keys exist, their dot products give a similarity score between every pair of tokens. Scaling these scores and passing them through a softmax turns them into weights that sum to one — a probability distribution rather than a fixed rule. That's what lets attention decide, for each token, what to focus on instead of applying the same pattern every time. A few things follow from this:

- Relevant context gets amplified, irrelevant context fades.
- Long-range relationships become as accessible as nearby ones.
- The same architecture adapts across languages, domains, and tasks.

The weighted sum of the value vectors, using those softmax weights, produces the output — a blend that reflects what the model is, in effect, paying attention to.

## Splitting Attention Into Heads

Transformers typically don't rely on a single attention computation. Multi-head attention runs several query-key-value operations in parallel, so where one head might capture a single kind of pattern, multiple heads can capture several at once.

## What Stays the Same

What carries over as the field moves — new architectures, new tricks — is the same linear-algebra core: vectors, projections, weighted sums. That's the part worth actually understanding.
