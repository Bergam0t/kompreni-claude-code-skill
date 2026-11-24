# Kompreni – Project Handover

## 1. Project overview

**Working name:** `kompreni`

**Meaning:** Esperanto for "to understand" or "to comprehend".

**Core purpose:**

Help people understand, maintain and develop knowledge of codebases as AI coding agents make changes to them.

Kompreni is an idea for an AI agent skill (initially targeting Claude Code) that goes beyond the standard completion summary. It should help users understand what has changed, why it has changed, how the changes interact with the existing codebase, and what they need to know to maintain the resulting software.

The central philosophy is:

> Help people understand not just what an AI agent has changed, but how and why their codebase has evolved.

This is fundamentally about supporting human understanding, learning and retention, rather than simply generating changelogs or displaying diffs.

## 2. Background and motivation

AI coding agents can make substantial changes to codebases, often across multiple files and components.

Their normal completion summaries are useful, but frequently insufficient for maintaining a meaningful understanding of the software.

There are several related problems:

- Users can lose track of how their codebase works as agents modify it.
- Conventional Git diffs show what changed, but not necessarily why.
- Agent explanations often summarise implementation details without helping users develop a deeper mental model.
- Important architectural decisions and implementation rationale can disappear into old conversations.
- Future agents may repeat previous mistakes or make decisions without understanding the history of the codebase.

Kompreni aims to address these problems by turning agent activity into accessible explanations and, where appropriate, structured learning materials and persistent knowledge.

An important distinction is that this is not intended to replace Git, conventional documentation or existing codebase-understanding tools.

It should complement them.

## 3. Existing related project

The author has an existing project:

https://github.com/Bergam0t/tutorial-codebase-knowledge-claude-code-skill

This provides useful background and potentially reusable ideas.

That project focuses on understanding an existing codebase as a whole, producing structured tutorials that explain its architecture, abstractions and interactions.

Kompreni has a different emphasis:

- The existing tutorial skill explains how a codebase works.
- Kompreni explains how and why a codebase has changed.

The two could eventually work together: the tutorial provides an initial understanding, while Kompreni helps maintain that understanding as the software evolves.

Avoid simply duplicating the existing tutorial skill's functionality.

## 4. Proposed functionality

The project should be considered in three complementary layers.

### Layer 1: Conversational explanation

This is the simplest and potentially most frequently used functionality.

After an agent makes changes, Kompreni provides a deeper explanation in the conversation.

Potential content:

- Summary of the overall purpose of the changes.
- Changes grouped by functionality rather than simply by filename.
- Explanation of important implementation decisions.
- Before/after descriptions of relevant behaviour.
- Explanation of how modified components interact.
- Important limitations and potential consequences.
- Relevant tests and verification.

This should be relatively lightweight and should not require creating additional files.

A minor change should not trigger an unnecessarily elaborate report.

### Layer 2: Structured walkthroughs

For more substantial changes, Kompreni should be able to generate a structured Markdown or Quarto document.

Preferred formats:

- `.md` for straightforward Markdown documentation.
- `.qmd` for richer Quarto documents.
- HTML as an optional rendered output.

The purpose is to create a guided learning experience rather than a conventional change report.

Potential sections:

1. Overview of the changes.
2. The problem being addressed.
3. How the relevant functionality worked previously.
4. What has changed.
5. How the new implementation works.
6. How components interact.
7. Important implementation decisions and alternatives.
8. Tests and verification.
9. Limitations and potential knock-on effects.
10. Questions or exercises to reinforce understanding.

Potential Quarto features:

- Mermaid or other architecture diagrams.
- Annotated code snippets.
- Before/after comparisons.
- Cross-references to source files and relevant functions.
- Tabs for alternative implementations or explanations.
- Interactive learning exercises.
- Short knowledge-check questions.

The document should be useful independently of the original agent conversation.

It should also be proportionate: not every change warrants a full Quarto document.

### Layer 3: Persistent codebase knowledge

This is the longer-term ambition.

