def get_weather(city: str) -> dict:
    """
    Retrieves the current weather report for a specified city.

    :param str city:  The name of the city (e.g., "New York", "London", "Tokyo").
    :return: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    :rtype: dict
    """
    # docstringは英語で
    # 戻り値はJSON 変換可能な値で

    # ベストプラクティス: Tool内でログ書いておいたほうがデバッグしやすいよ
    print(f"--- Tool: get_weatherが呼び出されました city: {city} ---")
    city_normalized = city.lower().replace(" ", "") # とりあえずDict Keyなので軽くNormalizeする

    # モック天気情報
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    # ベストプラクティス:Tool内でわかってるエラーハンドリングはなるべくやっておく
    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}
