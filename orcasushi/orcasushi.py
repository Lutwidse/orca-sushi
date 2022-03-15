import requests
import csv
import time

class OrcaSushi:
    def __init__(self):
        self.transactions = []
        self.bids = []
    
    def get_transactions(self):
        offset = 0
        while True:
            res = requests.get(f"https://fcd.terra.dev/v1/txs?offset={offset}&limit=100&account=terra13nk2cjepdzzwfqy740pxzpe3x75pd6g0grxm2z")
            if res.status_code != 200:
                    print("Request Error")
                    return
            transactions = res.json()
            if "next" not in transactions:
                break

            self.transactions.append(transactions)
            offset = transactions["next"]
            time.sleep(1.5)
    
    def get_bids(self):
        bids = []
        for transaction in self.transactions:
            for i in transaction["txs"]:
                bids.append(i)
        self.bids = bids
    
    # Amount (In) - bLUNA
    def generate_bids_csv(self):
        with open("bids.csv", "w") as csvfile:
            fieldnames = ["timestamp", "amount", "premium_slot", "strategy_activate_ltv", "strategy_activate_amount"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for i in self.bids:
                logs = i["logs"]
                if len(logs) != 3:
                    continue

                events = logs[2]["events"]
                if len(events) != 4:
                    continue

                timestamp = i["timestamp"]
                wasm = events[3]["attributes"]
                amount = wasm[8]["value"]
                premium_slot = wasm[9]["value"]
                collateral_token = wasm[10]["value"]
                strategy_activate_ltv = wasm[12]["value"]
                strategy_activate_amount = wasm[13]["value"]
                if collateral_token == "terra1kc87mu460fwkqte29rquh4hc20m54fxwtsx7gp":
                    writer.writerow({
                        "timestamp": timestamp,
                        "amount": amount[:-6],
                        "premium_slot": int(premium_slot)/100,
                        "strategy_activate_ltv": int(strategy_activate_ltv)/100,
                        # Some people still bidding at the 2.5m thresholding. which is 11 digits zero.
                        "strategy_activate_amount": strategy_activate_amount.replace("0", "")+"0"*6
                        })