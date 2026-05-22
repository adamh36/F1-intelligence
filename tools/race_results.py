import fastf1

fastf1.Cache.enable_cache('cache')


def get_race_results(year: int, race_name: str) -> str:
    """Load a race session and return formatted results including positions,
    grid positions, time gaps, points, fastest lap, and retirement status."""

    session = fastf1.get_session(year, race_name, 'R')
    session.load(telemetry=False, weather=False, messages=False)

    results = session.results

    lines = [f"{year} {race_name} Grand Prix — Race Results\n"]

    for _, driver in results.iterrows():
        pos = driver['Position']
        name = driver['Abbreviation']
        team = driver['TeamName']
        grid = int(driver['GridPosition'])
        points = driver['Points']
        status = driver['Status']

        if int(pos) == 1:
            gap = 'WINNER | Podium'
        elif int(pos) == 2:
            gap = "2nd Place | Podium"
        elif int(pos) == 3:
            gap = "3rd Place | Podium"
        elif status == 'Finished':
            gap = f"P{int(pos)}"
        else:
            gap = status if '+' in str(status) else f"DNF ({status})"

        lines.append(
            f"P{int(pos)} | {name} | {team} | Grid: {grid} | {gap} | Pts: {int(points)}"
        )

    return "\n".join(lines)
