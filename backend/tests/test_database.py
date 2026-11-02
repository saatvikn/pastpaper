from sqlalchemy import text


def test_database_target(test_engine):
    with test_engine.connect() as connection:
        result = connection.execute(text("SELECT current_database()"))
        assert result.scalar_one() == "pastpaper_test"
