from datetime import datetime
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import Ticket
from knowledge_service import search_knowledge

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="智服流 API",
    description="企业客服与工单智能体工作台的后端接口",
    version="0.2.0",
)


class TicketCreate(BaseModel):
    customer_name: str = Field(min_length=1, description="客户姓名")
    question: str = Field(min_length=5, description="客户问题")
    order_no: str | None = Field(default=None, description="订单号")
    priority: Literal["low", "medium", "high"] = "medium"


class TicketStatusUpdate(BaseModel):
    status: Literal["pending", "processing", "resolved"]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ticket_to_dict(ticket: Ticket) -> dict:
    return {
        "id": ticket.id,
        "customer_name": ticket.customer_name,
        "question": ticket.question,
        "order_no": ticket.order_no,
        "priority": ticket.priority,
        "status": ticket.status,
        "created_at": ticket.created_at.isoformat(),
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "zhifu-flow"}


@app.post("/tickets")
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    new_ticket = Ticket(
        customer_name=ticket.customer_name,
        question=ticket.question,
        order_no=ticket.order_no,
        priority=ticket.priority,
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return ticket_to_dict(new_ticket)


@app.get("/tickets")
def list_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).order_by(Ticket.id.desc()).all()
    return {
        "total": len(tickets),
        "items": [ticket_to_dict(ticket) for ticket in tickets],
    }


@app.patch("/tickets/{ticket_id}")
def update_ticket_status(
    ticket_id: int,
    update: TicketStatusUpdate,
    db: Session = Depends(get_db),
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="工单不存在")

    ticket.status = update.status
    db.commit()
    db.refresh(ticket)
    return ticket_to_dict(ticket)


@app.get("/knowledge/search")
def search_knowledge_endpoint(query: str, top_k: int = 3):
    results = search_knowledge(query=query, top_k=top_k)

    return {
        "query": query,
        "total": len(results),
        "items": results,
    }