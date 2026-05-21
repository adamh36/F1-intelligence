import fastf1
fastf1.Cache.enable_cache('cache')
session = fastf1.get_session(2024, 'Monaco', 'R')
session.load()
print(session.results[['DriverNumber', 'Abbreviation', 'Position', 'Points']])

# Get lap data for Leclerc
lec = session.laps.pick_driver('LEC')
fastest_lap = lec.pick_fastest()
telemetry = fastest_lap.get_telemetry()
print(telemetry[['Distance', 'Speed', 'Throttle', 'Brake', 'nGear', 'DRS']].head(20))