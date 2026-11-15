"""Administrator-only delivery receipts, separate from key validity and secrets."""
import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone

STEPS = ('issued', 'delivered', 'client_updated', 'client_verified')


def record(db_path, key_id, state, actor, receipt):
    if not re.fullmatch(r'KEY-[0-9a-f]{8}', key_id or ''):
        raise ValueError('key_id_required_not_token')
    if state not in (*STEPS, 'revoked'):
        raise ValueError('invalid_delivery_state')
    if not actor or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,100}', receipt or ''):
        raise ValueError('actor_and_safe_receipt_id_required')
    if len(actor)>100 or 'Bearer ' in actor or 'gd_' in actor:
        raise ValueError('no_secrets_in_actor')
    db = sqlite3.connect(db_path)
    try:
        db.execute('CREATE TABLE IF NOT EXISTS delivery_events (id INTEGER PRIMARY KEY,key_id TEXT,state TEXT,actor TEXT,receipt_id TEXT,at TEXT,UNIQUE(key_id,receipt_id))')
        with db:
            old=db.execute('SELECT state,actor FROM delivery_events WHERE key_id=? AND receipt_id=?',(key_id,receipt)).fetchone()
            if old:
                if old!=(state,actor):raise ValueError('receipt_conflict')
                return {'status':'existing','state':state}
            prior=db.execute('SELECT state FROM delivery_events WHERE key_id=? ORDER BY id DESC LIMIT 1',(key_id,)).fetchone()
            expected=STEPS[0] if not prior else None if prior[0] in ('client_verified','revoked') else STEPS[STEPS.index(prior[0])+1]
            if state!='revoked' and state!=expected:raise ValueError('invalid_state_transition')
            if prior and prior[0]=='revoked':raise ValueError('revoked_delivery_is_terminal')
            db.execute('INSERT INTO delivery_events(key_id,state,actor,receipt_id,at) VALUES(?,?,?,?,?)',
                (key_id,state,actor,receipt,datetime.now(timezone.utc).isoformat()))
        return {'status':'recorded','state':state,'scope':'receipt_record_not_key_authorization_or_automatic_customer_verification'}
    finally:db.close()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ('db','key-id','state','actor','receipt'):p.add_argument('--'+arg,required=True)
    a=p.parse_args()
    print(json.dumps(record(a.db,a.key_id,a.state,a.actor,a.receipt)))
