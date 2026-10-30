# TESTING.md — Required submission

## Environment & Execution Summary
- **Python Version:** Python 3.11
- **Setup Command:** `python -m pip install -r requirements-dev.txt`
- **Pytest Command:** `python -m pytest -q`
- **Main Script Command:** `python -m main`

### Results Breakdown
- **Initial Baseline (`python -m pytest -q`):** `67 failed, 147 passed`
- **Initial Main Output (`python -m main`):** `Points example: 28` / `Repeat warnings: []`
- **Final Result after Fixes (`python -m pytest -q`):** `214 passed` 
- **Final Main Output (`python -m main`):** `Points example: 27` / `Repeat warnings: []`

## Documented Edge Cases (5 Cases)

1. **Zero Cap Override (`cap_points = 0`)**
   - **Input:** `calculate_points(50000, 2, 50, 0)`
   - **Expected Behaviour:** Returns `0` even though uncapped points would be `15`.
   - **Actual Result:** `0`
   - **Test:** `tests/test_acceptance_matrix.py::test_bonus_and_cap_matrix`

2. **Negative Rule Values (`points_per_100_rupees < 0` or `bonus_percent < 0`)**
   - **Input:** `calculate_points(100000, -1, 0, None)` and `calculate_points(100000, 1, -1, None)`
   - **Expected Behaviour:** Returns `0` and never produces negative points.
   - **Actual Result:** `0`
   - **Test:** `tests/test_acceptance_matrix.py::test_invalid_rule_values_do_not_create_negative_points`

3. **Duplicate Refund Event Replay**
   - **Input:** Re-sending `{'event_id': 'EV2', 'type': 'refund_processed', 'transaction_id': 'TX1', 'amount_paise': 30000}` twice.
   - **Expected Behaviour:** Points are reversed only on the first call; second call returns the account unchanged.
   - **Actual Result:** `points_balance == 6`, `len(ledger) == 2`, `processed_event_ids == ['EV1', 'EV2']`.
   - **Test:** `tests/test_contract.py::test_duplicate_refund_event_id_ignored`

4. **Non-Integer Refund Values (`True`, `None`, `"20000"`, `10.5`)**
   - **Input:** `refund_processed` event where `amount_paise` is not an `int`.
   - **Expected Behaviour:** Event is ignored safely without raising `TypeError` or treating `True` as `1`.
   - **Actual Result:** `points_balance == 4`, `refunded_paise == 0`.
   - **Test:** `tests/test_contract.py::test_non_int_refund_types_rejected`

5. **Negative or Zero Repeat Threshold (`threshold <= 0`)**
   - **Input:** `flag_repeat_transactions(rows, threshold=-1)`
   - **Expected Behaviour:** Clamps threshold to `1` and returns a valid `list` without flagging single transactions.
   - **Actual Result:** `[]`
   - **Test:** `tests/test_contract.py::test_negative_threshold_repeat_transactions`
