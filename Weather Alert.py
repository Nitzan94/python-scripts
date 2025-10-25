# ABOUTME: Fetches weather forecast and sends alerts for rain/snow/extreme conditions
# ABOUTME: Provides daily weather summary with configurable location and alerts

import argparse
import sys
from datetime import datetime
from typing import Dict, Optional
import requests


def get_weather(city: str, api_key: str) -> Dict:
    """
    Fetch weather data from OpenWeatherMap API.

    Args:
        city: City name
        api_key: OpenWeatherMap API key

    Returns:
        Weather data dictionary
    """
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "cnt": 8  # 24 hours (3-hour intervals)
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch weather: {e}")
        sys.exit(1)


def analyze_forecast(data: Dict) -> Dict[str, any]:
    """
    Analyze forecast for alerts.

    Args:
        data: Weather API response

    Returns:
        Analysis with alerts
    """
    alerts = []
    conditions = []
    temps = []

    for item in data["list"]:
        temp = item["main"]["temp"]
        temps.append(temp)

        weather = item["weather"][0]
        main_condition = weather["main"]
        description = weather["description"]
        conditions.append(description)

        # Check for alerts
        if main_condition in ["Rain", "Drizzle"]:
            time = datetime.fromtimestamp(item["dt"]).strftime("%I%p")
            alerts.append(f"Rain expected around {time}: {description}")
        elif main_condition == "Snow":
            time = datetime.fromtimestamp(item["dt"]).strftime("%I%p")
            alerts.append(f"Snow expected around {time}: {description}")
        elif main_condition == "Thunderstorm":
            time = datetime.fromtimestamp(item["dt"]).strftime("%I%p")
            alerts.append(f"Thunderstorm expected around {time}: {description}")

        # Extreme temps
        if temp > 35:
            alerts.append(f"Extreme heat: {temp:.1f}C")
        elif temp < -10:
            alerts.append(f"Extreme cold: {temp:.1f}C")

    return {
        "city": data["city"]["name"],
        "country": data["city"]["country"],
        "alerts": alerts,
        "conditions": conditions,
        "temp_min": min(temps),
        "temp_max": max(temps),
        "temp_avg": sum(temps) / len(temps)
    }


def display_summary(analysis: Dict, verbose: bool = False) -> None:
    """
    Display weather summary.

    Args:
        analysis: Weather analysis data
        verbose: Show detailed forecast
    """
    print(f"\n[INFO] Weather for {analysis['city']}, {analysis['country']}")
    print(f"[INFO] Temperature: {analysis['temp_min']:.1f}C - {analysis['temp_max']:.1f}C (avg: {analysis['temp_avg']:.1f}C)")

    if analysis["alerts"]:
        print(f"\n[WARN] {len(analysis['alerts'])} alert(s) for next 24 hours:")
        for alert in analysis["alerts"]:
            print(f"  - {alert}")
    else:
        print("\n[OK] No weather alerts for next 24 hours")

    if verbose:
        print("\n[INFO] Forecast conditions:")
        unique_conditions = list(dict.fromkeys(analysis["conditions"]))
        for condition in unique_conditions:
            print(f"  - {condition}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Weather alert bot with forecast checking"
    )
    parser.add_argument(
        "city",
        help="City name (e.g., 'London', 'New York')"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="OpenWeatherMap API key (or set OPENWEATHER_API_KEY env var)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed forecast"
    )

    args = parser.parse_args()

    # Get API key
    import os
    api_key = args.api_key or os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        print("[ERROR] API key required. Get free key at https://openweathermap.org/api")
        print("[INFO] Usage:")
        print("  1. Set environment variable: set OPENWEATHER_API_KEY=your_key")
        print("  2. Or pass with -k flag: python 'Weather Alert.py' London -k your_key")
        sys.exit(1)

    print(f"[INFO] Fetching weather for {args.city}...")
    data = get_weather(args.city, api_key)
    analysis = analyze_forecast(data)
    display_summary(analysis, args.verbose)


if __name__ == "__main__":
    main()
