from models import new_account
from service import calculate_points, apply_reward_event, flag_repeat_transactions


def test_points_use_floor(): assert calculate_points(19999,1)==1

def test_bonus_then_cap(): assert calculate_points(50000,2,50,6)==6

def test_negative_amount_gives_zero(): assert calculate_points(-10000,1)==0

def test_cap_zero_is_respected(): assert calculate_points(50000,1,cap_points=0)==0

def test_purchase_event_once():
    a=new_account('A'); e={'event_id':'E1','type':'purchase_captured','transaction_id':'T1','amount_paise':25000}; rules={'points_per_100_rupees':1}
    a=apply_reward_event(a,e,rules); b=apply_reward_event(a,e,rules); assert a['points_balance']==2 and b['points_balance']==2 and b['processed_event_ids']==['E1']

def test_input_account_not_mutated():
    a=new_account('A'); out=apply_reward_event(a,{'event_id':'E1','type':'purchase_captured','transaction_id':'T1','amount_paise':25000},{'points_per_100_rupees':1}); assert a['points_balance']==0 and out['points_balance']==2

def test_declined_event_does_not_award():
    out=apply_reward_event(new_account('A'),{'event_id':'E1','type':'purchase_declined','transaction_id':'T','amount_paise':25000},{'points_per_100_rupees':1}); assert out['points_balance']==0

def test_partial_refund_reverses_proportionally():
    rules={'points_per_100_rupees':1}; a=apply_reward_event(new_account('A'),{'event_id':'E1','type':'purchase_captured','transaction_id':'T','amount_paise':100000},rules); b=apply_reward_event(a,{'event_id':'E2','type':'refund_processed','transaction_id':'T','amount_paise':50000},rules); assert b['points_balance']==5 and b['transactions']['T']['reversed_points']==5

def test_invalid_or_excess_refund_ignored():
    rules={'points_per_100_rupees':1}; a=apply_reward_event(new_account('A'),{'event_id':'E1','type':'purchase_captured','transaction_id':'T','amount_paise':100000},rules)
    for amount in [-1,150000]:
        b=apply_reward_event(a,{'event_id':'E2','type':'refund_processed','transaction_id':'T','amount_paise':amount},rules); assert b['transactions']['T']['refunded_paise']==0 and b['points_balance']==10

def test_unknown_refund_safe(): assert apply_reward_event(new_account('A'),{'event_id':'E1','type':'refund_processed','transaction_id':'X','amount_paise':1000},{'points_per_100_rupees':1})['points_balance']==0

def test_repeat_group():
    rows=[{'transaction_id':str(i),'account_id':'A','date':'D','amount_paise':1000} for i in range(3)]; assert flag_repeat_transactions(rows,2)[0]['transaction_ids']==['0','1','2']

def test_different_accounts_not_grouped():
    rows=[{'transaction_id':'1','account_id':'A','date':'D','amount_paise':1000},{'transaction_id':'2','account_id':'B','date':'D','amount_paise':1000}]; assert flag_repeat_transactions(rows,1)==[]
    
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_duplicate_refund_event_id_ignored():
    rules = {'points_per_100_rupees': 2}
    acct = apply_reward_event(new_account('U1'), {'event_id': 'EV1', 'type': 'purchase_captured', 'transaction_id': 'TX1', 'amount_paise': 60000}, rules)
    ref = {'event_id': 'EV2', 'type': 'refund_processed', 'transaction_id': 'TX1', 'amount_paise': 30000}
    first = apply_reward_event(acct, ref, rules)
    second = apply_reward_event(first, ref, rules)
    assert second['points_balance'] == 6
    assert len(second['ledger']) == 2
    assert second['processed_event_ids'] == ['EV1', 'EV2']

def test_multiple_partial_refunds_exceeding_total_blocked():
    rules = {'points_per_100_rupees': 1}
    acct = apply_reward_event(new_account('U1'), {'event_id': 'EV1', 'type': 'purchase_captured', 'transaction_id': 'TX1', 'amount_paise': 90000}, rules)
    acct = apply_reward_event(acct, {'event_id': 'EV2', 'type': 'refund_processed', 'transaction_id': 'TX1', 'amount_paise': 50000}, rules)
    acct = apply_reward_event(acct, {'event_id': 'EV3', 'type': 'refund_processed', 'transaction_id': 'TX1', 'amount_paise': 50000}, rules)
    assert acct['transactions']['TX1']['refunded_paise'] == 50000
    assert acct['points_balance'] == 4

def test_non_int_refund_types_rejected():
    rules = {'points_per_100_rupees': 1}
    acct = apply_reward_event(new_account('U1'), {'event_id': 'EV1', 'type': 'purchase_captured', 'transaction_id': 'TX1', 'amount_paise': 40000}, rules)
    for bad_val in [True, False, None, "20000", 10.5]:
        res = apply_reward_event(acct, {'event_id': 'EV2', 'type': 'refund_processed', 'transaction_id': 'TX1', 'amount_paise': bad_val}, rules)
        assert res['points_balance'] == 4
        assert res['transactions']['TX1']['refunded_paise'] == 0

def test_unrecognized_event_does_not_pollute_processed_ids():
    acct = new_account('U1')
    res = apply_reward_event(acct, {'event_id': 'EV_PENDING', 'type': 'purchase_pending', 'transaction_id': 'TX1', 'amount_paise': 30000}, {'points_per_100_rupees': 1})
    assert res['processed_event_ids'] == []

def test_negative_threshold_repeat_transactions():
    data = [{'transaction_id': '1', 'account_id': 'U1', 'date': '2026-10-21', 'amount_paise': 2000}]
    assert flag_repeat_transactions(data, threshold=-1) == []