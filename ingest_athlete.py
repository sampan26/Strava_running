import requests
from sql_methods import read_db, write_db_replace


client_id = '40695'

def get_athlete(bearer_token):
    url = 'https://www.strava.com/api/v3/athlete'
    data = ''
    headers = {"Authorization": "Bearer " + bearer_token}
    response = requests.get(url, data=data, headers=headers)
    athlete_data = response.json()

    try:
        athlete_id = athlete_data['id']
        print(str(athlete_id))
    except Exception:
        print ("Error requesting athlete data from Strava")
        return 1
    
    return athlete_data

def get_athlete_data_status(athlete_id):

    import pandas as pd
    
    processing_status = read_db('processing_status')
    
    if str(athlete_id) in processing_status["athlete_id"].values:        
        ingest_status = processing_status[processing_status["athlete_id"] == str(athlete_id)]["status"].values[0]
        return ingest_status
    
    return "to process"

def queue_athlete_for_processing(athlete_id, bearer_token, refresh_token):

    import pandas as pd  
      
    processing_status = read_db('processing_status')
    processing_status = processing_status.append({'athlete_id': athlete_id,
                                                  'status': 'none',
                                                  'bearer_token': bearer_token,
                                                  'refresh_token': refresh_token}, ignore_index = True)
    write_db_replace(processing_status, 'processing_status')           
    
    return "none"