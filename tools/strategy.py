import fastf1


fastf1.Cache.enable_cache('cache')


def analyze_strategy(year: int, race_name: str) -> str:
    """Fetch pit stop data, tire compounds, and stint lengths for a race."""

    session = fastf1.get_session(year, race_name, 'R')
    session.load(telemetry=False, weather=False, messages=False)

    laps = session.laps

    lines = [f"{year} {race_name} GP — Race Strategy\n"]

    # group by driver to build each driver's stint breakdown
    for driver in laps['Driver'].unique():
        driver_laps = laps.pick_drivers(driver)

        stints = driver_laps.groupby('Stint')[['LapNumber', 'Compound']].agg(
            start=('LapNumber', 'min'),
            end=('LapNumber', 'max'),
            compound=('Compound', 'first')
        ).reset_index()

        stint_str = ' → '.join(
            f"{row['compound']} (L{int(row['start'])}-L{int(row['end'])})"
            for _, row in stints.iterrows()
        )

        lines.append(f"  {driver}: {stint_str}")

    return "\n".join(lines)
