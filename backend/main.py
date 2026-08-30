from datetime import datetime
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="智服流 API",
    description="企业客服与工单智能体工作台的后端接口",
    version="0.1.0",
)

tickets = []


class TicketCreate(BaseModel):
    customer_name: str = Field(min_length=1, description="客户姓名")
    question: str = Field(min_length=5, description="客户问题")
    order_no: str | None = Field(default=None, description="订单号")
    priority: Literal["low", "medium", "high"] = "medium"

class TicketStatusUpdate(BaseModel):
    status: Literal["pending", "processing", "resolved"]


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "zhifu-flow"}


@app.post("/tickets")
def create_ticket(ticket: TicketCreate):
    new_ticket = {
        "id": len(tickets) + 1,
        "customer_name": ticket.customer_name,
        "question": ticket.question,
        "order_no": ticket.order_no,
        "priority": ticket.priority,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    tickets.append(new_ticket)
    return new_ticket


@app.get("/tickets")
def list_tickets():
    return {"total": len(tickets), "items": tickets}
@app.patch("/tickets/{ticket_id}")
def update_ticket_status(ticket_id: int, update: TicketStatusUpdate):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["status"] = update.status
            return ticket

    raise HTTPException(status_code=404, detail="工单不存在")