#!/usr/bin/env python3
"""Auditoria rápida (só leitura) das skills que seus agentes carregam.

Conta as skills (pastas com SKILL.md) do Claude Code, Codex e outras pastas
de agente, mede o peso da descrição (lida em toda sessão) e conta quantas vezes
cada uma foi usada nos últimos N dias, a partir do histórico local do Claude Code
(~/.claude/projects/**/*.jsonl) e do Codex (~/.codex/sessions).

Não apaga, não move, não edita nada. Não manda nada para a internet.

Uso:
  python3 auditar_skills.py                 # resumo no terminal
  python3 auditar_skills.py --dias 90 --json relatorio.json
  python3 auditar_skills.py --projetos ~/projetos   # inclui .claude/skills dos projetos
"""
import argparse
import json
import os
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

HOME = Path.home()


def ler_frontmatter(p: Path):
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None, "", 0
    nome, desc = None, ""
    m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
    if m:
        fm = m.group(1)
        mn = re.search(r"^name:\s*(.+)$", fm, re.M)
        if mn:
            nome = mn.group(1).strip().strip("'\"")
        md = re.search(r"^description:\s*(.*?)(?=^\w[\w-]*:|\Z)", fm, re.M | re.S)
        if md:
            desc = " ".join(md.group(1).split()).strip("'\"|> ")
    return nome, desc, len(txt.split())


def achar_skills(raizes):
    """Devolve {nome: {paths, origem, palavras, palavras_desc, tem_codigo}}."""
    skills = {}
    vistos = set()
    for origem, raiz in raizes:
        if not raiz.exists():
            continue
        for skill_md in raiz.rglob("SKILL.md"):
            pasta = skill_md.parent
            try:
                real = pasta.resolve()
            except OSError:
                continue
            nome, desc, palavras = ler_frontmatter(skill_md)
            nome = nome or pasta.name
            tem_codigo = any(
                f.suffix in {".py", ".js", ".ts", ".mjs", ".sh", ".cjs"}
                for f in pasta.rglob("*") if f.is_file()
            )
            s = skills.setdefault(nome, {
                "nome": nome, "paths": [], "origens": set(), "palavras": palavras,
                "palavras_desc": len(desc.split()), "tem_codigo": tem_codigo,
            })
            if str(real) not in s["paths"]:
                s["paths"].append(str(real))
            s["origens"].add(origem)
            vistos.add(real)
    return skills


def contar_uso(dias):
    limite = time.time() - dias * 86400
    uso = Counter()
    ultimo = {}
    semanas = defaultdict(Counter)
    re_cmd = re.compile(r"<command-name>/?([\w:.-]+)</command-name>")
    re_codex = re.compile(r"skills/([\w.-]+)/SKILL\.md")

    def marca(nome, ts):
        uso[nome] += 1
        ultimo[nome] = max(ultimo.get(nome, 0), ts)
        semanas[nome][time.strftime("%G-%V", time.localtime(ts))] += 1

    proj = HOME / ".claude" / "projects"
    if proj.exists():
        for f in proj.rglob("*.jsonl"):
            try:
                if f.stat().st_mtime < limite:
                    continue
                fh = f.open(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            with fh:
                for linha in fh:
                    if '"Skill"' not in linha and "command-name" not in linha:
                        continue
                    try:
                        ev = json.loads(linha)
                    except ValueError:
                        continue
                    ts_txt = ev.get("timestamp") or ""
                    try:
                        ts = time.mktime(time.strptime(ts_txt[:19], "%Y-%m-%dT%H:%M:%S"))
                    except ValueError:
                        ts = f.stat().st_mtime
                    if ts < limite:
                        continue
                    msg = ev.get("message") or {}
                    cont = msg.get("content")
                    if isinstance(cont, list):
                        for c in cont:
                            if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "Skill":
                                nome = (c.get("input") or {}).get("skill")
                                if nome:
                                    marca(nome, ts)
                    elif isinstance(cont, str) and ev.get("type") == "user":
                        for nome in re_cmd.findall(cont):
                            marca(nome, ts)

    codex = HOME / ".codex" / "sessions"
    if codex.exists():
        for f in codex.rglob("*.jsonl"):
            try:
                st = f.stat().st_mtime
                if st < limite:
                    continue
                txt = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for nome in set(re_codex.findall(txt)):
                marca(nome, st)
    return uso, ultimo, semanas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dias", type=int, default=90)
    ap.add_argument("--json", help="grava o relatório completo neste arquivo")
    ap.add_argument("--projetos", help="pasta com seus projetos (procura .claude/skills dentro)")
    a = ap.parse_args()

    raizes = [
        ("claude", HOME / ".claude" / "skills"),
        ("plugin", HOME / ".claude" / "plugins"),
        ("codex", HOME / ".codex" / "skills"),
        ("agents", HOME / ".agents" / "skills"),
        ("gemini", HOME / ".gemini" / "skills"),
    ]
    if a.projetos:
        for d in Path(a.projetos).expanduser().glob("*/.claude/skills"):
            raizes.append(("projeto", d))

    skills = achar_skills(raizes)
    uso, ultimo, semanas = contar_uso(a.dias)

    def base(n):  # "plugin:skill" -> "skill"
        return n.split(":")[-1]

    uso_base = Counter()
    for n, q in uso.items():
        uso_base[base(n)] += q

    linhas = []
    for nome, s in skills.items():
        q = uso_base.get(nome, 0)
        linhas.append({
            "nome": nome, "usos": q, "origens": sorted(s["origens"]), "paths": s["paths"],
            "palavras_skill": s["palavras"], "palavras_descricao": s["palavras_desc"],
            "tem_codigo": s["tem_codigo"],
            "ultimo_uso": time.strftime("%Y-%m-%d", time.localtime(ultimo[nome])) if nome in ultimo else None,
        })
    linhas.sort(key=lambda r: -r["usos"])

    total = len(linhas)
    usadas = [r for r in linhas if r["usos"] > 0]
    nunca = total - len(usadas)
    de_plugin = sum(1 for r in linhas if r["origens"] == ["plugin"])
    desc_total = sum(r["palavras_descricao"] for r in linhas)
    top10 = sum(r["usos"] for r in linhas[:10])
    soma = sum(r["usos"] for r in linhas) or 1

    print(f"Skills encontradas: {total}  (só de plugin: {de_plugin})")
    print(f"Usadas pelo menos 1 vez em {a.dias} dias: {len(usadas)}")
    print(f"Nunca usadas em {a.dias} dias: {nunca}")
    print(f"Palavras de descrição lidas no início de cada sessão: ~{desc_total}")
    print(f"As 10 mais usadas somam {round(100 * top10 / soma)}% de todos os usos")
    print("\nTop 10:")
    for r in linhas[:10]:
        print(f"  {r['usos']:5d}  {r['nome']}")
    if a.json:
        Path(a.json).write_text(json.dumps({
            "gerado": time.strftime("%Y-%m-%d %H:%M"), "dias": a.dias,
            "total": total, "usadas": len(usadas), "nunca": nunca, "so_plugin": de_plugin,
            "palavras_descricao": desc_total, "top10_pct": round(100 * top10 / soma),
            "skills": linhas,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nRelatório: {a.json}")


if __name__ == "__main__":
    main()
