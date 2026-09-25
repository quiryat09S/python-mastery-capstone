import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from labs.day12_solid.adapters import (
    InMemoryOrderRepository,
    SqlOrderRepository,
)
from labs.day12_solid.domain import Order
from labs.day12_solid.providers import provide_order_service
from labs.day12_solid.sql_adapters import SqlAlchemyOrderRepository
from labs.day12_solid.sql_models import Base


def test_in_memory_repository_saves_and_reads_order():
    repository = InMemoryOrderRepository()
    service = provide_order_service(repository)

    order = Order(
        id=1,
        customer="Alice",
        total=100.0,
    )

    service.create_order(order)

    assert service.find_order(1) == order


def test_sql_repository_saves_and_reads_order():
    repository = SqlOrderRepository()
    service = provide_order_service(repository)

    order = Order(
        id=2,
        customer="Bob",
        total=250.0,
    )

    service.create_order(order)

    assert service.find_order(2) == order


def test_missing_order_returns_none():
    repository = InMemoryOrderRepository()
    service = provide_order_service(repository)

    assert service.find_order(999) is None


def test_sqlalchemy_repository_saves_and_reads_order():
    engine = create_engine(
        "sqlite://",
    )

    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        repository = SqlAlchemyOrderRepository(session)
        service = provide_order_service(repository)

        order = Order(
            id=3,
            customer="Diana",
            total=450.0,
        )

        service.create_order(order)

        assert service.find_order(3) == order

    engine.dispose()


# Verifica principio LSP
@pytest.mark.parametrize(
    "repository_class",
    [
        InMemoryOrderRepository,
        SqlOrderRepository,
    ],
)
def test_repositories_are_substitutable(
    repository_class,
):
    repository = repository_class()
    service = provide_order_service(repository)

    order = Order(
        id=10,
        customer="Charlie",
        total=75.5,
    )

    saved_order = service.create_order(order)

    assert saved_order == order
    assert service.find_order(10) == order
