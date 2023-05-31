from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import HTMLResponse, JSONResponse
from database import connect_to_mongodb
from models import Movie, User
from jwt_manager import create_token


app = FastAPI()
app.title = "Mi aplicacion con FastAPI"
app.version = "0.0.1"

""" Conexion BD """
@app.on_event("startup")
async def startup():
    app.mongodb_client = connect_to_mongodb()

""" End Point """
@app.get('/', tags=['Home']) 
def message():
    return HTMLResponse('<h1>Hola mundo</h1>')

""" Ruta Usuario Token """
@app.post("/login", tags=['auth'])
def login(user: User):
    if user.email == "admin@gmail.com" and user.password =="admin":
        token: str = create_token(user.dict())
        return JSONResponse(status_code = 200, content=token)
    else:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

""" Ver todas las peliculas """
@app.get('/movies', tags=['movies'], status_code=200)
def get_movies():
    movies_collection = app.mongodb_client["movies"] #tomar la coleccion movies de la DB
    movies = movies_collection.find() #Utilizar busuqeda en mongoDB
    movie_list = []
    for movie in movies:
        movie["_id"] = str(movie["_id"])  # Convertir ObjectId a cadena
        movie_list.append(movie)

    if len(movie_list) == 0:
        raise HTTPException(status_code=404, detail="No se encontraron películas")
    
    return movie_list(status_code=200, content=movies)

""" Buscar movie por id """
@app.get('/movies/{id}', tags=['movies'])
def get_movie_by_id(id: int = Path(ge = 1, le = 99999)):
    movies_collection = app.mongodb_client["movies"]
    movie = movies_collection.find_one({"id": id})
    if movie:
        movie["_id"] = str(movie["_id"])  # Convertir ObjectId a cadena
        return movie
    else:
        raise HTTPException(status_code=404, detail="Película no encontrada")

""" Buscar película por categoria """
@app.get('/movies/categoria/{categoria}', tags=['movies'])
def get_movie_by_category(categoria: str):
    movies_collection = app.mongodb_client["movies"]
    movies = movies_collection.find({"categoria": categoria})  # Buscar películas por categoría
    movie_list = []
    for movie in movies:
        movie["_id"] = str(movie["_id"])
        movie_list.append(movie)
    
    if len(movie_list) == 0:
        raise HTTPException(status_code=404, detail="No se encontraron películas en la categoría especificada")
    
    return movie_list

""" Insertar nueva pelicula """
@app.post('/movies', tags=['movies'], status_code=201)
def add_movie(movie: Movie):
    movies_collection = app.mongodb_client["movies"]
    movie_dict = movie.dict()  # Convertir la instancia de Movie a un diccionario
    result = movies_collection.insert_one(movie_dict)
    if result.inserted_id:
        return {"message": "Película agregada correctamente"}
    else:
        raise HTTPException(status_code=500, detail="Error al agregar la película")


""" Actualizar una película """
@app.put('/movies/{id}', tags=['movies'], status_code=200)
def update_movie(id: int, movie_data: Movie):
    movies_collection = app.mongodb_client["movies"]
    movie_dict = movie_data.dict()  
    result = movies_collection.update_one({"id": id}, {"$set": movie_dict})
    
    if result.matched_count == 1:
        return {"message": "Película actualizada correctamente"}
    elif result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    else:
        raise HTTPException(status_code=500, detail="Error al actualizar la película")

""" Eliminar una película """
@app.delete('/movies/{id}', tags=['movies'], status_code=200)
def delete_movie(id: int):
    movies_collection = app.mongodb_client["movies"]
    result = movies_collection.delete_one({"id": id})

    if result.deleted_count == 1:
        return {"message": "Película eliminada correctamente"}
    elif result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    else:
        raise HTTPException(status_code=500, detail="Error al eliminar la película")



