from app.services.chat_memory_service import ChatMemoryService


def test_generate_title_uses_normalized_message():
    title = ChatMemoryService.generate_title("  What   is the ISS mission?\n")

    assert title == "What is the ISS mission?"


def test_generate_title_truncates_long_message():
    title = ChatMemoryService.generate_title("a" * 61)

    assert title == f"{'a' * 57}..."
    assert len(title) == 60
