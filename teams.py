#-*-coding:utf-8-*-
import json
import teamdao
import network
import logging
import env
from wand.image import Image
from img.imagesaver import ImageSaver

def _get_team_logo(abbr):
    resp = network.req("GET",
                "http://stats.nba.com/media/img/teams/logos/%s_logo.svg" % (abbr))

    with Image(blob = resp.content, format="svg") as image:
        with image.convert('png') as png:
            if env.saver.save_stream(png.make_blob(), "nba", abbr + ".png", "image/png"):
                return env.conf["cdn"] + "/nba/%s.png" % (abbr)

def _parse_team_common_info(obj):
    field = {}
    for idx, header in enumerate(obj["headers"]):
        field[header] = idx

    if len(obj["rowSet"]) == 0:
        return False
    rows = obj["rowSet"][0]
    team_id = rows[field["TEAM_ID"]]
    team = teamdao.getByTeamId(team_id)
    if not team:
        teamdao.save({"team_id": team_id})
        logging.info("saved new team %s" % team_id)

    values = {}
    values["city"] = rows[field["TEAM_CITY"]]
    values["name"] = rows[field["TEAM_NAME"]]
    values["abbr"] = rows[field["TEAM_ABBREVIATION"]]
    values["conference"] = rows[field["TEAM_CONFERENCE"]]
    values["division"] = rows[field["TEAM_DIVISION"]]
    values["code"] = rows[field["TEAM_CODE"]]
    values["logo"] = _get_team_logo(values["abbr"])
    
    return teamdao.save(values, team_id)
    
def crawl(team_id, season):
    url = "http://stats.nba.com/stats/teaminfocommon?LeagueID=00&SeasonType=Regular+Season&TeamID=%s&season=%s" % (team_id, season)
    resp = network.req("GET", url)
    obj = json.loads(resp.content)
    
    for result in obj["resultSets"]:
        if result["name"] == "TeamInfoCommon":
            if not _parse_team_common_info(result):
                logging.warn("unknown team [%s]: [%s]" % (url, team_id))
                return False
