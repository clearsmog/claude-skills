# Advanced Plaintext Syntax

The PlaintextConverter supports additional features beyond basic indentation. Use these only when the user explicitly requests emphasis, connections, or annotations.

## Node Colors

Override a node's color with `{color: #hex}` after the topic text:

```
- Root Topic
  - Important Point {color: #e64553}
    - Detail
  - Normal Point
```

## Node IDs and Arrows

Assign an ID with `[^id]` and draw labeled connections between nodes:

```
- Root Topic
  - Concept A [^a]
    - Detail
  - Concept B [^b]
    - Detail
> [^a] <-influences-> [^b]
```

Arrow syntax: `> [^from] <-label-> [^to]` (bidirectional) or `> [^from] --label-> [^to]` (one-way).

## Summaries

Annotate a group of sibling nodes with `}` at the same indent level:

```
- Root Topic
  - Branch
    - Item 1
    - Item 2
    - Item 3
    } These three form a group
```

Use `}:N` to span only N siblings above: `}:2 Just these two`.
