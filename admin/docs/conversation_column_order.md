# Column order for conversation artifacts

An artifact that reports messages, chats, conversations, comments or posts puts the fields an
examiner reads first at the front of the table. The order is not a per-artifact choice. It is
derived from the roles the artifact already declares in its `data_views.conversation` block.

## The order

1. The declared `timeColumn`.
2. Every other column typed `datetime` or `date`, keeping their existing relative order.
3. `directionColumn`
4. `senderColumn`
5. `conversationLabelColumn`
6. `textColumn`
7. `mediaColumn`
8. Everything else, in whatever order the artifact already used.

A role that the artifact does not declare is simply skipped, and the columns after it move up.

`admin/scripts/check_conversation_column_order.py` enforces this and runs in CI.

## Why these fields, in this order

The timestamp leads because the report is read chronologically, and because an artifact that
goes to the timeline needs a `datetime` or `date` first column anyway.

Direction, sender, conversation and message text are what identify a message: when, which way,
who, in what thread, saying what. Media sits next to the message text because a media column
renders a thumbnail and is physically wide, so keeping it beside the text keeps the row that
carries the content readable.

Everything else is identifiers, state flags and raw values. Those matter, they are just not
what the examiner reads first.

## Reorder the row tuple in the same edit

`data_headers` and the row appended to `data_list` are co-indexed. Move one without the other
and every value lands under the wrong header. Nothing raises, and each value still looks
plausible, so this is not caught by reading the report.

Where the row comes straight from a query (`data_list.append(tuple(row))`), the `SELECT` list
is the row order. Reorder the `SELECT`, not the Python.

## What to do when a role is not declared

If a conversation artifact has a direction column that `data_views` does not name as
`directionColumn`, the mechanical order leaves it where it is, because the check only moves
what is declared.

Adding the declaration is worth doing, but it is a behaviour change, not a formatting one:
`directionColumn` and `directionSentValue` decide which side of LAVA's conversation view a
message renders on. Establish what the stored value means from a source before declaring it.
Do not guess a `directionSentValue` to make the column move.

## There is no external standard for this

CASE/UCO standardises the vocabulary for exchanging message data, not the layout of a report.
Its `observable:MessageFacet` defines `application`, `from`, `to`, `sentTime`, `messageID`,
`messageText`, `messageType` and `sessionID`, and nothing about column order. It has no
direction property at all, and no attachment property on the message facet, so the Direction
and Media columns here are LEAPP concepts with no outside standard to defer to.

Reference: Unified Cyber Ontology, `ontology/uco/observable/observable.ttl`, commit
`7ebb3957e9e9a2e1bb9c66cd1ede8c912a726344`,
https://github.com/ucoProject/UCO/blob/7ebb3957e9e9a2e1bb9c66cd1ede8c912a726344/ontology/uco/observable/observable.ttl
