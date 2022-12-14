import requests
from datetime import datetime
import dateutil.parser
from credentials import keys

# Search (departures, one way) https://rapidapi.com/tipsters/api/priceline-com-provider
class ApiPassagem:
    def get_passagem(data, passageiros, aero_origem, aero_destino):
        TOKEN = keys.get('token')
        url = "https://priceline-com-provider.p.rapidapi.com/v2/flight/departures"
        querystring = {
            "sid": "iSiX639",
            "departure_date": data,
            "adults": passageiros,
            "convert_currency": "BRL",
            "origin_airport_code": aero_origem,
            "destination_airport_code": aero_destino
        }
        headers = {
            "X-RapidAPI-Key": TOKEN,
            "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        response = response.json()
        response = response['getAirFlightDepartures']['results']['result']['itinerary_data']
        lista_voo = []

        for i in response:
            voo = {
                "preco": response[i]['price_details']['display_total_fare_per_ticket'],
                "duracao": response[i]['slice_data']['slice_0']['info']['duration'],
                "qtde_conn": response[i]['slice_data']['slice_0']['info']['connection_count'],
                "empresa": response[i]['slice_data']['slice_0']['airline']['name'],
                "data_partida": response[i]['slice_data']['slice_0']['departure']['datetime']['date_time'],
                "data_chegada": response[i]['slice_data']['slice_0']['arrival']['datetime']['date_time']
            }
            
            voo['duracao'] = datetime.strptime(voo['duracao'], '%H:%M:%S').time()
            voo['data_partida'] = dateutil.parser.parse(voo['data_partida'])
            voo['data_chegada'] = dateutil.parser.parse(voo['data_chegada'])
            lista_voo.append(voo)
            
        return lista_voo

# get_passagem('2022-10-16', 2, 'GRU', 'GIG')