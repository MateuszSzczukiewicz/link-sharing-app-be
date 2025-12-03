import sqlite3


class FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    def fetchone(self):
        if isinstance(self._rows, list):
            return self._rows[0] if self._rows else None
        return self._rows

    def fetchall(self):
        if isinstance(self._rows, list):
            return self._rows
        return [self._rows] if self._rows is not None else []


class FakeConnection:
    IntegrityError = sqlite3.IntegrityError

    def execute(self, query, params=()):
        q_upper = query.strip().upper()
        if q_upper.startswith("UPDATE"):
            raise sqlite3.IntegrityError("Simulated IntegrityError on UPDATE")
        if q_upper.startswith("DELETE"):
            raise sqlite3.IntegrityError("Simulated IntegrityError on DELETE")
        if q_upper.startswith("INSERT"):
            if "INTO LINKS" in q_upper:
                if len(params) >= 2 and params[1] == "Twitter":
                    raise sqlite3.IntegrityError("Simulated IntegrityError on INSERT")
            return FakeCursor(None)
        if q_upper.startswith("SELECT"):
            if "FROM USERS" in q_upper and "WHERE ID = ?" in q_upper:
                fake_user = {
                    "email": "test@gmail.com",
                    "first_name": "Test",
                    "last_name": "Testowy",
                    "image_url": "https://link_to_image.com",
                }
                return FakeCursor(fake_user)
            if "FROM LINKS" in q_upper:
                if "WHERE USER_ID = ?" in q_upper:
                    fake_link = {
                        "id": 1,
                        "user_id": params[0],
                        "platform": "Twitter",
                        "url": "https://twitter.com/test",
                        "created": "2025-03-16 12:00:00",
                    }
                    return FakeCursor([fake_link])
                if "WHERE ID = ?" in q_upper:
                    if params[0] == 1:
                        fake_link = {
                            "id": 1,
                            "user_id": 1,
                            "platform": "Twitter",
                            "url": "https://twitter.com/test",
                            "created": "2025-03-16 12:00:00",
                        }
                        return FakeCursor(fake_link)
                    return FakeCursor(None)
            return FakeCursor(None)
        return FakeCursor(None)

    def commit(self):
        pass

    def close(self):
        pass
