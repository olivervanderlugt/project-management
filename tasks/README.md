# Tasks

One file per task. This is the queue the overnight run works from.

## The statuses

| Status    | Means                                                     | Overnight run                          |
| --------- | --------------------------------------------------------- | -------------------------------------- |
| `inbox`   | Captured, not thought through yet                          | Sharpens it into a proposal. No code.  |
| `ready`   | `## Done means` is written and concrete                    | May build it.                          |
| `doing`   | Someone is on it right now                                 | Leaves it alone.                       |
| `blocked` | Waiting on Ollie or on something external                  | Leaves it alone, may say why.          |
| `done`    | Finished and merged                                        | Ignores it.                            |

The line between `inbox` and `ready` is the whole point. A task without a
finish line produces work you throw away in the morning — which costs tokens
and gives you nothing.

## Capture is free, building is a decision

Anything Ollie says during the day lands here immediately as `inbox`. That is
cheap and never needs permission. Promoting a task to `ready` is a deliberate
act — his, or a proposal he approves.
