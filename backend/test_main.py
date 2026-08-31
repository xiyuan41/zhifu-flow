import os

os.environ["DATABASE_URL"] = "sqlite:///./test_zhifu_flow.db"
from fastapi.testclient import TestClient

from database import SessionLocal
from main import app
from models import Ticket

client = TestClient(app)


def clear_tickets():
    db = SessionLocal()
    try:
        db.query(Ticket).delete()
        db.commit()
    finally:
        db.close()


def test_create_and_update_ticket():
    clear_tickets()

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
    clear_tickets()

    response = client.patch(
        "/tickets/999999",
        json={"status": "processing"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "工单不存在"

def test_knowledge_answer_is_grounded():
    response = client.get("/knowledge/answer", params={"query": "物流"})

    assert response.status_code == 200
    data = response.json()
    assert data["grounded"] is True
    assert "售后规则.md" in data["sources"]


def test_knowledge_answer_refuses_unknown_query():
    response = client.get("/knowledge/answer", params={"query": "股票投资"})

    assert response.status_code == 200
    data = response.json()
    assert data["grounded"] is False
    assert data["sources"] == []