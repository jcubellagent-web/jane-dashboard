#!/bin/bash
# Check recent SMS messages on Jane's Twilio number
SID="AC16585d69e555f726163f16583a9eaae2"
TOKEN="c3802b5f85bf1182d3dfbd76fa407187"
PHONE="+15187413592"

curl -s -u "$SID:$TOKEN" \
  "https://api.twilio.com/2010-04-01/Accounts/$SID/Messages.json?To=$PHONE&PageSize=${1:-5}" \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
msgs=d.get('messages',[])
if not msgs: print('No messages')
for m in msgs:
    print(f\"{m['date_sent']} | From: {m['from']} | {m['body']}\")
"