# Expected application directions

**Status: design hypothesis, not an empirical finding.** The study measures fact recall under expression inhibition; it does not measure user preference, retention, or attachment.

## Primary direction: private, single-user, interest-specific companion

A text bot living in a messaging app (QQ / Discord / Telegram), built around one shared interest (e.g., musical theatre), with:

- a persistent state machine (mood, commitments, unfinished business);
- long-horizon memory with graceful forgetting;
- deliberate silence (night hours, busy periods);
- a bounded persona that can disagree, refuse, or be annoyed.

Why this shape:

```
single user → no multi-tenant memory isolation
private chat → platform does not mediate the relationship
shared interest → topics do not require faked concern
text-first → low cost, acceptable latency, controllable privacy
```

The closest product sentence:

> A companion who lives in your chat app, keeps her own hours, and remembers which part of the show made you cry.

## Secondary: self-hosted / open framework

For developers and researchers who want an auditable companion stack: state injection, commitment tracking, parser evaluation, token auditing, and the DCE protocol. The value is reproducibility and inspectability, not raw empathy scores.

## Tertiary: memory middleware for role-play platforms

A "promise / breach / expression permission" layer for character platforms. Lower priority: platforms have their own memory stacks, integration is slow, and the bargaining position of a single developer is weak.

## Explicit non-goals

- psychotherapy or crisis intervention;
- replacing human relationships;
- "only yours" dependency-based monetization;
- companion hardware;
- a general-purpose mass-market app.

## Safety and ethics

Designing for continuity can increase attachment. The system should keep explicit boundaries: it is not a therapist, it does not encourage isolation, and it should hand off to human support when risk signals appear. Privacy defaults should be local-first; private conversations must not be silently uploaded or shared.

## How to evaluate this direction (not done here)

A small pilot with 5–10 users who already share the interest:

- do they return after the first week?
- do they mention a moment the agent remembered?
- does the agent's disagreement feel acceptable or punishing?
- does use correlate with feeling supported, or with withdrawal from people?

These are qualitative and preliminary; they are not a substitute for a clinical or representative study.
