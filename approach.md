# approach.md - Required submission

## 1. Baseline Observation & Code Walkthrough
I started by installing the dev requirements and running `python -m pytest -q`. Out of 214 total tests, **147 passed and 67 failed**. Running `python -m main` printed `Points example: 28` and `Repeat warnings: []`.

Reading through the repository:
- `models.py`, `fixtures.py`, and `main.py` are helper/setup modules with no defects.
- `service.py` holds all the reward calculation, event processing, and repeat detection logic. All 67 test failures traced back to `service.py`.

## 2. Root Causes Identified
1. **`calculate_points` rounding & validation defects:**
   - Used `round(amount_paise / 10000)` instead of floor division `amount_paise // 10000`, causing values with `.5` or higher (like `259900` or `19999` paise) to round up.
   - Used `if cap_points:`, which skipped capping whenever `cap_points = 0` because `0` is falsy.
   - Lacked checks for `amount_paise <= 0`, `points_per_100_rupees <= 0`, and `bonus_percent < 0`.
2. **`apply_reward_event` idempotency & refund defects:**
   - Never checked if `event_id` was already in `out['processed_event_ids']` before running the logic, and appended `event_id` unconditionally at the bottom of the function.
   - Did not validate `refund` in `refund_processed`: non-integers (`None`, `True`, strings), negative/zero values, and refunds exceeding `amount_paise` were applied directly.
3. **`flag_repeat_transactions` threshold edge case:**
   - Did not guard against `threshold <= 0`, which could flag non-repeating transactions when `threshold` was `0` or negative.

## 3. Implementation Decisions & Verification
I updated `service.py` to:
- Return `0` in `calculate_points` if `amount_paise <= 0 or points_per_100_rupees <= 0 or bonus_percent < 0`, use `// 10000`, and check `if cap_points is not None:`.
- Check `if not event_id or event_id in out['processed_event_ids']: return out` at the beginning of `apply_reward_event`, and only append `event_id` inside valid `purchase_captured` and `refund_processed` branches.
- Validate refunds with `if type(refund) is not int or refund <= 0 or txn['refunded_paise'] + refund > txn['amount_paise']: return out` and protect the balance with `max(0, out['points_balance'] - delta)`.
- Use `max(1, threshold)` in `flag_repeat_transactions`.

After adding 5 new unit tests in `tests/test_contract.py`, `python -m pytest -q` passed all **214 tests**.