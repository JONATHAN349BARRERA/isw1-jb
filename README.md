# ISW1 - Sistema de Gestión Financiera de Clientes

## Herramientas utilizadas
- **Lenguaje Backend:** Python 3.11 + Flask 3.0
- **Lenguaje Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Base de datos:** SQLite (via SQLAlchemy)
- **IDE:** VS Code

## Cómo ejecutar
1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar: `python app.py`
4. Abrir: http://localhost:5000

## Script de base de datos
```sql
CREATE TABLE cliente (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  numero_identificacion VARCHAR(50) NOT NULL UNIQUE,
  correo VARCHAR(100) NOT NULL,
  nombre_completo VARCHAR(150) NOT NULL
);

CREATE TABLE tarjeta_credito (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  numero_tarjeta VARCHAR(20) NOT NULL UNIQUE,
  fecha_vencimiento VARCHAR(7) NOT NULL,
  franquicia VARCHAR(20),
  estado VARCHAR(10) DEFAULT 'ACTIVO',
  cupo_total FLOAT NOT NULL,
  cupo_disponible FLOAT NOT NULL,
  cupo_utilizado FLOAT,
  cliente_id INTEGER NOT NULL,
  FOREIGN KEY (cliente_id) REFERENCES cliente(id)
);
```
