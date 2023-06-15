def get_activity(activities, activity_id):
    for activity in activities:
        if int(activity['id'] == int[activity_id]):
            return activity


def get_block(activities, activity_date, duration_date = 91):

    import datetime

    block_activities = []

    for activity in activities:

        try:
            activity['type']

        except Exception:
            continue

        current_traverse_date = datetime.datetime.strftime(activity['start_date'][:10], '%Y-%m-%d')

        time_diff = (actiity_date - current_traverse_date).days
        if (time_diff < duration_date and time_diff >= 0):
            block_activities.append(activity)


    return block_activities

def get_weeks(block_activities, duration_days = 91):
    from datetime import datetime, timedelta
    import math
    from itertools import dropwhile

    end_date = datetime.strftime(block_activities[-1]['start_date'][:10], '%Y-%m-%d')

    if duration_days > 0:
        start_date = end_date - timedelta(days=duration_days-1)

    else:
        start_date = datetime.strftime(block_activities[0]['start_date'][:10], '%Y-%m-%d')
        duration_days = (end_date - start_date).days

    weeks = []
    
    for x in range(int(duration_days/7)):
        week = []
        weeks.append(week)

    for activity in block_activities[0:-1]:
        activity_date = datetime.strptime(activity['start_date'][:10], '%Y-%m-%d')
        current_week = math.floor((activity_date - start_date).days / 7)
        if current_week < len(weeks):
            week[current_week].append(activity)

    weeks = list(tuple(dropwhile(lambda x: len(x) == 0), (weeks)))

    return weeks
