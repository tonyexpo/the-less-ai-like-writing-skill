Large language models are changing how we write, search, and build software, and the mechanism at their core is **attention**. The math behind it comes straight from linear algebra — vectors, projections, dot products — even though what it produces looks nothing like a textbook exercise.

## The Core Idea: Vectors in Conversation

Attention represents every token in a sequence as three vectors: a **query**, a **key**, and a **value**. These are linear projections — matrix multiplications — of the token's embedding. Rather than treating a sentence as a rigid, ordered list, attention lets every word "ask a question" (its query) and every other word "offer an answer" (its key).

## Not All Tokens Are Created Equal

Taking the dot product of a query with every key produces a similarity score between that token and every other token in the sequence. Scaling those scores and passing them through a softmax turns them into weights that sum to one. Because the weights are computed fresh for each input rather than fixed in advance, relevant context gets amplified, long-range relationships become as accessible as nearby ones, and the same mechanism works across languages, domains, and tasks without modification.

The output for each token is the weighted sum of the value vectors, using those softmax weights.

## Many Heads, Many Perspectives

Rather than running one query-key-value computation, transformers typically run several in parallel — multi-head attention. A single head might settle on one kind of pattern; running several at once lets the model pick up on more than one at a time.

## What Stays Constant

Vectors, projections, dot products, weighted sums — that's the whole toolkit attention is built from, and it's the same toolkit underneath every architecture built on top of it since. Understanding it is a reasonable place to start if you want to understand what comes next.
