#-*- coding:utf-8 -*-
import network
import datetime
import teamdao
import json
import logging
import teams
import time

def _handle_standing(obj, season):
    fields = {}
    for idx, header in enumerate(obj["headers"]):
        fields[header] = idx

    for team_obj in obj["rowSet"]:
        team_id = team_obj[fields["TEAM_ID"]]
        team = teamdao.getByTeamId(team_id)
        if not team or time.time() - team["update_time"] > 86400 * 30:
            logging.info("new team found, try to crawl")
            teams.crawl(team_id, season)
    
def crawl(time, season):
    resp = network.req("GET", "http://stats.nba.com/stats/scoreboard?DayOffset=0&LeagueID=00&gameDate=%s" % time.strftime("%m/%d/%Y"))
    obj = json.loads(resp.content)

    for result in obj["resultSets"]:
        if result["name"] == "EastConfStandingsByDay":
            _handle_standing(result, season)
        if result["name"] == "WestConfStandingsByDay":
            _handle_standing(result, season)
    
