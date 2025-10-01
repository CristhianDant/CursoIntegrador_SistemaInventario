
```
```mermaid
classDiagram
    direction LR

    class LoginRouter {
        <<FastAPI Router>>
        + POST /login
    }

    class LoginService {
        - db: Session
        + login(credentials)
    }

    class UsuarioModel {
        <<SQLAlchemy Model>>
        id_user: int
        username: str
        hashed_password: str
        nombre: str
        apellido: str
        email: str
        activo: bool
    }

    namespace schemas {
        class Token {
            <<Pydantic>>
            access_token: str
            token_type: str
        }
        class LoginRequest {
            <<Pydantic>>
            username: str
            password: str
        }
    }

    LoginRouter ..> LoginService : "utiliza"
    LoginService ..> UsuarioModel : "autentica contra"
    LoginRouter ..> LoginRequest : "recibe"
    LoginRouter ..> Token : "retorna"

