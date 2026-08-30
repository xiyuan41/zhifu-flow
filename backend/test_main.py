from fastapi.testclient import TestClient

from main import app, tickets

client = TestClient(app)


def test_create_and_update_ticket():
    tickets.clear()

    create_response = client.post(
        "/tickets",
        json={
            "customer_name": "测试用户",
            "question": "订单 B2001 显示已签收，但我没有收到商品。",
            "order_no": "B2001",
            "priority": "high",
        },
    )

    assert create_response.status_code == 200
    ticket = create_response.json()
    assert ticket["status"] == "pending"

    update_response = client.patch(
        f"/tickets/{ticket['id']}",
        json={"status": "processing"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "processing"


def test_update_missing_ticket_returns_404():
    tickets.clear()

    response = client.patch(
        "/tickets/999",
        json={"status": "processing"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "工单不存在"