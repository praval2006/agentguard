"""A deliberately small profile formatter with a visible schema contract."""

PROFILE = {"user_name": "Pratik"}


def display_name(profile: dict[str, str]) -> str:
    return profile["user_name"]


if __name__ == "__main__":
    print(display_name(PROFILE))
