from flask import jsonify, request, Blueprint
from Controller.paciente import carregar_paciente, criar_paciente, atualizar_paciente, inativar_paciente, carregar_paciente_por_id, carregar_pacientes_por_id_usuario, cadastrar_anamnese, carregar_anamnese_por_id
from datetime import datetime, date

paciente_bp = Blueprint("paciente_bp", __name__)

@paciente_bp.route('/paciente', methods = ['GET'])
def get_paciente():
    pacientes = carregar_paciente()
    return jsonify(pacientes)

@paciente_bp.route('/paciente/anamnese/<int:cd_paciente>', methods = ['GET'])
def api_carregar_anamnese_por_id(cd_paciente):
    try:
        anamnese = carregar_anamnese_por_id(cd_paciente)
        if anamnese:
            return jsonify(anamnese)
        else:
            return jsonify({"error": "Paciente não encontrado!"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@paciente_bp.route('/paciente/<int:cd_paciente>', methods = ['GET'])
def api_carregar_paciente_por_id(cd_paciente):
    try:
        paciente = carregar_paciente_por_id(cd_paciente)
        if paciente:
            return jsonify(paciente)
        else:
            return jsonify({"error": "Paciente não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@paciente_bp.route('/paciente/por_usuario/<int:cd_usuario>', methods = ['GET'])
def api_carregar_paciente_por_usuario(cd_usuario):
    pacientes = carregar_pacientes_por_id_usuario(cd_usuario)
    return jsonify(pacientes)    

@paciente_bp.route('/paciente', methods = ['POST'])
def post_paciente():
    data = request.json
    try:
        return criar_paciente(
            nm_paciente = data.get('nm_paciente'),
            dt_nasc = data.get('dt_nasc'),
            sexo = data.get('sexo'),
            cd_genero = data.get('cd_genero'),
            tip_sang = data.get('tip_sang'),
            cd_usuario = data.get('cd_usuario'),
            cd_perfil = data.get('cd_perfil')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@paciente_bp.route('/paciente/<int:id>', methods = ['PUT'])
def put_pacientes(id):
    data = request.json
    return atualizar_paciente(id, **data)

@paciente_bp.route('/paciente/anamnese/<int:cd_paciente>', methods = ['PUT'])
def put_pacientes_anamnese_endpoint(cd_paciente):
    data = request.json
    return cadastrar_anamnese(cd_paciente, **data)

# @paciente_bp.route('/pacientes/<int:id>', methods = ['DELETE'])
# def deletar_paciente_fim(id):
#     deletar_paciente(id)
#     return jsonify({"message": "Pacientes deletado com sucesso!"})

@paciente_bp.route('/paciente/toggle/<int:id>', methods=['PUT'])
def put_inativar_paciente(id):
    return inativar_paciente(id)
