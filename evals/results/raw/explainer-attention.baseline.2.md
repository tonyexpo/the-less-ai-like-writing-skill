## Vectors in Conversation

Attention is the mechanism at the core of large language models, and the math behind it draws on linear algebra you already know. It represents every token in a sequence as three vectors — a query, a key, and a value — each one a linear projection, a matrix multiplication, of the token's embedding. Rather than treating a sentence as a fixed, ordered list, this lets every word ask a question through its query and every other word offer an answer through its key.

## Not All Tokens Are Created Equal

Once queries and keys exist, their dot products give a similarity score between every pair of tokens. Scaling those scores and passing them through a softmax turns them into weights that sum to one, so attention isn't a fixed rule but a decision made fresh for each sequence. Relevant context gets amplified while irrelevant context fades, a token far back in the sequence stays as reachable as the one right before it, and the same architecture carries over across languages, domains, and tasks. The weighted sum of value vectors, using those softmax weights, produces the output — a blend of what the model has chosen to attend to.

## Many Heads, Many Perspectives

Transformers typically run several query-key-value operations in parallel rather than just one — multi-head attention. Where a single head might catch one kind of pattern, several heads run together can catch more than one at a time.

Hold onto the vectors, the projections, and the weighted sums, and most of what follows in a transformer paper will make sense.
