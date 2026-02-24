# Importando bibliotecas necessárias.
import pandas as pd
import numpy as np
from unidecode import unidecode
import re

# Maneira visual de mostrar o progresso do Script. Aqui ele busca o arquivo, dá uma preview do arquivo antes dele ser
# tratado e começa a rodar os tratamentos.
print("- Processando vendas_raw.csv...")
df = pd.read_csv('vendas_raw.csv')
print(f"- Original: {df.shape}")

# 1. TRATAMENTOS NUMÉRICOS - Lógicas para tratar os números conforme foi pedido.
# Aqui a lógica é a mais complexa de todas as etapas.
# Primeiro ele preenche quantidades ausentes na coluna quantidade com 1 quando preco_unitario for igual a valor_total
# Depois ele cria uma máscara booleana para identificar linhas onde preco_unitario está nulo ou inconsistente
# (preço × quantidade ≠ total, tolerância 0.01) e depois recalcula apenas nessas linhas usando valor_total / quantidade.
# Por fim, só por garantia (apesar de isso não acontecer neste exercício), ele aplica mediana nas raras células que
# ainda podem estar vazias, garantindo dados coerentes para análises sem desestabilizar valores estatísticos.
df['quantidade'] = df['quantidade'].fillna(1.0)

mask_recalc = (
                      df['preco_unitario'].isna() |
                      (abs(df['preco_unitario'].fillna(0) * df['quantidade'] - df['valor_total'].fillna(0)) > 0.01)
              ) & (df['quantidade'] > 0) & (df['valor_total'] > 0)

df.loc[mask_recalc, 'preco_unitario'] = df.loc[mask_recalc, 'valor_total'] / df.loc[mask_recalc, 'quantidade']

for col in ['quantidade', 'preco_unitario', 'valor_total']:
    nulls = df[col].isna().sum()
    if nulls > 0:
        med = df[col].median()
        df[col] = df[col].fillna(med)

# Maneira visual de mostrar o Progresso do Script. Aqui ele mostra que terminamos de tratar os missings dos números.
print("- Numéricos tratados")


# 2. EMAIL LGPD - Lógica utilizada para censurar emails conforme foi pedido.
# Primeiro forçamos a célula para texto, verificamos se contém @ (se não tiver o código ignora),
# Se o email não existe, deixa igual. Se não, pode tratar ele censurando entre primeiro caractere e último antes do @.
def mask_email(email):
    if pd.isna(email):
        return email
    email = str(email)
    if '@' in email:
        local, domain = email.split('@', 1)
        if len(local) > 1:
            masked = local[0] + '*' * (len(local) - 2) + local[-1]
            return f"{masked}@{domain}"
    return email


df['email_cliente'] = df['email_cliente'].apply(mask_email)

print("- Emails censurados")

# 3. DATAS - Lógica utilizada para unificar formato de data conforme foi pedido.
def fix_date(date_str):
    if pd.isna(date_str):
        return pd.NaT
    s = str(date_str).strip()
    try:
        return pd.to_datetime(s, dayfirst=True)
    except:
        return pd.to_datetime(s, errors='coerce')


df['data_venda'] = df['data_venda'].apply(fix_date)
df['data_venda'] = df['data_venda'].dt.strftime('%Y-%m-%d')

print("- Datas unificadas")

# 4. CATEGORIAS - Formatando e unificando categorias de produtos conforme foi pedido.
# Aqui utilizei a biblioteca do RE (também conhecida como REGEX) só pra encontrar os textos.
# Nele eu não só encontro os possíveis nomes, mas também suas possíveis variáveis (como plurais) que podem (ou não)
# estar na planilha.
def clean_cat(cat):
    if pd.isna(cat):
        return 'Desconhecida'
    s = unidecode(str(cat).lower().strip())

    if re.search(r'movei(s?)', s):
        return 'Móveis'
    elif re.search(r'acess(or|ório|orios?)', s):
        return 'Acessórios'
    elif re.search(r'eletr[oô]n(?:ico|icos?)', s):
        return 'Eletrônicos'
    elif re.search(r'eletrodom(?:ést|est)icos?', s):
        return 'Eletrodomésticos'
    else:
        return str(cat).title()


df['categoria'] = df['categoria'].apply(clean_cat)

print("- Categorias corrigidas")

# 5. TEXTOS - Etapa extra que adicionei para não haver caracteres desnecessários (como espaço antes ou depois da célula)
# e que seja forçado como texto.

for col in ['cliente', 'produto', 'regiao']:
    df[col] = df[col].astype(str).str.strip()

print("- Textos devidamente formatados")
print("- Salvando...")

# SALVAR - Aqui eu crio um novo arquivo .csv para manipulação dos dados,
# mostro quantas linhas e colunas deu no total, mostro se tivemos "missings" (dados nulos)
# e por fim dou uma rápida preview das 5 primeiras linhas.
df.to_csv('vendas_dadostratados.csv', index=False)
print("\n- SALVO: vendas_dadostratados.csv")

print(f"- Final: {df.shape}")
print("- Nulos:", df.isna().sum().sum())
print("\n- Preview:")
print(df[['id_venda', 'data_venda', 'cliente', 'categoria', 'valor_total']].head())

# Adicionei essa etapa extra só pra exportar pra excel também que é muito útil.
print("- Exportando em arquivo Excel")
df.to_excel('vendas_dadostratados.xlsx', index=False)
print("\n- SALVO: vendas_dadostratados.xlsx")