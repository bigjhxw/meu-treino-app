import flet as ft
from datetime import datetime
import json
import os
import asyncio

ARQUIVO = "dados_treino.json"

BG = "#080B10"
CARD = "#111722"
CARD_2 = "#151D2A"
NEON = "#36F5A2"
BLUE = "#4D7CFE"
PURPLE = "#9B5CFF"
ORANGE = "#FFB020"
RED = "#FF4D6D"
TEXT_MUTED = "#94A3B8"

TREINOS_BASE = {
    "Upper A": [
        {"nome": "Supino com halter", "series": "4x 10-15"},
        {"nome": "Remada com barra", "series": "4x 10-12"},
        {"nome": "Desenvolvimento com halter", "series": "3x 10-12"},
        {"nome": "Elevação lateral", "series": "3x 12-15"},
        {"nome": "Rosca bíceps barra W", "series": "3x 10-12"},
        {"nome": "Tríceps banco", "series": "3x até falhar"},
    ],
    "Lower A": [
        {"nome": "Agachamento com barra", "series": "4x 10-12"},
        {"nome": "Afundo com halter", "series": "3x 10 cada perna"},
        {"nome": "Stiff", "series": "3x 10-12"},
        {"nome": "Panturrilha em pé", "series": "4x 15-20"},
        {"nome": "Prancha", "series": "3x 30-60s"},
    ],
    "Cardio + Core": [
        {"nome": "Esteira caminhada inclinada", "series": "20-30 min leve"},
        {"nome": "Prancha", "series": "3x 30-60s"},
        {"nome": "Abdominal crunch", "series": "3x 15-20"},
        {"nome": "Elevação de pernas", "series": "3x 10-15"},
    ],
    "Upper B": [
        {"nome": "Supino inclinado com halter", "series": "4x 10-15"},
        {"nome": "Remada unilateral com halter", "series": "4x 10-12 cada lado"},
        {"nome": "Arnold press", "series": "3x 10-12"},
        {"nome": "Elevação lateral lenta", "series": "3x 15-20"},
        {"nome": "Rosca martelo", "series": "3x 10-12"},
        {"nome": "Tríceps testa barra W", "series": "3x 10-12"},
    ],
    "Lower B": [
        {"nome": "Agachamento goblet", "series": "4x 12-15"},
        {"nome": "Passada andando", "series": "3x 10 cada perna"},
        {"nome": "Stiff unilateral", "series": "3x 10 cada perna"},
        {"nome": "Ponte de glúteo", "series": "4x 12-15"},
        {"nome": "Panturrilha", "series": "4x 20"},
    ],
}

TODOS_DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
PADRAO_DIAS_TREINO = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
ORDEM_TREINOS = ["Upper A", "Lower A", "Cardio + Core", "Upper B", "Lower B"]


def carregar():
    padrao = {
        "historico": [],
        "semana": {},
        "ciclo": 1,
        "medidas": [],
        "dias_treino": PADRAO_DIAS_TREINO,
    }

    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                dados = json.load(f)

            for chave, valor in padrao.items():
                if chave not in dados:
                    dados[chave] = valor

            return dados
        except Exception:
            return padrao

    return padrao


def salvar(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def numero(valor):
    try:
        return float(str(valor).replace(",", "."))
    except Exception:
        return 0


def dia_atual_pt():
    mapa = {
        0: "Segunda",
        1: "Terça",
        2: "Quarta",
        3: "Quinta",
        4: "Sexta",
        5: "Sábado",
        6: "Domingo",
    }
    return mapa[datetime.now().weekday()]


def bloco_do_ciclo(ciclo):
    posicao = ((ciclo - 1) % 4) + 1

    if posicao in [1, 2]:
        return {
            "nome": "BASE",
            "descricao": "Foco em execução perfeita, constância e controle.",
            "tag": "SEMANA 1–2",
            "ajuste": "Mantenha 1–2 reps sobrando. Descida controlada.",
        }

    return {
        "nome": "PROGRESSÃO",
        "descricao": "Foco em aumentar reps, carga ou dificuldade.",
        "tag": "SEMANA 3–4",
        "ajuste": "Tente subir carga ou adicionar 2–3 reps por exercício.",
    }


def aplicar_bloco_series(series, ciclo):
    bloco = bloco_do_ciclo(ciclo)
    if bloco["nome"] == "BASE":
        return series
    return f"{series} + progressão"


def gerar_semana(dias_treino, ciclo):
    semana = {}
    indice_treino = 0

    for dia in TODOS_DIAS:
        if dia in dias_treino:
            treino = ORDEM_TREINOS[indice_treino % len(ORDEM_TREINOS)]
            indice_treino += 1
        else:
            treino = "Descanso"

        semana[dia] = {
            "treino": treino,
            "feito": False,
            "data_conclusao": "",
            "bloco": bloco_do_ciclo(ciclo)["nome"],
        }

    return semana


def chip(texto, cor):
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        border_radius=30,
        bgcolor=cor,
        content=ft.Text(texto, size=11, weight=ft.FontWeight.BOLD),
    )


