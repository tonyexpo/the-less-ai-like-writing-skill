Large language models are changing how we write, search, and build software, and the mechanism driving them is **attention**. The math behind it draws on ideas from linear algebra — ideas that, once you see how they're used here, reach well past the classroom.

## The Core Idea: Vectors in Conversation

At its heart, attention takes every token in a sequence and represents it as three vectors: a **query**, a **key**, and a **value**. In practice these are just linear projections — matrix multiplications — of the token's embedding. It's a subtle but important design choice: rather than treating a sentence as a rigid, ordered list, attention lets every word "ask a question" (its query) and every other word "offer an answer" (its key).

## Not All Tokens Are Created Equal

Once queries and keys exist, their dot products give a similarity score between every pair of tokens. Scaling these scores and passing them through a softmax turns them into a probability distribution — weights that sum to one. That detail matters: attention isn't applying fixed rules, it's deciding on the fly what matters most for each token. A few things follow from this:

- Relevant context gets amplified, while irrelevant context fades.
- Long-range relationships become as accessible as nearby ones.
- The same architecture adapts across languages, domains, and tasks.

The weighted sum of value vectors, using those softmax weights, produces the output — a blend that reflects what the model has chosen to "pay attention to."

## Many Heads, Many Perspectives

Rather than relying on a single attention computation, transformers typically use **multi-head attention**, running several query-key-value operations in parallel. A single head might capture one kind of pattern; running several in parallel lets the model capture more than one at a time.

## What Stays Constant

Attention has proven itself as a flexible building block, and the underlying linear-algebra intuition — vectors, projections, weighted sums — is what makes it possible to follow along as the architecture keeps changing.
