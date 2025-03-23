import re
from datetime import datetime, timedelta

import pandas as pd
import requests
from pymongo import MongoClient

mongousername = "blabla"
mongopassword = "blabla"

client = MongoClient(
    "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
    % (mongousername, mongopassword)
)

dbarr = [
    ["1", "Angels_Results"],
    ["2", "Astros_Results"],
    ["3", "Athletics_Results"],
    ["4", "Brewers_Results"],
    ["5", "Cardinals_Results"],
    ["6", "Cubs_Results"],
    ["7", "Dodgers_Results"],
    ["8", "Giants_Results"],
    ["9", "Guardians_Results"],
    ["10", "Marlins_Results"],
    ["11", "Mets_Results"],
    ["12", "Nationals_Results"],
    ["13", "Orioles_Results"],
    ["14", "Phillies_Results"],
    ["15", "Pirates_Results"],
    ["16", "Rangers_Results"],
    ["17", "Rays_Results"],
    ["18", "RedSox_Results"],
    ["19", "Reds_Results"],
    ["20", "Royals_Results"],
    ["21", "Tigers_Results"],
    ["22", "Twins_Results"],
    ["23", "BrewersSpringTraining_Results"],
    ["24", "AngelsSpringTraining_Results"],
    ["25", "RangersSpringTraining_Results"],
    ["26", "GiantsSpringTraining_Results"],
    ["27", "GuardiansSpringTraining_Results"],
    ["28", "OriolesSpringTraining_Results"],
    ["29", "RedsSpringTraining_Results"],
    ["30", "RoyalsSpringTraining_Results"],
    ["31", "MetsSpringTraining_Results"],
    ["32", "MarinersSpringTraining_Results"],
    ["33", "PadresSpringTraining_Results"],
    ["34", "PhilliesSpringTraining_Results"],
    ["35", "CubsSpringTraining_Results"],
    ["36", "DodgersSpringTraining_Results"],
    ["37", "WhiteSoxSpringTraining_Results"],
]


# tid = request.args.get('tid')
# sdate = request.args.get('sdate')
# edatestr = request.args.get('edate')


