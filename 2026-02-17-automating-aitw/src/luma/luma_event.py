"""Example usage of the Luma API client."""

from luma_client import LumaClient


def main():
    """Fetch and display the next upcoming 'ai that works' event."""
    # Initialize the client (reads LUMA_API_KEY from environment)
    client = LumaClient()

    print("Fetching the next upcoming '🦄 ai that works' event...\n")

    # Get the next upcoming event
    event = client.get_next_ai_that_works_event()

    if event:
        print(f"URL: {event.url}")
        print(f"\nDescription:\n{event.clean_description}")
    else:
        print("No upcoming '🦄 ai that works' events found.")


if __name__ == "__main__":
    main()