Kompreni could maintain a searchable history of significant codebase changes.

This would act as a form of institutional memory for both humans and future agents.

Potential information to preserve:

- What changed.
- When it changed.
- Why it changed.
- Which files, functions and components were affected.
- Important architectural decisions.
- Alternatives considered.
- Tests performed and their results.
- Known limitations.
- Relevant Git commits or pull requests.
- Links to earlier explanations.

Future agents could consult this history before making changes.

The distinction from Git is important:

- Git records changes to files.
- Kompreni records the knowledge and context needed to understand those changes.

This should not become an attempt to duplicate the entire Git history or automatically preserve every trivial edit.

## 5. Claude Code integration

Claude Code is the initial target environment.

There are three potentially complementary mechanisms.

### Skills

The core functionality should initially be implemented as a Claude Code skill.

The skill should contain instructions for:

- Inspecting and interpreting changes.
- Grouping changes meaningfully.
- Producing explanations.
- Generating Markdown and Quarto walkthroughs.
- Recording structured knowledge where appropriate.

The skill should ideally be independent of any particular UI implementation.

### Claude Code mods

Claude Code mods are a potentially valuable extension.

They offer an opportunity to integrate Kompreni more naturally into the Claude Code interface.

Potential functionality:

**Automatic change detection**
- Observe agent activity during a turn.
- Identify files created, modified or deleted.
- Capture relevant context about the work.
- Detect when a turn has completed.

**Dedicated interface**
- Show a summary of detected changes.
- Group modifications by functionality.
- Offer actions to generate explanations or walkthroughs.
- Provide access to previous knowledge records.

**Interactive change exploration**
- Navigate between modified files.
- Explore related components.
- Ask questions about specific changes.
- Access relevant walkthroughs.

An illustrative interface might offer:

- Quick explanation.
- Generate walkthrough.
- Update project knowledge.

The mod should be optional, rather than a dependency of the core project.

Important considerations:

- Claude Code mods are still a relatively new and evolving extension mechanism.
- Their API and compatibility need to be investigated against current Anthropic documentation.
- File-change events may not capture all modifications, particularly those made through Bash, scripts or other tools.
- A final Git-based comparison should supplement event capture.
- Mods have security implications and should not be treated as sandboxed extensions.

Anthropic has published a relevant example called Replay Theater, which captures file edits and allows users to step through them.

Investigate this as a potential source of implementation ideas.

### Other agent integrations

Although Claude Code is the initial target, avoid unnecessarily tying the underlying functionality to Claude-specific APIs.

A longer-term ambition could be supporting other coding agents.

Keep the core change-analysis and report-generation logic as portable as practical.

## 6. Suggested architecture

A conceptual architecture:

```text
       AI coding agent
              |
              v
       Change capture
              |
       +------+------+
       |             |
       v             v
   Git diff      Agent context
       |             |
       +------+------+
              |
              v
       Kompreni core
              |
       +------+----------------+
       |             |         |
       v             v         v
   Explanation   Walkthrough  Knowledge
       |             |         |
       v             v         v
      Chat        MD / QMD   Searchable
                  / HTML      history
```

The core should ideally accept a structured representation of changes, including:

- Changed files.
- Relevant diffs.
- Agent-provided context.
- Related source-code context.
- Test results.
- Commit references, where available.

It should produce structured explanations that can be rendered in different ways.

The precise technical architecture remains to be determined.

Do not over-engineer this before validating the core user experience.

## 7. Design principles

These are important constraints for the project.

### Human understanding comes first

The purpose is not simply to produce more documentation.

The output should genuinely improve someone's ability to understand and maintain their software.

### Explain rather than merely summarise

Avoid simply repeating the agent's completion summary.

Explain relationships, implementation choices, implications and relevant context.

### Proportionality

Different changes warrant different levels of explanation.

A small bug fix might need a short conversational explanation. A substantial architectural change might warrant a full walkthrough.

### Evidence-based explanations

Distinguish between:

