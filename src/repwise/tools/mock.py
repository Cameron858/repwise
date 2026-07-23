def fetch_mock_history(exercise_name: str | None = None, limit: int = 3) -> dict:
    """Fetch recent workout entries and logged set performance from the database.

    Args:
        exercise_name: Optional specific exercise to filter by (e.g. "Squat", "Bench Press").
        limit: The max number of recent sessions to return (default: 3).

    Returns:
        dict: Status containing 'success' status and the structured exercise logs.
    """

    # Mock data mimicking a database lookup
    mock_db = [
        {
            "date": "2026-07-21",
            "exercise": "Squat",
            "sets": 3,
            "reps": 5,
            "weight": 100.0,
        },
        {
            "date": "2026-07-21",
            "exercise": "Bench Press",
            "sets": 3,
            "reps": 8,
            "weight": 80.0,
        },
        {
            "date": "2026-07-19",
            "exercise": "Deadlift",
            "sets": 1,
            "reps": 5,
            "weight": 140.0,
        },
        {
            "date": "2026-07-19",
            "exercise": "Squat",
            "sets": 3,
            "reps": 5,
            "weight": 97.5,
        },
    ]

    filtered_logs = mock_db
    if exercise_name:
        filtered_logs = [
            log for log in mock_db if exercise_name.lower() in log["exercise"].lower()
        ]

    return {
        "status": "success",
        "data": filtered_logs[:limit],
    }
