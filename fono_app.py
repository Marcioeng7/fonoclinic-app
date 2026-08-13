import streamlit as st
from datetime import date

st.title("🩺 Anamnese Infanto-Juvenil — FonoClinic")

# Função auxiliar para criar perguntas Sim/Não com padrão neutro/em branco
def pergunta_sim_nao(label, key, info_adicional=False, label_adicional="Detalhes"):
    col1, col2 = st.columns([1, 2])
    with col1:
        # Opções com string vazia primeiro para vir como "default" sem marcar nada
        resposta = st.radio(label, ["", "Sim", "Não"], index=0, key=key, horizontal=True)
    with col2:
        detalhe = ""
        if info_adicional and resposta == "Sim":
            detalhe = st.text_input(f"{label_adicional} ({label})", key=f"{key}_det")
    return resposta, detalhe

# --- SEÇÃO 1: DADOS IDENTIFICAÇÃO ---
with st.expander("👤 Dados de Identificação", expanded=True):
    col1, col2, col3 = st.columns([3, 1, 1])
    nome = col1.text_input("Nome Completo do Paciente")
    data_nasc = col2.date_input("Data de Nasc.", value=None, min_value=date(2000, 1, 1))
    sexo = col3.selectbox("Sexo", ["", "Masculino", "Feminino", "Outro"])
    
    col4, col5, col6 = st.columns([2, 2, 1])
    naturalidade = col4.text_input("Naturalidade")
    apelido = col5.text_input("Apelido")
    estuda = col6.selectbox("Estuda?", ["", "Sim", "Não"])
    
    if estuda == "Sim":
        col7, col8 = st.columns(2)
        turma = col7.text_input("Turma")
        turno = col8.selectbox("Turno", ["", "Manhã", "Tarde", "Integral"])
        
    col9, col10 = st.columns([3, 2])
    responsavel = col9.text_input("Nome do Responsável Legal")
    profissao = col10.text_input("Profissão do Responsável")
    
    col11, col12 = st.columns(2)
    telefone = col11.text_input("Telefone de Contato")
    emergencia = col12.text_input("Em caso de emergência ligar para:")

# --- SEÇÃO 2: QUEIXA E HISTÓRICO CLÍNICO ---
with st.expander("📋 Queixa Principal e Histórico Clínico", expanded=False):
    queixa = st.text_area("Queixa Principal (O que te trouxe aqui?)")
    
    resp_terapia, quais_terapias = pergunta_sim_nao("Faz terapia com outros profissionais?", "terapia", True, "Quais?")
    diagnostico = st.text_input("Tem diagnóstico fechado? (Se sim, qual?)")
    
    resp_alergico, quais_alergias = pergunta_sim_nao("É Alérgico?", "alergia", True, "Quais alergias?")
    resp_medica, quais_meds = pergunta_sim_nao("Toma alguma medicação?", "medicao", True, "Quais medicações e dosagem?")
    
    com_quem_passa_tempo = st.text_input("Com quem passa a maior parte do tempo?")
    pergunta_sim_nao("Pratica ou gosta de esportes?", "esportes")

# --- SEÇÃO 3: DESENVOLVIMENTO & LINGUAGEM ---
with st.expander("🗣️ Desenvolvimento de Linguagem e Interação", expanded=False):
    pergunta_sim_nao("É Verbal?", "verbal")
    pergunta_sim_nao("Interage bem socialmente?", "interage")
    pergunta_sim_nao("Olha no olho ao ser chamado?", "olha_olho")
    pergunta_sim_nao("Atende a comandos? (Ex: pega isso aqui e coloca na mesa)", "comandos")
    pergunta_sim_nao("Sabe expressar seus desejos/sentimentos?", "expressar")
    pergunta_sim_nao("Sabe o seu próprio nome?", "sabe_nome")
    pergunta_sim_nao("Sabe o nome dos responsáveis?", "nome_resp")
    
    st.subheader("Conhecimentos Pedagógicos Básicos")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1: st.radio("Sabe as vogais?", ["", "Sim", "Não"], key="vogais")
    with col_p2: st.radio("Sabe as cores?", ["", "Sim", "Não"], key="cores_sabe")
    with col_p3: st.radio("Sabe o alfabeto?", ["", "Sim", "Não"], key="alfabeto")
    with col_p4: st.radio("Fala/entende inglês?", ["", "Sim", "Não"], key="ingles")

    st.subheader("Marcos de Nomeação e Identificação")
    pergunta_sim_nao("Nomeia as cores?", "nomeia_cores")
    pergunta_sim_nao("Nomeia objetos comuns?", "nomeia_objetos")
    pergunta_sim_nao("Identifica figuras/imagens?", "identifica_figuras")
    pergunta_sim_nao("Nomeia animais?", "nomeia_animais")

