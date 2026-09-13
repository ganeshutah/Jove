# Chapter 7 &mdash; concept notebooks

One folder per *concept*, named for the concept rather than for a
lecture number or a course year. Each folder holds a notebook that
illustrates the concept, with definitions, tests and (where there is
a machine to show) an animation.

| Concept | Folder | Notebook |
|---|---|---|
| 1. Nondeterminism as Forking Tokens, and as Guessing | `Concept-Forking-Tokens/` | [Concept-Forking-Tokens.ipynb](Concept-Forking-Tokens/Concept-Forking-Tokens.ipynb) |
| 2. Why NFA Are Succinct, and Why They Are No More Powerful | `Concept-Why-NFA-Are-Succinct/` | [Concept-Why-NFA-Are-Succinct.ipynb](Concept-Why-NFA-Are-Succinct/Concept-Why-NFA-Are-Succinct.ipynb) |
| 3. $\varepsilon$-Transitions, and Whether They Are Essential | `Concept-Epsilon-Transitions/` | [Concept-Epsilon-Transitions.ipynb](Concept-Epsilon-Transitions/Concept-Epsilon-Transitions.ipynb) |
| 4. The Formal NFA: $(Q,\Sigma,\delta,Q_0,F)$ with $\delta: Q\times\Sigma_\varepsilon\to{\cal P}(Q)$ | `Concept-Formal-NFA-Tuple/` | [Concept-Formal-NFA-Tuple.ipynb](Concept-Formal-NFA-Tuple/Concept-Formal-NFA-Tuple.ipynb) |
| 5. Simulating an NFA Without $\varepsilon$: Tracking the Set of Token Positions | `Concept-Simulating-Without-Epsilon/` | [Concept-Simulating-Without-Epsilon.ipynb](Concept-Simulating-Without-Epsilon/Concept-Simulating-Without-Epsilon.ipynb) |
| 6. $Eclosure$: What $\varepsilon$ Edges Do to Simulation | `Concept-Eclosure/` | [Concept-Eclosure.ipynb](Concept-Eclosure/Concept-Eclosure.ipynb) |
| 7. The Language of an NFA: $\hat{\delta}$ via $Eclosure$–$\delta$–$Eclosure$ | `Concept-Delta-Hat-Via-Eclosure/` | [Concept-Delta-Hat-Via-Eclosure.ipynb](Concept-Delta-Hat-Via-Eclosure/Concept-Delta-Hat-Via-Eclosure.ipynb) |
| 8. Subset Construction: Converting an NFA to a DFA | `Concept-Subset-Construction/` | [Concept-Subset-Construction.ipynb](Concept-Subset-Construction/Concept-Subset-Construction.ipynb) |
| 9. Theorem: $L$ is Regular iff Some NFA Recognizes It | `Concept-Regular-Iff-NFA/` | [Concept-Regular-Iff-NFA.ipynb](Concept-Regular-Iff-NFA/Concept-Regular-Iff-NFA.ipynb) |
| 10. Brzozowski's Minimization: Reverse, Determinize, Reverse, Determinize | `Concept-Brzozowski-Minimization/` | [Concept-Brzozowski-Minimization.ipynb](Concept-Brzozowski-Minimization/Concept-Brzozowski-Minimization.ipynb) |
| 11. Reversal of a DFA Yields an NFA | `Concept-Reversal-Yields-NFA/` | [Concept-Reversal-Yields-NFA.ipynb](Concept-Reversal-Yields-NFA/Concept-Reversal-Yields-NFA.ipynb) |
| 12. A Complete Illustration of Brzozowski's Minimization on `blimp` | `Concept-Brzozowski-On-Blimp/` | [Concept-Brzozowski-On-Blimp.ipynb](Concept-Brzozowski-On-Blimp/Concept-Brzozowski-On-Blimp.ipynb) |

The prose for each concept lives in the companion workbook repo,
as `Concepts/Chapter-7-Concept-<N>.md`.
