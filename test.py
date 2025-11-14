import requests


city = "Ошибка"
res = requests.get('http://api.openweathermap.org/data/2.5/forecast', params={'q': f'{city}', 'type': 'like', 'units': 'metric', 'APPID': '2b845cde2521735273dfaba14ada0b8f'})
data = res.json()
if data['cod'] != 200:
    print('Error')
    return
date = "00-00-00"
day = -1
for i in data['list']:
    if i['dt_txt'][:10] != date:
        day += 1
        print(i['dt_txt'] ,i['main']['temp'], i['weather'][0]['description'])
        if "snow" in i['weather'][0]['description']:
            print(f"Snow will fall in {day} days")
            break
        date = i['dt_txt'][:10]
if day < 0:
    print("So far, there is no snow")   





