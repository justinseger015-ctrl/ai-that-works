---
guid: aitw-030
title: "Event-driven agentic loops"
description: |
  Key takeaway: treat agent interactions as an event log, not mutable state. Modeling user inputs, LLM chunks,
  tool calls, interrupts, and UI actions as a single event stream lets you project state for the UI, agent loop,
  and persistence without drift. We walk through effect-ts patterns for subscribing to the bus, deriving “current”
  state via pure projections, and deciding when to persist or replay events—plus trade-offs for queuing, cancelation,
  and tool orchestration in complex agent UX.
event_link: https://luma.com/event-driven-agents
eventDate: 2025-11-04T18:00:00.000Z
media:
  url: https://www.youtube.com/watch?v=_VB9TT1Vus4
  type: video/youtube
links:
  code: https://github.com/ai-that-works/ai-that-works/tree/main/2025-11-05-event-driven-agents
  youtube: https://www.youtube.com/watch?v=_VB9TT1Vus4
season: 2
episode: 30
event_type: episode
---




