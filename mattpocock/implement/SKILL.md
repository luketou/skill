---
name: implement
description: "Implement a piece of work based on a spec or set of tickets, with the smallest diff that does the job."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets. Aim for the **smallest diff** that does the job: reuse what exists, subtract before you add.

If the user passes a ticket reference, fetch it from the issue tracker and state its title before starting. If the reference is ambiguous, ask.

## Steps

1. **Survey.** Find the code the work touches, and every existing function, helper and pattern that already does part of the job. Done when you can name what you will reuse and what you must add.
2. **Subtract.** In the code the work touches, delete what the change makes dead: unused code, redundant checks, stubs. Code beyond that is out of scope: list it in your final report for the user to decide on.
3. **Build.** Call the Skill tool with "tdd" where possible, at pre-agreed seams, following the lean rules below. Run typechecking regularly, single test files regularly, and the full test suite once at the end.
4. **Audit the diff.** For every function, type, file, parameter and option the diff adds, name why existing code or a few inline lines could not do the job; fold in each addition that has no answer. Done when every addition has one.
5. Call the Skill tool with "code-review" to review the work.
6. Commit your work to the current branch.

## Lean rules

- A new abstraction (function, class, wrapper, layer, config option) earns its place with two callers in this diff, or because the spec names it as a seam. Otherwise inline it.
- Each decision lives in one place; other code receives it as a plain value.
- When a new value would thread through several layers (types, schemas, signatures), first look for a direct path from where it is produced to where it is used.
- Keep the hierarchy flat: a reader can trace what the change does within three files.
- Tests the work needs are part of the smallest diff.
