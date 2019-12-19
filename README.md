# Conjunto de ferramentas para medição
Conjunto de ferramentas em Python que automatizam parte do processo de processamento e controle de qualidade da medição de pontos de controle.
As ferramentas estão disponibilizadas como *processing*, logo não se esqueça de ativar a aba processing do QGIS!
Para funcionalidade completa, deverá ser utilizado com o repositório localizado em XXX

## Instalação
Realize o download deste repositório e o extraia na pasta de plugins do QGIS, geralmente situada em (windows) C:\Users\user\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins

### 1- Criar banco de dados
Esta ferramenta cria o banco de dados de pontos de controle necessário para a gerência do projeto.
Os parâmetros necessários são:
- *IP da máquina* (se trabalhando localmente utilizar localhost)
- *Porta* (geralmente 5432 para PostgreSQL)
- *Nome* do banco a ser gerado
- *Usuário* do PostgreSQL
- *Senha* do PostgreSQL
Caso já exista um banco de dados com o mesmo nome a ferramenta não irá sobrescrevê-lo.

### 2- Valida estrutura de pontos de controle
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
        "dur_min" : 38
    },

    "default": {
        "modelo_gps" : "TRIMBLE 5700II",
        "modelo_antena" : "TRM39105.00",
        "tipo_ref" : 3,
        "sistema_geodesico" : 2,
        "referencial_altim" : 2,
        "referencial_grav" : 97,
    }
}
```
Os seguintes atributos podem ser validados na aba validação:
- Altura máxima da antena : alt_max_ant
- Duração mínima do rastreio: dur_min

Os seguintes atributos podem ser pré-definidos (caso não sejam definidos aqui serão lidos do CSV):
- Modelo do GPS : modelo_gps
- Modelo da antena : modelo_antena
- Tipo de referência : tipo_ref (*)
- Sistema geodésico : sistema_geodesico (*)
- Referencial altimétrico : referencial_alt (*)
- Referencial gravimétrico : referencial_grav (*)

## Atualiza banco de dados de controle
Esta rotina busca na pasta definida e nas suas subpastas pelos arquivos .CSV padrão de medição e atualiza o banco de dados de pontos de controle.

As seguintes informações são atualizadas:
* *medidor*: Nome do operador que realizou a medição
* *data_medicao*: Dada que ocorreu a medição
* *tipo_situacao_id*: Atualiza com o valor 4 (Aguardando avaliação)

É interessante que seja executada a rotina **Valida estrutura de pontos de controle** antes da execução desta rotina.

### Execução

A rotina possui os seguintes parâmetros:
* *pasta dos pontos de controle*: Pasta com a estrutura de pontos de controle
* *servidor*: IP do servidor de banco de dados PostgreSQL
* *porta*: Porta de acesso ao servidor de banco de dados
* *nome do banco de dados*: Nome do banco de dados de ponto de controle
* *usuario*: Usuário com acesso ao banco de dados
* *senha*: Senha para o usuário definido

