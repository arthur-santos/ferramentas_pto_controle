# Conjunto de ferramentas para medição
Conjunto de ferramentas em Python que automatizam parte do processo de processamento e controle de qualidade da medição de pontos de controle.
As ferramentas estão disponibilizadas como *processing*, logo não se esqueça de ativar a aba processing do QGIS!
Para funcionalidade completa, deverá ser utilizado com o repositório localizado em XXX

## Instalação
Realize o download deste repositório e o extraia na pasta de plugins do QGIS, geralmente situada em (windows) C:\Users\user\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins

## 1- Criar banco de dados
Esta ferramenta cria o banco de dados de pontos de controle necessário para a gerência do projeto.
Os parâmetros necessários são:
- *IP da máquina* (se trabalhando localmente utilizar localhost)
- *Porta* (geralmente 5432 para PostgreSQL)
- *Nome* do banco a ser gerado
- *Usuário* do PostgreSQL
- *Senha* do PostgreSQL
Caso já exista um banco de dados com o mesmo nome a ferramenta não irá sobrescrevê-lo.

## 2- Valida estrutura de pontos de controle
Esta rotina verifica se a pasta definida atende as padronizações determinadas no Manual Técnico de Medição de Pontos de Controle do 1º Centro de Geoinformação.

### Execução
A rotina possui os seguintes parâmetros:
* *pasta dos pontos de controle*: Pasta com a estrutura de pontos de controle
* *operadores*: Nome dos operadores separados por ;
* *data*: Data de realização da medição, no formato YYYY-MM-DD
* *fuso horário*: Fuso horário dos tempos informados
* *ignora_processamento*: Valor booleano que informa se deve ignorar as pastas e arquivos de processamento na avaliação.
* *log*: Arquivo com o relatório de erros
* *JSON* com parâmetros default e parâmetros de validação: Arquivo no formato JSON que possui regras default e regras de validação. Seu formato é o seguinte:
```
{
    "validacao": {
        "alt_max_ant" : 9,
        "dur_min" : 38,
        "modelo_gps" : "TRIMBLE 5700II",
        "modelo_antena" : "TRM39105.00"
    },

    "default": {
        "modelo_gps" : "TRIMBLE 5700II",
        "modelo_antena" : "TRM39105.00",
        "tipo_ref" : 3,
        "sistema_geodesico" : 2,
        "referencial_altim" : 2,
        "referencial_grav" : 97
        \\ Outros atributos ...
    }
}
```
Os seguintes atributos do objeto **validacao** *precisam* ser definidos para uma validação completa da estrutura de pastas:
- Altura máxima da antena: alt_max_ant
- Duração mínima do rastreio: dur_min
- Modelo do GPS:  modelo_gps
- Modelo da antena: modelo_antena

Os seguintes atributos do objeto **default** podem ser pré-definidos para compartilhar informações comuns aos pontos. Os seguintes atributos podem ser definidos:
Atributo | Atributo no JSON
Modelo do GPS | modelo_gps
Modelo da antena | modelo_antena
Tipo de referência | tipo_ref (*)
Sistema geodésico | sistema_geodesico (*)
Referencial altimétrico | referencial_alt (*)
Referencial gravimétrico | referencial_grav (*)
Meridiano central | meridiano_central
Fuso | fuso
Outra referência planimétrica | outra_ref_plan
Fuso horário | fuso_horario
Precisão vertical esperada | precisao_vertical_esperada
Precisão horizontal esperada | precisao_horizontal_esperada
Referencial altimétrico | referencial_altim (*)
Outro referencial altimétrico | outro_ref_alt
Lote | lote
Método de posicionamento | metodo_posicionamento (*)
Ponto base | ponto_base
Máscara de elevação | mascara_elevacao
Taxa de gravação | taxa_gravacao
Modelo geoidal | modelo_geoidal (*)
Órgão executante | orgao_executante
Projeto | projeto
Engenheiro responsável | engenheiro_responsavel
CREA do engenheiro responsável | engenheiro_responsavel
Geometria aproximada | geometria_aproximada (True ou False)
Tipo de referência geodésica | tipo_pto_ref_geod_topo (*)
Rede de referência | rede_referencia (*)
Referencial gravimétrico | referencial_grav (*)

Valores em __(*)__ devem usar code_list, disponível nas tabelas de domínio do banco de pontos de controle. (Ou na [sql](createDB/new_db.sql) do banco)

Notas:
- O campo __validação__ é de preenchimento obrigatório. Caso não esteja preenchido corretamente a rotina não será executada
- Caso o atributo não seja definido no objeto __default__, ele será pesquisado no CSV. Opte por definir valores default no JSON caso os pontos de controle compartilhem o mesmo valor de atributo, mas em casos específicos a definição dos valores poderá ser feita diretamente no CSV.
- Cuidado com a tipologia do arquivo JSON (uso de aspas duplas, uso de ':' para definir um atributo/objeto, chaves devem estar fechadas, etc)

## 3- Atualiza banco de dados de controle
Esta rotina busca na pasta definida e nas suas subpastas pelos arquivos .CSV padrão de medição e atualiza o banco de dados de pontos de controle.

Todos os campos do CSV e todos os atributos definidos no campo _default_ do JSON serão utilizados. Caso o mesmo atributo exista no JSON e no CSV, a prioridade será do CSV. O campo *tipo_situacao_id* será atualizado com o valor 4 (Aguardando avaliação).

É essencial que seja executada a rotina **2- Valida estrutura de pontos de controle** antes da execução desta rotina.
Verifique o preenchimento do objeto __default__ no arquivo JSON antes de executar esta rotina

### Execução
Os parâmetros necessários são:
- *pasta dos pontos de controle*: Pasta com a estrutura de pontos de controle
- *IP da máquina* (se trabalhando localmente utilizar localhost)
- *Porta* (geralmente 5432 para PostgreSQL)
- *Nome* do banco de pontos de controle
- *Usuário* do PostgreSQL
- *Senha* do PostgreSQL
- *JSON* (o mesmo utilizado na ferramenta anterior)

## 4- Preparar para PPP

## 5- PPP

## 6- Procedimento pós PPP

## 7- Atualizar o banco com resultados do PPP

## 8- Gerar monografias

## Preparar insumos para carregamento no BPC
