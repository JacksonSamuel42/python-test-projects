import enum

from sqlalchemy import (
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

# Create the db connection
db = create_engine("sqlite:///database/banco.db")

# Create db data
Base = declarative_base()


# Create classes/tables from db
class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    admin: Mapped[bool] = mapped_column(Boolean, default=False)

    def __init__(
        self,
        name: str,
        email: str,
        password: str,
        active: bool = True,
        admin: bool = False,
    ):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.admin = admin


class OrderStatus(enum.Enum):
    PENDING = "pending"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Orders(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    status: Mapped[str] = mapped_column(
        Enum(
            OrderStatus,
            name="order_status_type",
            values_callable=lambda e: [x.value for x in e],
        ),
        default=OrderStatus.PENDING.value,
        nullable=False,
    )

    user: Mapped[int] = mapped_column(ForeignKey("users.id"))
    price: Mapped[float] = mapped_column(Float)
    items = relationship("OrderItems", back_populates="order", cascade="all, delete")

    def __init__(
        self,
        user: int,
        status: str = OrderStatus.PENDING.value,
        price: float = 0,
    ):
        if status not in [s.value for s in OrderStatus]:
            raise ValueError(f"Invalid status: {status}")

        self.status = status
        self.user = user
        self.price = price

    def calculate_price(self):
        self.price = sum(item.unit_price * item.quantity for item in self.items)


class OrderItems(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quantity: Mapped[int] = mapped_column(Integer)
    flavor: Mapped[str] = mapped_column(String)
    size: Mapped[str] = mapped_column(String)
    unit_price: Mapped[float] = mapped_column(Float)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    order = relationship("Orders", back_populates="items")

    def __init__(
        self,
        quantity: int,
        flavor: str,
        size: str,
        unit_price: float,
        order_id: int,
    ):
        self.quantity = quantity
        self.flavor = flavor
        self.size = size
        self.unit_price = unit_price
        self.order_id = order_id
