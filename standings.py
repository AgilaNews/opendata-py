#-*- coding:utf-8 -*-
import network
import datetime
import teamdao
import seasondao
import standingdao
import matchdao
import json
import logging
import teams
import time
tz_off = time.timezone
et_off = 5 * 3600

def _check_team(team_id, season):
    team = teamdao.getByTeamId(team_id)
    if not team or time.time() - team["update_time"] > 86400 * 30:
        logging.info("new team found, try to crawl")
        return teams.crawl(team_id, season.season_description)
    return True

def _handle_standing(obj, conference):
    fields = {}
    season = None
    
    for idx, header in enumerate(obj["headers"]):
        fields[header] = idx

    for idx, team_obj in enumerate(obj["rowSet"]):
        team_id = team_obj[fields["TEAM_ID"]]
        season_year = team_obj[fields["SEASON_ID"]][-4:]
        if not season or season_year != season.year:
            season = seasondao.getByYear(season_year)
            if not season:
                logging.warn("not found season %s" % season_year)
                return
            
        if not _check_team(team_id, season):
            logging.warn("unknown standing team :%s" % team_id)
            continue
        
        values = {
            "win": team_obj[fields["W"]],
            "lost": team_obj[fields["L"]],
            "rank": idx + 1,
            "team_id": team_id,
            "season_year": season_year,
            "update_time": time.time(),
            "conference": conference,
        }
        
        standingdao.save(values)

def _handle_matches(obj):
    fields= {} 
    for idx, header in enumerate(obj["headers"]):
        fields[header] = idx

    for match in obj["rowSet"]:
        home_team_id = match[fields["HOME_TEAM_ID"]]
        visitor_team_id = match[fields["VISITOR_TEAM_ID"]]
        year = match[fields["SEASON"]]
        status = match[fields["GAME_STATUS_ID"]]
        game_id = match[fields["GAME_ID"]]

        if status == 1:
            d = datetime.datetime.strptime(match[fields["GAME_DATE_EST"]], "%Y-%m-%dT%H:%M:%S")
            t = datetime.datetime.strptime(match[fields["GAME_STATUS_TEXT"]], "%I:%M %p ET")
            f = time.mktime(datetime.datetime.combine(d.date(), t.time()).timetuple())
            f = f - et_off + tz_off   
        
        season = seasondao.getByYear(year)
        if not season:
            logging.info("unkown season year %s" % year)
            continue
        if not _check_team(home_team_id, season):
            logging.warn("unknown home team %s" % home_team_id)
            continue
        if not _check_team(visitor_team_id, season):
            logging.warn("unknown visitor team %s" % visitor_team_id)
            continue

        values = {
            "game_id": game_id,
            "time": f,
            "home_team_id": home_team_id,
            "visitor_team_id": visitor_team_id,
            "status": status,
            "season_year": season.year,
            "update_time": time.time(),
        }

        match = matchdao.getByGameId(game_id)
        if match:
            matchdao.save(values, game_id)
        else:
            matchdao.save(values)

        logging.info("updated match info: %s" % game_id)
            

def _handle_scores(obj):
    fields = {}
    
    for idx, header in enumerate(obj["headers"]):
        fields[header] = idx

    for game in obj["rowSet"]:
        game_id = game[fields["GAME_ID"]]
        pts = game[fields["PTS"]]
        team_id = game[fields["TEAM_ID"]]
        
        match = matchdao.getByGameId(game_id)
        if not match:
            logging.warn("error get game id %s" % game_id)
            continue

        values = {}
        
        if team_id == match.home_team_id:
            values["home_team_points"] = pts
        elif team_id == match.visitor_team_id:
            value["visitor_team_points"] = pts
        else:
            logging.warn("unknown team points: %s" % team_id)
            continue

        matchdao.save(values, game_id)
        logging.info("updated scores of %s" % game_id)
    
def crawl(time):
    url = "http://stats.nba.com/stats/scoreboard?DayOffset=0&LeagueID=00&gameDate=%s" % time.strftime("%m/%d/%Y")
    resp = network.req("GET", url)
    if resp.status_code != 200:
        logging.warn("get resp error: %s" % resp.status_code)
        return

    obj = json.loads(resp.content)
    for result in obj["resultSets"]:
        if result["name"] == "EastConfStandingsByDay":
            _handle_standing(result, "east")
        if result["name"] == "WestConfStandingsByDay":
            _handle_standing(result, "west")
        if result["name"] == "GameHeader":
            _handle_matches(result)
        if result["name"] == "LineScore":
            _handle_scores(result)
