import httpx

from app.infrastructure.db.database import Base, SessionLocal, engine
from app.infrastructure.db.models import DocenteORM, EvaluacionORM

URL = "http://localhost:8000/api/v1"

Base.metadata.create_all(bind=engine)
db = SessionLocal()
docente = db.query(DocenteORM).filter_by(nombre="Docente de Prueba").first()
if not docente:
    docente = DocenteORM(nombre="Docente de Prueba")
    db.add(docente)
    db.commit()
comentarios = [
    (5, "explica muy bien y siempre responde las dudas"),
    (4, "buena clase pero deja muchos trabajos"),
    (2, "a veces llega tarde y demora en subir las notas"),
    (5, "los ejemplos en clase ayudan mucho para el parcial"),
    (3, "normal, la clase es un poco aburrida"),
]
if not docente.evaluaciones:
    for puntaje, texto in comentarios:
        db.add(EvaluacionORM(id_docente=docente.id_docente, puntaje=puntaje, comentario=texto))
    db.commit()
id_docente = docente.id_docente
db.close()

preguntas = [
    ("Clasifica este comentario como Positivo, Negativo o Neutro: 'el profe no explica nada'", None),
    ("Clasifica este comentario como Positivo, Negativo o Neutro: 'buena clase, aprendi bastante'", None),
    ("Que opinan los estudiantes de este docente?", id_docente),
    ("Cual es el principal punto a mejorar de este docente?", id_docente),
]

for tecnica in ["zero-shot", "few-shot", "cot"]:
    for pregunta, docente_id in preguntas:
        datos = {"pregunta": pregunta, "tecnica": tecnica, "id_docente": docente_id}
        res = httpx.post(URL + "/ai", json=datos, timeout=30)
        print(tecnica, res.status_code)
        if res.status_code == 200:
            print(res.json()["respuesta"][:150])
        else:
            print(res.json())
        print("-----")

print("listo, revisar llamadas_ia.csv")
