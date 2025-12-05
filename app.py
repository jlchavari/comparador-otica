import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA (WIDE MODE) ---
st.set_page_config(layout="wide", page_title="Comparador Óptico Pro", page_icon="👓")

# ==========================================
# ⚙️ CONFIGURAÇÕES GERAIS
# ==========================================
# COLE O LINK DA SUA PLANILHA AQUI DENTRO DAS ASPAS:
URL_DA_SUA_PLANILHA = "https://docs.google.com/spreadsheets/d/1Zx1X9OwPiFYpsanXPzdCH9A919Brek7txZjiXz1m4Tk/edit?gid=0#gid=0"

# --- CSS PERSONALIZADO (DESIGN) ---
st.markdown("""
<style>
    /* Fundo geral mais limpo */
    .main {background-color: #f8f9fa;}
    
    /* Estilo dos Títulos das Lentes */
    .lens-header {
        color: #154c79;
        font-size: 28px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 10px;
        border-bottom: 2px solid #154c79;
    }
    
    /* Cards brancos para as lentes */
    .lens-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Destaque para o Diferencial */
    .benefit-box {
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 10px;
        border-radius: 8px;
        border-left: 5px solid #2196f3;
        font-size: 14px;
        margin-top: 10px;
    }
    
    /* Preço Grande */
    .price-tag {
        font-size: 32px;
        color: #2e7d32;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🛠️ FUNÇÕES DO SISTEMA
# ==========================================

@st.cache_data(ttl=60)
def load_data(sheet_url):
    # Lógica de proteção contra link vazio
    if not sheet_url or "google" not in sheet_url:
        return None
        
    try:
        # Tratamento do Link para CSV
        if "/edit" in sheet_url:
            base_url = sheet_url.split("/edit")[0]
            csv_url = f"{base_url}/export?format=csv"
        else:
            csv_url = sheet_url
            
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

# Função auxiliar para mostrar imagem com segurança
def mostrar_imagem(url_imagem):
    if pd.notna(url_imagem) and str(url_imagem).startswith("http"):
        try:
            st.image(url_imagem, use_container_width=True)
        except:
            st.warning("⚠️ Imagem indisponível")
    else:
        # Placeholder (Espaço vazio elegante se não tiver imagem)
        st.markdown("<div style='height:200px; background-color:#eee; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#999;'>Sem Imagem</div>", unsafe_allow_html=True)

# ==========================================
# 🔐 BARRA LATERAL (LOGIN)
# ==========================================
st.sidebar.title("🔐 Acesso Restrito")
senha = st.sidebar.text_input("Senha de Acesso", type="password")

nivel_acesso = None

if senha == "admin123":
    nivel_acesso = "admin"
    st.sidebar.success("✅ Modo Administrador")
elif senha == "venda2025":
    nivel_acesso = "vendedor"
    st.sidebar.info("👤 Modo Vendedor")
else:
    st.warning("🔒 Faça login para iniciar o sistema.")
    st.stop()

# ==========================================
# 🚀 APLICATIVO PRINCIPAL
# ==========================================

# Carrega os dados (Usando o link fixo ou um campo de backup)
df = load_data(URL_DA_SUA_PLANILHA)

if df is None:
    st.error("⚠️ Configure o link da planilha no código (variável URL_DA_SUA_PLANILHA)")
    novo_link = st.text_input("Ou cole um link temporário aqui:")
    if novo_link:
        df = load_data(novo_link)
    else:
        st.stop()

# Cabeçalho do Site
st.title("👓 Comparador de Lentes")
st.markdown("---")

col1, col_div, col2 = st.columns([1, 0.1, 1]) # Cria uma coluna fininha no meio para separar

# --- COLUNA ESQUERDA: LENTE PRINCIPAL ---
with col1:
    st.markdown("<div class='lens-card'>", unsafe_allow_html=True) # Início do Card Visual
    
    st.markdown("<div class='lens-header'>Lente Referência</div>", unsafe_allow_html=True)
    
    # Filtros (Agora mais limpos)
    c1, c2 = st.columns(2)
    with c1:
        marca_1 = st.selectbox("Marca", df['Marca'].unique())
    with c2:
        df_marca_1 = df[df['Marca'] == marca_1]
        material_1 = st.selectbox("Material", df_marca_1['Material'].unique())
    
    df_material_1 = df_marca_1[df_marca_1['Material'] == material_1]
    tratamento_1 = st.selectbox("Tratamento", df_material_1['Tratamento'].unique())
    
    # Pega os dados
    try:
        lente_1 = df_material_1[df_material_1['Tratamento'] == tratamento_1].iloc[0]
        
        # Nome Grande
        st.markdown(f"### {lente_1['Nome']}")
        
        # Imagem
        mostrar_imagem(lente_1['Imagem'])
        
        # Diferencial (Mantive aqui também para destaque visual rápido)
        st.markdown(f"<div class='benefit-box'>⭐ {lente_1['Beneficios']}</div>", unsafe_allow_html=True)
        st.write("") # Espaço
        
        # Preço
        st.caption("Preço de Venda Sugerido:")
        st.markdown(f"<div class='price-tag'>R$ {lente_1['Preco_Venda']}</div>", unsafe_allow_html=True)
        
        if nivel_acesso == "admin":
            st.error(f"🔒 Custo: R$ {lente_1['Preco_Custo']}")
            
    except IndexError:
        st.warning("Combinação não encontrada.")
        st.stop()
        
    st.markdown("</div>", unsafe_allow_html=True) # Fim do Card

# --- COLUNA DIREITA: CONCORRENTE ---
with col2:
    st.markdown("<div class='lens-card'>", unsafe_allow_html=True) # Início do Card Visual
    
    st.markdown("<div class='lens-header'>Concorrente</div>", unsafe_allow_html=True)
    
    # Lógica de Busca Automática
    grupo_alvo = lente_1['Grupo']
    df_concorrentes = df[(df['Grupo'] == grupo_alvo) & (df['Nome'] != lente_1['Nome'])]
    
    if df_concorrentes.empty:
        st.info("💡 Nenhuma concorrente direta cadastrada neste grupo.")
        lente_2 = None
    else:
        # Selectbox Inteligente
        lista_opcoes = df_concorrentes.apply(lambda x: f"{x['Marca']} - {x['Nome']}", axis=1)
        escolha = st.selectbox("Comparar com:", lista_opcoes)
        
        # Recupera os dados da escolha
        # (Truque para pegar a linha certa baseada no texto do selectbox)
        idx_escolhido = df_concorrentes.apply(lambda x: f"{x['Marca']} - {x['Nome']}", axis=1).values.tolist().index(escolha)
        lente_2 = df_concorrentes.iloc[idx_escolhido]
        
        # Exibição
        st.markdown(f"### {lente_2['Nome']}")
        
        mostrar_imagem(lente_2['Imagem'])
        
        st.markdown(f"<div class='benefit-box'>✅ {lente_2['Beneficios']}</div>", unsafe_allow_html=True)
        st.write("")
        
        st.caption("Preço de Venda Sugerido:")
        st.markdown(f"<div class='price-tag'>R$ {lente_2['Preco_Venda']}</div>", unsafe_allow_html=True)
        
        if nivel_acesso == "admin":
            st.error(f"🔒 Custo: R$ {lente_2['Preco_Custo']}")

    st.markdown("</div>", unsafe_allow_html=True) # Fim do Card

# ==========================================
# 📊 TABELA COMPARATIVA TÉCNICA (ATUALIZADA)
# ==========================================
if lente_2 is not None:
    st.markdown("### 🔍 Comparativo Técnico")
    
    # Cria um Dataframe só para visualização limpa
    # MUDANÇA AQUI: Troquei 'Grupo de Performance' por 'Principais Benefícios'
    dados_comparacao = {
        "Característica": ["Marca", "Material (Índice)", "Tratamento", "Principais Benefícios"],
        f"{lente_1['Nome']}": [lente_1['Marca'], lente_1['Material'], lente_1['Tratamento'], lente_1['Beneficios']],
        f"{lente_2['Nome']}": [lente_2['Marca'], lente_2['Material'], lente_2['Tratamento'], lente_2['Beneficios']]
    }
    
    df_compare = pd.DataFrame(dados_comparacao)
    
    # Mostra tabela sem o índice numérico lateral e com largura total
    st.table(df_compare.set_index("Característica"))

# Rodapé
st.markdown("---")
st.caption("Uso Exclusivo do MDO Botucatu e Jau")


