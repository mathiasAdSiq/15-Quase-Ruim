# Quase_Ruim
## Identificação

### Nome da Equipe

**Equipe Fence Guard**

### Integrantes e Funções

| Integrante        | Função                  |
| ----------------- | ----------------------- |
| Augusto Borges    | Programador             |
| Mathias Almeida   | Documentação            |
| Sofia Sonia       | Designer                |
| Carlos Daniel     | Negócios                |
| Pedro Prochnow    | Programador             |




#  Escopo do Projeto

ESCOPO DO PROJETO:
O Problema se baseia em uma simples vivencias dos donos de gado, porco e animais em geral. o problema de não saber se suas sercas estão ou não funcionando.
Nossa equipe decidiu ajudar essas pessoas desenvolvendo um produto/aplicativo que as permite controlar, ajustar e monitorar o funcionamento das suas cercas de um modo autonomo, facil e rapido, na palma de suas mãos, podendo monitorar se partes especificas de suas cercas estão ou não funcionando e controlar a potencia de areas especificas da cerca apenas com o uso do app do celular
## Problema

Sistemas de cercas elétricas rurais exigem monitoramento constante para garantir a segurança do perímetro, evitar invasões, identificar falhas elétricas e reduzir o tempo de resposta durante incidentes.

Em muitas propriedades, o acompanhamento é realizado de forma manual, dificultando a identificação rápida de problemas como:

* Queda de tensão;
* Rompimento de fios;
* Falhas em setores específicos;
* Desligamentos não planejados;
* Necessidade de manutenção preventiva.

## Solução Proposta

O projeto Fence Guard consiste em uma plataforma de monitoramento e controle de cercas elétricas rurais baseada em tecnologia web.

O sistema permite:

* Visualização gráfica da cerca em mapa interativo;
* Controle individual dos setores;
* Monitoramento da tensão em tempo real;
* Identificação automática de falhas;
* Sistema de alertas operacionais;
* Gerenciamento de manutenção;
* Visualização da condição dos fios através de cores;
* Expansão futura para integração com sensores físicos reais.

---

#  Stack Tecnológica

## Linguagens Utilizadas

* Python 3
* JavaScript
* HTML5
* CSS3

## Frameworks

### Backend

* Flask

### Frontend

* JavaScript Vanilla
* SVG Dinâmico

## Bibliotecas

* Flask
* Fetch API
* Tabler Icons
* Google Fonts

## Banco de Dados

Atualmente o sistema utiliza armazenamento em memória (RAM) para simulação dos dados.

Planejamento futuro:

* SQLite
* PostgreSQL

## APIs

### APIs Internas

| Endpoint              | Função                     |
| --------------------- | -------------------------- |
| /api/sensores         | Retorna sensores e estados |
| /api/controle         | Controle dos setores       |
| /api/tensao           | Alteração da tensão        |
| /api/alerta           | Consulta alertas           |
| /api/manutencao_todos | Executa manutenção geral   |
| /api/arquitetura      | Informações da arquitetura |
| /api/estatisticas     | Estatísticas operacionais  |
| /api/diagnostico      | Diagnóstico do sistema     |

---

#  Arquitetura

## Modelo da Arquitetura

# Diagrama Técnico da Arquitetura

![Logo do Projeto](/Captura de tela 2026-06-06 033352.png)

# Fluxo Operacional
https://github.com/mathiasAdSiq/15-Quase-Ruim/blob/f8a33509761031183f3ebf285c6962ea10ebe641/Captura%20de%20tela%202026-06-06%20033413.png
   # Modelo Arquitetural (Camadas)
https://github.com/mathiasAdSiq/15-Quase-Ruim/blob/36c9de153a27ea89dcad7049d8d7bac3006887a2/Captura%20de%20tela%202026-06-06%20033413.png)

### Componentes Principais

#### Interface Web (Frontend)

Responsável pela interação do operador com o sistema:

* Mapa da cerca;
* Controle dos setores;
* Ajuste de tensão;
* Visualização de alertas;
* Diagnóstico operacional.

#### API Flask (Backend)

Camada responsável pelo processamento das informações:

* Recebimento dos comandos;
* Controle dos estados;
* Simulação dos sensores;
* Gerenciamento das falhas;
* Atualização dos setores.

#### Núcleo SCADA

Responsável pelas regras de negócio:

* Controle de tensão;
* Simulação de falhas;
* Estados operacionais;
* Alertas;
* Manutenção.

#### Camada Física

Representação da infraestrutura real:

* Energizador;
* Sensores;
* Fios da cerca;
* Setores monitorados.

---

# v) Situação do Projeto

## Requisitos Planejados x Implementados

| Requisito                                       | Status                |
| ----------------------------------------------- | --------------------- |
| Dashboard Web                                   | ✅ Implementado        |
| Controle dos Setores                            | ✅ Implementado        |
| Monitoramento de Tensão                         | ✅ Implementado        |
| Alteração Manual de Tensão                      | ✅ Implementado        |
| Visualização Gráfica da Cerca                   | ✅ Implementado        |
| Mudança de Cor dos Fios por Tensão              | ✅ Implementado        |
| Sistema de Alertas                              | ✅ Implementado        |
| Manutenção Individual                           | ✅ Implementado        |
| Manutenção Geral                                | ✅ Implementado        |
| Diagnóstico de Falhas                           | ✅ Implementado        |
| Setores Dinâmicos                               | ✅ Implementado        |
| Layout Editável                                 | ✅ Implementado        |
| Histórico de Eventos                            | 🔄 Em desenvolvimento |
| Persistência em Banco de Dados                  | 🔄 Em desenvolvimento |
| Integração com Sensores Reais                   | 🔄 Em desenvolvimento |
| Aplicativo Mobile                               | 📋 Planejado          |
| Notificações Push                               | 📋 Planejado          |
| Inteligência Artificial para Predição de Falhas | 📋 Planejado          |
| Sistema ESP32                                   | 📋 Planejado          |


### Legenda

* ✅ Implementado
* 🔄 Em desenvolvimento
* 📋 Planejado

---

# Considerações Finais

O projeto Fence Guard SCADA apresenta uma solução moderna para monitoramento de cercas elétricas rurais, oferecendo visualização em tempo real, controle operacional e mecanismos de manutenção preventiva.

A arquitetura foi desenvolvida para permitir expansão futura, incluindo integração com dispositivos IoT, sensores físicos e banco de dados persistente.


