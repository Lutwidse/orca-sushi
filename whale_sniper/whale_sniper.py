import requests
from datetime import datetime
from zoneinfo import ZoneInfo   
LOCAL_TIMEZONE = datetime.utcnow().astimezone().tzinfo

API = "https://fcd.terra.dev/v1/txs?limit=100&account="
KUJIRA_ORCA_AUST_VAULT = "terra13nk2cjepdzzwfqy740pxzpe3x75pd6g0grxm2z"
BLUNA = "terra1kc87mu460fwkqte29rquh4hc20m54fxwtsx7gp"

bids = []

with open("whale.txt", "r") as f:
    for w in f.readlines():
        address = w.strip("\n")
        res = requests.get(f"{API}{address}")
        transaction = res.json()

        for i in transaction["txs"]:
            if len(i["logs"]) == 0:
                continue

            logs = i["logs"][0]
            if len(logs) != 3:
                continue

            events = logs["events"]
            if len(events) != 4:
                continue
            from_contract = events[1]["attributes"]
            wasm = events[3]["attributes"]

            if len(from_contract) !=16:
                continue

            if from_contract[3]["value"] != KUJIRA_ORCA_AUST_VAULT:
                continue

            collateral_token = wasm[10]["value"]
            if collateral_token == BLUNA:
                timestamp = i["timestamp"]
                utc_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=ZoneInfo("US/Central"))
                local_timestamp = utc_timestamp.astimezone(LOCAL_TIMEZONE)

                amount = wasm[8]["value"]
                premium_slot = wasm[9]["value"]
                strategy_activate_ltv = wasm[12]["value"]
                strategy_activate_amount = wasm[13]["value"]
                amount = amount[:-6] if len(amount) > 6 else amount[:-5]
                bids.append([local_timestamp.isoformat(" "), f"[{w[6:14]}] - [Amount] {'{:.2f}'.format((int(amount)/100000))}M - [Premium] {premium_slot}% - [Borrow Limit Threshold] {strategy_activate_ltv}% - [At-Risk Collateral Threshold] {int(strategy_activate_amount)/1000000000000}M"])

sorted_bids = sorted(bids, key=lambda t: datetime.strptime(t[0], "%Y-%m-%d %H:%M:%S%z"), reverse=True)
for i, j in sorted_bids:
    print(i, j)