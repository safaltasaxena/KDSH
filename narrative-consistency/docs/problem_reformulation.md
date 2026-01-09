## Problem Reformulation

We reformulate the task as a constraint consistency problem.

Given:
1. A long narrative describing the observable future behavior of a character.
2. A hypothetical backstory describing the character’s past.

The task is to decide whether the hypothetical backstory could logically and causally result in the observed narrative, without violating constraints implied by the narrative.

The system does not generate text or explanations.
It outputs a binary decision:
- 1: Backstory is globally consistent
- 0: Backstory is globally inconsistent
