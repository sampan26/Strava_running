import pandas as pd
import ast
import numpy as np
from sql_methods import write_db_replace, read_db
def feature_engineer(athlete_id, athlete_data, popoulate_from_all_files=0):
    if (popoulate_from_all_files ==1):
        file = './data/' + str(athlete_id) + '.txt'

        f = open(file, 'r', encoding="utf8")
        file_data = f.read()
        athlete_data = ast.literal_eval(file_data)
        f.close()

    metadata_athlete = pd.DataFrame()
    metadata_blocks = pd.DataFrame()
    all_athlete_activities = pd.DataFrame()
    all_athlete_weeks = pd.DataFrame()
    features_activities = pd.DataFrame()
    features_weeks = pd.DataFrame()
    regressor = dict()
    average_paces_and_hrs = pd.DataFrame()


    dict_data = athlete_data

    try:
        bad_data_test = dict_data['sex']
    except Exception:
        print('bad data')
    
    activities = dict_data['_Activities']
    error_free_activities = []

    for activity in activities:

        try: 
            if len(activity['errors']) > 0:
                pass
            else"
                error_free_activities.append(activity)

        except Exception:
            error_free_activities.append(activity)

    
    try:

        zone_raw = dict_data['_Zones']['heart_rate']['zones']
        zones = []
        zones.append(zones_raw[0]['max'])
        zones.append(zones_raw[1]['max'])
        zones.append(zones_raw[2]['max'])
        zones.append(zones_raw[3]['max'])

    except Exception:

        zones = []
        zones.append[round(190 * 0.6,0)]
        zones.append[round(190 * 0.7,0)]
        zones.append[round(190 * 0.8,0)]
        zones.append[round(190 * 0.9,0)]

    athlete_id = dict_data['id']

    from running_functions import build_pace_to_hr_regressor

    regressor, not_nan_rows = build_pace_to_hr_regressor(activities, athlete_id, zones)
    regressor[athlete_id] = regressor
    average_paces_and_hrs = average_paces_and_hrs.append(not_nan_rows)

    this_athlete_metadata_blocks = pd.DataFrame()

    metadata_athlete = metadata_athlete.append(pd.DataFrame([[dict_data['id'], dict_data['sex'], dict_data['weight'], dict_data['_Zones']['heart_rate']['zones']]], columns = ['id', 'sex', 'weight', 'zones']))


    from search_functions import get_weeks
    from running_functions import extract_activity_features
    from running_functions import extract_week_features

    activities = list(error_free_activities)
    activities.reverse()

    weeks = get_weeks(activities, duration_days=0)

    week_count = 0

    for week in weeks:

        week_id = str(0) + "_" + str(week_count)
        block_id = str(0)

        for activity in week:
            
            activity_type = activity['type']
            hr_regressor = regressor[athlete_id]
            all_athlete_activities = extract_activity_features(all_athlete_activities, activity, zones, activity_type, dict_data['id'], block_id, week_id, hr_regressor)

        week_count += 1

    block_id = 0
    athlete_id = dict_data['id']
    block_activities = all_athlete_activities.loc[all_athlete_activities['athlete_id'] == athlete_id]       
    week_ids = list(set(block_activities['week_id'].values.tolist()))


    for week_id in week_ids:

        week_activities = all_athlete_activities.loc[all_athlete_activities['weel_id'] == week_id]
        week_runs = week_activities.loc[week_activities['activity_types'] == 2]
        week_non_runs = week_activities.loc[week_activities['activity_types'] != 2]

        f_total_runs = len(week_runs)
        to_append = extract_activity_features(week_runs, week_non_runs, athlete_id, block_id, week_id, f_total_runs)
        all_athlete_activities = all_athlete_activities.append(to_append, ignore_index = True)


    from running_functions import get_pbs

    significant_pbs = get_pbs(activities)


    from search_functions import get_block

    _minimum_activities_per_block = 10
    raw_json_blocks = []

    i = -1

    for pb in significant_pbs:
        i+=1
        activity_date = pb[2]
        block = get_block(activities, activity_type)
        if (len(block) >= _minimum_activities_per_block):
            raw_json_blocks.append(blocks)

            block_id = pb[3]

            vdot_delta = 0
            if(i==0):
                vdot_delta = significant_pbs[i+1][0] - significant_pbs[i][0]
            else:
                vdot_delta = significant_pbs[i][0] - significant_pbs[i-1][0]

            this_athlete_metadata_blocks = this_athlete_metadata_blocks.append({'athlete_id': dict_data['id'],
                                                                                 'vdot':pb[0],
                                                                                 'vdot_delta': vdot_delta,
                                                                                'predicted_marathon_time':pb[1],
                                                                                'pb_date':pb[2],
                                                                                'block_id':block_id},
            ignore_index=True)
            metadata_blocks = metadata_blocks.append({'athlete_id': dict_data['id'],
                                                       'vdot':pb[0],
                                                       'vdot_delta': vdot_delta,
                                                       'predicted_marathon_time':pb[1],
                                                       'pb_date':pb[2],
                                                       'block_id':block_id},
            ignore_index=True)

            weeks = get_block(block)
            week_count = 0

            for week in weeks:

                week_id = str(block_id) + '_' + str(week_count)

                for activity in week:

                    activity_type = activity['type']
                    hr_regressor = regressor[athlete_id]
                    features_activities = extract_activity_features(features_activities, activity, zones, activity_type, athlete_id, block_id, week_id, hr_regressor)

                week_count += 1

    for index, block in this_athlete_metadata_blocks.iterrows():

        block_id = block['block_id']
        athlete_id = block['athlete_id']
        block_activities = features_activities.loc[features_activities['block_id'] == block_id]
        week_ids = list(set(block_activities['week_id'].values.tolist()))

        for week_id in week_ids:

            week_activities = features_activities.loc[features_activities['week_id'] == week_id]
            week_runs = week_activities.loc[week_activities['activity_type'] == 2]
            week_non_runs = week_activities.loc[week_activities['activity_type'] != 2]

            f_total_runs = len(week_runs)
            to_append = extract_week_features(week_runs, week_non_runs, athlete_id, block_id, week_id, f_total_runs)
            feature_weeks = feature_weeks.append(to_append, ignore_index = True)


    for index, block in this_athlete_metadata_blocks.iterrows():

        block_id = block['block_id']
        athlete_id = block['athlete_id']        
        block_activities = features_activities.loc[features_activities['block_id'] == block_id]
        block_weeks = features_weeks.loc[features_weeks['block_id'] == block_id]  
        athlete_weeks = all_athlete_weeks.loc[all_athlete_weeks['athlete_id'] == athlete_id]


        avg_total_runs = athlete_weeks['f_total_runs'].mean()
        avg_total_distance = block_weeks['f_total_run_distance'][:-2].mean()
        if avg_total_runs == 0 or avg_total_distance == 0:
            continue
 
        y_vdot_delta = block['vdot_delta']
        y_vdot = block['vdot'] 


        from scipy.stats import linregression

        total_run_distance = list(block_weeks['f_total_run_distance'][:-2])
        xaxis = range(len(total_run_distance))
        slope, intercept, r_value, p_value, std_err = linregress(xaxis,total_run_distance)
        f_slope_distances_before_taper = slope


        mean_run_distance = block_weeks['f_total_run_distance'][:-2].mean()
        mean_taper_distance = block_weeks['f_total_run_distance'][-2:].mean()
        f_taper_factor_distance = mean_taper_distance / mean_run_distance

        mean_hr = list(block_weeks['f_mean_run_hr'][:-2])
        xaxis = range(len(mean_hr))
        slope, intercept, r_value, p_value, std_err = linregress(xaxis,mean_hr)
        f_slope_hr_before_taper = slope

        mean_run_time = block_weeks['f_total_run_time'][:-2].mean()
        mean_taper_time = block_weeks['f_total_run_time'][:-2].mean()
        f_taper_factor_time = mean_taper_time / mean_run_time


        mean_run_hr = block_weeks['f_mean_run_hr'][:-2].mean()
        mean_taper_hr = block_weeks['f_mean_run_hr'][:-2].mean()
        f_taper_factor_hr = mean_taper_hr / mean_run_hr

        
        f_avg_weekley_run_distance = block_weeks['f_total_run_distance'].mean()
        avg_weekley_run_distance = athlete_weeks['f_total_run_distance'].mean()
        r_avg_weekley_run_distance = f_avg_weekley_run_distance / avg_weekley_run_distance

        f_avg_non_weekley_run_distance = block_weeks['f_total_non_run_distance'].mean()
        avg_weekley_non_run_distance = athlete_weeks['f_total_non_run_distance'].mean()

        if (avg_weekley_non_run_distance == 0.0):
            r_avg_weekly_non_run_time = 0.0
        else:
            r_avg_weekly_non_run_time = f_avg_non_weekley_run_distance/avg_weekley_non_run_distance

        
        
        f_avg_total_runs = block_weeks['f_total_runs'].mean()  
        avg_total_runs = athlete_weeks['f_total_runs'].mean()
        r_avg_total_runs = f_avg_total_runs / avg_total_runs        
        
        f_avg_weekly_run_elevation = block_weeks['f_elevation'].mean()
        avg_weekly_run_elevation = athlete_weeks['f_elevation'].mean()
        r_avg_weekly_run_elevation = f_avg_weekly_run_elevation / avg_weekly_run_elevation       
        
        f_mean_athlete_count = block_weeks['f_mean_athlete_count'].mean()
        mean_athlete_count = athlete_weeks['f_mean_athlete_count'].mean()
        r_mean_athlete_count = f_mean_athlete_count / mean_athlete_count       

        f_avg_time_in_z1_runs = block_weeks['f_time_in_z1_runs'].mean()
        avg_time_in_z1_runs = np.nanmean(athlete_weeks['f_time_in_z1_runs'])
        r_avg_time_in_z1_runs = f_avg_time_in_z1_runs / avg_time_in_z1_runs
        
        f_avg_time_in_z2_runs = block_weeks['f_time_in_z2_runs'].mean()
        avg_time_in_z2_runs = np.nanmean(athlete_weeks['f_time_in_z2_runs'])
        r_avg_time_in_z2_runs = f_avg_time_in_z2_runs / avg_time_in_z2_runs
        
        f_avg_time_in_z3_runs = block_weeks['f_time_in_z3_runs'].mean()
        avg_time_in_z3_runs = np.nanmean(athlete_weeks['f_time_in_z3_runs'])
        r_avg_time_in_z3_runs = f_avg_time_in_z3_runs / avg_time_in_z3_runs
        
        f_avg_time_in_z4_runs = block_weeks['f_time_in_z4_runs'].mean()
        avg_time_in_z4_runs = np.nanmean(athlete_weeks['f_time_in_z4_runs'])
        r_avg_time_in_z4_runs = f_avg_time_in_z4_runs / avg_time_in_z4_runs
        
        f_avg_time_in_z5_runs = block_weeks['f_time_in_z5_runs'].mean()
        avg_time_in_z5_runs = np.nanmean(athlete_weeks['f_time_in_z5_runs'])
        r_avg_time_in_z5_runs = f_avg_time_in_z5_runs / avg_time_in_z5_runs  


        from running_functions import get_run_outliers

        f_num_distance_activities, f_num_intense_activities, f_num_varying_activities = get_run_outliers(features_activities, block_id, athlete_id)
        num_distance_activities, num_intense_activities, num_varying_activities = get_run_outliers(all_athlete_activities, '0', athlete_id)
        total_activities = len(all_athlete_activities)

        f_proportion_distance_activities = round(len(f_num_distance_activities) / len(block_activities),2)
        proportion_distance_activities = round(len(num_distance_activities) / len(total_activities),2)
        try:
            r_proportion_distance_activities = round(len(f_proportion_distance_activities) / len(proportion_distance_activities),2)
        except Exception:
            r_proportion_distance_activities = None

        f_proportion_intense_activities = round(len(f_num_intense_activities) / len(block_activities),2)
        proportion_intense_activities = round(len(num_intense_activities) / len(total_activities),2)
        try:
            r_proportion_intense_activities = round(len(f_proportion_intense_activities) / len(proportion_intense_activities),2)
        except Exception:
            r_proportion_intense_activities = None

        f_proportion_varying_activities = round(len(f_num_varying_activities) / len(block_activities),2)
        proportion_varying_activities = round(len(num_varying_activities) / len(total_activities),2)
        try:
            r_proportion_varying_activities = round(len(f_proportion_varying_activities) / len(proportion_varying_activities),2)
        except Exception:
            r_proportion_varying_activities = None


        f_proportion_swims = round(len(block_activities[block_activities['activity_type'] == 3])/len(block_activities),2)
        proportion_swims = round(len(all_athlete_activities[all_athlete_activities['activity_type'] == 3])/len(all_athlete_activities),2)
        try:
            r_proprotion_swims = f_proportion_swims / proportion_swims

        except Exception:
            r_proprotion_swims = None

        f_proportion_walks_hikes = round(len(block_activities[block_activities['activity_type'].issin([4,5])])/len(block_activities),2)
        proportion_walks_hikes = round(len(all_athlete_activities[all_athlete_activities['activity_type'].isin([4,5])])/len(all_athlete_activities),2)
        try:
            r_proportion_walks_hikes = f_proportion_walks_hikes / proportion_walks_hikes
        except Exception:
            r_proportion_walks_hikes = None
        
        f_proportion_alpine_ski = round(len(block_activities[block_activities['activity_type'] == 6])/len(block_activities),2)
        proportion_alpine_ski = round(len(all_athlete_activities[all_athlete_activities['activity_type'] == 6])/len(all_athlete_activities),2)        
        try:
            r_proportion_alpine_ski = f_proportion_alpine_ski / proportion_alpine_ski
        except Exception:
            r_proportion_alpine_ski = None
        
        f_proportion_workout = round(len(block_activities[block_activities['activity_type'] == 32])/len(block_activities),2)
        proportion_workout = round(len(all_athlete_activities[all_athlete_activities['activity_type'] == 32])/len(all_athlete_activities),2)        
        try:
            r_proportion_workout = f_proportion_workout / proportion_workout
        except Exception:
            r_proportion_workout = None
        
        f_proportion_yoga = round(len(block_activities[block_activities['activity_type'] == 34])/len(block_activities),2)
        proportion_yoga = round(len(all_athlete_activities[all_athlete_activities['activity_type'] == 34])/len(all_athlete_activities),2)        
        try:
            r_proportion_yoga = f_proportion_yoga / proportion_yoga
        except Exception:
            r_proportion_yoga = None
            
        f_proportion_crossfit = round(len(block_activities[block_activities['activity_type'] == 10])/len(block_activities),2)
        proportion_crossfit = round(len(all_athlete_activities[all_athlete_activities['activity_type'] == 10])/len(all_athlete_activities),2)        
        try:
            r_proportion_crossfit = f_proportion_crossfit / proportion_crossfit
        except Exception:
            r_proportion_crossfit = None


        f_proportion_other = round(len(block_activities[block_activities['activity_type'].isin([7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,33,34])])/len(block_activities),2)
        proportion_other = round(len(all_athlete_activities[all_athlete_activities['activity_type'].isin([7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,33,34])])/len(all_athlete_activities),2)        
        try:
            r_proportion_other = f_proportion_other / proportion_other
        except Exception:
            r_proportion_other = None


        features_blocks = features_blocks.append({'athlete_id': athlete_id,
                                            'block_id': block_id,
                                            'f_slope_distances_before_taper': f_slope_distances_before_taper,
                                            'f_taper_factor_distance': f_taper_factor_distance,
                                            'f_slope_time_before_taper': f_slope_time_before_taper,
                                            'f_taper_factor_time': f_taper_factor_time,
                                            'f_slope_hr_before_taper': f_slope_hr_before_taper,
                                            'f_taper_factor_hr': f_taper_factor_hr,
                                            'f_avg_weekly_run_distance': f_avg_weekly_run_distance,
                                            'r_avg_weekly_run_distance': r_avg_weekly_run_distance,
                                            #'f_avg_weekly_non_run_distance': f_avg_weekly_non_run_distance,
                                            #'r_avg_weekly_non_run_distance': r_avg_weekly_non_run_distance,
                                            #'f_avg_weekly_run_time': f_avg_weekly_run_time,
                                            #'r_avg_weekly_run_time': r_avg_weekly_run_time,
                                            'f_avg_weekly_non_run_time': f_avg_weekly_non_run_time,
                                            'r_avg_weekly_non_run_time': r_avg_weekly_non_run_time,
                                            'f_avg_total_runs': f_avg_total_runs,
                                            'r_avg_total_runs': r_avg_total_runs,
                                            'f_avg_weekly_run_elevation': f_avg_weekly_run_elevation,
                                            'r_avg_weekly_run_elevation': r_avg_weekly_run_elevation,
                                            'f_mean_athlete_count': f_mean_athlete_count,
                                            'r_mean_athlete_count': r_mean_athlete_count,
                                            'f_avg_time_in_z1_runs': f_avg_time_in_z1_runs,
                                            'f_avg_time_in_z2_runs': f_avg_time_in_z2_runs,
                                            'f_avg_time_in_z3_runs': f_avg_time_in_z3_runs,
                                            'f_avg_time_in_z4_runs': f_avg_time_in_z4_runs,
                                            'f_avg_time_in_z5_runs': f_avg_time_in_z5_runs,
                                            'r_avg_time_in_z1_runs': r_avg_time_in_z1_runs,
                                            'r_avg_time_in_z2_runs': r_avg_time_in_z2_runs,
                                            'r_avg_time_in_z3_runs': r_avg_time_in_z3_runs,
                                            'r_avg_time_in_z4_runs': r_avg_time_in_z4_runs,
                                            'r_avg_time_in_z5_runs': r_avg_time_in_z5_runs,
                                            'f_proportion_distance_activities': f_proportion_distance_activities,
                                            'f_proportion_intense_activities': f_proportion_intense_activities,
                                            'f_proportion_varying_activities': f_proportion_varying_activities,  
                                            'r_proportion_distance_activities': r_proportion_distance_activities,
                                            'r_proportion_intense_activities': r_proportion_intense_activities,
                                            'r_proportion_varying_activities': r_proportion_varying_activities,  
                                            'f_proportion_rides': f_proportion_rides,  
                                            'f_proportion_swims': f_proportion_swims,  
                                            'f_proportion_walks_hikes': f_proportion_walks_hikes,  
                                            'f_proportion_alpine_ski': f_proportion_alpine_ski,  
                                            'f_proportion_workout': f_proportion_workout,  
                                            'f_proportion_yoga': f_proportion_yoga,  
                                            'f_proportion_crossfit': f_proportion_crossfit,   
                                            'f_proportion_other': f_proportion_other,               
                                            'r_proportion_rides': r_proportion_rides,  
                                            'r_proportion_swims': r_proportion_swims,  
                                            'r_proportion_walks_hikes': r_proportion_walks_hikes,  
                                            'r_proportion_alpine_ski': r_proportion_alpine_ski,  
                                            'r_proportion_workout': r_proportion_workout,  
                                            'r_proportion_yoga': r_proportion_yoga,  
                                            'r_proportion_crossfit': r_proportion_crossfit,   
                                            'r_proportion_other': r_proportion_other,                                     
                                            'y_vdot_delta': y_vdot_delta,
                                            'y_vdot': y_vdot
                                            }, ignore_index=True)       

    processing_status = read_db('processing_status')
    processing_status_index = processing_status[processing_status['athlete_id'] == str(int(athlete_id))].index.values.astype(int)[0]
    processing_status.at[processing_status_index, 'status'] = 'processed'
    write_db_replace(processing_status, 'processing_status')
    
    try:

        metadata_athlete = metadata_athlete.append(read_db('metadata_athlete'), ignore_index = True)
        metadata_blocks = metadata_blocks.append(read_db('metadata_blocks'), ignore_index = True)
        all_athlete_activities = all_athlete_activities.append(read_db('all_athlete_activities'), ignore_index = True)
        all_athlete_weeks = all_athlete_weeks.append(read_db('all_athlete_weeks'), ignore_index=True)    
        features_activities = features_activities.append(read_db('features_activities'), ignore_index=True)    
        features_weeks = features_weeks.append(read_db('features_weeks'), ignore_index=True)
        features_blocks = features_blocks.append(read_db('features_blocks'), ignore_index=True)    
        average_paces_and_hrs = average_paces_and_hrs.append(read_db('average_paces_and_hrs'), ignore_index=True)    

    except Exception as e:
        print(e)

    write_db_replace(metadata_athlete.applymap(str), 'metadata_athletes')
    write_db_replace(metadata_blocks.applymap(str), 'metadata_blocks')
    write_db_replace(all_athlete_activities, 'all_athlete_activities')   
    write_db_replace(all_athlete_weeks, 'all_athlete_weeks')   
    write_db_replace(features_activities, 'features_activities')   
    write_db_replace(features_weeks, 'features_weeks')   
    write_db_replace(features_blocks, 'features_blocks')   
    write_db_replace(average_paces_and_hrs, 'average_paces_and_hrs')  
    