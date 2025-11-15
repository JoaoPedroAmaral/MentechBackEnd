from flask import Flask
from flask_cors import CORS
from Routes.transtornoRoutes import transtorno_bp
from Routes.subTipoTranstornoRoutes import subtipo_transtorno_bp
from Routes.metaRoutes import meta_bp
from Routes.pacienteRoutes import paciente_bp
from Routes.paciente_medicamentoRoutes import paciente_medicamento_bp
from Routes.paciente_metaRoutes import paciente_meta_bp
from Routes.patologiaRoutes import patologia_bp
from Routes.prontuarioRoutes import prontuario_bp
from Routes.atividadeRoutes import atividade_bp
from Routes.criterioDiagnosticoRoutes import criterio_diagnostico_bp
from Routes.enderecoRoutes import endereco_bp
from Routes.gravidadeRoutes import gravidade_bp
from Routes.responsavelRoutes import responsavel_bp
from Routes.pacienteTranstornoRoutes import pacienteTranstorno_bp
from Routes.usuario import usuario_bp
from Routes.mensagensRoutes import mensagem_bp
from Routes.telefoneRoutes import telefone_bp
from Routes.medicamentoRoutes import medicamento_bp
from Routes.generoRoutes import genero_bp
from Routes.alterarSenhaRoutes import alterar_senha_bp
from Routes.comportamento_pacienteRoutes import comportamento_paciente_bp
from Routes.percent_atividadesRoutes import percent_atividade_bp
from Routes.anamneseRoutes import anamnese_bp
from Routes.bdRoutes import bd_bp
from Routes.agendamento import agendamento_bp



app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

app.register_blueprint(alterar_senha_bp)
app.register_blueprint(genero_bp)
app.register_blueprint(transtorno_bp)
app.register_blueprint(subtipo_transtorno_bp)
app.register_blueprint(meta_bp)
app.register_blueprint(paciente_bp)
app.register_blueprint(paciente_medicamento_bp)
app.register_blueprint(paciente_meta_bp)
app.register_blueprint(patologia_bp)
app.register_blueprint(prontuario_bp)
#app.register_blueprint(prontuario_patologia_bp)
app.register_blueprint(atividade_bp)
app.register_blueprint(criterio_diagnostico_bp)
#app.register_blueprint(diagnostico_diferencial_bp)
app.register_blueprint(endereco_bp)
app.register_blueprint(gravidade_bp)
app.register_blueprint(responsavel_bp)
app.register_blueprint(pacienteTranstorno_bp)
app.register_blueprint(usuario_bp)
app.register_blueprint(mensagem_bp)
app.register_blueprint(telefone_bp)
app.register_blueprint(medicamento_bp)
app.register_blueprint(comportamento_paciente_bp)
app.register_blueprint(percent_atividade_bp)
app.register_blueprint(anamnese_bp)
app.register_blueprint(bd_bp)
app.register_blueprint(agendamento_bp)


if __name__ == "__main__":
    app.run(debug=True)

