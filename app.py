from flask import Flask, request
from flask_jwt_extended.view_decorators import verify_jwt_in_request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
#----------------------------------------------------------------------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost:3306/f1_andrei'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY']='secret'
db = SQLAlchemy(app)
api = Api(app)
jwt=JWTManager(app)
##---------------------------------------------------------------------------------------
class Pilotos(db.Model):
    id_piloto=db.Column(db.Integer,primary_key=True, nullable=False)
    piloto=db.Column(db.String(70), nullable=False)
    equipo=db.Column(db.String(70), nullable=False)
    puntos=db.Column(db.Integer, nullable=False)
    
    def __repr__(self) :
        return "[Pilotos %s]" % str(self.id_piloto)
db.create_all()

class Escuderias(db.Model):
    id_equipo=db.Column(db.Integer,primary_key=True, nullable=False)
    equipo=db.Column(db.String(70), nullable=False)
    puntos_equipo=db.Column(db.Integer, nullable=False)
    
    def __repr__(self) :
        return "[Escuderias %s]" % str(self.id_equipo)
db.create_all()

class Carreras(db.Model):
    id_carrera=db.Column(db.Integer,primary_key=True, nullable=False)
    lugar=db.Column(db.String(70), nullable=False)
    posicion=db.Column(db.Integer, nullable=False)
    piloto=db.Column(db.String(70), nullable=False)
    puntos=db.Column(db.Integer, nullable=False)
    
    def __repr__(self) :
        return "[Carreras %s]" % str(self.id_carrera)
db.create_all()

class Usuarios(db.Model):
    id_usuario=db.Column(db.Integer,primary_key=True)
    usuario=db.Column(db.String(30))
    contrasena=db.Column(db.String(20))
    rol=db.Column(db.String(50))
    def __repr__(self) :
        return "[Usuarios %s]" % str(self.id_usuario)
db.create_all()
##-----------------------------------------------------------------------------
inicio_sesion=reqparse.RequestParser()
inicio_sesion.add_argument('Usuario',required=True)
inicio_sesion.add_argument('Contrasena',required=True)

crear_usuario=reqparse.RequestParser()
crear_usuario.add_argument('Usuario',required=True)
crear_usuario.add_argument('Contrasena',required=True)
crear_usuario.add_argument('Rol',required=True)

recuperar_contrasena=reqparse.RequestParser()
recuperar_contrasena.add_argument('Usuario',required=True)
##-----------------------------------------------------------------------------
class Login(Resource):
    def post(self):
        datos_usuario=inicio_sesion.parse_args()
        usuario= datos_usuario['Usuario']
        contrasena=datos_usuario['Contrasena']
        usuario_ingresado=Usuarios.query.filter_by(usuario=usuario).first()
        contrasena_ingresada=Usuarios.query.filter_by(contrasena=contrasena).first()
        if usuario_ingresado.contrasena==contrasena_ingresada.contrasena:
            token_acceso=create_access_token(identity=usuario_ingresado.rol)
            
            return {"response":token_acceso},200
            
        else:
            return {"response":"Datos incorrectos"},401

class Registro(Resource):
    def post(self):
        datos_usuario=crear_usuario.parse_args()
        nuevo_usuario=Usuarios(usuario=datos_usuario['Usuario'],contrasena=datos_usuario['Contrasena'],rol=datos_usuario['Rol'])
        db.session.add(nuevo_usuario)
        db.session.commit()
        return{'response':'Usuario creado'},
    
class RecuperarContrasena(Resource):
    def post(self):
        datos_usuario=recuperar_contrasena.parse_args()
        usuario_olvidado=Usuarios.query.filter_by(usuario=datos_usuario['Usuario']).first()
        if usuario_olvidado:
            return{"response":"Se ha enviado un mensaje a su correo electronico para restablecer su contraseña"}
        else:
            return {'response':"El usuario ingresado no existe"},404
    
class ActualizarToken(Resource):
    def get(self):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        token_acceso=create_access_token(identity=identity,fresh=False)
        return{'response':token_acceso}
##--------------------------------------------------------
class IndexRoute(Resource):
    def get(self):
        return {'response': 'Bienvenido al API de la F1'},200
