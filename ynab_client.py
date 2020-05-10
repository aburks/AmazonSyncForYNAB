import requests
import json
import re

class YNAB(object):
    BASE_URL = "https://api.youneedabudget.com/v1"

    def __init__(self, token):
        self.token = token
        self.budgetID = self.getBudgetID()

    # TODO: Only gets the 0th budget available.
    # We should eventually check all budgets just in case
    def getBudgetID(self):
        url = self.BASE_URL + "/budgets"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
        }
        rawResponse = requests.get(url ,headers=headers)
        resp = json.loads(rawResponse.content.decode('utf-8'))
        return resp["data"]["budgets"][0]["id"]

    # TODO: Make date range based on current date
    def list_recent_amazon_transactions(self):
        #url = self.BASE_URL + "/budgets/6d515631-e0bc-43a2-bba6-a4242dfe307d/transactions?since_date=2020-04-03&type=uncategorized"
        url = self.BASE_URL + f"/budgets/{self.budgetID}/transactions?since_date=2020-04-01"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
        }
        rawResponse = requests.get(url ,headers=headers)
        resp = json.loads(rawResponse.content.decode('utf-8'))
        if rawResponse.status_code != 200:
            return None
        transactions = resp["data"]["transactions"]
        amazon = re.compile(r"[[aA]mazon|AMZN]")
        memo = re.compile(r"[Amazon|AMZN].*\*[\d|A-Z]+")
        memoFilter = filter(lambda item: item["memo"] == None or memo.match(item["memo"]), transactions)
        onlyAmazon = filter(lambda item: amazon.match(item["payee_name"]),memoFilter)
        onlyAmazon = list(onlyAmazon)
        for i in range(len(onlyAmazon)):
            onlyAmazon[i]["amount"] = onlyAmazon[i]["amount"]//10
        return list(onlyAmazon)

    '''
        transactions: [{"id": id, ...}]
    '''
    def patch_transactions(self, transactions):
        if len(transactions) == 0:
            print("No transactions to patch, skipping...")
            return
        url = self.BASE_URL + f"/budgets/{self.budgetID}/transactions"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        data = json.dumps({"transactions": transactions})
        resp = requests.patch(url, data, headers=headers)
        print(f"about to patch data: {data}")
        if resp.status_code != 200:
            print (f"Something went wrong, got response: {resp.content}")
        else:
            print (f"Successfully updated transactions {transactions}")