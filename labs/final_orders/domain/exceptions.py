class DomainError(Exception):
    """Error base de las reglas de negocio."""


class InvalidOrderError(DomainError):
    """La orden no cumple las reglas del dominio."""


class OrderNotFoundError(DomainError):
    """La orden solicitada no existe."""


class InvalidOrderStateError(DomainError):
    """La transición de estado no está permitida."""
