from typing import List

from dependencies import get_session, verify_token
from fastapi import APIRouter, Depends, HTTPException
from models import OrderItems, Orders, OrderStatus, Users
from schemas import OrderItemSchema, OrderSchema, ResponseOrderSchema
from sqlalchemy.orm import Session

order_router = APIRouter(
    prefix="/orders", tags=["order"], dependencies=[Depends(verify_token)]
)


@order_router.post("/order")
async def create_order(order_data: OrderSchema, session=Depends(get_session)):
    new_order = Orders(user=order_data.user)
    session.add(new_order)
    session.commit()

    return {"message": f"Order created successfully. orderId: {new_order.id}"}


@order_router.post("/order/calcel/{order_id}")
async def cancel_order(
    order_id: int,
    session: Session = Depends(get_session),
    user: Users = Depends(verify_token),
):
    order = session.query(Orders).filter(Orders.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="order not found")

    if not (user.admin or user.id == order.user):
        raise HTTPException(
            status_code=401, detail="you are not authorized to make this change"
        )

    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(400, detail="order is already cancelled")

    order.status = OrderStatus.CANCELLED.value
    session.commit()
    return {"message": f"order {order.id} cancelled successfully.", "order": order}


@order_router.get("/list")
async def orders_list(
    session: Session = Depends(get_session), user: Users = Depends(verify_token)
):
    if not user.admin:
        raise HTTPException(status_code=401, detail="you are not authorized")
    orders = session.query(Orders).all()
    return {"message": "all orders", "orders": orders}


@order_router.post("/order/add-item/{order_id}")
async def order_add_item(
    order_id: int,
    order_item: OrderItemSchema,
    session=Depends(get_session),
    user: Users = Depends(verify_token),
):
    order = session.query(Orders).filter(Orders.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="order not found")

    if not (user.admin or user.id == order.user):
        raise HTTPException(
            status_code=401, detail="you are not authorized to make this change"
        )

    order_item = OrderItems(
        quantity=order_item.quantity,
        flavor=order_item.flavor,
        size=order_item.size,
        unit_price=order_item.unit_price,
        order_id=order_id,
    )
    order.items.append(order_item)
    session.add(order_item)
    order.calculate_price()
    session.commit()
    return {
        "message": "order item added successfully.",
        "item_id": order_item.id,
        "order_price": order.price,
    }


@order_router.post("/order/remove-item/{order_item_id}")
async def order_remove_item(
    order_item_id: int,
    session=Depends(get_session),
    user: Users = Depends(verify_token),
):
    order_item = (
        session.query(OrderItems).filter(OrderItems.id == order_item_id).first()
    )
    order = session.query(Orders).filter(Orders.id == order_item.order_id).first()
    if not order_item:
        raise HTTPException(status_code=400, detail="order not found")

    if not (user.admin or user.id == order.user):
        raise HTTPException(
            status_code=401, detail="you are not authorized to make this change"
        )

    session.delete(order_item)
    order.calculate_price()
    session.commit()
    return {
        "message": "order item removed successfully.",
        "order_items_quantity": len(order.items),
        "order": order,
    }


@order_router.post("/order/finish/{order_id}")
async def finish_order(
    order_id: int,
    session: Session = Depends(get_session),
    user: Users = Depends(verify_token),
):
    order = session.query(Orders).filter(Orders.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="order not found")

    if not (user.admin or user.id == order.user):
        raise HTTPException(
            status_code=401, detail="you are not authorized to make this change"
        )

    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(400, detail="cannot finish a cancelled order")

    order.status = OrderStatus.COMPLETED.value
    session.commit()
    return {"message": f"order {order.id} finished successfully.", "order": order}


@order_router.get("/order/{order_id}")
async def get_order(
    order_id: int,
    session: Session = Depends(get_session),
    user: Users = Depends(verify_token),
):
    order = session.query(Orders).filter(Orders.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="order not found")

    if not (user.admin or user.id == order.user):
        raise HTTPException(
            status_code=401, detail="you are not authorized to view this order"
        )

    return {
        "order_items_quantity": len(order.items),
        "order": order,
    }


@order_router.get("/list/order_users", response_model=List[ResponseOrderSchema])
async def orders_list_user(
    session: Session = Depends(get_session), user: Users = Depends(verify_token)
):
    orders = session.query(Orders).filter(Orders.user == user.id).all()
    return orders
