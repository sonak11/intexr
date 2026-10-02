"""IntExR-Scope: evidence-scoped revision of multi-claim responses (pilot harness)."""

LABELS = ("D", "P", "K", "U")
VERDICTS = ("accept", "partial", "reject", "insufficient")
VALIDITY = ("valid", "false", "partial", "ambiguous", "outdated", "superseding", "unsupported")
# Claim-level actions observable in a revised response.
STATUSES = ("keep", "revised", "removed", "hedged")
