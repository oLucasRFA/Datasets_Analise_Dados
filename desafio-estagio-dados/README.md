# Desafio Técnico: Estágio em Dados

## Feito por: Lucas Ramalho

Conteúdo:
	Esse repositório contém as seguintes pastas:
		- Consultas SQL (Pasta contendo consultas SQLs que respondem às questões de SQL)
		- Script Python (Pasta contendo o script python que transforma o .csv sujo em dois arquivos: .csv limpo e .xlsx limpo)
		- Dashboard Power BI (Pasta contendo um Dashboard em Power BI que analisa o excel gerado pelo .py dentro da pasta Script Python)
		- Dicionário de Dados (Pasta contendo uma tabela com dicionário de dados sobre o .csv)

Objetivos:
	- 1. Tratar arquivo CSV que continha histórico de vendas de uma empresa fictícia usando Python + Pandas.
	- 2. Colocar em um Banco de Dados e realizar 4 consultas pedidas pelo enunciado.
	- 3. Analisar em BI e gerar relatório com insights.

Desafios:
	- 1. Tratamento de Nulos: Identificar e tratar valores nulos.
	- 2. Anonimização (LGPD): Mascarar o campo email_cliente (ex: j***@email.com) para garantir a privacidade dos dados.
	- 3. Padronização de Datas: O campo data_venda possui diversos formatos. Converter todos para o padrão YYYY-MM-DD.
	- 4. Normalização de Categorias: Corrijir variações de texto (ex: "Eletrônicos", "eletronicos", "ELETRÔNICOS" devem ser a mesma coisa).
	- 5. Dicionário de Dados: Criar uma tabela simples descrevendo as colunas e seus tipos.

1. Lógica por trás do Python:

- 1.1 Nulos Numéricos:

	Implementei uma abordagem em 4 etapas para os campos numéricos:

	- Quando preco_unitario = valor_total, assume-se venda unitária. Então: se "quantidade" for nulo e notar-se preco_unitario = valor_total então quantidade = 1
	- Máscara booleana inteligente: Detecta inconsistências matemáticas onde |preco_unitario × quantidade - valor_total| > 0.01
	- Quando tiver quantidade e valor_total mas não tiver preco_unitario, então: preco_unitario = valor_total ÷ quantidade
	- Não tinha nesse exercício mas apliquei uma regra a missings excedentes: aplicar mediana pra pelo menos o valor não ser nulo.

- 1.2 Censurar emails conforme LGPD:

	Implementei uma maneira eficiente de censurar entre o primeiro e último caráctere antes do @ do email.

- 1.3 Unificar datas da venda:

	Implementei uma medida para transformar todas as interpretações de datas em YYYY-MM-DD, que é padrão de Banco de Dados.

- 1.4 Normalização de Categorias:

	Implementei uma medida (usando regex) que encontra textos e seus semelhantes (para além dos dados recebidos no exercício) e os unifica.

- 1.5 (ETAPA EXTRA) Forçar formatação e remoção de espaços antes ou depois dos nomes:

	Implementei, por precaução, uma parte do script que força os dados das colunas 'cliente', 'produto', 'regiao' na formatação de texto.
	Assim previnindo evitar espaços ou formatação incorreta (o que gera células repetidas nos filtros do excel, por exemplo).

- 1.6 Dicionário de Dados:
	
	Dicionário de Dados que descreve cada tipo, descrição e o tratamento que apliquei pra cada coluna pode ser encontrado no git como Dicionario_Dados.xlsx

2. Ambientação e manipulação dos dados em SQL:

- 2.1 Criação da Tabela:

	Segue abaixo criação da tabela com devidas chaves, junto com uma linha inserida de exemplo.
