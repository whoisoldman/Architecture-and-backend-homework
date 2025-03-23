import os

import pandas as pd
from pymongo import MongoClient

mongousername = os.environ["MANGOU"]
mongopassword = os.environ["MANGOP"]


client = MongoClient(
    "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
    % (mongousername, mongopassword)
)

usersarr = [
    ["PATRICK", "U03RANJ8PDL"],
    ["CEASAR", "U0233NKSUE7"],
    ["KYLE", "U03RH8RBN75"],
    ["ISONE", "U03RKPM1U6Q"],
    ["MAK", "U049NEAJ7EW"],
    ["MARVIN", "U04HNAMTXBP"],
    ["TRIXIA", "U04JNNV7JTS"],
]


def payloadconstructor(invoiceid):
    def getsold():
        dbname = "mlb_sold_inventory"
        colname = "mlbsoldinventories"
        db = client[dbname]
        col = db[colname]
        soldmongoresults = col.find_one({})
        solddf = pd.DataFrame(soldmongoresults["data"])

        return solddf

    def getslackuserid(assigned):
        for user in usersarr:
            username = user[0]
            slackid = user[1]
            # print(type(assigned))
            # print(type(username))
            if str(assigned) == str(username):
                print("MATCH")
                touseslackid = slackid
                break
            else:
                touseslackid = "U03RPEH25L3"
        return touseslackid

    solddf = getsold()
    # print(solddf)
    invoicerow = solddf.loc[solddf["invoiceId"] == str(invoiceid)]
    print(invoicerow)
    assigned = invoicerow["ASSIGNED"].values.item()
    urgent = invoicerow["URGENT"].values.item()
    if urgent is True:
        urgentstr1 = ":alert:"
        urgentstr2 = "- URGENT:alert:"
    else:
        urgentstr1 = ""
        urgentstr2 = ""
    slackid = getslackuserid(assigned)

    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*%sPURCHASE REQUEST - %s %s*"
                    % (urgentstr1, invoiceid, urgentstr2),
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": "*INVOICE ID:* \n %s" % (invoiceid)},
                    {
                        "type": "mrkdwn",
                        "text": "*SEC:* \n %s" % (invoicerow["section"].values.item()),
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*ROW:* \n %s" % (invoicerow["row"].values.item()),
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*QTY:* \n %s" % (invoicerow["quantity"].values.item()),
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Event name:* \n %s"
                        % (invoicerow["event_name"].values.item()),
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Event date:* \n %s"
                        % (invoicerow["event_date"].values.item()),
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Total SOLD Cost:* \n %s"
                        % (invoicerow["total"].values.item()),
                    },
                ],
            },
            {
                "type": "section",
                "fields": [
                    # {
                    # 	"type": "mrkdwn",
                    # 	"text": "*ASSIGNED TO:* \n <@%s>"%(slackid)
                    # },
                    {
                        "type": "mrkdwn",
                        "text": "*CUSTOMER:* \n %s"
                        % (invoicerow["Customer"].values.item()),
                    },
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*PRIMARY LINK:*"},
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "PRIMARY LINK",
                        "emoji": True,
                    },
                    "value": "click_me_123",
                    "url": "%s" % (invoicerow["Primary_Link"].values.item()),
                    "action_id": "button-action",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*INVOICE LINK*"},
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "INVOICE LINK",
                        "emoji": True,
                    },
                    "value": "click_me_123",
                    "url": "%s" % (invoicerow["SBINVOICELINK"].values.item()),
                    "action_id": "button-action",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*SOLD INVENTORY LINK:*"},
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "SOLD INVENTORY LINK",
                        "emoji": True,
                    },
                    "value": "click_me_123",
                    "url": "%s" % (invoicerow["SBSOLDLINK"].values.item()),
                    "action_id": "button-action",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*INVENTORY LINK:*"},
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "INVENTORY LINK",
                        "emoji": True,
                    },
                    "value": "click_me_123",
                    "url": "%s" % (invoicerow["SBINVENTORYLINK"].values.item()),
                    "action_id": "button-action",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Purchased",
                        },
                        "style": "primary",
                        "value": "Purchased - %s" % (invoiceid),
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Reassign",
                        },
                        "style": "danger",
                        "value": "Reassign - %s" % (invoiceid),
                    },
                ],
            },
        ]
    }
    # print(payload)
    return payload


# invoiceid = '63452253'
# payloadconstructor(invoiceid)
