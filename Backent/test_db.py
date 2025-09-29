from database import engine

try:
    connection = engine.connect()
    print("¡Conexión a la base de datos exitosa!")
    connection.close()
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")