```
	CREATE TABLE vendas_dadostratados (id_venda INTEGER,data_venda DATE,cliente TEXT,email_cliente TEXT,produto TEXT,categoria TEXT,quantidade REAL,preco_unitario REAL,valor_total REAL,regiao TEXT);
	INSERT INTO vendas_dadostratados ('id_venda','data_venda','cliente','email_cliente','produto','categoria','quantidade','preco_unitario','valor_total','regiao') VALUES 
	('405','2023-06-10','Luiz Gustavo Cavalcante','n***********y@example.com','Armário','Móveis','8.0','4412.33','35298.64','Centro-Oeste'), 
```
- 2.2 Consulta 1 - Faturamento Total por Categoria:
```
	SELECT 
		categoria,
		ROUND(SUM(valor_total), 2) as faturamento_total
	FROM vendas_dadostratados
	GROUP BY categoria
	ORDER BY faturamento_total DESC;
```
- 2.3 Consulta 2 - Região que Mais Vendeu Qtd de Produtos:
```
	SELECT 
		regiao,
		SUM(quantidade) as total_produtos
	FROM vendas_dadostratados
	GROUP BY regiao
	ORDER BY total_produtos DESC
	LIMIT 1;
```
- 2.4 Consulta 3 - Top 5 Clientes que Mais Gastaram:
```
	SELECT 
		cliente,
		ROUND(SUM(valor_total), 2) as total_gasto
	FROM vendas_dadostratados
	GROUP BY cliente
	ORDER BY total_gasto DESC
	LIMIT 5;
```
- 2.5 Consulta 4 - Ticket Médio por Venda:
```
	SELECT 
		ROUND(AVG(valor_total), 2) as ticket_medio
	FROM vendas_dadostratados;
```
- 3. Visualização de Dados e Insights:

	Utilizando o Power BI gerei um Dashboard que contém a Visão Geral e a tabela de dados tratada para ser exportada.
	![Dashboard Power BI](desafio-estagio-dados/Dashboard%20Power%20BI/dashboard_vendas.png)
	Dentro da Visão Geral se observou os seguintes insights:

- 3.1 Estabilidade com Picos Sazonais:
	
	Faturamento trimestral estável entre R$1,1-1,7 milhões, sem oscilações sazonais negativas drásticas.
	Os picos identificados representam oportunidades para replicação de campanhas comerciais bem-sucedidas.
	Esta previsibilidade facilita planejamento de caixa e gestão de estoque.

- 3.2 Distribuição Geográfica Equilibrada:

	As cinco regiões contribuem similarmente para o faturamento total, reduzindo risco de dependência geográfica.
	Regiões ligeiramente acima da média (Centro-Oeste e Norte) devem ser estudadas para replicação de estratégias em áreas subperformáticas,
	se atentando para atender às necessidades de cada tipo de produto para cada região.

- 3.3 Mix de Produtos Resiliente:

	Distribuição saudável com relevância para Acessórios e Móveis.
	Ter um portfólio diversificado mitiga riscos setoriais, e as categorias menores são oportunidades de crescimento via mix ou reposicionamento.

- 4. (ETAPA EXTRA) Sugestão de melhorias:

- 4.1 Insight 1:

	Acompanhar faturamentos trimestrais mais de perto a fim de otimizá-las realizando a análise de causa raiz.
	Deve-se mapear promoções, datas comemorativas e condições macroeconômicas dos trimestres de pico.
	Além disso acompanhar cada campanha de marketing por perto e identificar leads que geraram em conversão de cliente.

- 4.2 Insight 2:

	O faturamento por região está bem equilibrado, porém deve-se acompanhar e mapear os resultados positivos das regiões Centro-Oeste e Norte
	e depois replicar as outras regiões que podem estar sendo sub-aproveitadas.
	Recomenda-se fazer um benchmarking, ou troca de conhecimento entre as regiões ou até mesmo fazer uma pesquisa de mercado de perfil de cliente
	para entender melhor as necessidades de cada região.

- 4.3 Insight 3:

	Acessórios e Móveis estão dominando, porém deve-se olhar para Eletrônicos e Eletrodomésticos também e criar planos de ação que converta mais
	clientes. Seja por campanhas de marketing, preço mais atrativo, vantagens para clientes ao comprar um produto ou desconto por troca de produto
	antigo (estratégia comum com eletrônicos). Tudo isso deve ser acompanhado com um CRM eficaz.