def titulo_secao(texto, subtitulo=None):
    itens = [ft.Text(texto, size=22, weight=ft.FontWeight.BOLD)]
    if subtitulo:
        itens.append(ft.Text(subtitulo, size=12, color=TEXT_MUTED))
    return ft.Column(itens, spacing=2)


def pro_card(content, color=CARD):
    return ft.Container(
        padding=16,
        border_radius=22,
        bgcolor=color,
        content=content,
    )


async def main(page: ft.Page):
    page.title = "Meu Treino"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 14
    page.scroll = ft.ScrollMode.AUTO
    page.window_width = 430
    page.window_height = 860
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)

    dados = carregar()

    if not dados["semana"]:
        dados["semana"] = gerar_semana(dados["dias_treino"], dados["ciclo"])
        salvar(dados)

    tela_atual = {"nome": "hoje"}
    treino_atual = {"dia": "", "nome": "", "itens": []}
    edicao_atual = {"indice": None, "campos": []}

    conteudo = ft.Column(spacing=14)
    seletores_dias = {}

    timer = {"ativo": False, "segundos": 90}
    timer_text = ft.Text("01:30", size=34, weight=ft.FontWeight.BOLD)
    timer_status = ft.Text("Pronto para descanso", color=TEXT_MUTED)

    def salvar_base():
        salvar(dados)

    def aviso(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    def formatar_tempo(segundos):
        return f"{segundos // 60:02d}:{segundos % 60:02d}"

    async def rodar_timer(segundos):
        timer["ativo"] = False
        await asyncio.sleep(0.1)

        timer["ativo"] = True
        timer["segundos"] = segundos
        timer_text.value = formatar_tempo(segundos)
        timer_status.value = "Descansando..."
        page.update()

        while timer["ativo"] and timer["segundos"] > 0:
            await asyncio.sleep(1)
            timer["segundos"] -= 1
            timer_text.value = formatar_tempo(timer["segundos"])
            page.update()

        if timer["segundos"] <= 0:
            timer["ativo"] = False
            timer_status.value = "Descanso finalizado ✅"
            page.update()

    def pausar_timer(e):
        timer["ativo"] = False
        timer_status.value = "Timer pausado"
        page.update()

    def resetar_timer(e):
        timer["ativo"] = False
        timer["segundos"] = 90
        timer_text.value = "01:30"
        timer_status.value = "Pronto para descanso"
        page.update()

    def progresso_semana():
        total = len(dados["semana"])
        feitos = sum(1 for v in dados["semana"].values() if v["feito"])
        return feitos, total, feitos / total if total else 0

    def resumo_semana():
        total_treino = sum(1 for v in dados["semana"].values() if v["treino"] != "Descanso")
        feitos_treino = sum(
            1 for v in dados["semana"].values()
            if v["treino"] != "Descanso" and v["feito"]
        )
        restantes = total_treino - feitos_treino

        proximo = "Nenhum"
        for dia, info in dados["semana"].items():
            if info["treino"] != "Descanso" and not info["feito"]:
                proximo = f"{dia} • {info['treino']}"
                break

        return total_treino, feitos_treino, restantes, proximo

    def melhores_cargas():
        melhores = {}

        for sessao in dados["historico"]:
            for ex in sessao.get("exercicios", []):
                nome = ex["nome"]
                carga = ex.get("carga", 0)

                if nome not in melhores or carga > melhores[nome]["carga"]:
                    melhores[nome] = {
                        "carga": carga,
                        "reps": ex.get("reps", ""),
                        "data": sessao["data"],
                    }

        return melhores

    def tipo_card(treino):
        if treino == "Descanso":
            return "RECOVERY", PURPLE
        if treino == "Cardio + Core":
            return "ENGINE", ORANGE
        if "Upper" in treino:
            return "UPPER", BLUE
        if "Lower" in treino:
            return "LOWER", NEON
        return "TRAIN", CARD_2

    def abrir_treino_do_dia(dia):
        info = dados["semana"][dia]
        nome_treino = info["treino"]

        if nome_treino == "Descanso":
            aviso("Dia de descanso. Cardio leve opcional.")
            return

        treino_atual["dia"] = dia
        treino_atual["nome"] = nome_treino
        treino_atual["itens"] = []

        for ex in TREINOS_BASE[nome_treino]:
            treino_atual["itens"].append(
                {
                    "nome": ex["nome"],
                    "series": aplicar_bloco_series(ex["series"], dados["ciclo"]),
                    "carga": ft.TextField(
                        label="Carga kg",
                        hint_text="Ex: 20",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        dense=True,
                        border_radius=14,
                    ),
                    "reps": ft.TextField(
                        label="Reps",
                        hint_text="Ex: 12",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        dense=True,
                        border_radius=14,
                    ),
                    "concluido": ft.Checkbox(label="Concluído"),
                }
            )

        mostrar_tela("treino")

    def concluir_descanso(dia):
        dados["semana"][dia]["feito"] = True
        dados["semana"][dia]["data_conclusao"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        salvar_base()
        aviso("Descanso marcado.")
        mostrar_tela(tela_atual["nome"])

    def desfazer_check(dia):
        dados["semana"][dia]["feito"] = False
        dados["semana"][dia]["data_conclusao"] = ""
        salvar_base()
        aviso(f"Check de {dia} desfeito.")
        mostrar_tela(tela_atual["nome"])

    def salvar_treino(e):
        if not treino_atual["nome"]:
            aviso("Nenhum treino aberto.")
            return

        exercicios = []
        concluidos = 0

        for item in treino_atual["itens"]:
            feito = bool(item["concluido"].value)

            if feito:
                concluidos += 1

            exercicios.append(
                {
                    "nome": item["nome"],
                    "series": item["series"],
                    "carga": numero(item["carga"].value),
                    "reps": item["reps"].value or "",
                    "concluido": feito,
                }
            )

        agora = datetime.now().strftime("%d/%m/%Y %H:%M")

        dados["historico"].append(
            {
                "data": agora,
                "dia": treino_atual["dia"],
                "treino": treino_atual["nome"],
                "bloco": bloco_do_ciclo(dados["ciclo"])["nome"],
                "total_exercicios": len(exercicios),
                "concluidos": concluidos,
                "exercicios": exercicios,
            }
        )

        dados["semana"][treino_atual["dia"]]["feito"] = True
        dados["semana"][treino_atual["dia"]]["data_conclusao"] = agora

        salvar_base()
        aviso("Treino salvo.")
        mostrar_tela("hoje")

    def nova_semana(e):
        dados["ciclo"] += 1
        dados["semana"] = gerar_semana(dados["dias_treino"], dados["ciclo"])
        salvar_base()
        mostrar_tela("hoje")

    def aplicar_dias_treino(e):
        escolhidos = []

        for dia, controle in seletores_dias.items():
            if controle.value:
                escolhidos.append(dia)

        if not escolhidos:
            aviso("Escolha pelo menos 1 dia de treino.")
            return

        dados["dias_treino"] = escolhidos
        dados["semana"] = gerar_semana(escolhidos, dados["ciclo"])
        salvar_base()

        aviso("Semana atualizada.")
        mostrar_tela("semana")

    def abrir_edicao(indice):
        edicao_atual["indice"] = indice
        edicao_atual["campos"] = []

        sessao = dados["historico"][indice]

        for ex in sessao.get("exercicios", []):
            campo_carga = ft.TextField(
                label="Carga kg",
                value=str(ex.get("carga", "")),
                keyboard_type=ft.KeyboardType.NUMBER,
                dense=True,
                border_radius=14,
            )

            campo_reps = ft.TextField(
                label="Reps",
                value=str(ex.get("reps", "")),
                keyboard_type=ft.KeyboardType.NUMBER,
                dense=True,
                border_radius=14,
            )

            concluido = ft.Checkbox(label="Concluído", value=ex.get("concluido", False))

            edicao_atual["campos"].append(
                {
                    "nome": ex["nome"],
                    "series": ex.get("series", ""),
                    "carga": campo_carga,
                    "reps": campo_reps,
                    "concluido": concluido,
                }
            )

        mostrar_tela("editar")

    def salvar_edicao(e):
        indice = edicao_atual["indice"]

        if indice is None:
            aviso("Nenhum treino selecionado para edição.")
            return

        exercicios = []
        concluidos = 0

        for item in edicao_atual["campos"]:
            feito = bool(item["concluido"].value)

            if feito:
                concluidos += 1

            exercicios.append(
                {
                    "nome": item["nome"],
                    "series": item["series"],
                    "carga": numero(item["carga"].value),
                    "reps": item["reps"].value or "",
                    "concluido": feito,
                }
            )

        dados["historico"][indice]["exercicios"] = exercicios
        dados["historico"][indice]["concluidos"] = concluidos
        dados["historico"][indice]["total_exercicios"] = len(exercicios)
        dados["historico"][indice]["editado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")

        salvar_base()
        aviso("Treino editado.")
        mostrar_tela("historico")

    def excluir_registro(indice):
        try:
            del dados["historico"][indice]
            salvar_base()
            aviso("Registro excluído.")
            mostrar_tela("historico")
        except Exception:
            aviso("Não foi possível excluir esse registro.")

    def card_resumo_semana():
        total_treino, feitos_treino, restantes, proximo = resumo_semana()
        bloco = bloco_do_ciclo(dados["ciclo"])
        feitos, total, perc = progresso_semana()

        return ft.Container(
            padding=18,
            border_radius=26,
            bgcolor=CARD,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("WEEK OVERVIEW", size=11, color=TEXT_MUTED),
                                    ft.Text(f"Semana {dados['ciclo']}", size=26, weight=ft.FontWeight.BOLD),
                                ],
                                spacing=0,
                            ),
                            chip(bloco["nome"], ORANGE if bloco["nome"] == "PROGRESSÃO" else BLUE),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(bloco["ajuste"], color=TEXT_MUTED, size=12),
                    ft.ProgressBar(value=perc, color=NEON, bgcolor="#253041"),
                    ft.Row(
                        [
                            chip(f"{feitos_treino}/{total_treino} treinos", NEON),
                            chip(f"{restantes} restantes", CARD_2),
                        ],
                        spacing=8,
                        wrap=True,
                    ),
                    ft.Text(f"Próximo: {proximo}", color=TEXT_MUTED, size=12),
                    ft.Text(f"Total da semana: {feitos}/{total} dias concluídos", color=TEXT_MUTED, size=12),
                ],
                spacing=10,
            ),
        )

    def card_dia(dia, info, destaque=False):
        feito = info["feito"]
        treino = info["treino"]
        tag, cor_tag = tipo_card(treino)

        if treino == "Descanso":
            tempo = "Recovery"
            cardio = "Cardio leve opcional: 15–20 min caminhada"
        elif treino == "Cardio + Core":
            tempo = "30–40 min"
            cardio = "Cardio principal do dia"
        else:
            tempo = "45–60 min"
            cardio = "Cardio leve: 10–20 min pós-treino"

        if feito:
            bg = "#10281F"
        elif destaque:
            bg = "#162238"
        else:
            bg = CARD

        botoes = []

        if treino == "Descanso":
            botoes.append(
                ft.OutlinedButton(
                    "Marcar descanso",
                    disabled=feito,
                    on_click=lambda e, d=dia: concluir_descanso(d),
                )
            )
        else:
            botoes.append(
                ft.FilledButton(
                    "Abrir sessão",
                    disabled=feito,
                    on_click=lambda e, d=dia: abrir_treino_do_dia(d),
                )
            )

        if feito:
            botoes.append(
                ft.TextButton(
                    "Desfazer",
                    on_click=lambda e, d=dia: desfazer_check(d),
                )
            )

        return ft.Container(
            padding=16,
            border_radius=24,
            bgcolor=bg,
            border=ft.border.all(1, NEON) if destaque and not feito else None,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(dia.upper(), size=11, color=TEXT_MUTED),
                                    ft.Text(treino, size=20, weight=ft.FontWeight.BOLD),
                                ],
                                spacing=1,
                            ),
                            ft.Column(
                                [
                                    chip(tag, cor_tag),
                                    ft.Text("✅" if feito else "⬜", text_align=ft.TextAlign.RIGHT),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.TIMER, size=16, color=TEXT_MUTED),
                            ft.Text(f"Tempo: {tempo}", color=TEXT_MUTED, size=12),
                        ],
                        spacing=6,
                    ),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.DIRECTIONS_RUN, size=16, color=TEXT_MUTED),
                            ft.Text(cardio, color=TEXT_MUTED, size=12),
                        ],
                        spacing=6,
                    ),
                    ft.Text(
                        f"Concluído em: {info['data_conclusao']}"
                        if feito and info["data_conclusao"]
                        else "",
                        size=11,
                        color=TEXT_MUTED,
                    ),
                    ft.Row(botoes, wrap=True),
                ],
                spacing=9,
            ),
        )

    def tela_hoje():
        hoje = dia_atual_pt()
        info = dados["semana"].get(hoje)

        itens = [
            titulo_secao("Hoje", "Sua sessão do dia, sem procurar na semana."),
            card_resumo_semana(),
        ]

        if not info:
            itens.append(pro_card(ft.Text("Não encontrei o dia atual na semana.", color=TEXT_MUTED)))
            return ft.Column(itens, spacing=12)

        itens.append(
            ft.Container(
                padding=18,
                border_radius=26,
                bgcolor="#0D1320",
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text("TODAY SESSION", size=11, color=NEON, weight=ft.FontWeight.BOLD),
                                        ft.Text(hoje, size=30, weight=ft.FontWeight.BOLD),
                                    ],
                                    spacing=0,
                                ),
                                chip("AGORA", NEON),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(
                            "O app destacou automaticamente o treino de hoje.",
                            size=12,
                            color=TEXT_MUTED,
                        ),
                    ],
                    spacing=8,
                ),
            )
        )

        itens.append(card_dia(hoje, info, destaque=True))

        return ft.Column(itens, spacing=12)

    def tela_semana():
        itens = [
            card_resumo_semana(),
            titulo_secao("Semana completa", "Planejamento semanal com check por dia."),
        ]

        hoje = dia_atual_pt()

        for dia, info in dados["semana"].items():
            itens.append(card_dia(dia, info, destaque=(dia == hoje)))

        itens.append(
            ft.Container(
                padding=16,
                border_radius=22,
                bgcolor=CARD_2,
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Reset de ciclo", weight=ft.FontWeight.BOLD),
                                ft.Text("Use quando virar a semana.", size=12, color=TEXT_MUTED),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.FilledButton("Nova semana", icon=ft.Icons.REFRESH, on_click=nova_semana),
                    ]
                ),
            )
        )

        return ft.Column(itens, spacing=12)

    def tela_treino():
        if not treino_atual["nome"]:
            return ft.Column([titulo_secao("Treino", "Abra uma sessão pela aba Hoje ou Semana.")])

        bloco = bloco_do_ciclo(dados["ciclo"])

        cards = [
            ft.Container(
                padding=18,
                border_radius=26,
                bgcolor=CARD,
                content=ft.Column(
                    [
                        ft.Text(treino_atual["dia"].upper(), size=11, color=TEXT_MUTED),
                        ft.Text(treino_atual["nome"], size=28, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            [
                                chip(bloco["nome"], ORANGE if bloco["nome"] == "PROGRESSÃO" else BLUE),
                                chip(bloco["tag"], CARD_2),
                            ],
                            spacing=8,
                        ),
                        ft.Text(bloco["ajuste"], color=TEXT_MUTED),
                    ],
                    spacing=6,
                ),
            ),
            pro_card(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("REST TIMER", size=16, weight=ft.FontWeight.BOLD),
                                chip("LIVE", BLUE),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        timer_text,
                        timer_status,
                        ft.Row(
                            [
                                ft.OutlinedButton("60s", on_click=lambda e: page.run_task(rodar_timer, 60)),
                                ft.OutlinedButton("90s", on_click=lambda e: page.run_task(rodar_timer, 90)),
                                ft.OutlinedButton("120s", on_click=lambda e: page.run_task(rodar_timer, 120)),
                            ],
                            wrap=True,
                        ),
                        ft.Row(
                            [
                                ft.TextButton("Pausar", on_click=pausar_timer),
                                ft.TextButton("Resetar", on_click=resetar_timer),
                            ]
                        ),
                    ],
                    spacing=8,
                )
            ),
        ]

        for idx, item in enumerate(treino_atual["itens"], start=1):
            cards.append(
                ft.Container(
                    padding=16,
                    border_radius=24,
                    bgcolor=CARD,
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    chip(f"#{idx}", CARD_2),
                                    ft.Text(item["nome"], size=17, weight=ft.FontWeight.BOLD, expand=True),
                                ],
                                spacing=8,
                            ),
                            ft.Text(item["series"], color=TEXT_MUTED, size=13),
                            ft.Row([item["carga"], item["reps"]], spacing=10),
                            item["concluido"],
                        ],
                        spacing=10,
                    ),
                )
            )

        cards.append(
            ft.FilledButton(
                "Salvar sessão e concluir dia",
                icon=ft.Icons.SAVE,
                height=52,
                on_click=salvar_treino,
            )
        )

        return ft.Column(cards, spacing=12)

    def tela_historico():
        itens = [titulo_secao("Histórico", "Edite ou exclua registros salvos.")]

        if not dados["historico"]:
            itens.append(pro_card(ft.Text("Nenhum treino salvo ainda.", color=TEXT_MUTED)))
            return ft.Column(itens, spacing=12)

        total = len(dados["historico"])

        for indice_reverso, sessao in enumerate(reversed(dados["historico"])):
            indice_real = total - 1 - indice_reverso

            linhas = []

            for ex in sessao.get("exercicios", []):
                status = "✅" if ex["concluido"] else "⬜"
                linhas.append(
                    ft.Text(
                        f"{status} {ex['nome']} | {ex['carga']} kg | {ex['reps'] or '-'} reps",
                        size=12,
                        color=TEXT_MUTED,
                    )
                )

            editado = sessao.get("editado_em", "")

            itens.append(
                pro_card(
                    ft.Column(
                        [
                            ft.Text(
                                f"{sessao['data']} • {sessao.get('dia', '')}",
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Row(
                                [
                                    chip(sessao["treino"], BLUE),
                                    chip(
                                        sessao.get("bloco", "BASE"),
                                        ORANGE if sessao.get("bloco") == "PROGRESSÃO" else CARD_2,
                                    ),
                                ],
                                spacing=8,
                            ),
                            ft.Text(
                                f"Concluídos: {sessao['concluidos']}/{sessao['total_exercicios']}",
                                color=TEXT_MUTED,
                            ),
                            ft.Text(
                                f"Editado em: {editado}" if editado else "",
                                size=11,
                                color=TEXT_MUTED,
                            ),
                            *linhas,
                            ft.Row(
                                [
                                    ft.TextButton(
                                        "Editar",
                                        icon=ft.Icons.EDIT,
                                        on_click=lambda e, i=indice_real: abrir_edicao(i),
                                    ),
                                    ft.TextButton(
                                        "Excluir",
                                        icon=ft.Icons.DELETE,
                                        style=ft.ButtonStyle(color=RED),
                                        on_click=lambda e, i=indice_real: excluir_registro(i),
                                    ),
                                ],
                                wrap=True,
                            ),
                        ],
                        spacing=7,
                    )
                )
            )

        return ft.Column(itens, spacing=12)

    def tela_editar():
        indice = edicao_atual["indice"]

        if indice is None:
            return ft.Column([titulo_secao("Editar", "Nenhum treino selecionado.")])

        sessao = dados["historico"][indice]

        itens = [
            ft.Container(
                padding=18,
                border_radius=26,
                bgcolor=CARD,
                content=ft.Column(
                    [
                        ft.Text("EDIT MODE", size=11, color=NEON, weight=ft.FontWeight.BOLD),
                        ft.Text(sessao["treino"], size=26, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{sessao['data']} • {sessao.get('dia', '')}", color=TEXT_MUTED),
                    ],
                    spacing=4,
                ),
            )
        ]

        for idx, item in enumerate(edicao_atual["campos"], start=1):
            itens.append(
                ft.Container(
                    padding=16,
                    border_radius=24,
                    bgcolor=CARD,
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    chip(f"#{idx}", CARD_2),
                                    ft.Text(item["nome"], size=17, weight=ft.FontWeight.BOLD, expand=True),
                                ],
                                spacing=8,
                            ),
                            ft.Text(item["series"], color=TEXT_MUTED, size=13),
                            ft.Row([item["carga"], item["reps"]], spacing=10),
                            item["concluido"],
                        ],
                        spacing=10,
                    ),
                )
            )

        itens.append(
            ft.Row(
                [
                    ft.OutlinedButton("Cancelar", on_click=lambda e: mostrar_tela("historico")),
                    ft.FilledButton("Salvar edição", icon=ft.Icons.SAVE, on_click=salvar_edicao),
                ],
                wrap=True,
            )
        )

        return ft.Column(itens, spacing=12)

    def tela_progresso():
        melhores = melhores_cargas()
        itens = [titulo_secao("Carga máxima", "Seus melhores registros por exercício.")]

        if not melhores:
            itens.append(pro_card(ft.Text("Salve treinos para ver sua evolução.", color=TEXT_MUTED)))
            return ft.Column(itens, spacing=12)

        maior = max([v["carga"] for v in melhores.values()] or [1])

        for nome, info in sorted(melhores.items()):
            valor = info["carga"] / maior if maior else 0

            itens.append(
                pro_card(
                    ft.Column(
                        [
                            ft.Text(nome, weight=ft.FontWeight.BOLD, size=16),
                            ft.Row(
                                [
                                    chip(f"{info['carga']} kg", NEON),
                                    chip(f"{info['reps'] or '-'} reps", BLUE),
                                ],
                                spacing=8,
                            ),
                            ft.ProgressBar(value=valor, color=NEON, bgcolor="#253041"),
                            ft.Text(info["data"], size=12, color=TEXT_MUTED),
                        ],
                        spacing=8,
                    )
                )
            )

        return ft.Column(itens, spacing=12)

    peso = ft.TextField(label="Peso kg", keyboard_type=ft.KeyboardType.NUMBER, border_radius=14)
    cintura = ft.TextField(label="Cintura cm", keyboard_type=ft.KeyboardType.NUMBER, border_radius=14)
    peito = ft.TextField(label="Peito cm", keyboard_type=ft.KeyboardType.NUMBER, border_radius=14)
    braco = ft.TextField(label="Braço cm", keyboard_type=ft.KeyboardType.NUMBER, border_radius=14)
    perna = ft.TextField(label="Perna cm", keyboard_type=ft.KeyboardType.NUMBER, border_radius=14)

    def salvar_medidas(e):
        dados["medidas"].append(
            {
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "peso": numero(peso.value),
                "cintura": numero(cintura.value),
                "peito": numero(peito.value),
                "braco": numero(braco.value),
                "perna": numero(perna.value),
            }
        )

        peso.value = cintura.value = peito.value = braco.value = perna.value = ""

        salvar_base()
        aviso("Medidas salvas.")
        mostrar_tela("medidas")

    def tela_medidas():
        itens = [
            titulo_secao("Medidas", "Acompanhe shape, peso e evolução corporal."),
            pro_card(
                ft.Column(
                    [
                        peso,
                        cintura,
                        peito,
                        braco,
                        perna,
                        ft.FilledButton("Salvar medidas", icon=ft.Icons.SAVE, on_click=salvar_medidas),
                    ],
                    spacing=10,
                )
            ),
        ]

        for m in reversed(dados["medidas"][-8:]):
            itens.append(
                pro_card(
                    ft.Column(
                        [
                            ft.Text(m["data"], weight=ft.FontWeight.BOLD),
                            ft.Text(f"Peso: {m['peso']} kg", color=TEXT_MUTED),
                            ft.Text(f"Cintura: {m['cintura']} cm", color=TEXT_MUTED),
                            ft.Text(f"Peito: {m['peito']} cm", color=TEXT_MUTED),
                            ft.Text(f"Braço: {m['braco']} cm", color=TEXT_MUTED),
                            ft.Text(f"Perna: {m['perna']} cm", color=TEXT_MUTED),
                        ],
                        spacing=4,
                    )
                )
            )

        return ft.Column(itens, spacing=12)

    def tela_config():
        seletores_dias.clear()

        bloco = bloco_do_ciclo(dados["ciclo"])

        controles = [
            titulo_secao(
                "Configurar semana",
                "Escolha os dias que você pretende treinar.",
            ),
            pro_card(
                ft.Column(
                    [
                        ft.Text("Bloco atual", weight=ft.FontWeight.BOLD),
                        ft.Row(
                            [
                                chip(bloco["nome"], ORANGE if bloco["nome"] == "PROGRESSÃO" else BLUE),
                                chip(bloco["tag"], CARD_2),
                            ],
                            spacing=8,
                        ),
                        ft.Text(bloco["descricao"], color=TEXT_MUTED, size=12),
                        ft.Text(bloco["ajuste"], color=TEXT_MUTED, size=12),
                    ],
                    spacing=8,
                ),
                CARD_2,
            ),
        ]

        for dia in TODOS_DIAS:
            selecionado = dia in dados["dias_treino"]
            checkbox = ft.Checkbox(label=dia, value=selecionado)
            seletores_dias[dia] = checkbox

            controles.append(
                ft.Container(
                    padding=12,
                    border_radius=18,
                    bgcolor=CARD,
                    content=checkbox,
                )
            )

        controles.append(
            pro_card(
                ft.Column(
                    [
                        ft.Text("Como a divisão é montada", weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "O app distribui nesta ordem: Upper A → Lower A → Cardio + Core → Upper B → Lower B.",
                            size=12,
                            color=TEXT_MUTED,
                        ),
                        ft.Text(
                            "Dias não selecionados viram descanso.",
                            size=12,
                            color=TEXT_MUTED,
                        ),
                        ft.FilledButton(
                            "Aplicar nova divisão",
                            icon=ft.Icons.CHECK,
                            on_click=aplicar_dias_treino,
                        ),
                    ],
                    spacing=8,
                ),
                CARD_2,
            )
        )

        return ft.Column(controles, spacing=12)

    botoes = {}

    def mostrar_tela(nome):
        tela_atual["nome"] = nome
        conteudo.controls.clear()

        if nome == "hoje":
            conteudo.controls.append(tela_hoje())
        elif nome == "semana":
            conteudo.controls.append(tela_semana())
        elif nome == "treino":
            conteudo.controls.append(tela_treino())
        elif nome == "historico":
            conteudo.controls.append(tela_historico())
        elif nome == "editar":
            conteudo.controls.append(tela_editar())
        elif nome == "progresso":
            conteudo.controls.append(tela_progresso())
        elif nome == "medidas":
            conteudo.controls.append(tela_medidas())
        elif nome == "config":
            conteudo.controls.append(tela_config())

        atualizar_nav()
        page.update()

    def botao_nav(nome, texto, icone):
        b = ft.TextButton(texto, icon=icone, on_click=lambda e: mostrar_tela(nome))
        botoes[nome] = b
        return b

    def atualizar_nav():
        for nome, botao in botoes.items():
            ativo = nome == tela_atual["nome"]
            botao.style = ft.ButtonStyle(
                color=ft.Colors.BLACK if ativo else ft.Colors.WHITE70,
                bgcolor=NEON if ativo else "transparent",
                shape=ft.RoundedRectangleBorder(radius=18),
            )

    nav = ft.Container(
        padding=8,
        border_radius=28,
        bgcolor=CARD,
        content=ft.Row(
            [
                botao_nav("hoje", "Hoje", ft.Icons.FLASH_ON),
                botao_nav("semana", "Semana", ft.Icons.CALENDAR_MONTH),
                botao_nav("treino", "Treino", ft.Icons.FITNESS_CENTER),
                botao_nav("historico", "Hist.", ft.Icons.LIST),
                botao_nav("progresso", "Carga", ft.Icons.TRENDING_UP),
                botao_nav("medidas", "Medidas", ft.Icons.MONITOR_WEIGHT),
                botao_nav("config", "Config", ft.Icons.SETTINGS),
            ],
            wrap=True,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        ),
    )

    page.add(
        ft.Container(
            padding=18,
            border_radius=30,
            bgcolor="#0D1320",
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("REP//LOG", size=13, color=NEON, weight=ft.FontWeight.BOLD),
                            ft.Text("Meu Treino", size=30, weight=ft.FontWeight.BOLD),
                            ft.Text("Hoje, semana, carga e evolução.", size=12, color=TEXT_MUTED),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    ft.Icon(ft.Icons.BOLT, color=NEON, size=34),
                ]
            ),
        ),
        nav,
        conteudo,
    )

    mostrar_tela("hoje")


ft.app(target=main)