def countsapi2(tid, sdate, edatestr):
    def threshold(x):
        cap = int(x["CAPACITY"])

        if cap == 0:
            threshold = 0
            return threshold
        elif cap > 100:
            threshold = round((cap * 0.1), 2)
            return threshold
        elif cap <= 100:
            threshold = round((cap * 0.25), 2)
            return threshold
        else:
            return "Error"

    def pricebreak(x):
        pricebreakrank = x["PRICE_rank"]
        size = x["SIZE"]
        if pricebreakrank == 1:
            return "LPB"
        elif pricebreakrank == size:
            return "HPB"
        else:
            return "MPB"

    def broadcast(x):
        size = x["SIZE"]
        countrank = x["COUNT_rank"]
        count = x["COUNT"]
        sumcount = int(x["COUNT_SUM"])
        threshold = float(x["THRESHOLD"]) + 16
        price = x["PRICE"]
        section = x["CODE"]

        if sumcount <= threshold:
            return "N"
        else:
            if countrank == size:
                if section in ["GA", "LAWNS", "LAWN", "BERM"]:
                    if price != "NA":
                        return "Y"
                    else:
                        return "N"
                else:
                    return "Y"
            else:
                if section in ["GA", "LAWNS", "LAWN", "BERM"]:
                    if price != "NA":
                        return "Y"
                    else:
                        return "N"
                else:
                    return "N"

    def intnotes(x):
        notes = x["notes"]
        pricer = str(notes).split(" -")[0]
        seatnumarr = x["seatnumbers"]
        firstseat = seatnumarr[0]

        if "BG" in pricer:
            return "Y", "N"
        elif "FP" in pricer:
            return "N", "Y"
        else:
            if str(firstseat) == "1":
                return "N", "Y"
            elif str(firstseat) == "2":
                return "Y", "N"
            else:
                return "N", "N"

    def notes(x, team):
        notes = x["notes"]
        qty = int(x["quantity"])
        bg = x["BG"]
        fp = x["FP"]
        broad = x["BROADCAST"]
        prevbroad = x["broadcast"]
        price = x["PRICE"]
        ycount = x["Y"]

        fees = x["fees"]
        if price != "NA":
            allinprice = float(price) + fees
            newfv = str(round((allinprice * 1.2), 2))
            if team == "Nationals" or team == "Mets" or team == "Angels":
                newfv = str(round((allinprice * 1.15), 2))

        if bg == "Y":
            if notes == "":
                print("BLANK")

            else:
                p = r"[\d]*[.][\d]+|[\d]+"
                if re.search(p, notes) is not None:
                    for catch in re.finditer(p, notes):
                        oldfv = catch[0]

            if (broad == "Y") & (prevbroad == "") & (qty == 1):
                if notes != "":
                    oldnotes = str(notes).split(oldfv)[1]
                    oldfv = float(oldfv)
                    bgnotes = "BG:" + newfv + oldnotes
                    return bgnotes, "NA", "New Broadcast"
                else:
                    bgnotes = (
                        "BG:%s -ticketevolution -tickpick -ticketnetwork -stubhub -gametime -ticketmaster"
                        % (newfv)
                    )
                    return bgnotes, "NA", "New Broadcast"
            elif (broad == "Y") & (prevbroad == "") & (qty > 1):
                if notes != "":
                    oldnotes = str(notes).split(oldfv)[1]
                    oldfv = float(oldfv)
                    bgnotes = "BG:" + newfv + oldnotes
                    return bgnotes, "NA", "Rebroadcast"
                else:
                    bgnotes = (
                        "BG:%s -ticketevolution -tickpick -ticketnetwork -stubhub -gametime -ticketmaster"
                        % (newfv)
                    )
                    return bgnotes, "NA", "Rebroadcast"
            elif (broad == "Y") & (prevbroad == "1"):
                oldnotes = str(notes).split(oldfv)[1]
                oldfv = float(oldfv)
                if float(newfv) == oldfv:
                    return "NA", "NA", "NO CHANGES"
                elif float(newfv) > oldfv:
                    bgnotes = "BG:" + newfv + oldnotes
                    return bgnotes, "NA", "Price Increase"
                elif float(newfv) < oldfv:
                    bgnotes = "BG:" + newfv + oldnotes
                    return bgnotes, "NA", "Price Decrease"
            elif (broad == "N") & (prevbroad == "1") & (ycount == 0):
                return "NA", "NA", "Unbroadcast"
            elif (broad == "N") & (prevbroad == "") & (ycount == 0):
                return "NA", "NA", "NA"
            else:
                return "NA", "NA", "NA"

        if fp == "Y":
            if notes == "":
                print("BLANK")
            else:
                p = r"[\d]*[.][\d]+|[\d]+"
                if re.search(p, notes) is not None:
                    for catch in re.finditer(p, notes):
                        oldfv = catch[0]

            if (broad == "Y") & (prevbroad == "") & (qty == 1):
                if notes != "":
                    oldnotes = str(notes).split(oldfv)[1]
                    oldfv = float(oldfv)
                    fpnotes = "FP:" + newfv + oldnotes
                    return "NA", fpnotes, "New Broadcast"
                else:
                    fpnotes = "FP:%s +vivid" % (newfv)
                    return "NA", fpnotes, "New Broadcast"
            elif (broad == "Y") & (prevbroad == "") & (qty > 1):
                if notes != "":
                    print(notes)
                    oldnotes = str(notes).split(oldfv)[1]
                    oldfv = float(oldfv)
                    fpnotes = "FP:" + newfv + oldnotes
                    return "NA", fpnotes, "Rebroadcast"
                else:
                    fpnotes = "FP:%s +vivid" % (newfv)
                    return "NA", fpnotes, "Rebroadcast"
            elif (broad == "Y") & (prevbroad == "1"):
                oldnotes = str(notes).split(oldfv)[1]
                oldfv = float(oldfv)
                if float(newfv) == oldfv:
                    return "NA", "NA", "NO CHANGES"
                elif float(newfv) > oldfv:
                    fpnotes = "FP:" + newfv + oldnotes
                    return "NA", fpnotes, "Price Increase"
                elif float(newfv) < oldfv:
                    fpnotes = "FP:" + newfv + oldnotes
                    return "NA", fpnotes, "Price Decrease"
            elif (broad == "N") & (prevbroad == "1") & (ycount == 0):
                return "NA", "NA", "Unbroadcast"
            elif (broad == "N") & (prevbroad == "") & (ycount == 0):
                return "NA", "NA", "NA"
            else:
                return "NA", "NA", "NA"

        elif ((bg == "N") | (fp == "N")) & (price != "NA"):
            if (broad == "Y") | (qty == 1):
                bgnotes = (
                    "BG:%s -ticketevolution -tickpick -ticketnetwork -stubhub -gametime -ticketmaster"
                    % (newfv)
                )
                fpnotes = "FP:%s +vivid" % (newfv)
                return bgnotes, fpnotes, "New Broadcast"
            elif (broad == "Y") | (qty > 1):
                bgnotes = (
                    "BG:%s -ticketevolution -tickpick -ticketnetwork -stubhub -gametime -ticketmaster"
                    % (newfv)
                )
                fpnotes = "FP:%s +vivid" % (newfv)
                return bgnotes, fpnotes, "Rebroadcast"
            else:
                return "NA", "NA", "NA"
        else:
            return "NA", "NA", "NA"

    def tags(x):
        tag = x["tags"]
        tagarr = str(tag).split(" ")
        newbroad = x["newbroad"]
        broad = x["BROADCAST"]
        pb = x["PB"]
        ycount = x["Y"]
        if (broad == "N") & (ycount == 0):
            if "donot-broadcast" in tagarr:
                return "NA", "NA"
            else:
                return "donot-broadcast", "NA"
        elif (broad == "Y") & (ycount > 0):
            if "donot-broadcast" in tagarr:
                return pb, "donot-broadcast"
            else:
                return pb, "NA"
        else:
            return "NA", "NA"

    client = MongoClient(
        "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
        % (mongousername, mongopassword)
    )

    def getteamid(tid):
        for teamarr in dbarr:
            teamid = teamarr[0]
            if str(teamid) == str(tid):
                team = teamarr[1]
                print("Team that was being requested: ", team)

                return team

    yesterday = (datetime.today() - timedelta(days=1)).strftime("%m%d%Y")
    feesarr = [
        ["Nationals", 13],
        ["Mets", 13.5],
        ["Reds", 11],
        ["Angels", 18],
        ["Pirates", 18],
        ["Marlins", 10],
        ["Rays", 11],
        ["Phillies", 22],
        ["RedSox", 32],
        ["PhilliesSpringTraining", 6.5],
    ]
    # tid = '12'
    # sdate = '12232022'
    # edatestr = '2023-06-06'
    print(tid)
    team = getteamid(tid)
    print(team)
    edate = edatestr.split("T")[0].replace("/", "_").replace("-", "_")
    print(sdate)
    # print(edate)
    # sdate = '12092022'
    # yesterday = "12152022"

    if team != "":
        db = client[team]
        col = db[sdate]
        results = col.find({"edate": edate})
        ed_count = results.explain().get("executionStats", {}).get("nReturned")
        print("Number of Results on the same day: ", ed_count)
        if ed_count == 0:
            sdate = yesterday
            # if team == "Phillies_Results":
            sdate = "02202023"
            col = db[sdate]
            results = col.find({"edate": edate})
            ed_count = results.explain().get("executionStats", {}).get("nReturned")
            print("Number of Results on the same day based on yesterday: ", ed_count)
        if ed_count > 1:
            for data in results:
                datadf = pd.DataFrame(data["data"])
                dateinfo = data["data"][0]["DATE"]
                datadf["CODE"] = datadf["CODE"].apply(
                    lambda x: "GA" if "GA" in x else x
                )
                datadf["CODE"] = datadf["CODE"].apply(
                    lambda x: "LAWNS" if "LAWNS" in x else x
                )
                datadf["CODE"] = datadf["CODE"].apply(
                    lambda x: "LAWN" if "LAWN" in x else x
                )
                datadf["CODE"] = datadf["CODE"].apply(
                    lambda x: "BERM" if "BERM" in x else x
                )
                datestr = str(dateinfo).split("T")[0]
                teamname = team.split("_Results")[0]
                csvname = teamname + datestr + ".csv"
                sglistdbname = (team.split("_Results")[0]) + "_SGELIST"
                sgelistdb = client[sglistdbname]
                sgelistcol = sgelistdb[sglistdbname]
                sglistresults = sgelistcol.find_one({})
                sglistdf = pd.DataFrame(sglistresults["elist"])
                sgidrow = sglistdf.loc[sglistdf["EDATE"] == datestr]
                sgid = sgidrow["EVENTID"].item()
                skyvssgdbname = "SKYBOXID_VS_SGID"
                skyvssgdb = client[skyvssgdbname]
                skyvsgcol = skyvssgdb[skyvssgdbname]
                skyvssgresults = skyvsgcol.find_one({"SGID": str(sgid)})
                skyid = skyvssgresults["SBID"]
                datadf.drop_duplicates(keep="first", inplace=True)

                # datadf.to_csv("datadfwiththreshold.csv",index=False)
                datadf["COUNT"] = datadf["COUNT"].astype(int)
                datadf["CAPACITY"] = datadf["CAPACITY"].astype(int)
                sumdf = datadf.groupby(["CODE"]).agg({"COUNT": "sum"})
                lawncapsumdf = datadf.groupby(["CODE"]).agg({"CAPACITY": "sum"})
                lawncapsumdf = lawncapsumdf.loc[
                    lawncapsumdf.index.isin(["GA", "LAWNS", "LAWN", "BERM"])
                ]
                lawncapsumdf.reset_index(inplace=True)
                datadf = datadf.merge(
                    lawncapsumdf, on="CODE", how="left", suffixes=(None, "_SUM")
                )
                datadf = datadf.merge(
                    sumdf, how="left", on="CODE", suffixes=(None, "_SUM")
                )
                # datadf.to_csv("datadfaftersumdf.csv",index=False)

                datadf["COUNT"] = datadf.apply(
                    lambda x: x["COUNT_SUM"]
                    if x["CODE"] in ["GA", "LAWNS", "LAWN", "BERM"]
                    else x["COUNT"],
                    axis=1,
                )
                datadf["CAPACITY"] = datadf.apply(
                    lambda x: x["CAPACITY_SUM"]
                    if x["CODE"] in ["GA", "LAWNS", "LAWN", "BERM"]
                    else x["CAPACITY"],
                    axis=1,
                )
                datadf["THRESHOLD"] = datadf.apply(lambda x: threshold(x), axis=1)
                datadf.drop_duplicates(
                    subset=["CODE", "COUNT", "CAPACITY", "PRICE"],
                    keep="first",
                    inplace=True,
                )
                nonlawnsdf = datadf.loc[
                    ~datadf["CODE"].isin(["GA", "LAWNS", "LAWN", "BERM"])
                ]
                lawnsdf = datadf.loc[
                    datadf["CODE"].isin(["GA", "LAWNS", "LAWN", "BERM"])
                ]
                lawnsdf = lawnsdf.loc[lawnsdf["PRICE"] != "NA"]
                datadf = pd.concat([nonlawnsdf, lawnsdf])
                countgroupdf = datadf.groupby(["CODE"])["COUNT"].rank(
                    ascending=True, method="first"
                )
                pricegroupdf = datadf.groupby("CODE")["PRICE"].rank(
                    ascending=True, method="first"
                )
                datadf = datadf.merge(
                    countgroupdf,
                    how="left",
                    suffixes=(None, "_rank"),
                    left_index=True,
                    right_index=True,
                )
                datadf = datadf.merge(
                    pricegroupdf,
                    how="left",
                    suffixes=(None, "_rank"),
                    left_index=True,
                    right_index=True,
                )
                sizedf = pd.DataFrame((datadf.groupby(["CODE"]).size()))
                sizedf.rename({0: "SIZE"}, inplace=True, axis=1)
                datadf = datadf.merge(sizedf, how="left", on="CODE")
                # datadf.to_csv('Aftergroupdf.csv',index=False)
                datadf["PB"] = datadf.apply(lambda x: pricebreak(x), axis=1)
                # datadf.to_csv('AfterPB.csv',index=False)
                datadf["BROADCAST"] = datadf.apply(lambda x: broadcast(x), axis=1)
                # datadf.to_csv("afterBroad.csv",index=False)
                broadresults = requests.get(
                    "https://api.blabla.com/event_listings.php?token=blabla&eventid=%s&includeTags=zone"
                    % (skyid)
                )
                broadresponse = broadresults.json()
                broaddf = pd.DataFrame(broadresponse["data"])
                if broaddf.empty:
                    datadf[["BG", "FP"]] = "NO SK DATA"
                    datadf[["bgnotes", "fpnotes", "newbroad"]] = "NO SK DATA"
                    datadf[["tagstoadd", "tagstoremove"]] = "NO SK DATA"
                    finalcolstokeep = [
                        "section",
                        "CODE",
                        "EVENT",
                        "DATE",
                        "BROADCAST",
                        "newbroad",
                        "BG",
                        "bgnotes",
                        "FP",
                        "fpnotes",
                        "tagstoadd",
                        "tagstoremove",
                        "COUNT_SUM",
                        "THRESHOLD",
                        "CAPACITY",
                        "PRICE",
                        "COUNT",
                        "PUBLIC DESC",
                        "DESC",
                    ]
                    datadf.drop(
                        datadf.columns.difference(finalcolstokeep), axis=1, inplace=True
                    )
                    datadf = datadf.reindex(finalcolstokeep, axis=1)
                    cleandf = datadf
                    cleandf.fillna("No Data", inplace=True)
                    # datadf.to_csv("Final.csv",index=False)
                    return cleandf
                else:
                    broaddf = broaddf.loc[
                        broaddf["notes"].str.contains(".com") == False
                    ]

                    broaddfcolstokeep = [
                        "section",
                        "notes",
                        "broadcast",
                        "tags",
                        "quantity",
                        "seatnumbers",
                    ]
                    broaddf.drop(
                        broaddf.columns.difference(broaddfcolstokeep),
                        inplace=True,
                        axis=1,
                    )
                    # broaddf.to_csv('broaddf.csv',index=False)
                    cleandf = broaddf.merge(
                        datadf, left_on=["section"], right_on=["CODE"], how="left"
                    )
                    # cleandf.to_csv('cleandf.csv',index=False)
                    cleandf[["BG", "FP"]] = cleandf.apply(
                        lambda x: intnotes(x), axis=1, result_type="expand"
                    )
                    # cleandf.to_csv('cleandfafterinnotes.csv',index=False)

                    for f in feesarr:
                        t = f[0]
                        if teamname in t:
                            fees = f[1]
                        else:
                            fees = 10
                    cleandf["fees"] = fees
                    groubbydf = pd.crosstab(
                        cleandf["CODE"], cleandf["BROADCAST"]
                    ).reset_index(names="CODE")
                    print(groubbydf)
                    cleandf = cleandf.merge(groubbydf, on="CODE", how="left")
                    cleandf[["bgnotes", "fpnotes", "newbroad"]] = cleandf.apply(
                        lambda x: notes(x, teamname), axis=1, result_type="expand"
                    )
                    # cleandf.to_csv("AfternotesCleandf.csv",index=False)
                    cleandf[["tagstoadd", "tagstoremove"]] = cleandf.apply(
                        lambda x: tags(x), axis=1, result_type="expand"
                    )
                    finalcolstokeep = [
                        "section",
                        "CODE",
                        "EVENT",
                        "DATE",
                        "BROADCAST",
                        "newbroad",
                        "BG",
                        "bgnotes",
                        "FP",
                        "fpnotes",
                        "tagstoadd",
                        "tagstoremove",
                        "COUNT_SUM",
                        "THRESHOLD",
                        "CAPACITY",
                        "PRICE",
                        "COUNT",
                        "PUBLIC DESC",
                        "DESC",
                    ]
                    cleandf.drop(
                        cleandf.columns.difference(finalcolstokeep),
                        axis=1,
                        inplace=True,
                    )
                    cleandf = cleandf.reindex(finalcolstokeep, axis=1)
                    cleandf.fillna("No Data", inplace=True)
                    cleandf.drop_duplicates(keep="first", inplace=True)
                    # datadf.to_csv("Final.csv",index=False)
                    return cleandf

            # client.close()

        else:
            for data in results:
                datadf = pd.DataFrame(data["data"])
                dateinfo = data["data"][0]["DATE"]
                datadf["CODE"] = datadf["CODE"].apply(
                    lambda x: "GA" if "GA" in x else x
                )
                datadf["CODE"] = datadf["CODE"].apply(
                    lambda x: "LAWNS" if "LAWNS" in x else x
                )
                datadf["CODE"] = datadf["CODE"].apply(
                    lambda x: "LAWN" if "LAWN" in x else x
                )
                datadf["CODE"] = datadf["CODE"].apply(
                    lambda x: "BERM" if "BERM" in x else x
                )

                datestr = str(dateinfo).split("T")[0]
                teamname = team.split("_Results")[0]
                csvname = teamname + datestr + ".csv"
                sglistdbname = (team.split("_Results")[0]) + "_SGELIST"
                if "Training" in team:
                    sglistdbname = (team.split("Training_Results")[0]) + "_SGELIST"
                print("SGELIST DBNAME: ", sglistdbname)
                sgelistdb = client[sglistdbname]
                sgelistcol = sgelistdb[sglistdbname]
                sglistresults = sgelistcol.find_one({})
                sglistdf = pd.DataFrame(sglistresults["elist"])
                sgidrow = sglistdf.loc[sglistdf["EDATE"] == datestr]
                sgid = sgidrow["EVENTID"].item()
                skyvssgdbname = "SKYBOXID_VS_SGID"
                skyvssgdb = client[skyvssgdbname]
                skyvsgcol = skyvssgdb[skyvssgdbname]
                skyvssgresults = skyvsgcol.find_one({"SGID": str(sgid)})
                if skyvssgresults == None:
                    print("NO SKY DATA")
                    return "NO SKY DATA"

                else:
                    skyid = skyvssgresults["SBID"]
                    datadf.drop_duplicates(keep="first", inplace=True)

                    # datadf.to_csv("datadfwiththreshold.csv",index=False)
                    datadf["COUNT"] = datadf["COUNT"].astype(int)
                    datadf["CAPACITY"] = datadf["CAPACITY"].astype(int)
                    sumdf = datadf.groupby(["CODE"]).agg({"COUNT": "sum"})
                    lawncapsumdf = datadf.groupby(["CODE"]).agg({"CAPACITY": "sum"})
                    lawncapsumdf = lawncapsumdf.loc[
                        lawncapsumdf.index.isin(["GA", "LAWNS", "LAWN", "BERM"])
                    ]
                    lawncapsumdf.reset_index(inplace=True)
                    # lawncapsumdf.to_csv('lawncapsumdf.csv')
                    datadf = datadf.merge(
                        lawncapsumdf, on="CODE", how="left", suffixes=(None, "_SUM")
                    )
                    datadf = datadf.merge(
                        sumdf, how="left", on="CODE", suffixes=(None, "_SUM")
                    )
                    # datadf.to_csv("datadfaftersumdf.csv",index=False)

                    datadf["COUNT"] = datadf.apply(
                        lambda x: x["COUNT_SUM"]
                        if x["CODE"] in ["GA", "LAWNS", "LAWN", "BERM"]
                        else x["COUNT"],
                        axis=1,
                    )
                    datadf["CAPACITY"] = datadf.apply(
                        lambda x: x["CAPACITY_SUM"]
                        if x["CODE"] in ["GA", "LAWNS", "LAWN", "BERM"]
                        else x["CAPACITY"],
                        axis=1,
                    )
                    datadf["THRESHOLD"] = datadf.apply(lambda x: threshold(x), axis=1)
                    datadf.drop_duplicates(
                        subset=["CODE", "COUNT", "CAPACITY", "PRICE"],
                        keep="first",
                        inplace=True,
                    )
                    nonlawnsdf = datadf.loc[
                        ~datadf["CODE"].isin(["GA", "LAWNS", "LAWN", "BERM"])
                    ]
                    lawnsdf = datadf.loc[
                        datadf["CODE"].isin(["GA", "LAWNS", "LAWN", "BERM"])
                    ]
                    lawnsdf = lawnsdf.loc[lawnsdf["PRICE"] != "NA"]
                    datadf = pd.concat([nonlawnsdf, lawnsdf])
                    countgroupdf = datadf.groupby(["CODE"])["COUNT"].rank(
                        ascending=True, method="first"
                    )
                    pricegroupdf = datadf.groupby("CODE")["PRICE"].rank(
                        ascending=True, method="first"
                    )
                    # datadf.to_csv("datadfaftersumdf.csv",index=False)
                    datadf = datadf.merge(
                        countgroupdf,
                        how="left",
                        suffixes=(None, "_rank"),
                        left_index=True,
                        right_index=True,
                    )
                    datadf = datadf.merge(
                        pricegroupdf,
                        how="left",
                        suffixes=(None, "_rank"),
                        left_index=True,
                        right_index=True,
                    )
                    sizedf = pd.DataFrame((datadf.groupby(["CODE"]).size()))
                    sizedf.rename({0: "SIZE"}, inplace=True, axis=1)
                    datadf = datadf.merge(sizedf, how="left", on="CODE")
                    # datadf.to_csv('Aftergroupdf.csv',index=False)
                    datadf["PB"] = datadf.apply(lambda x: pricebreak(x), axis=1)
                    # datadf.to_csv('AfterPB.csv',index=False)
                    datadf["BROADCAST"] = datadf.apply(lambda x: broadcast(x), axis=1)
                    # datadf.to_csv("afterBroad.csv",index=False)
                    broadresults = requests.get(
                        "https://api.blabla.com/event_listings.php?token=blabla&eventid=%s&includeTags=zone"
                        % (skyid)
                    )
                    broadresponse = broadresults.json()
                    broaddf = pd.DataFrame(broadresponse["data"])
                    if broaddf.empty:
                        datadf[["BG", "FP"]] = "NO SK DATA"
                        datadf[["bgnotes", "fpnotes", "newbroad"]] = "NO SK DATA"
                        datadf[["tagstoadd", "tagstoremove"]] = "NO SK DATA"
                        finalcolstokeep = [
                            "section",
                            "CODE",
                            "EVENT",
                            "DATE",
                            "BROADCAST",
                            "newbroad",
                            "BG",
                            "bgnotes",
                            "FP",
                            "fpnotes",
                            "tagstoadd",
                            "tagstoremove",
                            "COUNT_SUM",
                            "THRESHOLD",
                            "CAPACITY",
                            "PRICE",
                            "COUNT",
                            "PUBLIC DESC",
                            "DESC",
                        ]
                        datadf.drop(
                            datadf.columns.difference(finalcolstokeep),
                            axis=1,
                            inplace=True,
                        )
                        datadf = datadf.reindex(finalcolstokeep, axis=1)
                        datadf.fillna("No Data", inplace=True)
                        # datadf.to_csv("Final.csv",index=False)
                        return datadf
                    else:
                        broaddf = broaddf.loc[
                            broaddf["notes"].str.contains(".com") == False
                        ]

                        broaddfcolstokeep = [
                            "section",
                            "notes",
                            "broadcast",
                            "tags",
                            "quantity",
                            "seatnumbers",
                        ]
                        broaddf.drop(
                            broaddf.columns.difference(broaddfcolstokeep),
                            inplace=True,
                            axis=1,
                        )
                        # broaddf.to_csv('broaddf.csv',index=False)
                        cleandf = broaddf.merge(
                            datadf, left_on=["section"], right_on=["CODE"], how="left"
                        )
                        # cleandf.to_csv('cleandf.csv',index=False)
                        cleandf[["BG", "FP"]] = cleandf.apply(
                            lambda x: intnotes(x), axis=1, result_type="expand"
                        )
                        # cleandf.to_csv('cleandfafterinnotes.csv',index=False)

                        for f in feesarr:
                            t = f[0]
                            if teamname in t:
                                fees = f[1]
                            else:
                                fees = 10
                        cleandf["fees"] = fees
                        groubbydf = pd.crosstab(
                            cleandf["CODE"], cleandf["BROADCAST"], dropna=False
                        ).reset_index(names="CODE")
                        print(groubbydf)
                        cleandf = cleandf.merge(groubbydf, on="CODE", how="left")

                        cleandf[["bgnotes", "fpnotes", "newbroad"]] = cleandf.apply(
                            lambda x: notes(x, teamname), axis=1, result_type="expand"
                        )

                        # cleandf.to_csv("AfternotesCleandf.csv",index=False)
                        cleandf[["tagstoadd", "tagstoremove"]] = cleandf.apply(
                            lambda x: tags(x), axis=1, result_type="expand"
                        )
                        finalcolstokeep = [
                            "section",
                            "CODE",
                            "EVENT",
                            "DATE",
                            "BROADCAST",
                            "newbroad",
                            "BG",
                            "bgnotes",
                            "FP",
                            "fpnotes",
                            "tagstoadd",
                            "tagstoremove",
                            "COUNT_SUM",
                            "THRESHOLD",
                            "CAPACITY",
                            "PRICE",
                            "COUNT",
                            "PUBLIC DESC",
                            "DESC",
                        ]
                        cleandf.drop(
                            cleandf.columns.difference(finalcolstokeep),
                            axis=1,
                            inplace=True,
                        )
                        cleandf = cleandf.reindex(finalcolstokeep, axis=1)
                        cleandf.drop_duplicates(keep="first", inplace=True)
                        cleandf.fillna("No Data", inplace=True)
                        return cleandf
                    # cleandf.to_csv(csvname,index=False)
                # returndf = objdf.to_json(index=False)
            # client.close()

    else:
        # client.close()
        cleandf = pd.DataFrame(
            columns=[
                "section",
                "CODE",
                "EVENT",
                "DATE",
                "BROADCAST",
                "newbroad",
                "BG",
                "bgnotes",
                "FP",
                "fpnotes",
                "tagstoadd",
                "tagstoremove",
                "COUNT_SUM",
                "THRESHOLD",
                "CAPACITY",
                "PRICE",
                "COUNT",
                "PUBLIC DESC",
                "DESC",
            ]
        )
        cleandf[
            [
                "section",
                "CODE",
                "EVENT",
                "DATE",
                "BROADCAST",
                "newbroad",
                "BG",
                "bgnotes",
                "FP",
                "fpnotes",
                "tagstoadd",
                "tagstoremove",
                "COUNT_SUM",
                "THRESHOLD",
                "CAPACITY",
                "PRICE",
                "COUNT",
                "PUBLIC DESC",
                "DESC",
            ]
        ] = "No Tickets Data"
        cleandf.fillna("No Tickets Data", inplace=True)
        return cleandf
