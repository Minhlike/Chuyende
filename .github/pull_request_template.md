## Summary of Changes

### Scope of Pull Request:
- [ ] `protocol`: Experimental protocol or pre-registration amendment
- [ ] `data`: Dataset processing, parser, or split manifest
- [ ] `feat`: Model architecture or extractor implementation
- [ ] `experiment`: Experiment runner or configuration
- [ ] `thesis`: Academic composition or typesetting
- [ ] `audit`: Invariant verification or hash audit

### Verification Checklist:
- [ ] `python scripts/verify_invariants.py` passed with 0 violations.
- [ ] `pytest tests/` passed 100%.
- [ ] Frozen Chapter 1 & Chapter 2 hashes verified identical to baseline.
- [ ] No un-acquired raw dataset files or binary databases staged.
- [ ] No secrets, keys, or private tokens committed.
- [ ] If protocol modified, corresponding `PROTOCOL-AMENDMENTS.md` entry logged.
