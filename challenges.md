# challenges.md - COMPULSORY submission

## 1. Python `bool` vs `int` in Refund Validation
While fixing `test_invalid_or_excess_refund_does_not_change_account`, the test passed a list of invalid refund amounts: `[0, -1, -50, -1000, 100001, 150000, 200000, 999999, True, None, "100", 1.5, [], {}, False]`.

- **What I tried first:** I initially checked `if not refund or refund <= 0 or txn['refunded_paise'] + refund > txn['amount_paise']:`.
- **What failed:**
  1. For strings (`"100"`), lists (`[]`), and dicts (`{}`), Python raised `TypeError: '<=' not supported between instances of 'str' and 'int'`.
  2. For `True`, `not refund` was `False`, and because `bool` inherits from `int` in Python (`True == 1`), `True <= 0` was `False` and `0 + True <= 100000` was `True`! So `txn['refunded_paise']` became `1` instead of staying `0`.
- **How I resolved it:** Using `type(refund) is not int` as the first condition cleanly rejected `True`, `False`, `None`, `"100"`, `1.5`, `[]`, and `{}` before the `<=` operator even ran.

## 2. Unconditional `processed_event_ids.append(event_id)`
In the starter code, `out['processed_event_ids'].append(event_id)` was placed at the very end of `apply_reward_event`. When I added the idempotency check at the top (`if event_id in out['processed_event_ids']: return out`), I noticed that if an invalid refund or a `purchase_declined` event came in, its `event_id` would still get added to `processed_event_ids` if that line stayed at the bottom. Moving `.append(event_id)` inside the valid `purchase_captured` and `refund_processed` blocks ensured only actually accepted events are recorded.