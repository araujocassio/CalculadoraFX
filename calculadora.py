import streamlit as st
import requests

# Funções auxiliares
def obter_cotacao(par_moedas):
    """
    Obtém a cotação para o par de moedas especificado.
    """
    base, quote = par_moedas.split('/')
    url = 'https://openexchangerates.org/api/latest.json'
    params = {
        'app_id': st.secrets['API_key'],  # Substitua pela sua chave da API
        'symbols': f"{base},{quote}"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise ValueError("Erro ao obter a cotação. Verifique sua API Key e a conexão com a internet.")

    data = response.json()
    rates = data.get('rates', {})
    if base not in rates or quote not in rates:
        raise ValueError(f"Cotações para {par_moedas} não encontradas.")

    # Retorna a taxa de câmbio base/quote
    return rates[quote] / rates[base]

def calcular_lote_e_risco(risco_brl, par_moedas, pips):
    """
    Calcula o tamanho do lote diretamente pelo risco em USD e pips ajustados.
    """
    # Converter BRL para USD
    taxa_brl_usd = obter_cotacao('USD/BRL')
    risco_usd = risco_brl / taxa_brl_usd

    # Ajustar o tamanho do stop com 15% de margem
    pips_ajustado = pips * 1.15

    # Calcula o tamanho do lote
    tamanho_lote = risco_usd / pips_ajustado

    return tamanho_lote, risco_usd, pips_ajustado

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Calculadora de Lote e Risco",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Cabeçalho da página
st.title("📊 Calculadora de Lote e Risco")

# Formulário principal
st.markdown("---")
st.subheader("🛠 Configurações da Operação")
col1, col2, col3 = st.columns(3)

with col1:
    risco_brl = st.number_input(
        "💰 Risco em BRL:", min_value=0.0, step=0.01, value=100.0,
        help="Quantia em reais que você está disposto a arriscar."
    )

with col2:
    par_moedas_input = st.text_input(
        "🌐 Par de Moedas:", value="AUDUSD",
        help="Informe o par no formato BASEQUOTE (ex.: USDJPY)."
    ).upper()
    par_moedas = f"{par_moedas_input[:3]}/{par_moedas_input[3:]}" if len(par_moedas_input) == 6 else par_moedas_input

with col3:
    pips = st.number_input(
        "📉 Stop Loss (Pips):", min_value=1.0, step=1.0, value=100.0,
        help="Tamanho do stop loss em pips."
    )

# Botão principal
calcular = st.button("🔍 Calcular")

# Resultados
st.markdown("---")
st.subheader("📈 Resultados do Cálculo")

if calcular:
    try:
        # Realizar o cálculo
        tamanho_lote, risco_usd, pips_ajustado = calcular_lote_e_risco(risco_brl, par_moedas, pips)

        # Exibir os resultados
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📏 Tamanho do Lote", f"{tamanho_lote:.2f}")
        with col2:
            st.metric("💵 Risco em USD", f"${risco_usd:.2f}")

        st.success("Cálculo realizado com sucesso! Confira os resultados acima.")

    except ValueError as e:
        st.error(f"❌ Erro: {e}")
    except Exception as e:
        st.error(f"❌ Erro inesperado: {e}")
else:
    st.info("Preencha os parâmetros e clique em 'Calcular' para visualizar os resultados.")
