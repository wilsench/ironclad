# Extending to another rule domain

The database policy is the shipped default, not the ceiling. A company has opinions about API shape, error envelopes, naming, feature flags, logging. Same architecture applies: policy file carries the rule, checker carries the mechanical part.

## 1. Write the rule with an ID

Namespace by domain so citations stay short and sortable:

| Prefix | Domain |
|---|---|
| `DB-` | schema, migrations, storage |
| `API-` | request/response contract, versioning, error shape |
| `APP-` | layering, naming, dependency direction |
| `SEC-` | auth, secrets, input validation |
| `PR-` | process — review, tests, release |

Rules must be **checkable or reviewable**. "Code should be clean" is neither; delete it. "Every list endpoint returns `{data, meta}` with `meta.total`" is reviewable and mostly checkable.

## 2. Add a checker rule

In `scripts/check_schema.py`, follow the existing shape:

```python
# 1. compile the pattern once, at module level
NEW_RULE = re.compile(r"...", re.I)

# 2. inside check_file(), after the existing rules
m = NEW_RULE.search(line)
if m:
    findings.append({"rule": "API-01", "line": i, "file": str(path),
                     "msg": "..."})
```

Three constraints that keep the checker trustworthy:

- **Skip comments.** The loop already strips `//`, `#`, `--`, `*`, and block comments. A checker that flags its own documentation gets disabled.
- **Skip the legitimate exception.** `CHECK (...)` is where literal codes belong; `DB-02` skips them via paren depth. Every rule needs its exception understood before it ships.
- **Test both directions.** One fixture that must fail, one that must pass. A rule that only ever fires is either wrong or miscalibrated.

## 3. Widen the file scan

`TARGETS` and `SKIP_DIRS` at the top of the script control what gets read. Add an extension only after confirming the rule's pattern does not fire on unrelated syntax in that language.

```python
TARGETS = {".sql", ".php", ".prisma", ".ts"}   # add deliberately
SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".next",
             "storage", "__pycache__"}
```

## 4. Roll out without a mutiny

A checker that fails 400 legacy violations on day one gets deleted from CI by lunch. Sequence:

1. **Report-only.** Print findings, exit 0. Let the team see the shape of the debt.
2. **Gate changed files.** Run on the diff, not the repo. New violations block; old ones do not.
3. **Gate the repo.** Only after the baseline is clean or explicitly allowlisted.

An allowlist file (`standards-ignore.txt`) with one path per line and a required comment beats a `# noqa` culture, because it is reviewable in a PR.

## 5. Keep the policy file honest

The policy file is the contract. When someone adds a `CHECK` that hardcodes every legal code, or a status column with no FK, the fix belongs in review against `.agent/standards.md` — not in a private exception inside the checker. Every exception that lives only in code is a rule that will be re-litigated next quarter.