# --- SEÇÃO 4: ROTINA, COMPORTAMENTO & COMPORTAMENTOS ATÍPICOS ---
with st.expander("🧠 Comportamento e Rotina Diária", expanded=False):
    pergunta_sim_nao("Apresenta Seletividade alimentar?", "seletividade")
    pergunta_sim_nao("Dorme bem?", "dorme_bem")
    pergunta_sim_nao("Gosta de música?", "musica")
    
    resp_desenho, quais_desenhos = pergunta_sim_nao("Assiste desenho animado?", "desenho", True, "Quais desenhos assiste?")
    
    # Comportamentos de Alerta / Atípicos
    st.markdown("---")
    st.write("**Sinais de Alerta / Comportamentos Atípicos:**")
    pergunta_sim_nao("Apresenta Estereotipia?", "estereotipia")
    pergunta_sim_nao("Apresenta Ecolalia?", "ecolalia")
    pergunta_sim_nao("Possui Fixação em algo específico?", "fixacao")
    pergunta_sim_nao("Apresenta alguma Dificuldade motora?", "dif_motora")
    pergunta_sim_nao("Pratica Auto-agressão?", "auto_agressao")
    
    resp_agressivo, quando_agressivo = pergunta_sim_nao(
        "É Agressivo com os outros?", "agressivo_outros", True, "Em quais momentos?"
    )
    pergunta_sim_nao("Gosta de animais?", "gosta_animais")

# --- SEÇÃO 5: HISTÓRICO DE AUTONOMIA & INFÂNCIA ---
with st.expander("🚽 Autonomia e Histórico de Desenvolvimento Inicial", expanded=False):
    pergunta_sim_nao("Usa Fralda?", "fralda")
    pergunta_sim_nao("Sabe pedir para ir ao banheiro?", "banheiro")
    pergunta_sim_nao("Se veste sozinho?", "veste_sozinho")
    
    st.markdown("---")
    col_parto, col_perfil = st.columns(2)
    with col_parto:
        parto = st.radio("Tipo de Parto:", ["", "Cesária", "Normal"], key="parto")
        intercorrencia = st.text_input("Alguma intercorrência no parto?")
    with col_perfil:
        # Multi-seleção para características de comportamento
        perfil_comportamental = st.multiselect(
            "Ele(a) é predominantemente:",
            ["Agitado", "Tranquilo", "Inseguro", "Impaciente"]
        )
        
    amamentacao = st.text_input("Ele(a) mamou peito ou fórmula?")
    pergunta_sim_nao("Usou e ainda usa chupeta, dedo ou mamadeira?", "chupeta_dedo")
    
    brincadeiras = st.text_area("O que ele(a) gosta de brincar?")
    hobbies = st.text_area("O que ele(a) mais gosta de fazer?")

# --- ASSINATURA ---
st.markdown("---")
realizada_com = st.text_input("Anamnese realizada com (Acompanhante/Fonte das informações):")
st.caption("Avaliação registrada por: Michelle Neves - Estagiária de Fonoaudiologia")

if st.button("Salvar Anamnese Expandida"):
    # Aqui entra o seu código de validação e salvamento no banco de dados / estado
    st.success("Anamnese salva localmente com sucesso!")
