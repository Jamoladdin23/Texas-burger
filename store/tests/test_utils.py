import pytest
from store.utils import send_telegram_message
from unittest.mock import patch

@pytest.mark.django_db
@patch("store.utils.requests.post")
def test_send_telegram_message(mock_post):
    mock_post.return_value.status_code = 200  # ✅ Подменяем Telegram API
    mock_post.return_value.json.return_value = {"ok": True}
    response = send_telegram_message("Тестовое сообщение")
    assert response == {"ok": True}
