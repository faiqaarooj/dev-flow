# 10 — Demo and Presentation Plan

## Demo objective

Prove the complete loop: a real finding is identified, explained, proposed for remediation, and checked again. Do not rely only on slides or AI-generated claims.

## Preparation

- Choose a small, public Python repository the team has permission to analyze, or use a local synthetic fixture for scanner testing.
- Verify the selected Bandit rule and expected result with the exact pinned tool version.
- Ensure no real secrets or personal data are present.
- Pre-test the GitHub and OpenAI network paths.
- Prepare a fallback recording/screenshots labeled as fallback if live connectivity fails.

## Live sequence

1. Explain the pain point: scanner output alone is hard to act on.
2. Paste the repository URL.
3. Show repository coverage and any excluded files.
4. Show Bandit findings with source, rule, file, line, and evidence where available.
5. Show AI explanations separately from scanner-confirmed results.
6. Select one finding and generate a proposed diff.
7. Explain the change and review notes.
8. Re-scan the proposed content.
9. Show `resolved`, `still_detected`, or `unverified` with the evidence and scope.
10. State limitations: no code execution, no upstream writes, Python-first, configured checks only.

## Suggested pitch structure

- Problem (20–30 seconds).
- Product and differentiator (30 seconds).
- Architecture and safe agent workflow (30 seconds).
- Live demo (2–3 minutes, depending on event rules).
- What is implemented versus planned (truthfully distinguish both).

## Differentiator

The differentiator is not merely “multiple agents.” It is a traceable remediation loop that connects a real scanner result to an explainable patch proposal and a fresh re-scan, while exposing remaining risk and coverage limits.

## Judge questions to prepare for

- How do you know the finding is real? Explain Bandit evidence versus AI-only observations.
- Can a repository prompt-inject the model? Explain that files are untrusted data and outputs are validated.
- Do you execute the submitted project? No.
- Does “resolved” mean secure? No; it means the relevant configured check no longer reports the matching finding in the analyzed content.
- What happens if the scanner or AI provider fails? The stage is marked failed/partial; it is not treated as zero findings.
- What does DNotifier specifically do? Answer only after confirming and testing the actual integration.
