# 08 — Testing and Quality Plan

## 1. Testing layers

### Unit tests
- GitHub URL parsing and validation.
- Path normalization and rejection of traversal paths.
- Bandit JSON parsing and finding normalization.
- Finding priority/rationale schema validation.
- Verification status calculation.
- Patch target-path validation.

### Integration tests
- GitHub API adapter against mocked responses or a controlled public test repository.
- Bandit adapter against intentionally vulnerable sample files.
- OpenAI adapter against mocked model outputs, including malformed JSON and timeouts.
- API route contracts and error responses.
- SQLite persistence and retrieval if enabled.

### End-to-end tests
- Submit a repository and display findings.
- Request a patch and view the diff.
- Re-scan a patch that removes a known Bandit finding.
- Show still-detected and unverified states.
- Confirm original GitHub repository remains unchanged.

## 2. Test fixture

Create a small local fixture folder containing safe synthetic examples designed to trigger a known Bandit rule. Do not put real credentials in the fixture. Keep expected findings tied to the pinned Bandit version because rule output can change across versions.

## 3. Failure cases to test

- Malformed URL, unsupported host, nonexistent repository.
- GitHub API rate limit or network timeout.
- Empty repository and repository with no Python files.
- File count/size limit reached.
- Bandit not installed, timeout, nonzero exit, or invalid output.
- OpenAI API timeout, quota error, malformed response, refusal, or invalid patch.
- Patch references a file outside the scanned set.
- Re-scan fails or coverage differs.

## 4. Definition of done for a feature

A feature is done only when:
1. Its contract is documented.
2. Its implementation is committed.
3. Its normal path is tested.
4. At least one relevant failure path is tested.
5. The UI does not hide errors or overstate certainty.

## 5. Demo quality gates

- Pin dependencies where possible before final demo.
- Test with a known controlled repository, not a random repository discovered minutes before judging.
- Keep a fallback recorded screenshot or local fixture if network access fails, while clearly labeling it as fallback data.
- Never fabricate live scan output and describe it as real.