##--------------------------------------------------------------------------------------------------------------------------
class IndexRoutePiloto(Resource):
    def get(self):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        all_pilotos = Pilotos.query.all()
        response=[]
        if all_pilotos:
            for pilotos in all_pilotos:
                response.append({
                    "Id del Piloto":pilotos.id_piloto,
                    "Piloto":pilotos.piloto,
                    "Equipo":pilotos.equipo,
                    "Puntos":pilotos.puntos,
                })
        return {'response':response},200

    def post(self):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        if identity=='admin':
            new_piloto=request.get_json()
            pilotos = Pilotos(piloto=new_piloto['Piloto'], equipo=new_piloto['Equipo'], puntos=new_piloto['Puntos'])
            db.session.add(pilotos)
            db.session.commit()
            return {"response":"¡Piloto registrado exitosamente!"}, 200
        else:
            return{'response':'Permisos necesarios para realizar esta accion'}

class PilotobyID(Resource):
    def get(self,id_piloto):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        piloto_id=Pilotos.query.filter_by(id_piloto=id_piloto).first()
        if piloto_id:
            return{'response':{
                "Id del Piloto":piloto_id.id_piloto,
                "Piloto":piloto_id.piloto,
                "Equipo":piloto_id.equipo,
                "Puntos":piloto_id.puntos,
            }},200
        else:
            return{"response":"Id de Piloto no registrada"},404
    
    def put(self,id_piloto):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        if identity=='admin':
            piloto_id=Pilotos.query.filter_by(id_piloto=id_piloto).first()
            if piloto_id:
                datos = request.get_json()
                piloto_id.piloto = datos['Piloto']
                piloto_id.equipo = datos['Equipo']
                piloto_id.puntos = datos['Puntos']
                db.session.commit()
                return {"response": "Piloto actualizado con exito!"}
            else:
                return{"response":"Datos no validos"},404
        else:
            return{'response':'Permisos necesarios para realizar esta accion'}


    def delete(self,id_piloto):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        if identity=='admin':
            piloto_id=Pilotos.query.filter_by(id_piloto=id_piloto).first()
            db.session.delete(piloto_id)
            db.session.commit()
            if piloto_id:
                return { "response": "Piloto con Id: {piloto_id}. Borrado exitosamente.".format(piloto_id=id_piloto)}, 200
            else:
                return{"response":"Id de Piloto no registrada, no se puede borrar"},404
        else:
            return{'response':'Permisos necesarios para realizar esta accion'}
##--------------------------------------------------------------------------------------------------------------------------
class IndexRouteEquipo(Resource):
    def get(self):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        all_equipos = Escuderias.query.all()
        response=[]
        if all_equipos:
            for equipos in all_equipos:
                response.append({
                    "Id del Equipo":equipos.id_equipo,
                    "Equipo":equipos.equipo,
                    "Puntos":equipos.puntos_equipo,
                })
        return {'response':response},200

    def post(self):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        if identity=='admin':
            new_equipo=request.get_json()
            escuderias = Escuderias(equipo=new_equipo['Equipo'], puntos_equipo=new_equipo['Puntos'])
            db.session.add(escuderias)
            db.session.commit()
            return {"response":"¡Equipo registrado exitosamente!"}, 200
        else:
            return{'response':'Permisos necesarios para realizar esta accion'}

class EquipobyID(Resource):
    def get(self,id_equipo):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        equipo_id=Escuderias.query.filter_by(id_equipo=id_equipo).first()
        if equipo_id:
            return{'response':{
                "Id del Equipo":equipo_id.id_equipo,
                "Equipo":equipo_id.equipo,
                "Puntos":equipo_id.puntos_equipo,
            }},200
        else:
            return{"response":"Id de Equipo no registrada"},404
    
    def put(self,id_equipo):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        if identity=='admin':
            equipo_id=Escuderias.query.filter_by(id_equipo=id_equipo).first()
            if equipo_id:
                datos = request.get_json()
                equipo_id.equipo = datos['Equipo']
                equipo_id.puntos_equipo = datos['Puntos']
                db.session.commit()
                return {"response": "Equipo actualizado con exito!"}
            else:
                return{"response":"Datos no validos"},404
        else:
            return{'response':'Permisos necesarios para realizar esta accion'}

    def delete(self,id_equipo):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        if identity=='admin':
            equipo_id=Escuderias.query.filter_by(id_equipo=id_equipo).first()
            db.session.delete(equipo_id)
            db.session.commit()
            if equipo_id:
                return { "response": "Equipo con Id: {equipo_id}. Borrado exitosamente.".format(equipo_id=id_equipo)}, 200
            else:
                return{"response":"Id de Equipo no registrada, no se puede borrar"},404
        else:
            return{'response':'Permisos necesarios para realizar esta accion'}
