from bs4 import BeautifulSoup
import requests
import re

class Requests_Matches:
    
    def __init__(self, id):
        """
        URL REQUESTS
        """
        self.url = f"https://www.vlr.gg/{id}"
        self.response = requests.get(self.url)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')
    def get_tournament_and_round(self):
        divs = self.soup.find_all("div")
        imgs = self.soup.find_all('img')
        round_tournament = self.soup.find("div", class_="match-header-event-series").text.strip()
        round_tournament = round_tournament.replace('\n', '').replace('\t', '')
        img_src = ""
        # Duyệt qua tất cả thẻ img
        for img in imgs:
            if img.get('style') == "height: 32px; width: 32px; margin-right: 6px;":
                img_src = img['src']
        tournament = ""
        for div in divs:
            if div.get('style') == "font-weight: 700;":
                tournament = div.text.strip()
        return {
            "data":{
                "status": 200,
                "segment": [
                    {
                        "tournament": tournament,
                        "tour_ico": img_src,
                        "round_tournament": round_tournament
                    }
                    ]
                }
        }
                
    def get_result(self):
        lived = self.soup.find_all("span","match-header-vs-note mod-live")
        upcoming__ = self.soup.find_all("span", "match-header-vs-note mod-upcoming")
        
        team_elements = self.soup.find_all('div', class_='wf-title-med')
        teams = [element.text.strip() for element in team_elements]
        # Kiem tra neu tran dau dang dien ra
        if len(lived) != 0 and len(upcoming__) == 0:
            div = self.soup.find('div', {'class': 'js-spoiler'})
            spans = div.find_all('span')
            values = [span.text.strip() for span in spans if span.text.strip().isdigit()]

            self.res_ = {
                "data":{
                "status": 200,
                "segment": [
                    {
                        "team1_name": teams[0],
                        "team2_name": teams[1],
                        "score" : values,
                        "game_status":"LIVE",
                        "time" :0
                    }
                    ]
                }
            }
        elif len(lived) == 0 and len(upcoming__) != 0:
            
            self.res_ = {
                "data":{
                "status": 200,
                "segment": [
                    {
                        "team1_name": teams[0],
                        "team2_name": teams[1],
                        "score" : ["",""],
                        "game_status":"UPCOMING",
                        "time" : upcoming__[0].text.strip()
                    }
                    ]
                }
            }
            return self.res_
            
        else:
            all_matches = self.soup.find_all(class_=["match-header-vs-score-loser", "match-header-vs-score-winner"])
            class_list = [int(match.text.strip()) for match in all_matches]
            self.res_ = {
                "data":{
                "status": 200,
                "segment": [
                    {
                        "team1_name": teams[0],
                        "team2_name": teams[1],
                        "score" : class_list,
                        "game_status":"FINISHED",
                        "time" :0
                    }
                    ]
                }
            }
        
        return self.res_
        
    def get_team_abbr(self):
        element = self.soup.find(class_='match-header-link wf-link-hover mod-1')
        href_1 = element.get('href')
        
        element_2 = self.soup.find(class_='match-header-link wf-link-hover mod-2')
        href_2 = element_2.get('href')
        
        
        response_2 = requests.get("https://www.vlr.gg{}".format(href_1))
        soup_2 = BeautifulSoup(response_2.text, 'html.parser')
        team_abbr_1 = soup_2.find("h2",class_ ="wf-title team-header-tag")
        if team_abbr_1 == None:
            team_abbr_1 = soup_2.find("h1",class_ ="wf-title")
            
        response_3 = requests.get("https://www.vlr.gg{}".format(href_2))
        soup_3 = BeautifulSoup(response_3.text, 'html.parser')
        team_abbr_2 = soup_3.find("h2",class_ ="wf-title team-header-tag")
        
        if team_abbr_2 == None:
            team_abbr_2 = soup_3.find("h1",class_ ="wf-title")
        return [team_abbr_1.text,team_abbr_2.text]
    def get_veto(self, map_pool):
        try:
            veto_maps = [i.text.strip() for i in self.soup.find_all('div', class_='match-header-note')]
            best_of = [i.text.strip() for i in self.soup.find_all("div", "match-header-vs-note")]
            if len(veto_maps) > 1:
                tmp = veto_maps[1]
            else:
                tmp = veto_maps[0]
            pos = tmp.find(" ")
            first_veto_team = tmp[0:pos]
            names = map_pool
            matches = re.findall('|'.join(names), str(tmp))
            print(matches)
            return {
                "data":{
                "status": 200,
                "segment":[
                    {
                        "start_veto": first_veto_team,
                        "veto": matches,
                        "best_of": int(best_of[1][2])
                    }
                ]
            }
                
            }
        except:
            return {
            "data":{
                "status": 404
            }
        }
    def get_map_score(self):
        
        try: 
            url = self.url
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            elements = soup.find_all('div', class_='score')
            scores = [int(element.text.strip()) for element in elements]
            t1_score = []
            t2_score = []
            for i in range(len(scores)):
                if i % 2== 0:
                    t1_score.append(scores[i])
                else:
                    t2_score.append(scores[i])
                
            return {
                "data":{
                "status": 200,
                "segment": [
                    {
                    "map_scores": {
                    "team_1": t1_score,
                    "team_2": t2_score
                    }
                    }
                ]
            }
                
                
            }
        except:
            return {
            "data":{
                "status": 404
            }
        }
    def get_note(self):
        try:
            notes_ = [i.text.strip() for i in self.soup.find_all('div', class_='match-header-note')]
            
            if len(notes_) > 1:
                return {
                    "response": 202,
                    "note_message": notes_[0]
                }
            else:
                return {
                    "response": 202,
                    "note_message": ""
                }
        except:
            return {
            "data":{
                "status": 404
            }
        }
            
if __name__ == "__main__":
    id_match = 51296
    matches = Requests_Matches(id_match)

    res = matches.get_result()
    map_pool = matches.get_veto(("Ascent","Bind","Breeze","Icebox","Lotus","Split","Sunset","Haven","Fracture","Pearl"))
    map_score = matches.get_map_score()
    abbr = matches.get_team_abbr()
    print(res)
    print(matches.get_tournament_and_round())
    print(map_pool)
    print(map_score)
    print(abbr)
