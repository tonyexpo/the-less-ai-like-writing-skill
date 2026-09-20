Large language models are reshaping how we write, search, and build software, which makes the mechanism at their core worth understanding on its own terms. That mechanism is **attention**, and the math behind it draws on linear algebra you likely already know.

## The Core Idea: Vectors in Conversation

Attention represents every token in a sequence as three vectors: a **query**, a **key**, and a **value**. In practice these are linear projections — matrix multiplications — of the token's embedding. Rather than treating a sentence as a rigid, ordered list, attention lets every word "ask a question" (its query) and every other word "offer an answer" (its key).

## Not All Tokens Are Created Equal

Once queries and keys exist, their dot products give a similarity score between every pair of tokens. Scaling these scores and passing them through a softmax turns them into weights that sum to one. Attention isn't memorizing fixed rules; it's deciding, on the fly, what matters most for a given token. Relevant context gets amplified, irrelevant context fades, and long-range relationships become as accessible as nearby ones — all from the same mechanism.

The output is a weighted sum of value vectors, using those softmax weights: a blend of what the model has chosen to attend to.

## Many Heads, Many Perspectives

Transformers typically use **multi-head attention** — running several query-key-value operations in parallel rather than relying on one. A single head might capture one kind of pattern; several heads, run together, can capture more than one at once.

## Where This Leaves Us

The vectors, projections, and weighted sums underneath attention are ordinary linear algebra. What they produce — a mechanism that decides what to weigh, per token, per context — is most of why current language models work as well as they do.
