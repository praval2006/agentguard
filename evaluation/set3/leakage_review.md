# Specification leakage review

This administrative document is not planner/grounder input.

Reviewed all five specs before freeze:

- No scenarios, action-schema examples, verdicts, executable percentages or derivation
  instructions occur in the specs. No implementation exists to reveal or annotate.
- Display names have no concrete example merely for grounding. Their free-form meaning
  is specified as product policy, while storage and unrelated-field preservation remain.
- Weight boundaries, cents tariff and currency make a shipping quote implementable.
  They are business rules, not a target test outcome or deliberately planted boundary bug.
- Catalog retains collection membership, ordering and empty results despite current
  assertion limitations; catalog records will be ordinary local inventory, not answer keys.
- LOCAL10 is a published promotion requirement, not a supplied successful request or
  benchmark hint. Preview non-commitment and rounding remain genuine obligations.
- Preferences retain partial-update persistence, atomic validation and an unrelated
  setting. No workflow is inserted to force abstention and none is erased for convenience.
- Not every obligation is about synthetic values. Collections, state preservation,
  side effects and domain-specific promotion facts remain alongside scalar validation.

No identified leakage required a specification correction before freeze. New fixtures
must not reuse Set-2 implementations. User-selected subjects may overlap historical
subjects; domain overlap is disclosed rather than claimed as independent novelty.
README credits requested separately are deferred because this commit is explicitly
restricted to protocol/specification artifacts and the append-only work log.
