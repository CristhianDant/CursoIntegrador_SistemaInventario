id_producto: int
            tipo_movimiento: str
            motivo: str
            cantidad: Decimal
            precio_venta: Decimal
            id_user: int
        }
        class MovimientoProductoTerminadoCreate {
            <<Pydantic>>
        }
        class MovimientoProductoTerminado {
            <<Pydantic>>
            id_movimiento: int
            fecha_movimiento: datetime
            anulado: bool
        }
    }

    MovimientoProductoTerminadoRouter ..> MovimientoProductoTerminadoService : "utiliza"
    MovimientoProductoTerminadoService ..> MovimientoProductoTerminadoRepository : "utiliza"
    MovimientoProductoTerminadoRepository ..> MovimientoProductoTerminadoModel : "opera sobre"

    MovimientoProductoTerminadoRouter ..> MovimientoProductoTerminadoCreate : "recibe"
    MovimientoProductoTerminadoRouter ..> MovimientoProductoTerminado : "retorna"

    MovimientoProductoTerminadoBase <|-- MovimientoProductoTerminadoCreate
    MovimientoProductoTerminadoBase <|-- MovimientoProductoTerminado
````markdown
classDiagram
    direction LR

    class MovimientoProductoTerminadoRouter {
        <<FastAPI Router>>
        + POST /
        + GET /
        + GET /(id)
        + DELETE /(id)
    }

    class MovimientoProductoTerminadoService {
        - repository: MovimientoProductoTerminadoRepository
        + create(data)
        + get_all()
        + get(id)
        + anular(id)
    }

    class MovimientoProductoTerminadoRepository {
        - db: Session
        + create(item)
        + get_all()
        + get(id)
        + update(item)
    }

    class MovimientoProductoTerminadoModel {
        <<SQLAlchemy Model>>
        id_movimiento: int
        numero_movimiento: str
        id_producto: int
        tipo_movimiento: str
        motivo: str
        cantidad: Decimal
        precio_venta: Decimal
        id_user: int
        fecha_movimiento: datetime
        anulado: bool
    }

    namespace schemas {
        class MovimientoProductoTerminadoBase {
            <<Pydantic>>
            numero_movimiento: str
            id_producto: int
            tipo_movimiento: str
            motivo: str
            cantidad: Decimal
            precio_venta: Decimal
            id_user: int
        }
        class MovimientoProductoTerminadoCreate {
            <<Pydantic>>
        }
        class MovimientoProductoTerminado {
            <<Pydantic>>
            id_movimiento: int
            fecha_movimiento: datetime
            anulado: bool
        }
    }

    MovimientoProductoTerminadoRouter ..> MovimientoProductoTerminadoService : "utiliza"
    MovimientoProductoTerminadoService ..> MovimientoProductoTerminadoRepository : "utiliza"
    MovimientoProductoTerminadoRepository ..> MovimientoProductoTerminadoModel : "opera sobre"

    MovimientoProductoTerminadoRouter ..> MovimientoProductoTerminadoCreate : "recibe"
    MovimientoProductoTerminadoRouter ..> MovimientoProductoTerminado : "retorna"

    MovimientoProductoTerminadoBase <|-- MovimientoProductoTerminadoCreate
    MovimientoProductoTerminadoBase <|-- MovimientoProductoTerminado
````
