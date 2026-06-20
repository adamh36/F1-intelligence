import fastf1


import os; os.makedirs('cache', exist_ok=True); fastf1.Cache.enable_cache('cache')

# if session_type is None, pull data from all sessions for richer comparison
SESSIONS = ['FP1', 'FP2', 'FP3', 'Q', 'R']

def Head_to_Head(year: int, driver1: str, driver2: str, race_name: str, session_type: str = None) -> str:
    """Compare two drivers across all sessions (or a specific one) at a given race weekend."""

    sessions_to_run = [session_type] if session_type else SESSIONS
    lines = [f"{year} {race_name} GP — {driver1} vs {driver2}\n"]

    for stype in sessions_to_run:
        try:
            session = fastf1.get_session(year, race_name, stype)
            session.load(telemetry=True, weather=False, messages=False)

            lap1 = session.laps.pick_drivers(driver1).pick_fastest()
            lap2 = session.laps.pick_drivers(driver2).pick_fastest()

            # get_car_data() returns telemetry channels: Speed, RPM, Gear, Throttle, Brake
            tel1 = lap1.get_car_data()
            tel2 = lap2.get_car_data()

            max_speed1 = tel1['Speed'].max()
            max_speed2 = tel2['Speed'].max()
            avg_speed1 = round(tel1['Speed'].mean(), 2)
            avg_speed2 = round(tel2['Speed'].mean(), 2)

            # LapTime is a timedelta — total_seconds() converts to a float
            lap_time1 = lap1['LapTime'].total_seconds()
            lap_time2 = lap2['LapTime'].total_seconds()

            faster = driver1 if lap_time1 < lap_time2 else driver2
            delta = round(abs(lap_time1 - lap_time2), 3)

            lines.append(
                f"[{stype}]\n"
                f"  {driver1} | Lap: {lap_time1}s | Max Speed: {max_speed1} km/h | Avg Speed: {avg_speed1} km/h\n"
                f"  {driver2} | Lap: {lap_time2}s | Max Speed: {max_speed2} km/h | Avg Speed: {avg_speed2} km/h\n"
                f"  Faster: {faster} by {delta}s\n"
            )

        except Exception:
            # session may not exist (e.g. no FP3 at sprint weekends)
            lines.append(f"[{stype}] — data unavailable\n")

    return "\n".join(lines)
