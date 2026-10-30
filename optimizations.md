# optimizations.md - Required submission

## Optimizations Implemented
1. **Short-Circuit Input Validation:**
   - Added guard clauses at the start of `calculate_points` and `apply_reward_event`. Duplicate `event_id`s and invalid numeric inputs exit in $O(1)$ steps without executing point math or mutating ledger lists.
2. **Integer Floor Division (`//`):**
   - Replaced `round(amount_paise / 10000)` with `(amount_paise // 10000)`. Integer division avoids float conversion overhead and prevents floating-point rounding inaccuracies.
3. **Inline Threshold Clamping (`max(1, threshold)`):**
   - Kept `flag_repeat_transactions` as a single pass $O(N)$ dictionary grouping loop and used `max(1, threshold)` in the list comprehension filter.

## Trade-offs Considered
1. **`deepcopy(account)` vs. Manual Shallow Copying:**
   - Calling `deepcopy(account)` on every event has an $O(N)$ memory/time cost proportional to the account's history. However, because `test_event_processing_does_not_mutate_input_account` strictly checks that the original dictionary and its nested `transactions`/`ledger` are never modified in place, `deepcopy` provides guaranteed safety and clean, readable code.
2. **`list` vs. `set` for `processed_event_ids`:**
   - Using a `set` would make `event_id in out['processed_event_ids']` $O(1)$ instead of $O(N)$. I decided to keep it as a `list` because `models.py` defines it as `[]` and the test suite explicitly asserts `twice["processed_event_ids"] == [event_id]`.

## What I Would Improve Next
- If an account has a huge number of transactions over time, we could validate schema types using Python `dataclasses` or `TypedDict` and index `event_id` in a database table for fast lookups.