- What can be established from the code and diffs.
- What the agent says it intended.
- What is inferred about the rationale.

Do not invent historical reasoning or confidently attribute motivations without evidence.

### Support learning and retention

Consider how explanations can help users develop lasting mental models.

Knowledge checks, guided examples and explanations of before/after behaviour are potentially valuable.

### Don't force documentation

Conversational explanations should remain a first-class output.

Not every agent interaction should produce a persistent document.

### Preserve provenance

Where possible, link explanations to actual files, functions, diffs, tests and commits.

### Keep the core portable

Claude Code-specific integrations should not dictate the architecture of the underlying project.

## 8. Naming and identity

The current preferred name is:

**Kompreni**

The name is Esperanto for understanding or comprehension.

It also fits alongside other projects using Esperanto-inspired naming conventions:

- `vidigi`
- `lokigi`
- `kompreni`

The name reflects the desired outcome rather than the implementation mechanism.

A possible tagline:

**Understand what changed, why it changed, and how it fits into your codebase.**

An alternative shorter tagline:

**Understand your code.**

The name has been subject to a preliminary web collision search. No obvious directly competing developer tool was identified, although some unrelated uses exist. A proper GitHub, package registry, domain and trademark availability check is still required.

## 9. Suggested initial development roadmap

The recommended approach is incremental.

### Phase 1: Establish the core skill

Create a working Claude Code skill that:

- Identifies changes made during an agent task.
- Examines the relevant diffs.
- Groups changes by purpose.
- Produces a substantially better explanation than the default completion summary.
- Can be invoked explicitly when the user wants a deeper explanation.

Test this on several different types of changes.

### Phase 2: Introduce Quarto

Add the ability to generate structured walkthroughs.

Experiment with:

- Markdown versus Quarto.
- Appropriate document structures.
- Annotated code.
- Architecture diagrams.
- Before/after explanations.
- Learning questions.

Determine when a full walkthrough is worthwhile.

### Phase 3: Define a structured knowledge format

Establish a reusable representation of a change explanation.

Consider Markdown with YAML front matter, or another simple structured format.

The format should support future search and agent consumption.

Do not prematurely commit to a database or elaborate knowledge graph.

### Phase 4: Explore Claude Code mods

Investigate the current mod API and build a small proof of concept.

The first useful interaction might simply be:

1. Detect that a meaningful agent task has completed.
2. Offer a Kompreni explanation.
3. Allow the user to request a Quarto walkthrough.

Avoid building a complex interface initially.

### Phase 5: Persistent knowledge

Explore how reports can accumulate into a searchable project history.

Investigate how future agents can retrieve relevant records before making changes.

Consider how to avoid duplicated, stale or contradictory knowledge.

## 10. Questions for the next agent to investigate

The following are open questions, not decisions already made.

1. What is the best way to capture a complete and reliable account of changes made by Claude Code?
2. Which Claude Code lifecycle events and mod APIs are relevant?
3. Can a skill, mod and hooks work together cleanly?
4. What information should be captured during an agent turn versus reconstructed afterwards?
5. How should changes be grouped into meaningful functional units?
6. What makes a change walkthrough genuinely educational rather than just verbose?
7. How can Quarto be used to improve the learning experience without creating unnecessary complexity?
8. What should the persistent knowledge format look like?
9. How should future agents search and retrieve previous change explanations?
10. What is the simplest useful MVP?

## 11. Immediate recommendation

Start with a relatively small, working version of Kompreni as a Claude Code skill.

The initial success criterion should be:

> Given a completed coding task, can Kompreni produce an explanation that helps a developer understand the changes substantially better than the agent's normal completion summary?

Once this works, experiment with Quarto walkthroughs.

Treat persistent knowledge and Claude Code mods as important future directions, but don't let either delay validation of the fundamental idea.

The long-term ambition is more exciting than a conventional diff explanation tool: a system that helps people and AI agents maintain an evolving understanding of a codebase, including the history and reasoning behind its development.
