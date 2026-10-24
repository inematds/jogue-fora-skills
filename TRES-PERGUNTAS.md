# As três perguntas para cada skill

Antes de manter uma skill, faça estas três perguntas.

## 1. Ela roda código que tem que sair igual toda vez?

Script que precisa repetir o mesmo tratamento, sessão após sessão (editar vídeo, gerar relatório num formato fixo, publicar), é o melhor motivo para uma skill existir. Nem o melhor modelo repete o mesmo resultado de uma sessão para outra sem esse código.
Confira se outra ferramenta mantida por alguém já faz isso.

## 2. Ela sabe algo que o modelo não sabe nem acha na internet?

Seu processo, o que cada cliente exige, seu jeito de escrever, suas regras. Isso o modelo não tem no treino nem encontra numa busca: vale manter.
Confira se não repete o que já está no seu `memory.md`, `CLAUDE.md` ou `AGENTS.md`. Muitas vezes a skill inteira vira **uma linha** nesses arquivos.

## 3. Já existe um produto ou conector que faz o mesmo?

Skill que ensinava o modelo a usar a API de um serviço perde o sentido no dia em que o serviço lança um servidor MCP ou conector oficial.
Confira se o conector cobre mesmo a tarefa antes de aposentar a skill, e guarde as instruções únicas.

## Depois de responder

| Resultado | O que fazer |
|---|---|
| Sim na 1 ou na 2, e usada nos últimos 90 dias | **Manter** |
| Passa, mas faz o mesmo que outra | **Juntar** numa skill mais enxuta |
| Não na 1 e na 2, ou sim na 3 | **Arquivar** (pasta de backup com data) |
| Sem certeza, sem histórico | **Revisar** com calma |

Nada vai direto para a lixeira: vai para uma pasta de backup com data, para você poder desfazer.

## Skill na hora certa (just in time)

Skill de uso raro (de uma época, de um cliente, de um projeto) não precisa carregar em toda sessão. Guarde numa pasta que o agente **não** carrega sozinho, por exemplo `~/skills-guardadas/`. Quando precisar, peça:

> Lê a skill `~/skills-guardadas/<nome>/SKILL.md` e segue o que ela diz.

A skill é uma cola bem escrita: ela entra na hora certa e o contexto fica limpo o resto do tempo. Confira antes como a sua ferramenta carrega skills, e faça a mudança como um passo separado, depois da auditoria.
