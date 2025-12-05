import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Comparador Óptico")

# --- CSS PARA ESTILO VISUAL ---
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0;}
    .lens-title {color: #2E86C1; font-size: 24px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE CARREGAMENTO CORRIGIDA ---
@st.cache_data(ttl=60)
def load_data(sheet_url):
    # 1. Verifica se é um link do Google
    if "docs.google.com/spreadsheets" not in sheet_url:
        st.error("Erro: O link não parece ser do Google Sheets.")
        st.stop()
    
    # 2. Transforma qualquer link de visualização em link de exportação CSV
    # A lógica aqui é: pega tudo antes de "/edit" e adiciona "/export?format=csv"
    try:
        base_url = sheet_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        
        # Lê o CSV
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"Erro ao processar o link. Detalhe: {e}")
        st.stop()
# --- SIDEBAR: LOGIN E CONFIGURAÇÃO ---
st.sidebar.title("🔐 Acesso")
senha = st.sidebar.text_input("Digite sua senha", type="password")

nivel_acesso = None

# DEFINA SUAS SENHAS AQUI
if senha == "admin123":
    nivel_acesso = "admin"
    st.sidebar.success("Modo Administrador (Custos Visíveis)")
elif senha == "venda2025":
    nivel_acesso = "vendedor"
    st.sidebar.info("Modo Vendedor (Apenas Venda)")
else:
    st.warning("Por favor, faça login para acessar.")
    st.stop() # Para o código aqui se não tiver senha

# --- CARREGAMENTO DA PLANILHA ---
# Substitua este link pelo link da SUA planilha (tem que estar pública para leitura ou configurar secrets depois)
# Para testar rápido: Deixe sua planilha como "Qualquer pessoa com o link pode ver"
sheet_url = st.text_input("Cole o Link da sua Planilha Google aqui (ou fixe no código):")

if not sheet_url:
    st.info("Cole o link da planilha acima para começar.")
    st.stop()

# ... trecho anterior do código ...
try:
    df = load_data(sheet_url)
    
    # ADICIONE ESTAS LINHAS AQUI PARA TESTE:
#    st.write("👀 Espiando os dados que chegaram:")
#   st.write(df.head()) # Mostra as 5 primeiras linhas
 #   st.write(df.columns) # Mostra os nomes das colunas que o Python leu
    
except:
    # ... resto do código ...
    st.error("Erro ao ler a planilha. Verifique se o link está correto e se o compartilhamento está público.")
    st.stop()

st.title("👓 Comparador de Lentes")
st.markdown("---")

# --- SELEÇÃO DA LENTE PRINCIPAL (ESQUERDA) ---
col1, col2 = st.columns(2)

with col1:
    st.header("Lente Referência")
    
   # Filtros em cascata
    marca_1 = st.selectbox("Selecione a Marca", df['Marca'].unique())
    
    df_marca_1 = df[df['Marca'] == marca_1]
    material_1 = st.selectbox("Selecione o Material", df_marca_1['Material'].unique())
    
    # LINHA CORRIGIDA ABAIXO:
    df_material_1 = df_marca_1[df_marca_1['Material'] == material_1]
    
    tratamento_1 = st.selectbox("Selecione o Tratamento", df_material_1['Tratamento'].unique())
    
    # Localiza a linha exata da lente escolhida
    lente_1 = df_material_1[df_material_1['Tratamento'] == tratamento_1].iloc[0]
    
    # --- EXIBIÇÃO LADO ESQUERDO ---
    st.markdown(f"<div class='lens-title'>{lente_1['Nome']}</div>", unsafe_allow_html=True)
    
    # Imagem com proteção contra erros
    imagem_url = lente_1['Imagem']
    if pd.notna(imagem_url) and str(imagem_url).startswith("http"):
        try:
            st.image(imagem_url, use_container_width=True)
        except:
            st.warning("⚠️ Erro ao carregar imagem (Link inválido)")
    else:
        st.info("Sem imagem cadastrada")
    
    # Preços
    st.metric(label="Preço de Venda", value=f"R$ {lente_1['Preco_Venda']}")
    
    if nivel_acesso == "admin":
        st.markdown(f"🔒 **Custo:** R$ {lente_1['Preco_Custo']}")


# --- SELEÇÃO DA LENTE CONCORRENTE (DIREITA) ---
with col2:
    st.header("Comparativo / Concorrente")
    
    # A MÁGICA: Filtra apenas lentes do mesmo GRUPO da lente 1
    grupo_alvo = lente_1['Grupo']
    df_concorrentes = df[(df['Grupo'] == grupo_alvo) & (df['Nome'] != lente_1['Nome'])]
    
    if df_concorrentes.empty:
        st.warning("Não encontrei concorrentes diretos cadastrados neste grupo.")
    else:
        # Cria uma lista de nomes amigáveis para escolher
        lista_concorrentes = df_concorrentes.apply(lambda x: f"{x['Marca']} - {x['Nome']} ({x['Material']})", axis=1)
        escolha_concorrente = st.selectbox("Escolha com quem comparar:", lista_concorrentes)
        
        # Pega os dados da escolha
        # (Lógica simples para recuperar a linha baseada na seleção)
        marca_sel = escolha_concorrente.split(" - ")[0]
        lente_2 = df_concorrentes[df_concorrentes.apply(lambda x: f"{x['Marca']} - {x['Nome']} ({x['Material']})", axis=1) == escolha_concorrente].iloc[0]

        # --- EXIBIÇÃO LADO DIREITO ---
        st.markdown(f"<div class='lens-title'>{lente_2['Nome']}</div>", unsafe_allow_html=True)
        
        # Imagem com proteção contra erros
    imagem_url = lente_2['Imagem']
    if pd.notna(imagem_url) and str(imagem_url).startswith("http"):
        try:
            st.image(imagem_url, use_container_width=True)
        except:
            st.warning("⚠️ Erro ao carregar imagem (Link inválido)")
    else:
        st.info("Sem imagem cadastrada")
            
        st.success(f"**Diferencial:** {lente_2['Beneficios']}")
        
        st.metric(label="Preço de Venda", value=f"R$ {lente_2['Preco_Venda']}")
        
        if nivel_acesso == "admin":
            st.markdown(f"🔒 **Custo:** R$ {lente_2['Preco_Custo']}")

# --- RODAPÉ ---
st.markdown("---")
st.caption("Sistema Interno de Comparação - Mercadão dos Óculos (Uso Exclusivo)")





