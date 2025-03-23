import json
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytz
import requests
from flask import Flask, render_template, request
from pymongo import MongoClient

from countsapi import countsapi2
from generatepayload import payloadconstructor
from outputslack import send_slack_message

mongousername = os.environ["MANGOU"]
mongopassword = os.environ["MANGOP"]
tokenkey = os.environ["TOKEN"]

# client = MongoClient("mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"%(mongousername,mongopassword))

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

print(dbarr)


def create_app():
    app = Flask(__name__)

    @app.route("/web/counts", methods=["get"])
    def counts():
        client = MongoClient(
            "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
            % (mongousername, mongopassword)
        )

        team = request.args.get("team")
        sdate = request.args.get("sdate")
        edatestr = request.args.get("edate")
        # sdate = '10032022'

        team = team + "SpringTraining_Results"

        print("Team that was being requested: ", team)
        edate = edatestr.split("T")[0].replace("-", "_")
        print(edate)
        if team != "":
            db = client[team]
            col = db[sdate]
            results = col.find({"edate": edate})
            ed_count = results.explain().get("executionStats", {}).get("nReturned")
            print("Count Found. ", ed_count)
            if ed_count > 1:
                for data in results:
                    dateinfo = data["data"][0]["DATE"]
                    if edatestr in dateinfo:
                        objdata = data["data"]
                        objdf = pd.DataFrame(objdata)
                        print(objdf)
                        tables = [objdf.to_html()]
                client.close()
                return render_template("table.html", tables=tables, titles=[""])

            else:
                for data in results:
                    objdata = data["data"]
                    objdf = pd.DataFrame(objdata)
                    print(objdf)
                    tables = [objdf.to_html()]

                client.close()
                return render_template("table.html", tables=tables, titles=[""])
        else:
            client.close()
            return "Invalid Request"

    @app.route("/api/counts", methods=["get"])
    def countsapi():
        tid = request.args.get("tid")
        sdate = request.args.get("sdate")
        edatestr = request.args.get("edate")
        print(tid)
        data = countsapi2(tid, sdate, edatestr)
        print(data)
        if data.empty:
            print("empty Data")
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
            ] = "No Tickets.com Data"
            # cleandf.reindex(list(range(0,2))).reset_index(drop=True,inplace=True)
            # returndata = cleandf.fillna("No Tickets.com Data",inplace=True)
            data = cleandf
            print(data)

        returndata = data.values.tolist()

        print(returndata)

        return returndata

    @app.route("/api/col", methods=["get"])
    def getawayteam():
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

        tid = request.args.get("tid")
        sdate = request.args.get("sdate")

        team = getteamid(tid)
        teamsingle = team.split("_")[0]
        teamsingle = teamsingle.split("Training")[0]
        teamlistarr = [
            "Angels",
            "Astros",
            "Athletics",
            "Brewers",
            "Cardinals",
            "Cubs",
            "Dodgers",
            "Giants",
            "Guardians",
            "Marlins",
            "Mets",
            "Nationals",
            "Orioles",
            "Phillies",
            "Pirates",
            "Rangers",
            "Rays",
            "RedSox",
            "Reds",
            "Royals",
            "Tigers",
            "Twins",
            "Diamondbacks",
            "Braves",
            "White Sox",
            "Rockies",
            "Yankees",
            "Padres",
            "Mariners",
            "Blue Jays",
        ]
        dbname = teamsingle + "_SGELIST"
        db = client[dbname]
        col = db[dbname]
        results = col.find_one()
        eventarr = []
        elist = results["elist"]

        elistdf = pd.DataFrame(elist)

        elistdf["Awayteam"] = elistdf["ENAME"].apply(lambda x: str(x).split(" at ")[0])

        ateamunique = elistdf["Awayteam"].unique().tolist()
        print(ateamunique)
        client.close()
        return ateamunique

        # sched

    @app.route("/api/sched", methods=["get"])
    def getsched():
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

        teamlistarr = [
            "Angels",
            "Astros",
            "Athletics",
            "Brewers",
            "Cardinals",
            "Cubs",
            "Dodgers",
            "Giants",
            "Guardians",
            "Marlins",
            "Mets",
            "Nationals",
            "Orioles",
            "Phillies",
            "Pirates",
            "Rangers",
            "Rays",
            "RedSox",
            "Reds",
            "Royals",
            "Tigers",
            "Twins",
            "Diamondbacks",
            "Braves",
            "White Sox",
            "Rockies",
            "Yankees",
            "Padres",
            "Mariners",
            "Blue Jays",
        ]
        tid = request.args.get("tid")
        ateam = request.args.get("ateam")
        team = getteamid(tid)
        sdate = request.args.get("sdate")
        teamsingle = team.split("_")[0]
        teamsingle = teamsingle.split("Training")[0]
        dbname = teamsingle + "_SGELIST"
        db = client[dbname]
        col = db[dbname]
        results = col.find_one()
        elist = results["elist"]

        elistdf = pd.DataFrame(elist)
        elistdf["Awayteam"] = elistdf["ENAME"].apply(lambda x: str(x).split(" at ")[0])
        teamdf = elistdf[elistdf["Awayteam"].isin([ateam])]
        print(teamdf)
        schedarr = teamdf["EDATE"].to_list()

        print(schedarr)

        client.close()
        return schedarr

    @app.route("/api/specalert", methods=["get"])
    def getspecalert():
        client = MongoClient(
            "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
            % (mongousername, mongopassword)
        )
        today = datetime.today().strftime("%m%d%Y")
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%m%d%Y")

        db = client["Threshold_Daily"]
        col = db[today]
        # today = '10042022'
        results = col.find_one()
        if results == None:
            col = db[yesterday]
            results = col.find_one()

        data = results["data"]
        maindf = pd.DataFrame(data=data)
        specdf = maindf[maindf["SPECALERT"] == "Unbroadcast"]
        print(specdf)
        specdata = specdf.values.tolist()
        client.close()
        return specdata

    @app.route("/api/spinalert", methods=["get"])
    def getspinalert():
        client = MongoClient(
            "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
            % (mongousername, mongopassword)
        )
        today = datetime.today().strftime("%m%d%Y")
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%m%d%Y")
        today = "10052022"
        db = client["Threshold_Daily"]
        col = db[today]
        results = col.find_one()
        if results == None:
            col = db[yesterday]
            results = col.find_one()

        data = results["data"]
        maindf = pd.DataFrame(data=data)
        spindf = maindf[maindf["SPINALERT"] == "SPIN"]
        print(spindf)
        spindata = spindf.values.tolist()
        client.close()
        return spindata

    @app.route("/api/sglistsingle", methods=["get"])
    def sglistsingle():
        def matchfunction(x):
            sgqty = x["QTY_LISTED"]
            skyseatmin = x["minskyseat"]
            skyseatmax = x["maxskyseat"]
            sgseatmin = x["sgminseat"]
            sgseatmax = x["sgmaxseat"]
            if sgseatmin != "NA":
                sgseatmin = int(sgseatmin)
                if skyseatmin != "NA":
                    skyseatmin = int(x["minskyseat"])
            else:
                sgseatmin = 0
            if sgseatmax != "NA":
                sgseatmax = int(sgseatmax)
                if skyseatmax != "NA":
                    skyseatmax = int(x["maxskyseat"])
            else:
                sgseatmax = 0
            sbrow = x["row_match"]
            sgrow = x["ROW_NAME"]
            # fv = x['FACE_VALUE']
            # sbprice = float(x['listprice'])
            # skyqty = int(x['quantity'])

            ## Newcode using Seat and Qty and row
            if sbrow != "NA":
                if sbrow == sgrow:
                    if (sgseatmin >= skyseatmin) & (sgseatmax <= skyseatmax):
                        return "Y"
                    else:
                        return "N"
                else:
                    return "N"
            else:
                return "N"

        def bpricegen(x):
            ownlist = x["Own_listing"]
            listprice = x["listprice"]

            if ownlist == "N":
                if x["FACE_VALUE"] == "NA":
                    x_facevalue = 0
                else:
                    x_facevalue = x["FACE_VALUE"]
                newbprice = x_facevalue * 1.07
                return newbprice
            else:
                return listprice

        def lowest(x):
            own = x["Own_listing"]
            ownsize = x["OWNSIZE"]
            size = x["SIZE"]

            # eg. 500 - 450 = 50 Means that we are above by 50 (if positive)
            # eg. 450 - 500 = -50 means that we are below by 50 (if negative)
            # eg 300 - 350 = -40 = mrkup
            # 310 - LD = Y
            # 320 - company 1
            # 333 - Company 2
            # min FV = 310
            # difference = 310 - 310 = 0
            # if  310 == 310 just return 310

            if own == "Y":
                lowest_comp_price = x["min_fv"]
                if lowest_comp_price != "NO COMP":
                    fv = float(x["floor_value"])
                    lowest_comp_price = float(lowest_comp_price)

                    face_value = x["FACE_VALUE"]
                    listprice = float(x["listprice"])

                    difference = face_value - lowest_comp_price
                    suggestedbprice = lowest_comp_price * 1.07
                    singleprice = fv * 1.5

                    if (
                        (face_value <= lowest_comp_price)
                        & (size > ownsize)
                        & (difference >= -2)
                        & (difference <= 0)
                    ):
                        return round(listprice, 2), "NO CHANGES"
                    # positive difference == lower bprice
                    elif (difference > 0) & (suggestedbprice < fv) & (size > ownsize):
                        # IF THE COMPETITOR IS LOWER THEN THE FV IT WILL SET TO BFLOOR (MEANING WE ARE AT FV BUT WE ARE NOT THE LOWEST ANYMORE)
                        # SO THE TEAM WHEN THEY SEE BFLOOR WILL COMPARE TO THE 2ND LOWEST AND -1 TO THEIR APROX BPRICE THEREFORE AVOIDING ANY WEIRD BPRICE FROM
                        # OTHER BROKERS WHO MAY TRY TO PUSH DOWN OUR PRICING.

                        return fv, "BFLOOR"
                    elif (difference > 0) & (size > ownsize):
                        return round(suggestedbprice, 2), "MRKDWN"
                    # negative difference = increase bprice but only if difference of more than 5 dollars (to monitor)
                    # need to find the 2nd lowest comp price that is "N" then push that.
                    # this would need to be seperated out as a seperate column with a different logic behind it.

                    elif size == ownsize:
                        return round(singleprice, 2), "RETAIN SINGLE"
                    else:
                        return "ERROR", "ERROR"
                else:
                    fv = float(x["floor_value"])
                    face_value = x["FACE_VALUE"]
                    lowest_comp_price = face_value
                    singleprice = fv * 1.5
                    return round(singleprice, 2), "RETAIN SINGLE"

            else:
                return "NA", "NA"

        def markup(x):
            own = x["Own_listing"]
            mrk = x["MRK"]
            ownsize = x["OWNSIZE"]
            size = x["SIZE"]
            sec_low = x["2ND_LOWEST"]
            face_value = x["FACE_VALUE"]
            pricesuggestion = x["pricesuggest"]
            newbprice = sec_low * 1.07
            difference = sec_low - face_value

            if (own == "Y") & (difference > 2) & (mrk == "ERROR") & (size > ownsize):
                fv = float(x["floor_value"])
                if fv > newbprice:
                    return round(fv, 2), "BFLOOR"
                else:
                    print("MRKUP")
                    return round(newbprice, 2), "MRKUP"
            else:
                return pricesuggestion, mrk

        today = datetime.today().strftime("%m%d%Y")
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%m%d%Y")
        mongousername = os.environ["MANGOU"]
        mongopassword = os.environ["MANGOP"]
        client = MongoClient(
            "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
            % (mongousername, mongopassword)
        )
        t = request.args.get("t")
        eid = request.args.get("eid")
        team = t  # this is inputs from api calls
        team = str(team).replace(" ", "")
        print(team)

        skydbname = "SKYBOXID_VS_SGID"
        skydb = client.get_database(skydbname)
        skycol = skydb[skydbname]
        result = skycol.find()
        skyiddf = pd.DataFrame(list(result))
        filterdf = skyiddf[(skyiddf["SGID"] == eid)]
        skyid = filterdf["SBID"].item()
        response = requests.get(
            "https://api.blabla.com/event_listings.php?token=blabla&eventid=%s"
            % (skyid)
        )
        today = datetime.today().strftime("%m%d%Y")
        # client = MongoClient("mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"%(mongousername,mongopassword))
        jsonresponse = response.json()
        jsondata = jsonresponse["data"]
        listdf = pd.DataFrame(jsondata)
        broaddf = listdf[
            (listdf["tags"].str.contains("donot-broadcast") == False)
            & (listdf["notes"].str.contains("BG:") == True)
            & (listdf["tags"].str.contains("for-spin") == False)
        ]
        broaddf["floor_value"] = broaddf["notes"].apply(
            lambda x: str(x).split(" -")[0].split("BG:")[1]
        )
        if team == "Reds" or team == "Cubs" or team == "Guardians":
            broaddf["floor_value"] = broaddf["notes"].apply(
                lambda x: str(x).split("-ticketevolution")[0].split("BG:")[1]
            )
        elif team == "Royals":
            broaddf["floor_value"] = broaddf["notes"].apply(
                lambda x: str(x).split("-ticketevolution")[0].split("BG:")[1]
            )

        # requires a mapper for some teams.
        if team == "blank":
            broaddf["section_match"] = broaddf["section"].apply(
                lambda x: "Section " + x[0:3] + " " + x[4:]
            )
            print(broaddf)
        elif (
            team == "WhiteSox"
            or team == "Cardinals"
            or team == "Athletics"
            or team == "Cubs"
            or team == "Diamondbacks"
            or team == "Marlins"
            or team == "Padres"
            or team == "Rangers"
            or team == "RedSox"
            or team == "BlueJays"
            or team == "Braves"
            or team == "Pirates"
            or team == "Brewers"
        ):
            # generate the Map from MongoDB:
            mapname = team + "_Map"
            mapdb = client[mapname]
            mapcol = mapdb[mapname]
            mapresults = mapcol.find_one({})
            mapdf = pd.DataFrame(mapresults["mapdata"])
            broaddf = broaddf.merge(mapdf, left_on="section", right_on="SK CODE")

            broaddf.drop(columns=["DESC", "SG ROW START"], inplace=True)
            broaddf.rename({"SG CODE": "section_match"}, inplace=True, axis=1)
        else:
            broaddf["section_match"] = broaddf["section"].apply(
                lambda x: "Section " + x
            )
        broaddf["row_match"] = broaddf["row"].apply(lambda x: "Row " + x)
        skyseatnumdf = broaddf["seatnumbers"].str.split(",", expand=True)
        skyseatnumarr = skyseatnumdf.to_numpy(dtype=float, na_value=np.nan)
        skyminseatarr = [np.nanmin(m) for m in skyseatnumarr]
        skymaxseatarr = [np.nanmax(m) for m in skyseatnumarr]
        newseatnumdf = pd.DataFrame()
        newseatnumdf["maxskyseat"] = pd.DataFrame(list(skymaxseatarr))
        newseatnumdf["minskyseat"] = pd.DataFrame(list(skyminseatarr))
        skycolstokeep = ["maxskyseat", "minskyseat"]
        newseatnumdf.drop(
            columns=newseatnumdf.columns.difference(skycolstokeep), inplace=True
        )
        broaddf.reset_index(inplace=True, drop=True)
        broaddf = broaddf.join(newseatnumdf)
        filterdf = skyiddf[(skyiddf["SBID"] == skyid)]
        sgid_val = filterdf["SGID"].item()
        dbname = team + "_SG_Results"
        db = client.get_database(dbname)
        collection = db[today]
        result = collection.find_one({"eid": int(sgid_val)})
        if result == None:
            collection = db[yesterday]
            result = collection.find_one({"eid": int(sgid_val)})
        data = result["data"]
        datadf = pd.DataFrame(data)
        seatnumarr = datadf["SEAT_NUMBERS"].tolist()
        minseatarr = [min(m, default="NA") for m in seatnumarr]
        maxseatarr = [max(m, default="NA") for m in seatnumarr]
        seatnumdf = pd.DataFrame()
        seatnumdf["sgmaxseat"] = pd.DataFrame(maxseatarr)
        seatnumdf["sgminseat"] = pd.DataFrame(minseatarr)
        datadf = datadf.join(seatnumdf, how="left")
        colstokeep = [
            "TOTAL_PRICE",
            "FEES",
            "FACE_VALUE",
            "QTY_LISTED",
            "SECTION_NAME",
            "ROW_NAME",
            "IHD",
            "sgmaxseat",
            "sgminseat",
        ]
        datadf.drop(columns=datadf.columns.difference(colstokeep), axis=1, inplace=True)
        datadf["SECTION_NAME"] = datadf["SECTION_NAME"].convert_dtypes()
        broaddf["section_match"] = broaddf["section_match"].convert_dtypes()
        datadf["maxseat"] = datadf["sgmaxseat"]
        datadf["minseat"] = datadf["sgminseat"]
        broaddf["maxseat"] = broaddf["maxskyseat"]
        broaddf["minseat"] = broaddf["minskyseat"]
        compdf = datadf.loc[datadf["minseat"] == "NA"]
        compdf = datadf.loc[datadf["maxseat"] == "NA"]
        datadf = datadf.loc[datadf["minseat"] != "NA"]
        datadf = datadf.loc[datadf["maxseat"] != "NA"]
        datadf["maxseat"] = datadf["maxseat"].astype(int)
        datadf["minseat"] = datadf["minseat"].astype(int)
        broaddf["maxseat"] = broaddf["maxseat"].astype(int)
        broaddf["minseat"] = broaddf["minseat"].astype(int)
        newdf = broaddf.merge(
            datadf,
            right_on=["SECTION_NAME", "maxseat", "minseat"],
            left_on=["section_match", "maxseat", "minseat"],
            how="left",
        )
        balancedf = pd.merge(
            broaddf,
            datadf,
            how="outer",
            right_on=["SECTION_NAME", "maxseat", "minseat"],
            left_on=["section_match", "maxseat", "minseat"],
        )
        balancedf.fillna("NA", inplace=True)
        balancedf = balancedf[balancedf["section_match"] == "NA"].reset_index(drop=True)
        newdf = pd.concat([newdf, compdf, balancedf], ignore_index=True)
        newdf.fillna("NA", inplace=True)
        newdf.drop(
            [
                "id",
                "event_date",
                "event_name",
                "performer_name",
                "shid",
                "venue_name",
                "facevalue",
                "notes",
                "seattype",
                "seatnumbers",
                "tags",
                "taxedcost",
                "broadcast",
                "publicnotes",
                "timestamp",
                "lvc",
                "lvt",
            ],
            axis=1,
            inplace=True,
            errors="ignore",
        )
        # newdf['floor_value'] = newdf['floor_value'].astype(float)
        # newdf['minskyseat'] = newdf['minskyseat'].astype(int) ##new changes
        # newdf['maxskyseat'] = newdf['maxskyseat'].astype(int)
        newdf["Own_listing"] = newdf.apply(lambda x: matchfunction(x), axis=1)
        # to eliminate two Y's in the same section #to code when i see the situation
        sizedf = pd.DataFrame((newdf.groupby("SECTION_NAME").size()))
        ownsizefilterdf = newdf.loc[newdf["Own_listing"] == "Y"]
        ownsizedf = pd.DataFrame(ownsizefilterdf.groupby("SECTION_NAME").size())
        ownsizedf.rename({0: "OWNSIZE"}, inplace=True, axis=1)
        if ownsizedf.empty:
            datadf = pd.DataFrame(data)
            broadcols = broaddf.columns
            if "SK_CODE" in broadcols:
                print("Contain SK CODE")
            else:
                broaddf.rename({"section": "SK CODE"}, inplace=True, axis=1)

            colstokeep = [
                "TOTAL_PRICE",
                "FEES",
                "FACE_VALUE",
                "QTY_LISTED",
                "SECTION_NAME",
                "ROW_NAME",
                "IHD",
                "sgmaxseat",
                "sgminseat",
            ]
            datadf.drop(
                columns=datadf.columns.difference(colstokeep), axis=1, inplace=True
            )
            newdf = broaddf.merge(
                datadf, right_on=["SECTION_NAME"], left_on=["section_match"], how="left"
            )
            # newdf.rename({'section':'SK CODE'},inplace=True,axis=1)
            newdf.fillna("NA", inplace=True)
            newdf[["pricesuggest", "MRK"]] = "NA"
            newdf["Own_listing"] = "N"
            colstokeepfinal = [
                "listprice",
                "quantity",
                "floor_value",
                "FACE_VALUE",
                "TOTAL_PRICE",
                "QTY_LISTED",
                "ROW_NAME",
                "FEES",
                "SECTION_NAME",
                "Own_listing",
                "pricesuggest",
                "MRK",
                "SK CODE",
            ]
            newdf.drop(newdf.columns.difference(colstokeepfinal), axis=1, inplace=True)
            colorder = [
                "TOTAL_PRICE",
                "FEES",
                "FACE_VALUE",
                "QTY_LISTED",
                "ROW_NAME",
                "SECTION_NAME",
                "listprice",
                "quantity",
                "floor_value",
                "Own_listing",
                "pricesuggest",
                "MRK",
                "SK CODE",
            ]
            # duplicate_cols = newdf.columns[newdf.columns.duplicated(keep='first')]
            # newdf.drop(columns=duplicate_cols, inplace=True)
            newdf = newdf.reindex(colorder, axis=1)
            newdf.fillna("NA", inplace=True)
        else:
            sizedf.rename({0: "SIZE"}, inplace=True, axis=1)
            newdf = newdf.merge(sizedf["SIZE"], on="SECTION_NAME")
            newdf = newdf.merge(ownsizedf["OWNSIZE"], on="SECTION_NAME")
            newdf["bprice"] = newdf.apply(lambda x: bpricegen(x), axis=1)
            newdf["bprice"] = newdf["bprice"].astype(float)
            # newdf['floor_value'] = newdf['floor_value'].astype(float)
            newdf.drop(["row_match", "section_match", "eventid"], axis=1, inplace=True)

            newdf.drop(newdf.loc[newdf["SECTION_NAME"] == "NA"].index, inplace=True)
            lowestcomdf = newdf.groupby(["SECTION_NAME", "Own_listing"]).agg(
                min_fv=("FACE_VALUE", "min"), mean_fv=("FACE_VALUE", "mean")
            )
            lowestcomdf.reset_index(level=["Own_listing"], inplace=True)
            lowestcomdf = lowestcomdf.loc[lowestcomdf["Own_listing"] == "N"]
            lowestcomdf.drop("Own_listing", inplace=True, axis=1)
            # meanmindf = newdf.groupby('SECTION_NAME').agg(min_fv=('FACE_VALUE','min'),mean_fv=('FACE_VALUE','mean'))
            newdf = newdf.merge(lowestcomdf, how="left", on="SECTION_NAME")
            newdf.fillna("NO COMP", inplace=True)

            newdf[["pricesuggest", "MRK"]] = newdf.apply(
                lambda x: lowest(x), axis=1, result_type="expand"
            )
            newdf.drop(["min_fv", "mean_fv"], axis=1, inplace=True)
            # to find the Mrkup 2nd lowest price only if there is more than 1 count and if it is nochanges
            newdf["FACE_VALUE"] = newdf["FACE_VALUE"].astype(float)
            secondlowdf = newdf.groupby(["SECTION_NAME", "Own_listing"])["FACE_VALUE"]
            secondlowdf = (
                secondlowdf.nsmallest(1, "first")
                .groupby(level=["SECTION_NAME", "Own_listing"])
                .last()
                .rename("2ND_LOWEST")
            )
            secondlowdf = pd.DataFrame(secondlowdf)
            secondlowdf.reset_index(level=["Own_listing"], inplace=True)
            secondlowdf = secondlowdf.loc[secondlowdf["Own_listing"] == "N"]
            secondlowdf.drop("Own_listing", inplace=True, axis=1)
            newdf = newdf.merge(secondlowdf, on="SECTION_NAME", how="left")
            newdf[["pricesuggest", "MRK"]] = newdf.apply(
                lambda x: markup(x), axis=1, result_type="expand"
            )
            newdfcols = newdf.columns
            if "section" not in newdfcols:
                print("Section does not exist")
            elif "SK CODE" in newdfcols:
                print("SK CODE exist")
            else:
                newdf.rename({"section": "SK CODE"}, inplace=True, axis=1)
                pass
            # newdf.drop(['row','section','SIZE','bprice','2ND_LOWEST'],axis=1,inplace=True)

            colstokeepfinal = [
                "listprice",
                "quantity",
                "floor_value",
                "FACE_VALUE",
                "TOTAL_PRICE",
                "QTY_LISTED",
                "ROW_NAME",
                "FEES",
                "SECTION_NAME",
                "Own_listing",
                "pricesuggest",
                "MRK",
                "SK CODE",
            ]
            newdf.drop(newdf.columns.difference(colstokeepfinal), axis=1, inplace=True)

            colorder = [
                "TOTAL_PRICE",
                "FEES",
                "FACE_VALUE",
                "QTY_LISTED",
                "ROW_NAME",
                "SECTION_NAME",
                "listprice",
                "quantity",
                "floor_value",
                "Own_listing",
                "pricesuggest",
                "MRK",
                "SK CODE",
            ]
            newdf = newdf.reindex(colorder, axis=1)
            newdf.fillna("NA", inplace=True)
        dataarr = newdf.values.tolist()
        client.close()
        print(newdf)
        return dataarr

    @app.route("/api/sgreport", methods=["get"])
    def sgreport():
        today = datetime.today().strftime("%m%d%Y")
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%m%d%Y")
        mongousername = os.environ["MANGOU"]
        mongopassword = os.environ["MANGOP"]

        client = MongoClient(
            "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
            % (mongousername, mongopassword)
        )

        t = request.args.get("t")
        eid = request.args.get("eid")

        team = t  # this is inputs from api calls
        team = str(team).replace(" ", "")
        print(team)

        skydbname = "SKYBOXID_VS_SGID"
        skydb = client.get_database(skydbname)
        skycol = skydb[skydbname]
        result = skycol.find()
        skyiddf = pd.DataFrame(list(result))

        filterdf = skyiddf[(skyiddf["SGID"] == eid)]
        skyid = filterdf["SBID"].item()

        response = requests.get(
            "https://api.blabla.com/event_listings.php?token=blabla&eventid=%s"
            % (skyid)
        )

        today = datetime.today().strftime("%m%d%Y")

        client = MongoClient(
            "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
            % (mongousername, mongopassword)
        )

        jsonresponse = response.json()

        jsondata = jsonresponse["data"]

        listdf = pd.DataFrame(jsondata)

        broaddf = listdf[
            (listdf["tags"].str.contains("donot-broadcast") == False)
            & (listdf["notes"].str.contains("BG:") == True)
            & (listdf["tags"].str.contains("for-spin") == False)
        ]
        colvals = broaddf.columns
        broaddf["floor_value"] = broaddf["notes"].apply(
            lambda x: str(x).split(" -")[0].split("BG:")[1]
        )
        if (
            team == "Royals"
            or team == "Pirates"
            or team == "Reds"
            or team == "Cubs"
            or team == "Guardians"
        ):
            broaddf["floor_value"] = broaddf["notes"].apply(
                lambda x: str(x).split(" -ticketevolution")[0].split("BG:")[1]
            )

        if team == "blank":
            broaddf["section_match"] = broaddf["section"].apply(
                lambda x: "Section " + x[0:3] + " " + x[4:]
            )
            print(broaddf)
        elif (
            team == "Athletics"
            or team == "Cubs"
            or team == "Diamondbacks"
            or team == "Marlins"
            or team == "Padres"
            or team == "Rangers"
            or team == "RedSox"
            or team == "BlueJays"
            or team == "Braves"
            or team == "Pirates"
            or team == "Brewers"
        ):
            # generate the Map from MongoDB:
            mapname = team + "_Map"
            mapdb = client[mapname]
            mapcol = mapdb[mapname]
            mapresults = mapcol.find_one({})
            # print(mapresults['mapdata'])
            mapdf = pd.DataFrame(mapresults["mapdata"])
            broaddf = broaddf.merge(mapdf, left_on="section", right_on="SK CODE")

            broaddf.drop(columns=["SK CODE", "DESC", "SG ROW START"], inplace=True)
            broaddf.rename({"SG CODE": "section_match"}, inplace=True, axis=1)
        else:
            broaddf["section_match"] = broaddf["section"].apply(
                lambda x: "Section " + x
            )

        broaddf["row_match"] = broaddf["row"].apply(lambda x: "Row " + x)
        skyseatnumdf = broaddf["seatnumbers"].str.split(",", expand=True)
        skyseatnumarr = skyseatnumdf.to_numpy(dtype=float, na_value=np.nan)
        skyminseatarr = [np.nanmin(m) for m in skyseatnumarr]
        skymaxseatarr = [np.nanmax(m) for m in skyseatnumarr]
        newseatnumdf = pd.DataFrame()
        newseatnumdf["maxskyseat"] = pd.DataFrame(list(skymaxseatarr))
        newseatnumdf["minskyseat"] = pd.DataFrame(list(skyminseatarr))
        skycolstokeep = ["maxskyseat", "minskyseat"]
        newseatnumdf.drop(
            columns=newseatnumdf.columns.difference(skycolstokeep), inplace=True
        )
        broaddf.reset_index(inplace=True, drop=True)
        broaddf = broaddf.join(newseatnumdf)

        filterdf = skyiddf[(skyiddf["SBID"] == skyid)]

        sgid_val = filterdf["SGID"].item()

        dbname = team + "_SG_Results"
        db = client.get_database(dbname)
        collection = db[today]
        result = collection.find_one({"eid": int(sgid_val)})

        if result == None:
            collection = db[yesterday]
            result = collection.find_one({"eid": int(sgid_val)})

        data = result["data"]

        datadf = pd.DataFrame(data)
        seatnumarr = datadf["SEAT_NUMBERS"].tolist()
        minseatarr = [min(m, default="NA") for m in seatnumarr]
        maxseatarr = [max(m, default="NA") for m in seatnumarr]
        seatnumdf = pd.DataFrame()
        seatnumdf["sgmaxseat"] = pd.DataFrame(maxseatarr)
        seatnumdf["sgminseat"] = pd.DataFrame(minseatarr)

        datadf = datadf.join(seatnumdf, how="left")
        colstokeep = [
            "TOTAL_PRICE",
            "FEES",
            "FACE_VALUE",
            "QTY_LISTED",
            "SECTION_NAME",
            "ROW_NAME",
            "IHD",
            "sgmaxseat",
            "sgminseat",
        ]
        datadf.drop(columns=datadf.columns.difference(colstokeep), axis=1, inplace=True)

        datadf["SECTION_NAME"] = datadf["SECTION_NAME"].convert_dtypes()
        broaddf["section_match"] = broaddf["section_match"].convert_dtypes()

        newdf = datadf.merge(
            broaddf, left_on=["SECTION_NAME"], right_on=["section_match"], how="right"
        )
        newdf.fillna("NA", inplace=True)
        newdf.drop(
            [
                "id",
                "event_date",
                "event_name",
                "performer_name",
                "shid",
                "venue_name",
                "facevalue",
                "notes",
                "seattype",
                "seatnumbers",
                "tags",
                "taxedcost",
                "broadcast",
                "publicnotes",
                "timestamp",
                "lvc",
                "lvt",
            ],
            axis=1,
            inplace=True,
            errors="ignore",
        )

        def matchfunction(x):
            sgqty = x["QTY_LISTED"]
            skyseatmin = x["minskyseat"]
            skyseatmax = x["maxskyseat"]
            sgseatmin = x["sgminseat"]
            sgseatmax = x["sgmaxseat"]
            if sgseatmin != "NA":
                sgseatmin = int(sgseatmin)
            else:
                sgseatmin = 0
            if sgseatmax != "NA":
                sgseatmax = int(sgseatmax)
            else:
                sgseatmax = 0
            sbrow = x["row_match"]
            sgrow = x["ROW_NAME"]
            fv = x["FACE_VALUE"]
            sbprice = float(x["listprice"])
            skyqty = int(x["quantity"])

            if sbrow == sgrow:
                if (sgseatmin >= skyseatmin) & (sgseatmax <= skyseatmax):
                    return "Y"
                else:
                    return "N"
            else:
                return "N"

        def bpricegen(x):
            ownlist = x["Own_listing"]
            listprice = x["listprice"]

            if ownlist == "N":
                if x["FACE_VALUE"] == "NA":
                    x_facevalue = 0
                else:
                    x_facevalue = x["FACE_VALUE"]
                newbprice = x_facevalue * 1.2
                return newbprice
            else:
                return listprice

        def lowest(x):
            lowest_comp_price = x["min_fv"]
            own = x["Own_listing"]
            fv = x["floor_value"]
            face_value = x["FACE_VALUE"]
            listprice = x["listprice"]
            size = x["SIZE"]
            difference = face_value - lowest_comp_price
            suggestedbprice = lowest_comp_price * 1.2
            singleprice = fv * 1.5
            suggestedbprice = round(suggestedbprice, 2)
            singleprice = round(singleprice, 2)

            if own == "Y":
                if (face_value == lowest_comp_price) & (size > 1):
                    return listprice, "NO CHANGES"

                elif (difference > 0) & (suggestedbprice < fv) & (size > 1):
                    return fv, "BFLOOR"
                elif (difference > 0) & (size > 1):
                    return suggestedbprice, "MRKDWN"

                elif size == 1:
                    return singleprice, "RETAIN SINGLE"
                else:
                    return "ERROR", "ERROR"

            else:
                return "NA", "NA"

        def markup(x):
            own = x["Own_listing"]
            mrk = x["MRK"]
            sec_low = x["2ND_LOWEST"]
            face_value = x["FACE_VALUE"]
            pricesuggestion = x["pricesuggest"]
            newbprice = sec_low * 1.2
            difference = sec_low - face_value

            if (own == "Y") & (difference > 5) & (mrk == "NO CHANGES"):
                print("MRKUP")
                return newbprice, "MRKUP"
            else:
                return pricesuggestion, mrk

        newdf["floor_value"] = newdf["floor_value"].astype(float)
        newdf["minskyseat"] = newdf["minskyseat"].astype(int)  ##new changes
        newdf["maxskyseat"] = newdf["maxskyseat"].astype(int)
        newdf["Own_listing"] = newdf.apply(lambda x: matchfunction(x), axis=1)
        # to eliminate two Y's in the same section #to code when i see the situation

        sizedf = pd.DataFrame((newdf.groupby("SECTION_NAME").size()))
        sizedf.rename({0: "SIZE"}, inplace=True, axis=1)

        newdf = newdf.merge(sizedf["SIZE"], on="SECTION_NAME")

        newdf["bprice"] = newdf.apply(lambda x: bpricegen(x), axis=1)
        newdf["bprice"] = newdf["bprice"].astype(float)
        newdf["floor_value"] = newdf["floor_value"].astype(float)

        newdf.drop(["row_match", "section_match", "eventid"], axis=1, inplace=True)

        newdf.drop(newdf.loc[newdf["SECTION_NAME"] == "NA"].index, inplace=True)
        meanmindf = newdf.groupby("SECTION_NAME").agg(
            min_fv=("FACE_VALUE", "min"), mean_fv=("FACE_VALUE", "mean")
        )
        newdf = newdf.merge(meanmindf, how="left", on="SECTION_NAME")

        newdf[["pricesuggest", "MRK"]] = newdf.apply(
            lambda x: lowest(x), axis=1, result_type="expand"
        )
        newdf.drop(["min_fv", "mean_fv"], axis=1, inplace=True)

        # to find the Mrkup 2nd lowest price only if there is more than 1 count and if it is nochanges
        newdf["FACE_VALUE"] = newdf["FACE_VALUE"].astype(float)
        secondlowdf = (
            newdf.groupby("SECTION_NAME")["FACE_VALUE"]
            .nsmallest(2)
            .groupby(level="SECTION_NAME")
            .last()
            .rename("2ND_LOWEST")
        )

        newdf = newdf.merge(secondlowdf, on="SECTION_NAME", how="left")

        newdf[["pricesuggest", "MRK"]] = newdf.apply(
            lambda x: markup(x), axis=1, result_type="expand"
        )
        newdf.drop(
            ["row", "section", "SIZE", "bprice", "2ND_LOWEST"], axis=1, inplace=True
        )

        colstokeep = [
            "TOTAL_PRICE",
            "FEES",
            "FACE_VALUE",
            "QTY_LISTED",
            "ROW_NAME",
            "SECTION_NAME",
            "listprice",
            "quantity",
            "floor_value",
            "Own_listing",
            "pricesuggest",
            "MRK",
        ]
        newdf.drop(newdf.columns.difference(colstokeep), axis=1, inplace=True)

        datajson = newdf.to_json(orient="records")
        client.close()
        return datajson

    @app.route("/api/sglistfull", methods=["get"])
    def sglistfull():
        client = MongoClient(
            "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
            % (mongousername, mongopassword)
        )
        today = datetime.today().strftime("%m%d%Y")
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%m%d%Y")

        t = request.args.get("t")
        sdate = request.args.get("sdate")

        team = t  # this is inputs from api calls

        dbname = team + "_SG_Results"
        col = sdate

        db = client.get_database(dbname)
        collection = db[col]
        results = collection.find()
        arr = list(results)

        # if len(arr) == 0:

        #     collection = db[yesterday]
        #     results = collection.find()
        #     arr = list(results)
        #     datescrape = yesterday
        # else:

        #     datescrape = today

        fulldata = []
        for data in arr:
            eid = data["eid"]
            edata = data["data"]
            fulldata.append([eid, edata])

        df = pd.DataFrame(fulldata)
        df["scrapedate"] = sdate
        print(df)
        df.rename(columns={0: "SG_EID", 1: "Data"}, inplace=True)
        dataarr = df.to_json(index=False, orient="table")
        client.close()
        return dataarr

    @app.route("/api/soldinv", methods=["get"])
    def sgsoldinv():
        token = request.headers.get("TOKEN")
        print(token)
        if token == tokenkey:
            client = MongoClient(
                "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
                % (mongousername, mongopassword)
            )
            dbname = "mlb_sold_inventory"
            colname = "mlbsoldinventories"
            db = client[dbname]
            col = db[colname]
            soldmongoresults = col.find_one({})
            data = soldmongoresults["data"]
            df = pd.DataFrame(data)
            datajson = df.to_dict(orient="records")
            client.close()
            return datajson
        else:
            return "Invalid TOKEN"

    @app.route("/api/soldinvsingle/<int:inid>", methods=["get"])
    def sgsoldinvsingle(inid: int):
        token = request.headers.get("TOKEN")
        if token == tokenkey:
            client = MongoClient(
                "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
                % (mongousername, mongopassword)
            )
            dbname = "mlb_sold_inventory"
            colname = "mlbsoldinventories"
            db = client[dbname]
            col = db[colname]
            soldmongoresults = col.find_one({})
            data = soldmongoresults["data"]
            df = pd.DataFrame(data)
            df["filled_date"] = pd.to_datetime(
                df["filled_date"], errors="coerce"
            ).dt.strftime("%m/%d/%Y")
            df["PURCHASE_DATE"] = pd.to_datetime(
                df["PURCHASE_DATE"], errors="coerce"
            ).dt.strftime("%m/%d/%Y")
            df["filled_date"].fillna("NA", inplace=True)
            df["PURCHASE_DATE"].fillna("NA", inplace=True)
            print(df["PURCHASE_DATE"])
            print(df["filled_date"])
            print(df["PURCHASE_DATE"].dtype)
            print(df["filled_date"].dtype)
            print(df.columns)
            dfrow = pd.DataFrame(df[df["invoiceId"] == str(inid)]).reset_index()
            dfrow.replace(True, "True", inplace=True)
            dfrow.replace(False, "False", inplace=True)
            print(dfrow)
            datajson = dfrow.to_dict(orient="records")
            print(datajson)
            client.close()
            return datajson
        else:
            return "Invalid TOKEN"

    @app.route("/api/soldinvupdate/<int:inid>", methods=["PUT"])
    def sgsoldinvupdate(inid: int):
        def getsold():
            dbname = "mlb_sold_inventory"
            colname = "mlbsoldinventories"
            db = client[dbname]
            col = db[colname]
            soldmongoresults = col.find_one({})
            solddf = pd.DataFrame(soldmongoresults["data"])

            return solddf

        def soldupdate(solddict):
            dbname = "mlb_sold_inventory"
            colname = "mlbsoldinventories"
            db = client[dbname]
            col = db[colname]
            soldmongoresults = col.update_many(
                {"dataname": "soldinv"}, {"$set": {"data": solddict}}, upsert=True
            )
            print(soldmongoresults)
            return "Success"

        token = request.headers.get("TOKEN")
        if token == tokenkey:
            date_assigned = datetime.now(pytz.timezone("US/Eastern"))
            client = MongoClient(
                "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
                % (mongousername, mongopassword)
            )
            updated_invoice = json.loads(request.data)
            print(updated_invoice)
            upinvdf = pd.DataFrame(updated_invoice, index=[0])
            # upinvdf['DATE_ASSIGNED'] = datetime.now(pytz.timezone('US/Eastern'))
            upinvdf.replace("True", True, inplace=True)
            upinvdf.replace("False", False, inplace=True)
            solddf = getsold()
            invoiceid = upinvdf["invoiceId"].values.item()
            newpurchasestatus = upinvdf["purchased"].values.item()
            newfilledstatus = upinvdf["filled"].values.item()
            editedby = upinvdf["LastEditedBy"].values.item()
            changedf = solddf.loc[solddf["invoiceId"] == invoiceid]
            print(changedf)

            oldpurchasestatus = changedf["purchased"].values.item()
            oldfilledstatus = changedf["filled"].values.item()
            oldpurchasedate = changedf["PURCHASE_DATE"].values.item()
            oldfilleddate = changedf["filled_date"].values.item()
            oldpurchasedby = changedf["purchased_by"].values.item()
            oldfilledby = changedf["filledBy"].values.item()
            print("invoiceid ", invoiceid)
            print("oldfilleddate", oldfilleddate)
            print("oldfilleddate - dtype ", type(oldfilleddate))
            print("oldpurchasedate", oldpurchasedate)
            print("oldpurchasedate - dtype ", type(oldpurchasedate))
            # check if purchase status changed
            if newpurchasestatus == oldpurchasestatus:
                print("SAME purchase status")
                # no changes to purchased date
                if oldpurchasestatus == False:
                    pdate = "NA"
                    pby = "NA"
                else:
                    pdate = str(oldpurchasedate)
                    pby = oldpurchasedby
            else:
                if newpurchasestatus == False:
                    print("New p status is false clear previous")
                    # remove the date
                    pdate = "NA"
                    pby = "NA"

                else:
                    print("New p status is true update")
                    pdate = date_assigned
                    pby = editedby

            if newfilledstatus == oldfilledstatus:
                print("SAME filled status")
                # no changes to filled date
                if oldfilledstatus == False:
                    fdate = "NA"
                    fby = "NA"
                else:
                    fdate = str(oldfilleddate)
                    fby = oldfilledby
            else:
                if newfilledstatus == False:
                    print("New f status is false clear previous")
                    fdate = "NA"
                    fby = "NA"
                else:
                    print("New f status is true update")
                    fdate = date_assigned
                    fby = editedby

            upinvdf["PURCHASE_DATE"] = pdate
            upinvdf["filled_date"] = fdate
            upinvdf["purchased_by"] = pby
            upinvdf["filledBy"] = fby
            print(upinvdf["PURCHASE_DATE"])
            print(upinvdf["filled_date"])
            print(upinvdf["purchased_by"])
            print(upinvdf["filledBy"])

            solddf.set_index("invoiceId", inplace=True)
            upinvdf.set_index("invoiceId", inplace=True)
            solddf.update(upinvdf)
            solddf.reset_index(inplace=True)
            print(solddf.loc[solddf["invoiceId"] == updated_invoice["invoiceId"]])
            solddict = solddf.to_dict(orient="records")
            updateinvoice = soldupdate(solddict)

            client.close()
            return "1"
        else:
            return "Invalid TOKEN"

    @app.route("/api/mlbpinvslackalert/<int:inid>", methods=["post"])
    def slackalert(inid: int):
        token = request.headers.get("TOKEN")
        if token == tokenkey:
            print(inid)
            webhook = "https://hooks.slack.com/services/fefew/fewfew/fewfewfwe"
            payload = payloadconstructor(inid)
            createprequest = send_slack_message(payload, webhook)
            print(createprequest)
            return "1"
        else:
            return "Invalid TOKEN"

    # @app.route('/api/filtersoldinv/<str:key>/<str:val>',methods=['get'])
    # def filtersoldinv(key: str,val: str):
    #     print(key)
    #     print(val)
    #     return "1"
    # @app.route('/api/slackinteractmlb',methods=['post'])
    # def slackinteraction():
    #     slackpayload = json.loads(request.form.get("payload"))
    #     print(slackpayload)
    #     action_value = slackpayload["actions"][0].get("value")
    #     print(action_value)
    #     return "1"
    @app.route("/api/tmcounts", methods=["get"])
    def trtmlbcounts():
        client = MongoClient(
            "mongodb+srv://%s:%s@blabla.qjokq.mongodb.net/?retryWrites=true&w=majority"
            % (mongousername, mongopassword)
        )

        def dropcheck(x):
            if x == 0:
                return "N"
            elif x > 0:
                return "Decrease"
            elif x < 0:
                return "Drop"
            else:
                return "Error"

        def dynamic(x):
            minprice = x["mindynamic"]
            maxprice = x["maxdynamic"]
            if (minprice == 0) & (maxprice == 0):
                return "N"
            elif (minprice > 0) & (maxprice > 0):
                return "Y"
            elif (minprice > 0) | (maxprice > 0):
                return "Y"
            elif (minprice < 0) | (maxprice < 0):
                return "Decrease"
            else:
                return "Error"

        def unbroadcast(x):
            maxcap = x["Max"]
            count = x["sumcount_x"]
            if maxcap != "NA":
                threshold = int(maxcap) * 0.1
                if count <= threshold:
                    return "Unbroadcast"
                else:
                    return "NA"

            else:
                return "NA"

        def fpinternal(x):
            minprice = x["minprice_x"]
            unbroadcast = x["Unbroadcast"]
            fees = x["fees"]
            intnoteval = round(((minprice + fees) * 1.2), 2)
            intnotestr = "FP:%s +vivid" % (intnoteval)
            if unbroadcast != "Unbroadcast":
                return intnotestr
            else:
                return "NA"

        def bginternal(x):
            minprice = x["minprice_x"]
            unbroadcast = x["Unbroadcast"]
            sh = x["SH"]
            fees = x["fees"]
            intnoteval = round(((minprice + fees) * 1.2), 2)
            if sh == "Y":
                intnotestr = (
                    "BG:%s -vivid -ticketevolution -tickpick -ticketnetwork -ticketmaster"
                    % (intnoteval)
                )
            else:
                intnotestr = (
                    "BG:%s -vivid -ticketevolution -tickpick -ticketnetwork -stubhub -gametime -ticketmaster"
                    % (intnoteval)
                )
            if unbroadcast != "Unbroadcast":
                return intnotestr
            else:
                return "NA"

        feesarr = [["Braves", 8], ["Blue Jays", 10], ["Mariners", 8]]

        today = datetime.today().strftime("%Y-%m-%d")
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        print(today)
        print(yesterday)
        tmid = "0F005D6BD2C14EB8"
        url = "https://api.blabla.com/trt.php?token=blabla&tmid=%s" % (tmid)
        response = requests.get(url)
        jsonresponse = response.json()
        hometeam = jsonresponse["data"][len(jsonresponse["data"]) - 1]["eventartist"]

        countdf = pd.DataFrame(jsonresponse["section_data"])
        todaydf = countdf.loc[
            (
                (countdf["dayt"] == today)
                & (countdf["inventoryType"] == "primary")
                & (countdf["offerType"] == "standard")
            )
        ]
        yesterdaydf = countdf.loc[
            (
                (countdf["dayt"] == yesterday)
                & (countdf["inventoryType"] == "primary")
                & (countdf["offerType"] == "standard")
            )
        ]

        todaydf["count"] = todaydf["count"].astype(int)
        todaydf["min"] = todaydf["min"].astype(int)
        todaydf["max"] = todaydf["max"].astype(int)
        yesterdaydf["count"] = yesterdaydf["count"].astype(int)
        yesterdaydf["min"] = yesterdaydf["min"].astype(int)
        yesterdaydf["max"] = yesterdaydf["max"].astype(int)

        todaysumdf = todaydf.groupby("section").agg(
            sumcount=("count", "sum"), minprice=("min", "min"), maxprice=("max", "max")
        )
        todaydf = todaydf.merge(todaysumdf, how="left", on="section")
        yesterdaysumdf = yesterdaydf.groupby("section").agg(
            sumcount=("count", "sum"), minprice=("min", "min"), maxprice=("max", "max")
        )
        yesterdaydf = yesterdaydf.merge(yesterdaysumdf, how="left", on="section")
        todaydf.drop_duplicates(subset=["section"], keep="first", inplace=True)
        yesterdaydf.drop_duplicates(subset=["section"], keep="first", inplace=True)
        yesterdaydf.reset_index(inplace=True, drop=True)
        todaydf.reset_index(inplace=True, drop=True)

        # get new section Drops
        seccolstokeep = ["section"]
        todaysecdf = todaydf.drop(todaydf.columns.difference(seccolstokeep), axis=1)

        yesterdaysecdf = yesterdaydf.drop(
            yesterdaydf.columns.difference(seccolstokeep), axis=1
        )

        comparedsec = pd.concat([todaysecdf, yesterdaysecdf]).drop_duplicates(
            keep=False
        )

        dropsectionarr = comparedsec.values.tolist()

        if len(todaydf) > len(yesterdaydf):
            if len(dropsectionarr) >= 1:
                print("There is a new section drop: ", dropsectionarr)

        else:
            print("No New Drop")

        # counts Drop or difference:

        countsdropdf = pd.merge(
            left=todaydf,
            right=yesterdaydf[["section", "sumcount", "minprice", "maxprice"]],
            left_on=["section"],
            right_on=["section"],
            how="inner",
        )

        countsdropdf.replace("", 0, inplace=True)
        colstonumberic = countsdropdf.columns.drop(
            ["currency", "inventoryType", "offerType", "dayt", "tmid", "section"]
        )
        countsdropdf[colstonumberic] = countsdropdf[colstonumberic].apply(pd.to_numeric)

        countsdropdf["countdiff"] = (
            countsdropdf["sumcount_y"] - countsdropdf["sumcount_x"]
        )
        countsdropdf["mindynamic"] = (
            countsdropdf["minprice_x"] - countsdropdf["minprice_y"]
        )
        countsdropdf["maxdynamic"] = (
            countsdropdf["maxprice_x"] - countsdropdf["maxprice_y"]
        )
        # countsdropdf['diff'] = countsdropdf.apply(lambda x: x['sumcount_y'])
        countsdropdf["drops"] = countsdropdf["countdiff"].apply(lambda x: dropcheck(x))
        countsdropdf["dynamic"] = countsdropdf[["mindynamic", "maxdynamic"]].apply(
            lambda x: dynamic(x), axis=1
        )

        hometeam = str(hometeam).split(" ")[len(str(hometeam).split(" ")) - 1]
        for arr in feesarr:
            if hometeam in arr:
                fees = arr[1]
                print(fees)
        csvname = hometeam + " Max Cap.csv"
        maxcapdf = pd.read_csv(csvname)

        finaldf = countsdropdf.merge(
            maxcapdf, left_on="section", right_on="Section", how="left"
        )

        finaldf["SH"].fillna("NA", inplace=True)
        finaldf["Max"].fillna("NA", inplace=True)
        finaldf["fees"] = fees
        finaldf["Unbroadcast"] = finaldf[["Max", "sumcount_x"]].apply(
            lambda x: unbroadcast(x), axis=1
        )
        finaldf["unbroad_date"] = finaldf["Unbroadcast"].apply(
            lambda x: today if x == "Unbroadcast" else "NA"
        )

        finaldf["FP_innotes"] = finaldf[["minprice_x", "Unbroadcast", "fees"]].apply(
            lambda x: fpinternal(x), axis=1
        )
        finaldf["BG_innotes"] = finaldf[
            ["minprice_x", "Unbroadcast", "fees", "SH"]
        ].apply(lambda x: bginternal(x), axis=1)
        colstokeep = [
            "section",
            "sumcount_x",
            "minprice_x",
            "maxprice_x",
            "countdiff",
            "mindynamic",
            "maxdynamic",
            "drops",
            "dynamic",
            "Max",
            "Unbroadcast",
            "FP_innotes",
            "BG_innotes",
            "unbroad_date",
        ]
        finaldf.drop(finaldf.columns.difference(colstokeep), axis=1, inplace=True)

        client.close()
        print(finaldf)

    return app


app1 = create_app()

if __name__ == "__main__":
    app1.run()
