import requests
from credentials import keys

#AIRPORTS/SEARCH https://rapidapi.com/apidojo/api/travel-advisor
class ApiCidade:
    def get_location(cidade):
        TOKEN = keys.get('token')
        url = "https://travel-advisor.p.rapidapi.com/airports/search"
        querystring = {
            "query": cidade,
            "locale": "pt_BR"
        }
        headers = {
            "X-RapidAPI-Key": TOKEN,
            "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        response = response.json()
        
        i = 0
        while response[i]['country_code'] != "BR" or 'Airports' in response[i]['name'] or 'Aeroportos' in response[i]['name']:
            i += 1

        _dict = {
            "nome_cidade" : response[i]['city_name'],
            "estado": response[i]['state'],
            "location_id" : response[i]['location_id'],
            "aero_code" : response[i]['code'],
            "aero_nome": response[i]['name']
        }
        
        return _dict

# get_location('Belo Horizonte')