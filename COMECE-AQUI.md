# Comece aqui

Descubra quais skills ainda merecem a vaga no seu agente.

1. Abra o **Claude Code** ou o **Codex** no computador onde estão as suas skills, de preferência numa pasta vazia (o relatório vai ser criado ali).
2. Abra o `PROMPT-AUDITORIA.txt`, copie o arquivo **inteiro** e cole numa sessão nova. É um prompt de tarefa: não precisa instalar nada.
3. Diga ao agente quais pastas de projeto incluir. Deixe ele ler só as pastas de skills e o histórico que você quer auditar.
4. Abra `auditoria-skills-AAAA-MM-DD/relatorio.html` no navegador. Ele funciona offline. Leia a seção "Como foi contado" antes de agir.

Quer só os números, sem IA? Rode o script local (não apaga nada, não manda nada para a internet):

```bash
python3 scripts/auditar_skills.py --dias 90 --projetos ~/projetos
```

## O que você recebe

- Inventário de todas as skills, com onde moram e quem carrega cada uma.
- Uso real nos últimos 90 dias (radar das 10 mais usadas e mapa de calor por semana).
- Grade de sobreposição e ideias de fusão.
- Cada skill em Manter, Juntar, Arquivar ou Revisar, com o motivo.

## Antes de limpar

- A auditoria **não remove nada**. Confira cada recomendação.
- Histórico ausente quer dizer uso **desconhecido**, não zero.
- Pouco uso, sozinho, não prova que a skill é inútil (pode ser sazonal: guarde na pasta "na hora certa").
- Na limpeza, **mova para uma pasta de backup com data**, não apague.

## Se o resultado parecer errado

Peça ao agente para mostrar quais pastas e datas entraram, conferir o resumo contra as linhas, apontar logs que faltaram e separar uso de verdade de simples menção. Se ele não conseguir gravar o relatório, peça o resultado no chat em vez de liberar acesso a outras pastas.