##--------------------------------------------------------------------------------------------------------------------------
class IndexRouteCarrera(Resource):
    def get(self):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        all_carreras = Carreras.query.all()
        response=[]
        if all_carreras:
            for carrera in all_carreras:
                response.append({
                    "Id de la carrera":carrera.id_carrera,
                    "Lugar":carrera.lugar,
                    "Posicion":carrera.posicion,
                    "Piloto":carrera.piloto,
                    "Puntos":carrera.puntos,
                })
        return {'response':response},200

    def post(self):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        if identity=='admin':
            new_carrera=request.get_json()
            carrera = Carreras(lugar=new_carrera['Lugar'], posicion=new_carrera['Posicion'], piloto=new_carrera['Piloto'], puntos=new_carrera['Puntos'])
            db.session.add(carrera)
            db.session.commit()
            return {"response":"Carrera registrada exitosamente!"}, 200
        else:
            return{'response':'Permisos necesarios para realizar esta accion'}

class CarrerabyID(Resource):
    def get(self,id_carrera):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        carrera_id=Carreras.query.filter_by(id_carrera=id_carrera).first()
        if carrera_id:
            return{'response':{
                "Id de la carrera":carrera_id.id_carrera,
                "Lugar":carrera_id.lugar,
                "Posicion":carrera_id.posicion,
                "Piloto":carrera_id.piloto,
                "Puntos":carrera_id.puntos,
            }},200
        else:
            return{"response":"Id de Carrera no registrada"},404
    
    def put(self,id_carrera):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        if identity=='admin':
            carrera_id=Carreras.query.filter_by(id_carrera=id_carrera).first()
            if carrera_id:
                datos = request.get_json()
                carrera_id.lugar = datos['Lugar']
                carrera_id.posicion = datos['Posicion']
                carrera_id.piloto = datos['Piloto']
                carrera_id.puntos = datos['Puntos']
                db.session.commit()
                return {"response": "Carrera actualizada con exito!"}
            else:
                return{"response":"Datos no validos"},404
        else:
            return{'response':'Permisos necesarios para realizar esta accion'}


    def delete(self,id_carrera):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        if identity=='admin':
            carrera_id=Carreras.query.filter_by(id_carrera=id_carrera).first()
            db.session.delete(carrera_id)
            db.session.commit()
            if carrera_id:
                return { "response": "Carrera con Id: {carrera_id}. Borrado exitosamente.".format(carrera_id=id_carrera)}, 200
            else:
                return{"response":"Id de carrera no registrada, no se puede borrar"},404
        else:
            return{'response':'Permisos necesarios para realizar esta accion'}

class CarrerabyPiloto(Resource):
    def get(self,piloto):
        verify_jwt_in_request()
        identity=get_jwt_identity()
        print(identity)
        carrera_id=Carreras.query.filter_by(piloto=piloto).first()
        if carrera_id:
            return{'response':{
                "Id de la carrera":carrera_id.id_carrera,
                "Lugar":carrera_id.lugar,
                "Posicion":carrera_id.posicion,
                "Piloto":carrera_id.piloto,
                "Puntos":carrera_id.puntos,
            }},200
        else:
            return{"response":"Id de Carrera no registrada"},404

api.add_resource(IndexRoute,'/')
api.add_resource(Login,'/login')
api.add_resource(Registro,'/registro')
api.add_resource(RecuperarContrasena,'/recuperarcontrasena')
api.add_resource(ActualizarToken,'/actualizartoken')
api.add_resource(IndexRoutePiloto,'/piloto')
api.add_resource(IndexRouteEquipo,'/escuderia')
api.add_resource(IndexRouteCarrera,'/carrera')
api.add_resource(PilotobyID,'/piloto/<int:id_piloto>')
api.add_resource(EquipobyID,'/escuderia/<int:id_equipo>')
api.add_resource(CarrerabyID,'/carrera/<int:id_carrera>')
api.add_resource(CarrerabyPiloto,'/carrera/<piloto>')

if __name__ == "__main__":
    app.run(debug=True)