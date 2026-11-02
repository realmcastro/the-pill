import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, KeepTogether, NextPageTemplate, CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import re

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + "/"
pdfmetrics.registerFont(TTFont('G', F+'EBG-R.ttf'))
pdfmetrics.registerFont(TTFont('G-B', F+'EBG-B.ttf'))
pdfmetrics.registerFont(TTFont('G-I', F+'EBGI-R.ttf'))
pdfmetrics.registerFont(TTFont('G-BI', F+'EBGI-B.ttf'))
addMapping('G',0,0,'G'); addMapping('G',1,0,'G-B'); addMapping('G',0,1,'G-I'); addMapping('G',1,1,'G-BI')

INK = colors.HexColor('#1a1a1a'); GRAY = colors.HexColor('#6b6b6b')
W, H = A4
M = 2.7*cm

def footer(c, d):
    c.saveState(); c.setFont('G', 9.5); c.setFillColor(GRAY)
    c.drawCentredString(W/2, 1.5*cm, str(d.page)); c.restoreState()

class Livro(BaseDocTemplate):
    def afterFlowable(self, f):
        e = getattr(f, 'sumario', None)
        if e:
            self.notify('TOCEntry', (e[0], e[1], self.page))

doc = Livro(os.path.join(os.path.dirname(os.path.abspath(__file__)), "the-pill.pdf"), pagesize=A4, title="THE PILL - O caminho do mestre",
                      leftMargin=M, rightMargin=M, topMargin=2.6*cm, bottomMargin=2.4*cm)
fr = Frame(M, 2.4*cm, W-2*M, H-5*cm, id='f')
# A capa é desenhada direto no canvas; a página dela não leva texto corrido.
CAPA_BG = colors.HexColor('#141414'); CAPA_PAPEL = colors.HexColor('#ece6da')
CAPA_ACENTO = colors.HexColor('#b4442c'); CAPA_CINZA = colors.HexColor('#8a857c')
def capa(c, d):
    c.saveState()
    c.setFillColor(CAPA_BG); c.rect(0, 0, W, H, stroke=0, fill=1)
    cx, cy = W/2, H*0.60
    # Anéis finos à volta da cápsula: a imagem do foco, mais apagados para fora.
    c.setStrokeColor(CAPA_PAPEL); c.setLineWidth(0.35)
    for i, r in enumerate([2.6, 3.4, 4.4, 5.6, 7.0, 8.6, 10.4, 12.4]):
        c.setStrokeAlpha(max(0.05, 0.42 - i*0.05)); c.circle(cx, cy, r*cm, stroke=1, fill=0)
    c.setStrokeAlpha(1)
    c.translate(cx, cy); c.rotate(-35)
    L, w = 6.4*cm, 2.3*cm; r = w/2
    p = c.beginPath(); p.moveTo(0, -r); p.lineTo(-L/2 + r, -r)
    p.arcTo(-L/2, -r, -L/2 + 2*r, r, startAng=270, extent=-180); p.lineTo(0, r); p.close()
    c.setFillColor(CAPA_ACENTO); c.drawPath(p, stroke=0, fill=1)
    c.setStrokeColor(CAPA_PAPEL); c.setLineWidth(1.1)
    c.roundRect(-L/2, -r, L, w, r, stroke=1, fill=0)
    c.setLineWidth(0.7); c.line(0, -r, 0, r)
    c.restoreState()
    c.saveState()
    t = c.beginText(); t.setFont('G', 40); t.setCharSpace(14); t.setFillColor(CAPA_PAPEL)
    titulo = "THE PILL"; lw = pdfmetrics.stringWidth(titulo, 'G', 40) + 14*(len(titulo) - 1)
    t.setTextOrigin(W/2 - lw/2, H*0.255); t.textOut(titulo); c.drawText(t)
    # O espaçamento do título fica no estado gráfico; repõe-se antes do resto.
    c.restoreState(); c.saveState()
    c.setStrokeColor(CAPA_CINZA); c.setLineWidth(0.5); c.line(W/2 - 1.2*cm, H*0.235, W/2 + 1.2*cm, H*0.235)
    c.setFont('G-I', 17); c.setFillColor(CAPA_PAPEL); c.drawCentredString(W/2, H*0.195, "O caminho do mestre")
    c.setFont('G-I', 10.5); c.setFillColor(CAPA_CINZA)
    c.drawCentredString(W/2, 2.9*cm, "\u201cSeu verdadeiro ser não está escondido no fundo de você, mas imensamente acima de você.\u201d")
    c.setFont('G', 9); c.drawCentredString(W/2, 2.35*cm, "Nietzsche, Schopenhauer como educador")
    c.restoreState()
doc.addPageTemplates([PageTemplate('capa', [fr], onPage=capa), PageTemplate('corpo', [fr], onPage=footer)])

base = dict(fontName='G', textColor=INK)
TIT = ParagraphStyle('tit', **base, fontSize=40, leading=46, alignment=TA_CENTER, spaceAfter=10)
SUBT = ParagraphStyle('subt', fontName='G-I', textColor=INK, fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=40)
EPI = ParagraphStyle('epi', fontName='G-I', textColor=INK, fontSize=12.5, leading=17, alignment=TA_CENTER)
EPA = ParagraphStyle('epa', **{**base, 'textColor': GRAY}, fontSize=10, leading=13, alignment=TA_CENTER, spaceBefore=4)
LIV = ParagraphStyle('liv', **{**base, 'textColor': GRAY}, fontSize=10, leading=12, alignment=TA_CENTER, spaceAfter=4)
LT = ParagraphStyle('lt', fontName='G-I', textColor=INK, fontSize=24, leading=28, alignment=TA_CENTER, spaceAfter=26)
SEC = ParagraphStyle('sec', **base, fontSize=13.5, leading=17, alignment=TA_CENTER, spaceBefore=18, spaceAfter=10, keepWithNext=1)
P = ParagraphStyle('p', **base, fontSize=11.5, leading=16.2, alignment=TA_JUSTIFY, spaceAfter=8, firstLineIndent=0)
PI = ParagraphStyle('pi', parent=P, firstLineIndent=16)
PC = ParagraphStyle('pc', parent=P, alignment=TA_CENTER)
HEAD = ParagraphStyle('head', **base, fontSize=12, leading=15, spaceBefore=14, spaceAfter=3, keepWithNext=1)
WHEN = ParagraphStyle('when', fontName='G-I', textColor=GRAY, fontSize=11, leading=15, spaceAfter=5, keepWithNext=1)
VOICE = ParagraphStyle('voice', fontName='G-I', textColor=INK, fontSize=12, leading=17, leftIndent=26, spaceAfter=1)
BODY = ParagraphStyle('body', parent=P, spaceBefore=4)
NOTE = ParagraphStyle('note', **{**base, 'textColor': GRAY}, fontSize=9.5, leading=12.5, alignment=TA_JUSTIFY, spaceAfter=6)
LAW = ParagraphStyle('law', parent=P, leftIndent=22, firstLineIndent=-22, spaceAfter=4)
EXE = ParagraphStyle('exe', **base, fontSize=12.5, leading=16, spaceBefore=14, spaceAfter=2, keepWithNext=1)
EXQ = ParagraphStyle('exq', fontName='G-I', textColor=GRAY, fontSize=10.5, leading=13.5, spaceAfter=4, keepWithNext=1)
CRE = ParagraphStyle('cre', fontName='G-I', textColor=INK, fontSize=13, leading=20, alignment=TA_CENTER, spaceAfter=6)
FLEUR = ParagraphStyle('fl', **{**base, 'textColor': GRAY}, fontSize=14, alignment=TA_CENTER, spaceBefore=10, spaceAfter=10)
BOX = ParagraphStyle('box', fontName='G-I', textColor=INK, fontSize=13, leading=19, alignment=TA_CENTER,
                     borderColor=INK, borderWidth=0.6, borderPadding=14, spaceBefore=16, spaceAfter=20, leftIndent=30, rightIndent=30)
CARD = ParagraphStyle('card', **base, fontSize=9.8, leading=12.3)
TOC0 = ParagraphStyle('toc0', **base, fontSize=11.5, leading=15, spaceBefore=8, rightIndent=1.2*cm)
TOC1 = ParagraphStyle('toc1', **{**base, 'textColor': GRAY}, fontSize=10, leading=13.5, leftIndent=0.8*cm, rightIndent=1.2*cm)
TOC_TB = TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'), ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
                     ('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),1)])

st = []
def add(t, s=P): st.append(Paragraph(t, s))
def sp(h=10): st.append(Spacer(1, h))
QUANDO = {
 "Proêmio": "na noite em que abrir o livro",
 "Como usar este livro": "na noite em que abrir o livro",
 "Da outra chance": "na noite seguinte à primeira cruz",
 "Do estribilho": "depois de Da outra chance; quando a frase soar alheia",
 "Prólogo · Do dia zero": "no dia zero, passo a passo",
 "Do primeiro dia": "na noite do dia zero; o caso da mulher, na primeira cruz",
 "Livro I · Do pensamento": "as linhas I e VI no dia zero; as outras com o exercício que as traz",
 "Livro II · Da lei e do dia": "Do dia, na noite do dia zero; o resto quando o dia o chamar",
 "Livro III · Dos exercícios": "um exercício por passagem",
 "Livro IV · Do corte": "quando um hábito desfaz o resto",
 "Livro V · Do discernimento": "no meio das estações",
 "Interlúdio · Do hábito e de quem se é": "ao fim do ciclo",
 "Do homem": "para copiar na primeira passagem",
 "Do retorno": "ao fim do ciclo",
 "Manual operacional": "opcional, depois da quarta passagem",
 "Comentário ao estribilho": "quando o estribilho parecer alheio",
 "Fontes": "para consulta",
 "Glossário": "para consulta",
 "Breviário": "para ler toda manhã; copiar na primeira passagem",
 "Dias limpos": "no dia de um corte",
 "Folha de marcas": "para copiar, todas as noites",
 "Folha do dia zero": "para copiar no dia zero",
}
def sumario(p, nivel, texto):
    q = QUANDO.get(texto) if nivel == 0 else None
    if q: texto += f"&nbsp;&nbsp;<font size=9.5 color='#6b6b6b'><i>{q}</i></font>"
    p.sumario = (nivel, texto)
    return p
# Liga as sec() no sumário do Livro I ao Interlúdio; livro() e o Interlúdio controlam.
SEC_NO_SUMARIO = False
def fleur(): add("\u2766", FLEUR)
ESTR = "Reivindique-se para si. [...]<br/>Abrace todas as horas: você dependerá menos do amanhã<br/>se lançar mão do hoje."
ESTR_A = "Sêneca, <i>Cartas a Lucílio</i>, 1 (tradução livre)"
def estr_par(nome, size, leading, after=0):
    q = Paragraph(f"<i>“{ESTR}”</i>", ParagraphStyle(nome, fontName='G-I', textColor=INK, fontSize=size, leading=leading, alignment=TA_CENTER, spaceAfter=2))
    a = Paragraph(ESTR_A, ParagraphStyle(nome+'a', parent=EPA, fontSize=max(10, round(size*0.7, 1)), leading=max(13, round(size*0.9, 1)), spaceAfter=after))
    return [q, a]
def estribilho(size=12.5, before=18, after=10):
    st.append(KeepTogether([Spacer(1, before), Paragraph("\u2766", FLEUR)] + estr_par('es', size, size*1.45) + [Spacer(1, after)]))
def estribilho_pagina():
    st.append(PageBreak()); sp(9*cm)
    st.append(KeepTogether(estr_par('esp', 15, 23)))
def livro(n, titulo):
    estribilho_pagina()
    global SEC_NO_SUMARIO
    SEC_NO_SUMARIO = n != "VI"
    st.append(PageBreak()); sp(8); add(f"L I V R O &nbsp; {n}", LIV); add(titulo, LT)
    sumario(st[-1], 0, f"Livro {n} · {titulo}")
def sec(t):
    add(t.upper().replace(" ", " &nbsp;"), SEC)
    if SEC_NO_SUMARIO: sumario(st[-1], 1, t)
CX = ParagraphStyle('cx', **base, fontSize=10.5, leading=14, alignment=TA_LEFT, spaceAfter=3)
def _caixa(pars, antes, depois):
    t = Table([[pars]], colWidths=[W-2*M])
    t.setStyle(TableStyle([('BOX',(0,0),(-1,-1),0.5,INK), ('VALIGN',(0,0),(-1,-1),'TOP'),
                           ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),8),
                           ('TOPPADDING',(0,0),(-1,-1),8), ('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    st.append(KeepTogether([Spacer(1, antes), t, Spacer(1, depois)]))
# A caixa de abertura lista as ocasiões em que se lê ou relê o capítulo, e o que se leva dele.
def abertura(ocasioes, sais):
    pars = [Paragraph(f"<b>{q if q[-1] in '.?!:' else q + '.'}</b> {a}", CX) for q, a in ocasioes]
    pars.append(Paragraph(f"<b>Com o que você sai.</b> {sais}", CX))
    _caixa(pars, 6, 14)
# Quadro de procedimento: uma ação por linha, no imperativo. Linha que começa por "· " sai sem número.
PROC_L = ParagraphStyle('procl', parent=CX, leftIndent=16, firstLineIndent=-16, spaceAfter=2)
def proc(titulo, linhas):
    pars = [Paragraph(f"<b>{titulo.upper()}</b>", ParagraphStyle('proct', parent=CX, spaceAfter=5))]
    n = 0
    for l in linhas:
        if l.startswith("· "):
            pars.append(Paragraph(l[2:], CX))
        else:
            n += 1
            pars.append(Paragraph(f"{n}.&nbsp;&nbsp;{l}", PROC_L))
    _caixa(pars, 6, 12)
FLEUR_FX = ParagraphStyle('flfx', parent=FLEUR, spaceBefore=18, spaceAfter=0)
# A caixa de fecho vai junto com o que a precede (puxa itens do fim de st), para nunca
# ficar sozinha no alto de uma página quase vazia; orn põe o ornamento logo abaixo dela.
def fecho(linhas, orn=False, puxa=1):
    t = Table([[[Paragraph("<b>Antes de seguir.</b>", CX)] + [Paragraph(l, CX) for l in linhas]]], colWidths=[W-2*M],
              spaceBefore=8, spaceAfter=10)
    t.setStyle(TableStyle([('BOX',(0,0),(-1,-1),0.5,INK), ('VALIGN',(0,0),(-1,-1),'TOP'),
                           ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),8),
                           ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    grupo = st[-puxa:] + [t]
    del st[-puxa:]
    if orn: grupo.append(Paragraph("\u2766", FLEUR_FX))
    st.append(KeepTogether(grupo))
def rom(i):
    r = ""
    for v, s in ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while i >= v:
            r += s; i -= v
    return r

# ===================== CAPA =====================
sp(1)
st.append(NextPageTemplate('corpo'))
st.append(PageBreak()); sp(8.5*cm)
st.append(KeepTogether(estr_par('es0', 17, 27)))

# ===================== SUMÁRIO =====================
st.append(PageBreak()); sp(30)
add("Sumário", LT)
st.append(TableOfContents(levelStyles=[TOC0, TOC1], dotsMinLevel=1, tableStyle=TOC_TB))

# ===================== PROÊMIO =====================
st.append(PageBreak())
add("Proêmio", LT); sumario(st[-1], 0, "Proêmio")
add("Este livro conta uma história, e o personagem dela é você. A história começa na noite em que você o abre e termina na noite em que você volta ao começo dele, um ano ou mais depois. No meio há o dia zero e uma longa série de dias comuns, em que você aprende, um gesto de cada vez, a gastar as horas de outra maneira.", PI)
add("O título vem da história de um comprimido que bastaria tomar para ficar com a cabeça clara diante de uma só coisa, com as horas passando sem que se perceba. Esse comprimido não existe. O estado existe, e você já o conheceu, numa tarde em que esqueceu o relógio. Este livro prepara o lugar onde ele aparece, para que dependa menos da sorte, e ensina a ficar nele quando vem. Os gestos, as leis e os cortes tiram o que impede o estado; uma pergunta e uma frase, <i>Isto, até acabar</i>, mantêm você nele.", PI)
add("A tese deste livro cabe numa linha: o tempo trabalha para quem recomeça. Para quem espera estar pronto, cada dia é o rio do camponês de Horácio: ele espera a água passar para atravessar, e ela nunca termina de passar. Começar, aqui, é pequeno: um gesto do tamanho de um minuto, mesmo torto. Quem erra hoje e recomeça amanhã já está do lado certo do tempo. O tempo soma os recomeços, e a queda de ontem não apaga nenhum deles.", PI)
add("Depois do dia zero, o método cabe em cinco operações: um gesto só, a marca da noite, o <i>chegou</i>, o recomeço e a frase. Todas servem para fazer você começar hoje e começar de novo amanhã. Como a vontade é a primeira coisa a faltar, o livro põe no lugar dela o que já vem decidido: a ocasião, o terreno, o gesto, a frase.", PI)
add("O livro não conhece você. Sabe só o que vai lhe pedir, e conta esses atos como se já estivessem acontecendo. Quem os torna verdadeiros é você, no seu caderno, que o livro nunca lê. Onde ele não sabe o que se passou, a história se divide em ramos, <i>se você fez..., se cedeu...</i>, e você lê o que for verdadeiro no seu caso.", PI)
add("A forma do livro vem dos antigos que liam para mudar a maneira de viver. Sêneca escolhia um único pensamento por dia e o digeria; Pierre Hadot, historiador da filosofia antiga, chamou essas práticas de <i>exercícios espirituais</i>. Aqui, cada exercício ensina um gesto, repetido de propósito num momento certo do dia, até mudar esse momento.", PI)
add("Este é um manual de formação. Os filósofos entram como interlocutores: gente que tentou viver de certo modo e deixou escrito como. Quem procurar aqui uma filosofia nova sai de mãos vazias. O que o livro tem de próprio está no treino: o gesto que chega sem ser lembrado, o piso para os dias em que faltam condições, a passagem por decisão quando a resistência tem razão.", PI)
add("Outra palavra volta muitas vezes: <i>distração</i>. Pascal escreveu nos <i>Pensamentos</i>, no século XVII, que toda a infelicidade dos homens vem de não saberem ficar em repouso num quarto. Aqui, distração é o que toma o lugar daquilo que você tem à frente e desfaz o estado.", PI)
add("Leia ainda esta noite o capítulo seguinte.", PI)

# ===================== COMO USAR ESTE LIVRO =====================
st.append(PageBreak()); sp(30)
add("Como usar este livro", LT); sumario(st[-1], 0, "Como usar este livro")
# Estilo das tabelas de consulta; o Manual operacional e o Glossário também o usam.
CU_P = ParagraphStyle('cu1', parent=BODY, fontSize=10.5, leading=13.5, alignment=TA_LEFT, spaceBefore=0, spaceAfter=0)
add("Ainda é a mesma noite. Duas palavras voltam em quase todas as páginas. <i>Este livro</i> é o que você tem nas mãos. <i>O caderno</i> é um caderno seu, de papel, e é nele que você escreve à mão tudo o que o método pede. O dia zero é o primeiro a lhe pedir páginas dele.", PI)
proc("Esta noite", [
 "Arranje um caderno de papel e uma caneta.",
 "Antes de escrever a primeira página, leia <i>Do caderno, página a página</i>, no fim do livro.",
 "Deixe em branco, desde já, as primeiras páginas que ela reserva.",
 "Escreva no alto da página 39 a data do dia zero: um dia sem trabalho.",
 "Se amanhã é o dia zero, deixe o caderno aberto e a caneta sobre a mesa.",
 "Durma cedo, sem levar ao quarto nada que distraia.",
 "Não adiante resposta nenhuma. Não leia o Prólogo antes do dia zero.",
])
add("O que se escreve antes do dia zero é escrito com as defesas de pé. De manhã, você precisa encontrar as perguntas sem resposta preparada.", PI)
add("O livro lhe pede primeiro um dia de escrita, o dia zero: um dia sem trabalho, escolhido por você. Nele você vê pelos seus atos quem é e escreve quem quer ser. Depois, o caderno aberto todos os dias, de manhã e à noite, e as cinco operações de <i>Do caminho mínimo</i>. O resto, o corte do Livro IV inclusive, entra quando a hora dele chega.", PI)
add("O tempo de cada fase:", PI)
tb = Table([[Paragraph(f"<i>{a_}</i>", CU_P), Paragraph(b_, CU_P)] for a_, b_ in (
 ("Esta noite", "Uns quinze minutos: o Proêmio e este capítulo."),
 ("O dia zero", "Cerca de quatro horas e cinquenta minutos: duas horas ao acordar, quarenta e cinco minutos à tarde e duas horas à noite, com a primeira marca."),
 ("Cada dia, desde o dia um", "Cerca de dez minutos de manhã e dez à noite, mais alguns à noite enquanto a da vez pedir uma escrita; no fim do ciclo, uns vinte à noite."))],
 colWidths=[4.2*cm, 11.4*cm], style=[('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-2),0.3,colors.HexColor('#cccccc')),('BOTTOMPADDING',(0,0),(-1,-1),4)])
st.append(tb); sp(8)
add("Cada noite de passagem, em que um exercício sai do treino e entra o seguinte, pede cerca de uma hora a mais. A primeira, em que você também copia o breviário, pede cerca de uma hora e meia.", PI)
add("Chama-se <i>ciclo</i> o caminho pelas treze microações, do primeiro exercício ao décimo terceiro. Ele começa num dia zero e termina na prova do ciclo. Não tem número mínimo de dias e dura o que durar. Um estudo de Lally (2010) encontrou semanas a meses até um gesto se fazer sozinho; o autor acha que o ciclo passa de um ano. No fim dele, você terá no caderno a folha do dia zero, as folhas de marcas, as respostas da prova, e as treze microações feitas a cada dia na sua ocasião.", PI)
proc("Como ler", [
 "Esta noite, leia o Proêmio e este capítulo.",
 "No dia zero, leia o Prólogo, um passo de cada vez.",
 "Na noite do dia zero, faça o quadro <i>Esta noite</i> de <i>Do primeiro dia</i>.",
 "Depois, leia cada parte na hora em que ela serve.",
 "Se você se perder, procure no calendário de <i>Do caminho mínimo</i> o momento em que está.",
 "Leia só o que pertence a esse momento.",
 "Se algo acontecer fora da ordem, abra <i>O que está acontecendo?</i>, logo depois deste capítulo.",
 "Se um nome aparecer antes de ser ensinado, procure-o no <i>Glossário</i>, no fim do livro.",
 "· <i>Marca</i>, <i>chegou</i> e <i>passagem</i> aparecem antes de serem ensinados.",
])
add("Os filósofos que este livro cita propõem um modo de viver; os estudos que ele cita medem médias de grupos de pessoas. Nem uns nem outros provam nada sobre você. O que prova alguma coisa a seu respeito é a sua folha de marcas, noite após noite. Cada estudo vem com um de três graus: <i>está demonstrado</i>, <i>há indícios</i>, <i>o autor acha</i>.", PI)
add("Este livro é uma síntese pessoal dessas leituras; ele não trata doença alguma e não ocupa o lugar de quem trata. O que um autor disse, contado sem aspas, é paráfrase feita a partir de traduções; entre aspas vem a tradução do próprio trecho.", PI)
add("Um aviso. Se há semanas nada lhe dá prazer, se o sono não o descansa noite após noite, se lhe vêm pensamentos de morte, ou se, mais tarde, o exame da noite se tornar a pior hora do dia, procure um médico ou alguém com formação para ouvir você; nenhum livro faz esse ofício. Os sinais estão por inteiro no Livro V, na seção <i>Do escrúpulo</i>.", PI)
sec("Do caminho mínimo")
add("Este livro é longo, e o método cabe num cartão. Depois do dia zero, ele se reduz a cinco operações; sem qualquer uma delas, deixa de existir:", PI); sp(4)
add("<i>O gesto.</i> Uma microação em treino, uma só, feita na sua ocasião; a primeira é a da ordem.<br/><i>A marca.</i> Uma por noite, sobre a ocasião que mais pesou: traço se você fez o gesto, cruz se cedeu, ponto se a ocasião não veio.<br/><i>O chegou.</i> Na noite em que o gesto vier sem que o caderno o tenha lembrado; na manhã seguinte entra o próximo exercício.<br/><i>O recomeço.</i> Caiu hoje, recomece amanhã: nunca duas noites seguidas de queda, e nada volta ao começo.<br/><i>A frase.</i> O estribilho de manhã e, ao começar a obra, <i>Isto, até acabar</i>.", CU_P); sp(8)
add("Todo o resto do livro é ferramenta. Cada parte entra quando um gatilho a chama, e nenhuma precisa ser aprendida de antemão. O calendário a seguir diz quando cada uma chega; o que não tem data se lê quando acontece.", PI)
proc("Se o livro pesar", [
 "Se numa noite o livro inteiro lhe pesar, volte a este cartão.",
 "Faça só o que ele pede.",
])
# O calendário junta numa página o QUANDO de cada parte; as voltas ficam em O que está acontecendo?.
CAL_P = ParagraphStyle('cal', parent=CU_P, fontSize=9, leading=10.8)
cal = [
 ("Esta noite", "O Proêmio e <i>Como usar este livro</i>.", "O caderno; a data do dia zero escrita nele."),
 ("O dia zero", "O Prólogo, passo a passo; à tarde, o exercício da ordem, no Livro III; à noite, o começo de <i>Do primeiro dia</i>, as regras de <i>Da medida</i> e os passos de <i>Do dia</i>, no Livro II.", "A folha do dia zero; a lista da mesa; a folha de marcas copiada; o estribilho, as linhas I e VI, a frase e a pergunta de cor; a primeira marca."),
 ("Cada dia, desde o dia um", "De manhã, o breviário, no livro.", "A manhã e a noite pelos passos de <i>Do dia</i>."),
 ("A noite da primeira cruz", "O resto de <i>Do primeiro dia</i>, com o caso da mulher, e o §4 e o §5; na noite seguinte, <i>Da outra chance</i> e <i>Do estribilho</i>.", "A lista das provas e a carta."),
 ("Quando o dia chamar", "<i>Da máscara</i>, quando a voz antiga ganhar; <i>Da assentada</i>, quando a sessão se perder; a seção do estado do dia; a lei que o livro citar, e as nove antes da primeira passagem; cada linha, com o exercício que a traz.", ""),
 ("A primeira noite de passagem", "Depois da marca, a abertura do Livro III e o resto do exercício da ordem, com a Lição I; <i>Do homem</i>; o segundo exercício.", "As treze frases copiadas na segunda página; o breviário copiado nas páginas 3 e 4."),
 ("Cada passagem seguinte", "A Lição do exercício que chegou; o exercício seguinte, e só ele.", "Na manhã seguinte, a nova da vez."),
 ("Depois da quarta passagem", "O <i>Manual operacional</i>, no apêndice, se você quiser.", "Uma ou duas ações para o resto do dia, sem marca e sem soma."),
 ("No meio das estações", "O Livro V inteiro, numa noite sem pressa, e <i>Da prova</i> uma vez só.", "As quatro provas; os sinais de <i>Do escrúpulo</i> sabidos."),
 ("O fim do ciclo", "<i>Da prova</i>, de novo; o Interlúdio; as doze Lições relidas, nos seus exercícios; <i>Do retorno</i>, na véspera do novo dia zero e na manhã dele.", "As respostas da prova; o capítulo do ciclo; um caderno novo, com a nova folha do dia zero."),
 ("Numa noite limpa, quando quiser", "<i>Da luz antiga</i>.", ""),
]
CAL_TS = [('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-2),0.3,colors.HexColor('#cccccc')),
          ('LINEBELOW',(0,0),(-1,0),0.6,GRAY),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2)]
rows = [[Paragraph(f"<font color='#6b6b6b'>{h}</font>", CAL_P) for h in ("Quando", "O que se lê", "O que se faz")]]
for a_, b_, c_ in cal:
    rows.append([Paragraph(f"<i>{a_}</i>", CAL_P), Paragraph(b_, CAL_P), Paragraph(c_, CAL_P)])
tb = Table(rows, colWidths=[3.3*cm, 7.2*cm, 5.1*cm]); tb.setStyle(TableStyle(CAL_TS))
st.append(KeepTogether([tb])); sp(10)
sec("Da primeira marca")
add("Uma coisa não espera pelo dia um. Quem prometeu muitas vezes a si mesmo e não cumpriu deixa de acreditar na própria palavra, e tem razão: a palavra deixou de ter atos por trás. O lastro volta com uma série de promessas pequenas, decididas antes, com o que conta como cumprido também dito antes, e registradas à noite tal como aconteceram. Um traço diz só que, naquele dia, você fez o que tinha decidido; uma cruz, que não fez. Nenhum dos dois julga quem você é. A confiança na própria palavra se refaz pelo acúmulo desses registros, e este livro não tem outro mecanismo para isso.", PI)
add("Por isso a primeira marca se faz no próprio dia zero. À tarde você começa a treinar um só gesto, o do primeiro exercício: <b>quando você se sentar à mesa, tudo o que distrai sai dela; quando se levantar, a mesa volta à ordem.</b> Na noite desse mesmo dia, depois da síntese, você faz a primeira marca sobre ele.", PI)
add("Se você está relendo este livro, ou outro parecido, sem nenhuma marca no caderno, ler sobre o método ocupou o lugar dele. É a forma que a distração toma em quem já tentou muitas vezes, e este livro a serve tão bem quanto qualquer outro. Nesse caso, a história parou aqui.", PI)
proc("Se não há marca", [
 "Se você relê o livro sem nenhuma marca no caderno, feche o livro agora.",
 "Escreva no caderno a data do dia zero.",
 "Até lá, não leia mais nada.",
])
fleur()

# ===================== O QUE ESTÁ ACONTECENDO? =====================
# A triagem leva do que acontece fora da ordem à seção que trata disso; os obstáculos do instante ficam na chave de Da técnica.
st.append(PageBreak())
add("O que está acontecendo?", ParagraphStyle('tri', parent=LT, spaceAfter=8)); sumario(st[-1], 0, "O que está acontecendo?")
add("Procure à esquerda a frase mais parecida com a sua. Faça o que a direita diz.", PI)
tri = [
 ("Na marca e na queda", [
  ("Falhei hoje.", "Marque cruz e escreva a linha da queda; nada se compensa. Amanhã é dia sagrado: cumpra a da vez, com o piso se preciso (§4 e §5)."),
  ("Falhei dois dias seguidos.", "Nada volta ao começo: o próximo momento é seu. Releia as linhas da queda com <i>Das quatro quedas</i>."),
  ("Não sei se foi traço ou cruz.", "Marque cruz. <i>Da medida</i>."),
  ("Acho que chegou, mas não tenho certeza.", "Não escreva <i>chegou</i>. <i>Do chegou e do engano</i>."),
  ("Uma das que ficaram caiu duas noites seguidas.", "Amanhã ela volta a ser a da vez. <i>Da medida</i>."),
  ("Cedi no hábito que cortei.", "Escreva <i>caí; a linha continua</i>. Nunca dois dias seguidos. Esta noite, leia <i>Da queda</i>."),
  ("Depois da queda, penso que sou assim; uma frase herdada parece fato.", "Leia a Lição XII, no fim do Livro III."),
  ("Já tentei demais; perdoar-me parece indulgência.", "Leia <i>Por que mais uma vez</i> e <i>Da firmeza e do perdão</i>."),
 ]),
 ("No gesto que não chega", [
  ("O gesto não chega há semanas.", "Leia <i>Das quatro quedas</i> antes de mudar qualquer coisa; depois, <i>Da resistência que fala</i>."),
  ("Vejo um defeito no método.", "Escreva-o na folha de captura, com a data e a razão. Emende só na passagem (§9)."),
  ("A da vez parece pouco; o estribilho soa alheio.", "Leia <i>Do estribilho</i> e o <i>Comentário ao estribilho</i>."),
  ("Uma linha parece vazia quando a digo.", "Leia a seção <i>Do sentido</i> dessa linha, fora das horas da obra."),
 ]),
 ("Na sessão e no começo", [
  ("Não consigo começar; hoje não tenho vontade.", "Diga a linha VI e faça a versão de dois minutos. Sem vontade, faz-se igual (§3)."),
  ("No instante: a cabeça cheia, a dispersão, o medo, a raiva.", "Abra a chave de <i>Da técnica</i> e leia só a seção do obstáculo."),
  ("Sento sem saber o que fazer, adio na preparação, quero trocar de obra, me interrompem.", "Leia <i>Da assentada</i>; inteiro, na véspera de toda obra nova."),
  ("No meio da obra, quero parar.", "Diga a linha II, <i>é vontade, não fato</i>, e termine o passo. Nessa noite, leia <i>Do pêndulo</i>."),
  ("Não sei se é o pêndulo ou o cansaço.", "Leia o fim de <i>Do que volta</i>. Amanhã cedo, faça a prova do sono."),
  ("A voz antiga ganha; amanhã é um dia grande.", "Diga a pergunta: <i>O que ele faria agora?</i> <i>Da máscara</i>."),
  ("Um hábito estraga a sessão.", "Nessa noite, leia o Livro IV e <i>Dias limpos</i>."),
  ("Cortei um hábito e sobra uma hora vazia.", "Leia <i>Da paixão contrária</i>."),
 ]),
 ("No ânimo e no corpo", [
  ("Acordei com febre, em viagem, ou alguém da casa precisa de mim.", "De manhã, escreva <i>hoje, piso</i> no caderno. <i>Do piso</i>."),
  ("Há três manhãs, o peso da véspera não passa com o sono.", "Se a hora de parar foi cumprida, declare por escrito amanhã como dia de ócio. <i>Do descanso</i>."),
  ("Quero desistir de tudo.", "Leia a carta, no fundo do caderno. Se ainda não a escreveu, leia <i>Da outra chance</i> esta noite."),
  ("A voz diz que nada mudou.", "No começo, leia <i>Da luz antiga</i>; no fim do ciclo, <i>Da vontade que desceu</i>."),
  ("No fim do ciclo, me pergunto quem fez tudo isto.", "Leia <i>Da objeção que ficou</i> e <i>Do mesmo e de si</i>."),
  ("A anti-visão ou o exame da noite me afundam; a marca não se decide.", "Leia <i>Do escrúpulo</i>, no Livro V."),
  ("Estou mal há semanas: nada me dá prazer, o sono não descansa.", "Procure um médico ou alguém com formação para ouvir você; <i>Do escrúpulo</i>."),
  ("Um hábito cortado volta sempre e já me custa a saúde, o dinheiro ou as pessoas.", "Procure ajuda profissional; a nota de <i>Da contagem</i>; <i>Do escrúpulo</i>."),
  ("Tenho pensamentos de morte.", "Fale hoje com alguém e procure ajuda hoje; no Brasil, o CVV atende pelo 188 a qualquer hora. <i>Do escrúpulo</i>."),
 ]),
]
rows = [[Paragraph(f"<font color='#6b6b6b'>{h}</font>", CAL_P) for h in ("O que está acontecendo", "Para onde ir")]]
ts = list(CAL_TS)
for bloco, casos in tri:
    ts += [('SPAN',(0,len(rows)),(1,len(rows))), ('TOPPADDING',(0,len(rows)),(1,len(rows)),5)]
    rows.append([Paragraph(f"<font color='#6b6b6b'>{bloco.upper()}</font>", CAL_P), ""])
    for a_, b_ in casos:
        rows.append([Paragraph(f"<i>{a_}</i>", CAL_P), Paragraph(b_, CAL_P)])
tri_tb = Table(rows, colWidths=[6.3*cm, 9.3*cm]); tri_tb.setStyle(TableStyle(ts))
st.append(tri_tb)

# ===================== PRÓLOGO: DO DIA ZERO =====================
st.append(PageBreak()); sp(30)
add("Prólogo", LIV)
add("Do dia zero", LT); sumario(st[-1], 0, "Prólogo · Do dia zero")
add("<i>“Diga primeiro a si mesmo quem você quer ser; depois faça o que tem de fazer.”</i>", ParagraphStyle('pz1', parent=PC, fontSize=12, spaceAfter=2))
add("Epicteto, <i>Discursos</i>, III, 23", ParagraphStyle('pz2', parent=EPA, spaceAfter=18))
proc("Este capítulo", [
 "Leia o roteiro no dia zero, um passo de cada vez, na hora que o título dele indica.",
 "Onde o texto disser <i>escreverá</i>, escreva.",
 "Não leia o passo seguinte antes de terminar o que está fazendo.",
 "Se escrever a anti-visão afunda você em vez de movê-lo, leia <i>Como se escreve a visão</i> e passe à visão.",
 "Leia o Livro V depois do dia zero.",
 "· Sem a folha do dia zero escrita na primeira página do caderno, o dia um não começa.",
])
add("A frase do alto, em paráfrase, é de Epicteto. Ele nasceu escravo na Frígia e, liberto, ensinou filosofia em Roma e depois em Nicópolis. No capítulo de onde ela vem, lembra que quem se dedica ao atletismo decide primeiro que atleta quer ser, e só depois treina e come como esse atleta. Os atos de um dia só têm direção quando antes se decidiu quem se quer ser. Para os estoicos, essa decisão é das poucas coisas que dependem inteiramente de nós. O dia zero é a primeira metade da frase; os exercícios são a segunda.", PI)
add("O <b>dia zero</b> abre o ciclo; à tarde entra o primeiro gesto, e a noite dele termina com a primeira marca. Nele você examina a vida como está e escreve para onde quer levá-la. Este capítulo conta esse dia no futuro, porque você ainda não o viveu.", PI)
add("Você sai dele com um único objeto, a <b>folha do dia zero</b>: oito pontos de uma ou duas linhas, escritos à mão, à noite, na primeira página do caderno. Há um modelo em branco no fim do livro. A folha é relida nas noites de passagem e escrita de novo no começo de cada ciclo. Tudo o que vem depois trabalha para o que essa página disser.", PI)
add("A ideia vem de Dan Koe, escritor contemporâneo, no ensaio <i>Como consertar a vida inteira em um dia</i>. O centro dela é este: as pessoas não mudam porque tentam mudar os atos sem mudar quem são. E quem elas são está escrito nos atos com mais exatidão do que nas intenções. Por isso o dia zero lê atos: as perguntas da manhã pedem o que você fez.", PI)

# ---------- O ROTEIRO ----------
sec("O roteiro")
add("O dia zero tem quatro tempos, e cada um é um passo do roteiro: a manhã, o dia, a síntese e o fecho.", PI)
proc("O tempo do dia zero", [
 "Escolha um dia em que você não trabalhe.",
 "Reserve duas horas ao acordar, para a escavação.",
 "Reserve quarenta e cinco minutos à tarde, para a mesa.",
 "Reserve duas horas antes de dormir, para a síntese e a primeira marca.",
 "No resto do dia, viva normalmente e pare nos quatro horários.",
])
add("Tudo cabe num só dia de propósito. Um exame espalhado por muitos dias se dilui: cada resposta da segunda-feira seria corrigida pelo humor da terça. Num só dia, a escavação, as provas vivas e a síntese pertencem à mesma pessoa, no mesmo estado, e ela não tem tempo de reconstruir as defesas. O que os retiros longos faziam em semanas, este livro distribui depois pelos dias, uma microação de cada vez.", PI)

def passo(n, titulo, sub):
    st.append(CondPageBreak(4*cm))
    st.append(KeepTogether([Paragraph(f"{n}. &nbsp;{titulo}", ParagraphStyle('ps', parent=HEAD, fontSize=13.5, spaceBefore=18)),
                            Paragraph(sub, WHEN)]))
def pergunta(q, para, como):
    st.append(KeepTogether([Paragraph(q, ParagraphStyle('pq2', parent=VOICE, leftIndent=0, spaceBefore=10, spaceAfter=3)),
                            Paragraph(f"<b>Para quê.</b> {para}", BODY),
                            Paragraph(f"<b>Como.</b> {como}", BODY)]))

passo("I", "A manhã: a escavação", "Cerca de duas horas, logo ao acordar, antes de qualquer distração.")
add("Esta hora se chama escavação porque desce por camadas. Começa no que incomoda na superfície de um dia seu e termina no que você nunca disse a ninguém.", PI)
add("Na entrada do templo de Apolo, em Delfos, estava escrita uma frase curta: <i>conhece-te a ti mesmo</i>. O peregrino a lia antes de fazer a própria pergunta ao oráculo. Platão conta, na <i>Apologia</i>, que a sacerdotisa disse não haver ninguém mais sábio do que Sócrates. Sócrates, que se julgava ignorante, interrogou políticos, poetas e artesãos para entender a resposta. Todos julgavam saber o que não sabiam; a vantagem dele era não julgar saber. Em 399 a.C., condenado por esse exame, disse aos juízes que a vida sem exame não vale a pena para um homem.", PI)
add("Sócrates examinava em conversa, a dois. O exame desta manhã é feito a sós e por escrito. Dele o dia zero toma uma parte: descobrir que você julgava saber sobre si coisas que os seus atos desmentem.", PI)
proc("A escrita da manhã", [
 "Ao acordar, antes de qualquer outra coisa, sente-se diante do caderno aberto na página 39.",
 "Responda à mão às perguntas, na ordem.",
 "Escreva o que é verdade. Ninguém vai ler isto.",
 "Responda primeiro depressa.",
 "Depois aprofunde.",
 "Se uma resposta incomoda você, fique nela mais um pouco.",
 "Confira o sinal no fim do <b>Como</b> de cada pergunta.",
 "Se o sinal não está na sua página, volte à pergunta antes de passar à seguinte.",
])
add("O incômodo marca o lugar onde há alguma coisa.", PI)
pergunta("1. Que insatisfação surda você aprendeu a tolerar?",
 "Uma insatisfação tolerada há muito tempo deixa de ser notada, e por isso não se corrige. É preciso procurá-la de propósito.",
 "Percorra um dia seu, da hora em que você acorda à hora em que dorme. Anote cada momento em que algo pesa sem que você reclame. Escreva pelo menos três. Está respondida quando cada linha nomeia um momento, com hora ou lugar, e não só um estado de espírito.")
pergunta("2. Do que você se queixa há anos sem mudar nada?",
 "Quando uma queixa se repete há anos sem nenhuma ação, manter a situação serve a você de alguma maneira.",
 "Liste as queixas. Ao lado de cada uma, escreva o que você fez de fato para mudá-la. Onde a coluna estiver vazia, pergunte: o que eu ganho deixando isto como está? Conforto, desculpa, segurança, não arriscar? Está respondida quando, ao lado de cada coluna vazia, há um ganho escrito.")
pergunta("3. Se alguém observasse só os seus atos durante uma semana, o que concluiria que você quer?",
 "Aqui se vê a identidade real, a que os atos revelam, separada da que as intenções declaram.",
 "Descreva a última semana com honestidade: para onde foram o tempo, a atenção, o dinheiro. Depois complete uma frase: <i>os meus atos dizem que eu quero ____</i>. Não a suavize. Está respondida quando a frase desagrada ou surpreende você; se coincide com o que você diria de si numa conversa, você ainda descreveu intenções.")
add("Demore-se nesta pergunta: é o coração do dia. Todo comportamento persegue um fim, mesmo quando você não o admite. Quem diz que quer escrever e passa as noites nas distrações do próprio tempo cumpre um fim que não confessa: o alívio, não se expor, não ser julgado. As resoluções de começo de ano mudam o gesto e deixam o fim intacto. Na primeira semana difícil, a identidade antiga recupera o terreno, por coerência com o que você ainda quer sem confessar.", PI)
add("Mudar pede duas coisas, e o dia zero faz as duas. Ver quem você é agora, pelos atos. Decidir quem quer ser, também em atos, para que os dias seguintes acumulem as provas.", PI)
add("Ao escrever a frase, você vai objetar que é mais do que os seus atos: há intenções sem ocasião, um afeto que não sabe mostrar, um talento sem tempo. O dia zero não pronuncia sentença sobre o que você é no fundo. Ele lê provas, e só provas. Uma intenção que nunca toca um ato não governa os seus dias, e é dos dias que este livro se ocupa. Esta manhã, escreva a frase como os atos a ditam.", PI)
add("A quarta pergunta pede a anti-visão e tem um método próprio, logo abaixo.", ParagraphStyle('pc2', parent=PI, spaceBefore=8))
pergunta("4. Se nada mudar, como será uma terça-feira sua daqui a cinco anos? E daqui a dez?",
 "É a anti-visão em bruto. Uma terça-feira concreta pesa mais do que um futuro abstrato.",
 "Siga <i>Como se escreve a anti-visão</i>, logo abaixo: a seção faz parte desta pergunta. Está escrita quando a frase passa no teste do fim da seção.")

sec("Como se escreve a anti-visão")
add("A <b>anti-visão</b> é a vida que você terá se nada mudar, descrita com detalhe, sem drama e sem consolo. Ela dá peso. Quase ninguém sente com precisão quanto custa a vida atual, e enquanto esse preço é abstrato, a visão pesa pouco. Por isso a anti-visão vem antes da visão.", PI)
add("Os estoicos tinham um exercício parecido, a <i>praemeditatio malorum</i>, a meditação antecipada dos males. Lucílio, o amigo a quem Sêneca escrevia, temia um processo que podia arruiná-lo. Sêneca respondeu, na Carta 24, sem consolo: suponha que vai acontecer o que você teme, e meça esse mal. Verá que ele é menor, ou mais breve, do que o medo anunciava.", PI)
add("A anti-visão usa o mesmo gesto com a direção invertida. Os males de Sêneca vinham de fora, não dependiam de Lucílio, e o exercício ensinava a esperá-los com calma. O mal da anti-visão vem de dentro: é a sua própria semana, repetida. Ele depende de você, e o exercício troca a calma diante do inevitável pela recusa do evitável.", PI)
DOM = ParagraphStyle('dom', parent=LAW, spaceAfter=5)
add("A cena se escreve sobre seis partes da vida, as mesmas que a visão vai percorrer. Não as confunda com <i>o domínio</i>, no singular, que você escreve no fim da manhã. Se deixar uma de fora, desconfie: é a que você mais evita olhar.", PI)
for a_, b_ in [("O corpo.", "A força, a saúde, o sono, a energia com que você acorda, o que vê no espelho."),
               ("A obra.", "O trabalho, o estudo, o domínio: o que você faz com as suas melhores horas e o que fica feito."),
               ("A mente.", "A atenção, o humor, o que ocupa a cabeça quando ela está livre, o ruído e o silêncio."),
               ("As pessoas.", "A família, as amizades, o amor, quem está perto, quem se afastou, como tratam você e como você trata os outros."),
               ("A liberdade.", "O tempo que é seu, o dinheiro que permite ou impede escolhas, os lugares aonde você pode ir."),
               ("O caráter.", "O que dizem de você quando você não está, e o que você pensa de si quando está sozinho.")]:
    add(f"<b>{a_}</b> {b_}", DOM)
proc("A anti-visão", [
 "Pegue a semana que você descreveu na terceira pergunta.",
 "Imagine-a repetida duzentas e sessenta vezes: são cinco anos.",
 "Para cada parte da vida, pergunte onde essa repetição deixa você.",
 "Prolongue a tendência atual. Não invente catástrofe.",
 "Escreva uma cena: uma terça-feira daqui a cinco anos, na primeira pessoa e no presente.",
 "· <i>Acordo às..., o corpo está..., abro o dia com..., no trabalho...</i>",
 "Percorra o dia hora a hora, até o pensamento antes de dormir.",
 "Use os sentidos: o espelho, os ombros, o tom de voz de quem fala com você.",
 "Releia a cena e confira se cada uma das seis partes aparece nela.",
 "Onde faltar uma, acrescente uma frase.",
 "Escreva, em meia página, a terça-feira daqui a dez anos.",
 "Responda numa linha: se esta tivesse sido a vida inteira, o que direi dela no fim?",
 "Condense tudo numa frase: <i>Se nada mudar, serei alguém que ____.</i>",
 "Leve essa frase para a folha do dia zero.",
])
add("Se você exagera, o espírito descarta o texto como drama. Se é exato, ele não tem por onde fugir. Uma cena pesa mais do que uma lista, que se lê sem sentir e se discute com facilidade. O detalhe concreto dá o peso: o silêncio de quem deixou de falar com você. Na pergunta dos dez anos, a morte devolve a cada dia o seu peso.", PI)
proc("O teste da anti-visão", [
 "Releia a frase em voz baixa.",
 "Se ela incomoda você, está escrita.",
 "Se não incomoda, volte à cena e procure o que você suavizou.",
 "Se vier o pensamento <i>isto é exagero</i>, releia a cena frase a frase.",
 "Mantenha o que prolonga a semana real.",
 "Corte o que a ultrapassa.",
])
add("Depois desta manhã, a anti-visão é lida só nas noites de passagem e na onda. O peso dela se gasta com o uso.", PI)
add("A anti-visão serve para orientar. Se escrevê-la afunda você em vez de movê-lo, se o peso vira desespero, pare e passe à visão. Depois, leia o Livro V: ele ensina a distinguir a resistência que se atravessa da que se deve ouvir.", NOTE)

add("Com a frase escrita, as duas perguntas seguintes descem mais fundo, e são curtas.", PI)
pergunta("5. Que verdade sobre você seria a mais dura de admitir?",
 "A frase que você evita é a que explica o resto.",
 "Escreva-a numa linha. Se ela não aparecer, pergunte: o que eu não diria a ninguém sobre mim, nem a quem confio? Está escrita quando é uma frase que você não diria a ninguém; se a diria num jantar, ainda não é ela.")
pergunta("6. Que pessoa você teria de deixar de ser para mudar, e o que ela lhe dá que você teme perder?",
 "A identidade antiga dá a você alguma coisa em troca do que custa. Enquanto você não souber o quê, é difícil largá-la.",
 "Descreva essa pessoa em uma frase e, abaixo, o que ela garante a você: aprovação, conforto, uma desculpa pronta, a imagem intacta do que você poderia ter sido, que nenhuma prova desmentiu. Está respondida quando o que ela garante tem nome concreto: <i>conforto</i>, sozinho, ainda é vago; conforto de quê, e diante de quem?")
add("Agora, o contrário. Termine as seis antes de começar. Se a mão pesa e você quer fechar o caderno, vire a página mesmo assim: a exatidão da anti-visão ainda está fresca.", ParagraphStyle('pc3', parent=PI, spaceBefore=8))
pergunta("7. Se você pudesse viver uma terça-feira daqui a três anos exatamente como quisesse, como ela seria?",
 "É a visão em bruto. Uma terça-feira, porque a vida se passa nos dias comuns, e um sábado de férias mente sobre ela.",
 "Siga <i>Como se escreve a visão</i>, logo abaixo. Está escrita quando passa no teste do fim da seção.")

sec("Como se escreve a visão")
add("A <b>visão</b> é a vida que você quer daqui a três anos, descrita nas mesmas seis partes e com o mesmo detalhe da anti-visão. Ela dá direção ao peso que a anti-visão criou. Sozinha, a visão pesa pouco; sozinha, a anti-visão não indica para onde ir.", PI)
proc("A visão", [
 "Para cada uma das seis partes, escreva como ela está numa terça-feira daqui a três anos.",
 "Teste a ambição: alguém com os seus recursos, constante por três anos, conseguiria isso?",
 "Se a resposta é <i>nunca</i>, corte: é fantasia.",
 "Se a resposta é <i>facilmente</i>, aumente: é pequena demais.",
 "Descreva cada parte pelo que você faz.",
 "Troque cada estado por um ato: <i>acordo às seis, escrevo duas horas, treino à tarde</i>.",
 "Para cada linha, pergunte: <i>quero isto, ou quero ser visto com isto?</i>",
 "Risque as linhas que você quer para ser visto.",
 "Escreva a terça-feira hora a hora, com o detalhe e os sentidos da anti-visão.",
 "Condense numa frase: <i>Sou alguém que ____</i>, com os três atos mais característicos da cena.",
])
add("Três anos é um prazo longo o bastante para exigir mudança e curto o bastante para imaginar a terça-feira com detalhe. <i>Sou feliz e realizado</i> não se pratica. Os estados são consequência; só os atos se praticam. As duas cenas lado a lado mostram a distância exata a percorrer.", PI)
add("Sartre, em <i>O ser e o nada</i>, chamou de <i>olhar</i> a experiência de se sentir visto por outro e de passar a ser, aos próprios olhos, o que o outro vê. A visão emprestada faz desse olhar um plano de três anos: descreve a vida que os outros aprovariam ao ver você. Mais tarde você vai copiar os meios de quem já chegou. Os fins, você os escreve aqui, e eles são seus.", PI)
add("Para saber se a visão é sua, há um instrumento antigo. Inácio de Loyola começou a escrever os <i>Exercícios espirituais</i> em Manresa, em 1522, quando ainda não era ninguém: um ex-soldado coxo, que vivia de esmolas e anotava num caderno o que se passava na própria alma. No centro do retiro está a <i>eleição</i>, a escolha de um estado de vida. Para o tempo em que a alma está tranquila, ele propõe um exercício de imaginação. Considere como você estaria no leito de morte, pergunte que escolha quereria então ter feito, e faça essa escolha agora.", PI)
proc("O leito de morte", [
 "Depois de escrever a cena, imagine-se velho, perto do fim, olhando para trás.",
 "Pergunte, linha a linha: eu quereria ter vivido esses três anos assim?",
 "Risque as linhas que não aguentam a pergunta.",
])
add("As linhas que não aguentam são as que você queria para ser visto. Não é preciso a fé de Inácio para usar a distância que ele dava: perto da morte, a opinião dos outros conta pouco.", PI)
proc("O teste da visão", [
 "Leia a visão em voz alta.",
 "Se ela sugere um primeiro gesto, está escrita.",
 "Se ela só dá prazer, sem puxar para gesto nenhum, troque cada estado pelo que você faria.",
])
add("<b>A distância.</b> O espaço entre as duas terças-feiras é o que você tem a percorrer nos próximos anos. À noite, o alvo de um ano será o primeiro terço desse caminho.", PI)

pergunta("8. Que tipo de pessoa vive essa terça-feira? O que ela faz todos os dias?",
 "A visão só se pratica traduzida nos gestos diários de quem a vive. Essa pessoa é <i>ele</i>, o rosto da máscara, e os cinco gestos respondem todos os dias a <i>O que ele faria agora?</i>",
 "Liste cinco coisas que essa pessoa faz todos os dias, como gestos observáveis. Escreva <i>lê antes de dormir</i>, <i>treina às sete</i>; <i>é disciplinada</i> não serve. Está respondida quando cada uma das cinco pode ser marcada à noite como feita ou não feita.")
add("Antes de fechar o caderno, falta o <b>exercício zero</b>, o primeiro do livro e o único que se escreve hoje. Ele não tem microação nem marca: é feito uma vez por ciclo, nesta manhã. Ele dá ao caminho o <b>domínio</b>, o campo de trabalho ou de estudo em que você vai até o fundo e ao qual dará as suas melhores horas. Os outros treze exercícios treinam gestos, e um gesto precisa de uma obra à qual servir.", PI)
proc("O exercício zero", [
 "Liste à mão tudo o que você amou fazer ou estudar desde criança, sem filtro de utilidade.",
 "Ao lado de cada item, escreva o momento em que esqueceu o tempo fazendo aquilo.",
 "Sublinhe o que se repete.",
 "Escreva o domínio em uma frase. Uma combinação de campos serve.",
 "Embaixo, escreva o porquê com rosto: o que tira você da cama numa terça-feira, sem plateia.",
 "Explique o domínio em voz alta, em trinta segundos.",
 "Se a frase não sai limpa, escreva um domínio provisório. Não deixe a linha em branco.",
 "Se a lista não mostra nada, leia a estação zero, no Livro III.",
])
proc("Ao fim da manhã", [
 "Escreva no caderno quatro horários espalhados pelo dia: por exemplo, onze, uma e meia, quatro, sete.",
 "Feche o caderno.",
 "Não releia nada até a noite.",
])
add("Algumas páginas terão uma letra que já não é a do começo. O que você escreveu precisa assentar, e uma releitura no meio do dia é o primeiro convite para suavizar.", PI)

passo("II", "O dia: as interrupções", "Da manhã até a noite, vivendo normalmente.")
add("Depois da escavação, você vive o dia como sempre, com o curso habitual interrompido nos quatro horários. Em cada um, três perguntas:", PI)
for q in ["O que estou evitando agora, ao fazer isto?",
          "Se alguém me visse agora, que pessoa diria que sou?",
          "Isto me aproxima da terça-feira que quero ou da que recuso?"]:
    add(q, VOICE)
sp(4)
proc("As interrupções", [
 "Quando cada horário chegar, pare por um minuto, onde estiver.",
 "Escreva três linhas, uma resposta para cada pergunta acima.",
 "Não corrija nada ainda.",
 "Se um horário passar sem que você perceba, escreva as três linhas quando se lembrar.",
 "Anote a hora real e o esquecimento.",
 "Se vier a frase <i>agora não dá, escrevo depois</i>, escreva as três linhas mesmo assim.",
 "· Essa frase serve como primeira linha.",
 "Se há meia hora livre no meio da tarde, caminhe sozinho, sem ruído.",
 "Numa hora livre da tarde, leia no Livro III o exercício da ordem: o gesto do alto, <i>Do começo</i> e <i>Da marca</i>.",
 "Faça o que pede o quadro <i>Na tarde do dia zero</i>.",
])
add("A escavação da manhã mostrou o padrão na memória. As interrupções mostram o padrão acontecendo, como provas vivas para a noite. Ao fim do dia, você terá doze linhas, e o esquecimento também é matéria para a noite. A frase <i>agora não dá</i> vem da mesma voz que a primeira pergunta pede para observar, e ela acabou de responder por você.", PI)
add("Na caminhada, lembre-se de Sócrates. Ele examinava os atenienses na ágora, entre as bancas do mercado e as portas dos tribunais. Interrogava homens pegos no meio do que estavam fazendo, e ali as respostas deixavam de ser as que se preparam em casa. As interrupções fazem o mesmo, e por isso a resposta sai mais verdadeira.", PI)

passo("III", "A noite: a síntese", "Cerca de uma hora e meia, a sós e em silêncio.")
add("Esta hora se chama síntese porque, de muitas páginas, faz uma só: a folha do dia zero.", PI)
proc("A síntese", [
 "Sente-se à mesa arrumada, a sós.",
 "Antes de abrir o caderno, tire da mesa o que distrai.",
 "Releia tudo o que escreveu desde a manhã.",
 "Sublinhe o que se repete.",
 "Se o dia mostrou o que a manhã não viu, corrija a anti-visão, a visão e o domínio.",
 "Copie os três para a primeira página, com os oito títulos do modelo do fim do livro.",
 "Tire a frase de identidade da oitava pergunta.",
 "Escreva os outros quatro pontos descendo a escada.",
])

sec("Da escada: do ano ao dia")
add("A escada vai da visão, a três anos, até o gesto de amanhã. Cada degrau nasce do anterior.", PI)
esc = [
 ("O ano.", "O <b>alvo de um ano</b> é uma única conquista que, daqui a doze meses, estará feita ou não. São quatro critérios: uma só; verificável com sim ou não; dependente sobretudo de você; e que incomode você um pouco ao escrevê-la. Quem escolhe três não cumpre nenhuma."),
 ("A obra em curso.", "A <b>obra em curso</b> é o primeiro passo grande na direção do alvo. Ela deixa um objeto no mundo: um capítulo, uma entrega, uma marca no treino, uma prova feita. A medida de partida é um mês, mas ela termina quando existe, e o calendário não decide."),
 ("O dia.", "A <b>obra de hoje</b> desce da obra em curso toda manhã: é o pedaço dela que cabe num dia. As <b>alavancas diárias</b> são duas ou três ações de todos os dias que fazem avançar a obra em curso, descritas em gestos e minutos, como <i>estudar das oito e meia às dez</i>. Têm esse nome porque são pequenas ao lado do que movem. A alavanca é a ação; a obra de hoje é o que ela deixa feito. A da vez fica fora delas, porque acontece dentro do dia, na sua ocasião. As alavancas não têm marca própria: à noite, a linha do dia diz se foram feitas."),
 ("As regras.", "De três a cinco frases que começam com <i>não</i>: o que você não sacrificará para chegar lá. <i>Não durmo menos de sete horas. Não abandono quem depende de mim. Não minto para cumprir um prazo.</i> Se o plano exigir quebrá-las, refaça o plano."),
]
for i,(a_,b_) in enumerate(esc,1):
    add(f"{rom(i)}. &nbsp;<b>{a_}</b> {b_}", LAW)
proc("A escada", [
 "Desça de cima para baixo, sem pular degrau.",
 "Olhe a visão.",
 "Pergunte: que conquista, em doze meses, tornaria essa terça-feira muito mais provável?",
 "Escreva o alvo de um ano.",
 "Confira os quatro critérios.",
 "Divida o ano nos marcos que o compõem.",
 "Escreva o primeiro marco como obra em curso.",
 "Escreva duas ou três alavancas diárias, com hora e minutos.",
 "Escreva de três a cinco regras.",
 "Escreva cada degrau no caderno antes de passar à folha.",
])
proc("Quando a obra em curso fica pronta", [
 "Nessa noite, escreva a seguinte, descendo de novo a partir do ano.",
 "Reveja o ano no dia zero do ciclo seguinte.",
 "Se os doze meses do alvo terminam no meio do ciclo, reveja o alvo na passagem seguinte.",
 "Faça essa revisão por escrito, diante das marcas, como qualquer outra emenda.",
])
proc("A folha", [
 "Escreva na folha os oito pontos, na ordem.",
 "Aplique a cada um o seu teste.",
 "Se a resposta não passa, reescreva-a antes de passar ao ponto seguinte.",
])
sint = [
 ("A anti-visão.", "A frase de condensação: <i>Se nada mudar, serei alguém que ____.</i>", "Ao relê-la, deve incomodar. Se não incomoda, é fraca."),
 ("A visão.", "A frase de condensação da visão, dita em atos.", "Deve ser possível imaginar alguém fazendo isso. Se só tem adjetivos, reescreva."),
 ("O domínio.", "O campo em que você vai até o fundo, em uma frase, com o porquê com rosto embaixo, como você o escreveu de manhã no exercício zero.", "Você consegue explicá-lo em trinta segundos sem hesitar."),
 ("O alvo de um ano.", "Uma única coisa que, daqui a doze meses, estará feita ou não.", "Daqui a um ano, a resposta será sim ou não, sem discussão."),
 ("A obra em curso.", "O primeiro passo grande na direção do alvo, que deixa um objeto no mundo, e termina quando existe.", "Quando estiver feita, existirá algo que hoje não existe."),
 ("As alavancas diárias.", "Duas ou três ações de todos os dias que movem a obra em curso, com hora e minutos. A da vez não entra aqui.", "Cabem num dia comum, mesmo depois de uma noite mal dormida."),
 ("As regras.", "O que você não sacrificará para chegar lá: o sono, o corpo, as pessoas que ama, a sua ética.", "Se o plano exigir quebrá-las, o plano está errado."),
 ("A frase de identidade.", "<i>Sou alguém que ____</i>, três vezes, completadas com os gestos da pergunta oito.", "Cada frase descreve um ato que se pode verificar: feito ou não feito."),
]
for i,(t_,o_,te_) in enumerate(sint,1):
    st.append(KeepTogether([Paragraph(f"{rom(i)}. &nbsp;<b>{t_}</b> {o_}", LAW),
                            Paragraph(f"<font color='#6b6b6b'>Teste:</font> <i>{te_}</i>", ParagraphStyle('tst', parent=BODY, leftIndent=22, spaceBefore=0, spaceAfter=7))]))
add("", PI)
proc("As duas frases", [
 "Leia em voz alta a frase da anti-visão.",
 "Logo depois, leia em voz alta a frase da visão.",
 "Se uma soa mais verdadeira do que a outra sem razão, volte a ela.",
 "Procure onde você exagerou ou onde suavizou.",
])
add("Ouvidas juntas, as duas frases mostram que a distância entre elas cresce ou diminui com os dias que vierem. Se você não decidir nada, os dias seguem na direção da primeira.", PI)
add("Em Paris, nos anos em que aprendia com Rodin a olhar uma coisa até o fim, Rilke escreveu um poema sobre um torso arcaico de Apolo. A estátua não tem cabeça nem olhos, mutilada pelos séculos. E no entanto, diz o poema, a pedra brilha como se o olhar ainda ardesse lá dentro, e não há nela um ponto que não veja você. O último verso não parece decorrer do resto: <i>você tem de mudar a sua vida</i>. Diante de uma coisa feita por inteiro, quem olha se sente olhado e percebe o que na própria vida ainda está por fazer. A ordem de mudar vem desse ser visto, antes de qualquer argumento.", PI)
add("A folha desta noite mostra você a si mesmo de modo parecido, pelos seus atos e pela terça-feira que você quer. O que fazer com isso se decide nos dias seguintes.", PI)

sec("Dos erros comuns")
add("Estes seis erros são os modos de um dia zero falhar sem que se perceba.", PI)
proc("Antes de fechar o caderno", [
 "Confira a folha e as páginas da manhã contra os seis erros abaixo.",
 "Corrija esta noite o que encontrar.",
 "· A partir de amanhã, a folha só se emenda numa passagem.",
])
erros = [
 ("Escrever bonito.", "Frases que impressionariam alguém e não dizem nada a você. Ninguém vai ler isto."),
 ("Responder em adjetivos.", "<i>Ser mais disciplinado</i> descreve um estado, que não se marca; <i>treinar às sete</i> marca-se."),
 ("O alvo vago.", "<i>Melhorar no trabalho</i> não se verifica. Se daqui a um ano você não puder dizer sim ou não, o alvo não existe."),
 ("Fazer com a distração ao alcance.", "Uma única interrupção no meio da escavação basta para trocar a verdade pelo alívio. Se ela aconteceu, releia com mais desconfiança a resposta que você escrevia nesse momento."),
 ("A visão emprestada.", "Querer a vida que outro exibe. Pergunte, a cada linha da visão: quero isto, ou quero ser visto com isto?"),
 ("A semana zero.", "Transformar o dia zero em semanas de reflexão, guardando a folha para quando estiver perfeita. É um dia. No dia seguinte, começa-se."),
]
for i,(a_,b_) in enumerate(erros,1):
    add(f"{rom(i)}. &nbsp;<b>{a_}</b> {b_}", LAW)
add("Conferido o último erro, não acrescente mais nada à folha: o que faltar fica para os dias seguintes.", PI)

passo("IV", "O fecho", "Na mesma noite, depois da síntese.")
add("Esta noite a da vez já é a ordem, com as duas linhas de pensamento que a acompanham, a I e a VI. Amanhã, ao acordar, a folha vai parecer imperfeita. Aperfeiçoar a folha é um modo de adiar o começo.", PI)
proc("A folha depois do dia zero", [
 "Não reescreva a folha no meio do caminho.",
 "Emende-a só numa passagem, por escrito, com base no que você fez.",
 "· Passagem: a de um gesto que chegou, ou a passagem por decisão do Livro V.",
])

sec("Do que um dia pode")
add("O título do ensaio de Koe promete consertar a vida num dia. Um dia basta para ver; a nova identidade nasce depois, das provas. Cada traço na folha de marcas é uma prova a favor do que você escreveu.", PI)
proc("Esta noite", [
 "Abra <i>Do primeiro dia</i> e faça o quadro <i>Esta noite</i>.",
])
# O título, o parágrafo e o quadro vão juntos, para o quadro não ficar sozinho numa página.
st[-3:] = [KeepTogether(st[-3:])]
# ===================== DO PRIMEIRO DIA =====================
st.append(PageBreak()); sp(30)
add("Na noite do dia zero", LIV)
add("Do primeiro dia", LT); sumario(st[-1], 0, "Do primeiro dia")
SEC_NO_SUMARIO = True
proc("Esta noite", [
 "Leia este capítulo até o fim de <i>Durante o dia</i>.",
 "Copie à mão a folha de marcas do fim do livro na quinta página do caderno, ou imprima e cole.",
 "Escreva a primeira linha: a data de hoje e o número um.",
 "Leia as sete regras de <i>Da medida</i>.",
 "No Livro II, leia <i>Do dia</i>, de <i>De manhã</i> até o fim de <i>À noite</i>.",
 "No breviário do livro, decore o estribilho, com os colchetes calados.",
 "Decore também as linhas I e VI, a frase e a pergunta.",
 "Ao levantar, devolva a mesa à lista.",
 "Faça a primeira marca, sobre a síntese.",
 "Deixe vazia a coluna estreita.",
 "Escreva a primeira tarefa de amanhã.",
 "Deixe o caderno aberto na folha de marcas e durma sem nada que distraia no quarto.",
 "· Se a marca for cruz, amanhã é dia sagrado (§5).",
 "· O caso da mulher, adiante, se lê na noite da primeira cruz.",
])
sec("Do primeiro dia")
add("A folha está escrita na primeira página do caderno, com os oito pontos, cada um aprovado no seu teste, e a mesa está arrumada desde a tarde. O gesto da ordem já é a da vez. Este capítulo conta esta noite, amanhã e as semanas seguintes, até a noite em que o primeiro gesto deixar de precisar do caderno e o segundo entrar. O que houver para decidir, você decide esta noite.", PI)
add("O livro não sabe se a ocasião virá, se nela você fará o gesto ou cederá, se na semana que vem você terá febre. Onde não sabe, conta os dois caminhos. E conta o caso de uma mulher que fez este caminho antes de você. Ela é composta de casos comuns e não tem nome, porque o que importa dela são os casos.", PI)
add("Ela trabalhava num escritório durante o dia e, à noite, estudava para um exame do qual dependia uma mudança de carreira. No dia zero, escreveu como domínio uma área do direito e, como obra em curso, os três primeiros capítulos do programa, lidos e resumidos. Tinha duas mesas: a do escritório e a da sala de casa, onde estudava depois do jantar.", PI)
add("A <b>folha de marcas</b> é uma tabela com uma linha por dia e cinco colunas. A primeira é a data. A segunda é o número do exercício cuja microação está em treino; hoje, e durante algum tempo, é o um. A terceira é a marca da noite. A quarta é uma coluna estreita para uma palavra, <i>chegou</i>, de que você ainda não precisa. A quinta é a das quedas nas microações que já ficaram, e fica vazia até a primeira passagem.", PI)
add("Três palavras você vai usar todos os dias. A <b>microação</b> é a forma mínima de um exercício: um gesto central, curto, que se vê de fora e se faz na sua ocasião. Ela vem em negrito no alto de cada exercício do Livro III, e só ela se marca. A <b>ocasião</b> é o momento do dia que chama a microação; vem uma vez ou várias no dia, e uma pesa mais do que as outras. <b>A da vez</b> é a microação em treino, e há só uma. A sua primeira é a da ordem, e a ocasião dela é o sentar e o levantar da mesa.", PI)
add("Os <b>minutos da manhã</b> são uns dez. O que se abre primeiro fica com a manhã. Amanhã será a primeira manhã em que o estribilho pede algo que se pode verificar: esta primeira hora decidida por você, a ocasião de hoje feita inteira, a primeira tarefa posta no começo do dia. A anti-visão fica fechada, porque o peso dela se gasta com o uso.", PI)
add("No primeiro dia, a mulher escreveu: <i>A obra de hoje é o primeiro capítulo, lido e resumido.</i> No breviário, a linha da ordem diz, no quando, <i>Sento ou levanto da mesa</i>, e no gesto, <i>A distração sai. Mesa em ordem.</i> Ela contou seis ocasiões na primeira manhã: às nove, ao se sentar no escritório; no almoço, ao se levantar; ao voltar do almoço; às seis, ao sair; às oito e meia, à mesa da sala; perto das dez, ao fechar o livro. Este livro aposta que a que pesa mais é a sessão da obra de hoje; para a mulher, foi a sessão da sala.", PI)
add("A hora de parar se escreve de manhã porque à noite, cansado ou embalado, ninguém a julga bem. No dia zero, à tarde, a arrumação grande da mulher deixou na lista da sala só a luz, o caderno e uma caneta. A lista do escritório ela escreveu na segunda-feira, num papel, e passou-a para o caderno à noite.", PI)
add("Depois o caderno se fecha e o dia corre como correm os dias; o método só intervém nas ocasiões.", PI)
proc("Ao sentar para a obra", [
 "Entre puxar a cadeira e abrir a obra, repare na segunda frase interior antes de obedecer.",
 "· Ela diz <i>deixa isso aí, não incomoda</i>, ou <i>é só ver uma coisa, e já tiro</i>.",
 "Não discuta com ela.",
 "Tire a distração da mesa.",
 "Use até cinco minutos para a ordem e o silêncio da primeira linha.",
 "Passados os cinco minutos, comece com a mesa como estiver.",
 "Diga a linha I ao começar.",
 "Se nada em você quer começar, diga a linha VI.",
 "Começada a obra, diga por dentro <i>Isto, até acabar.</i>",
 "Se a hora de parar chega antes de a coisa estar feita, termine o passo em que está.",
])
add("A frase que negocia vem também disfarçada de exercício: <i>primeiro arruma tudo, e bem</i>. A mão responde antes dela. <i>Isto</i> é a coisa que você tem à frente, e acaba quando ela estiver feita. Diga a frase desde amanhã, antes de entendê-la inteira; o resto quem ensina é <i>Da assentada</i>, que você lê quando a sessão se perder.", PI)
proc("Durante o dia", [
 "Se numa ocasião menor você se pega à mesa com tudo à vista, tire tudo nesse instante.",
 "Continue sem pensar na marca. Ela se decide à noite.",
 "Ao levantar da sessão, gaste dois minutos e devolva a mesa ao que diz a lista.",
 "Deixe a folha de captura ao lado da obra.",
 "Escreva nela, numa linha, tudo o que vier sem pertencer à obra.",
 "Volte à obra.",
 "Fora de casa, use como folha de captura qualquer papel dobrado.",
 "À noite, passe essas linhas para o caderno.",
])
add("O levantar custa mais do que o sentar, porque chega no fim, quando a única vontade é sair. Na <b>folha de captura</b> vão uma lembrança, uma pendência, a vontade de fazer outra coisa. A linha não obriga você a nada: tira a coisa da cabeça, e você volta.", PI)
add("Os <b>minutos da noite</b> são uns dez, longe de toda distração. A <b>marca</b> é uma por noite, sobre a ocasião que você anotou de manhã: <b>traço</b> se você fez o gesto inteiro, <b>cruz</b> se cedeu ou fez só metade, <b>ponto</b> se a ocasião não veio.", PI)
add("Na linha da queda, pergunte onde estava o buraco. Deixe de fora o que a queda parece dizer de você.", PI)
proc("Na noite do dia zero", [
 "Pare aqui e passe às sete regras de <i>Da medida</i>.",
 "· O resto deste capítulo se lê na noite da primeira cruz, depois da marca.",
])
add("Mais cedo ou mais tarde vem uma noite em que a marca não se decide sozinha. A da mulher veio na quarta-feira da primeira semana. Ela se sentou à mesa da sala às oito e meia, tirou o que a distraía e estudou bem. Às dez e quinze, cansada, foi se deitar com o livro aberto, a xícara e as folhas espalhadas. Na ocasião que mais pesava, cumpriu metade. Procurou um argumento: o sentar era o mais difícil, e esse ela tinha feito.", PI)
add("A regra respondeu antes da pergunta: metade é ceder, e, na dúvida, é cruz. Ela marcou a cruz e escreveu embaixo a linha da queda: <i>Onde: o levantar das dez, cansada. Diferente: arrumo às quinze para as dez, antes do cansaço.</i>", PI)
add("Se, na noite da sua primeira cruz, a página lembrar você das tentativas antigas, pense em Benjamin Franklin. Ele marcava num caderno as faltas contra as virtudes que treinava. Conta na <i>Autobiografia</i> que nunca chegou à perfeição que ambicionava e que, ainda assim, o esforço o tornou melhor e mais feliz do que teria sido sem ele. O caderno de Franklin estava cheio de faltas marcadas, e foi sobre elas que ele trabalhou.", PI)
add("Depois da cruz, o que mais pesa é a manhã seguinte. Nela fala uma voz: <i>já há uma cruz, que diferença faz outra?</i> Responde a ela o §5: esse dia é sagrado.", PI)
proc("Depois de uma cruz", [
 "Na manhã seguinte, releia a linha da queda.",
 "Preveja a ocasião em que você cedeu.",
 "Cumpra a da vez hoje, com o piso do exercício se preciso.",
 "Não declare dia de ócio.",
])
add("A mulher, na quinta-feira, não estava doente e não declarou piso. Releu a linha da queda, previu a ocasião das quinze para as dez e, à noite, arrumou a mesa antes do cansaço. Traço. A cruz de quarta ficou isolada, como a lei pede.", PI)
add("No sábado ela passou o dia na casa da irmã, em outra cidade, e não se sentou para trabalhar em mesa nenhuma. A ocasião não veio: ponto. O ponto não separa duas cruzes: cruz na sexta e no domingo seriam duas seguidas. Se ela tivesse aberto os livros no meio da conversa e da louça, a ocasião teria vindo. Se tivesse ficado em casa evitando a mesa, também. Um ponto não se procura.", PI)
add("Na segunda-feira seguinte, o oitavo dia, ela escreveu na folha de captura uma suspeita: <i>a alavanca de estudar das oito e meia às dez é longa demais para o cansaço</i>. Não mudou a alavanca. O §9 não deixa o método mudar no meio do caminho, para que cada marca seja medida como as outras.", PI)
proc("Se você suspeita da ocasião ou do gesto", [
 "Escreva a suspeita na folha de captura, com a data.",
 "Não mude nada.",
 "Espere que as marcas confirmem ou desmintam a suspeita.",
 "Decida na passagem seguinte, por escrito.",
])
add("Na terça, ela acordou com febre. Antes de qualquer outra coisa, ainda na cama, escreveu no caderno: <i>hoje, piso</i>. Ficou em casa. No fim da tarde, sentou-se dez minutos para pagar uma conta, tirou da mesa o que a distraía, pagou e se levantou. Traço. Declarado às quatro da tarde, depois de um dia inteiro sentada com tudo à vista, o piso já não serviria: quem o escolheria seria o cansaço do dia. Por isso o piso se declara de manhã.", PI)
add("Na sexta, já sem febre, ela estudou bem e às dez e vinte foi se deitar com a mesa cheia. Era o mesmo buraco da primeira quarta-feira, e o remédio que ela mesma tinha escrito estava esquecido. Cruz, e a linha da queda disse o mesmo que a outra. No sábado, dia sagrado, ela releu a linha da queda, previu a ocasião e cumpriu o gesto. Traço.", PI)
add("Em algum momento dessas semanas você vai perguntar se o gesto já chegou. <b>Chegou</b> é a palavra que se escreve na coluna estreita, ao lado do traço, na noite em que, na ocasião que mais pesou, a microação aconteceu sem que o caderno a lembrasse. Quem lembrou você foi a ocasião, a mesa vista ao sentar.", PI)
proc("Antes de escrever chegou", [
 "Reconstrua a sessão por dentro e procure a decisão de fazer o gesto.",
 "Se você se lembra de ter pensado <i>agora tiro isto</i>, marque traço e deixe a coluna vazia.",
 "Se encontra a mesa limpa e não encontra a decisão, confira quem lembrou você.",
 "Se o caderno ou o breviário lembrou você, não escreva <i>chegou</i>.",
 "Nunca escreva <i>chegou</i> no dia em que a microação entrou.",
 "Nunca escreva <i>chegou</i> numa noite de cruz.",
 "Na dúvida, não chegou.",
])
add("Na quinta-feira da terceira semana, ao fazer a marca, a mulher se lembrou de que, ao sentar, a distração já estava fora antes que ela pensasse nisso. Mas também se lembrava de ter olhado o breviário, aberto em cima do caderno, quando chegou em casa. Não sabia se a lembrança tinha vindo da ocasião ou do caderno. Na dúvida, não chegou. Traço, e a coluna ficou vazia. A da vez continuou, e a noite em que fosse verdade viria depois.", PI)
add("Essa noite veio na terça seguinte. Ao fazer a marca, ela procurou a decisão do sentar das oito e meia e não a encontrou. Encontrou o livro aberto numa mesa limpa, a distração no quarto, e não se lembrava de tê-la levado para lá. Foi a mesa, quando ela a viu, que pôs as mãos dela para trabalhar. Às quinze para as dez, arrumou a mesa enquanto pensava num caso do capítulo, e só ao fazer a marca percebeu que tinha arrumado. Ao lado do traço, na coluna estreita, escreveu <i>chegou</i>.", PI)
add("Essa noite e a manhã seguinte se chamam <b>passagem</b>. A noite de passagem pede cerca de uma hora a mais.", PI)
proc("A noite de passagem", [
 "· Ver: <i>Passos da passagem</i>, no Livro II.",
])
add("A mulher tinha uma emenda esperando. Voltou à suspeita do oitavo dia e olhou as marcas, e as marcas a confirmavam: as duas cruzes tinham nascido no mesmo quarto de hora, o levantar das dez, cansada. Ela riscou a alavanca e escreveu a nova, com a data: <i>estudar até as quinze para as dez</i>.", PI)
add("Na manhã da passagem, a microação da ordem passa às que ficaram, e entra a segunda, a do terminar. A linha desse dia leva o número dois, e no breviário você lê outra linha. A ordem não sai da sua vida. <b>As que ficaram</b> são as microações já passadas: deixam de ser lidas de manhã e continuam a ser feitas. Só a atenção inteira passa à da vez.", PI)
proc("As que ficaram", [
 "Faça as que ficaram todos os dias, nas suas ocasiões.",
 "Não as marque.",
 "Se ceder numa delas, escreva o número dela na última coluna da folha de marcas.",
 "Nessa noite, escreva a linha da queda sobre ela.",
 "Se a mesma cai duas noites seguidas, ela volta a ser a da vez na manhã seguinte.",
])
add("No caso da mulher, doze dias depois, veio uma semana de prazos no escritório. Na terça ela saiu do trabalho com a mesa cheia e só percebeu no caminho para casa. À noite fez a marca do terminar e, na última coluna, escreveu o número da ordem, um. Uma queda sozinha não mudava nada. Na quarta, cansada, ela se sentou à mesa da sala com tudo à vista e só reparou no meio do capítulo. Outro um na coluna, na noite seguinte à primeira.", PI)
add("Eram duas noites seguidas de queda na mesma das que ficaram. Na manhã de quinta, a ordem voltou a ser a da vez, e a folha levou outra vez o número um. O terminar esperou, sem perder nada. A ordem chegou de novo quatro noites depois, mais depressa do que da primeira vez, porque já tinha sido aprendida. Essa noite foi uma passagem como as outras: na manhã seguinte, a ordem voltou às que ficaram e o terminar retomou o lugar.", PI)
add("Ao fim dessas semanas ela sabia, pelos próprios dias, o que nenhuma explicação lhe tinha ensinado de antemão. Você vai saber isso pelos seus.", PI)

sec("Da medida")
add("As regras da marca e da passagem ficam juntas nesta seção. Volte a ela antes de marcar, na noite que trouxer dúvida. Na noite do dia zero, leia só as sete regras e o parágrafo do H e do J, logo abaixo delas.", PI)
add("Os gregos tinham uma palavra para isso, e ela vinha do ginásio. <i>Askesis</i> era o treino de quem prepara o corpo para os jogos: o atleta que repete o mesmo movimento até que o movimento lhe pertença. Os filósofos tomaram a palavra emprestada para dizer que a alma também se treina, por repetição, com carga crescente, dia após dia.", PI)
add("Em Roma, no tempo de Nero, Musônio Rufo, que viria a ser o mestre de Epicteto, comparava o filósofo ao médico e ao músico: nenhum se torna o que é decorando preceitos, e sim praticando até que a mão os saiba. Epicteto, o discípulo, resume o treino numa frase: treine contra aquilo a que você se inclina, e não em proezas feitas para ser vistas. Andar na corda bamba também pede treino, lembra ele, e não serve para nada. Por isso cada microação se treina na ocasião em que você cede, e a marca pergunta pela que mais pesou.", PI)
add("A medida deste livro cabe em sete regras, cada uma com um nome curto, que é como o resto do livro a chama. Três leis do Livro II valem desde a primeira noite. Uma só microação nova de cada vez (§1). Nunca dois dias seguidos de queda (§5): queda é cruz na da vez ou ceder numa das que ficaram, o ponto não separa duas quedas, e o dia seguinte a uma cruz é sagrado. A régua não se muda no meio do caminho, só numa passagem e por escrito (§9).", PI)
medida = [
 "<i>Da marca.</i> Uma marca por noite, sobre o dia de hoje, e só sobre a da vez. Traço se, na ocasião que mais pesou, você fez o gesto; cruz se nela você cedeu; ponto se a ocasião da da vez não veio hoje, o que não é falha nem mérito. Na dúvida entre traço e cruz, é cruz.",
 "<i>Do chegou.</i> <i>Chegou</i> se escreve ao lado do traço na noite em que, na ocasião que mais pesou, a microação aconteceu sem que o caderno a lembrasse: quem lembrou você foi a ocasião, e não o breviário. Nunca no dia em que a microação entrou, nunca numa noite de cruz. Na dúvida, não chegou.",
 "<i>Da passagem.</i> A noite de um <i>chegou</i> e a manhã seguinte são a passagem. Na noite, a Lição do exercício que chegou é lida, a folha do dia zero e <i>Do homem</i> são relidos, e as emendas que as marcas pedirem são feitas por escrito. Na manhã, a da vez passa a ficar, e a seguinte, na ordem, entra.",
 "<i>Das que ficaram.</i> As que ficaram continuam todos os dias, nas suas ocasiões, sem marca própria. Se você ceder numa delas, escreva-a na linha da queda. Se a mesma cair duas noites seguidas, ela volta a ser a da vez na manhã seguinte; a que estava em treino espera, sem perder nada. A noite em que a que voltou chega de novo é uma passagem como as outras: na manhã seguinte, ela volta a ficar e a que esperava retoma. Nunca mais de uma da vez.",
 "<i>Da passagem por decisão.</i> Se a da vez não chega e a resistência não cede, há uma segunda forma de passagem, a passagem por decisão. Ela é declarada por escrito, sem <i>chegou</i>, numa noite sem cruz e só depois das quatro provas do Livro V. Não serve para pular exercício: a da vez só passa a ficar com <i>chegou</i>. O que se decide nela, e como, ensina <i>Da resistência que fala</i>, no Livro V.",
 "<i>Do ciclo.</i> Treze microações fazem um ciclo, o tempo que ele levar. No fim, a prova do ciclo; depois, um novo dia zero, num caderno novo, e de novo a primeira.",
 "<i>Do teto.</i> A marca e o exame que a decide cabem em cinco minutos, e os minutos da noite em uns dez. Fora da marca da da vez e das quedas das que ficaram, nada do dia se pontua; a linha do bloco, quando houver um bloco de obra, registra e não soma. Se o teto estourar sete noites seguidas, ou se abrir o caderno já trouxer angústia, o método passou a vigiar você: leia <i>Do escrúpulo</i>, no Livro V.",
]
for m in medida:
    add(m, LAW)
sp(4)
add("Alguns exercícios se tornam hábito, e estão marcados com <b>H</b>: com a repetição, acontecem quase sem decisão. Outros sempre pedirão juízo, e estão marcados com <b>J</b>: ficam mais rápidos e mais leves, mas nunca automáticos.", PI)
add("<i>Chegou</i> quer dizer que o gesto começou a nascer; a consolidação vem depois, devagar, entre as que ficaram. O sinal de consolidação, no fim de cada exercício, descreve o gesto já maduro, para que você o reconheça quando ele vier. Esse sinal não decide a passagem. Nos exercícios J, <i>chegou</i> significa que o gesto já não precisou do breviário para aparecer, e o juízo continua a ser pensado.", PI)
add("O livro não marca prazo para nenhum gesto, e de propósito. Em Londres, em 2010, a psicóloga Phillippa Lally e colegas acompanharam por doze semanas quase cem voluntários que tentavam instalar um gesto simples num momento fixo do dia, como comer uma fruta no almoço. Há indícios de que o tempo até o gesto sair quase sem pensar varia muito, de menos de três semanas a mais de meio ano. E faltar uma vez, isoladamente, quase não alterou o percurso.", PI)
add("Daí vêm duas coisas. Nenhum número de dias fixado de antemão serve para todos os gestos, e por isso o livro espera o sinal do próprio gesto. A falha avulsa não desfaz o caminho, e por isso o §5 é brando com a primeira cruz e severo só com a segunda. O que os voluntários anotavam, quanto o gesto já saía sem pensar, é a pergunta que o <i>chegou</i> faz a você.", PI)
add("Passar à microação seguinte no primeiro <i>chegou</i> parece cedo, se o hábito leva meses. Mas o que pesa no começo é lembrar, e o que se lembra com esforço só se lembra um de cada vez. Na noite em que o gesto chega, ele já não precisa do esforço inteiro da memória; precisa só não ser abandonado. As que ficaram dão isso a ele a baixo custo, e a coluna das quedas o vigia, como vigiou a ordem da mulher.", PI)
add("Se você escrever <i>chegou</i> cedo demais, numa noite de otimismo, o próprio gesto mostra o erro. Entre as que ficaram, um gesto que não tinha chegado cai depressa, e duas noites seguidas de queda o devolvem à da vez, sem castigo e sem perda. A verificação está nas folhas, e não na memória. O gesto que chegou de verdade, adiado pelo escrúpulo, volta a dar sinal em outra noite, como deu à mulher. Os critérios que separam o <i>chegou</i> do engano estão no Livro V, em <i>Do chegou e do engano</i>.", PI)
add("Sem contagem, o avanço se lê na folha de marcas. A coluna do número da da vez sobe devagar, e cada subida é uma passagem; essa sequência não se falsifica com facilidade, porque cada passagem pede um <i>chegou</i> escrito sem dúvida. As cruzes rareiam, e as que vêm ficam sozinhas. A linha do dia, relida numa noite de passagem, mostra a obra em curso crescendo. Um total de traços mediria só o cumprimento.", PI)
add("Se o gesto não chega nunca, a primeira resposta é paciência: as linhas da queda, relidas, mostram onde está o buraco. Há resistências que nenhuma paciência atravessa: a ocasião mal escolhida, o gesto que não cabe na sua vida, o domínio que já não é o seu. Para elas existe a passagem por decisão, que não se declara por cansaço. Quando essa noite é legítima, o Livro V ensina, com as quatro provas.", PI)
add("Estas regras não dizem o que você vai dizer por dentro no instante de se sentar, quando a vontade pedir outra coisa; quem diz é o primeiro livro.", PI)
proc("Agora", [
 "Feche o livro.",
 "Deixe o caderno aberto na folha de marcas.",
 "Vá dormir sem levar para o quarto nada que distraia você.",
])
fleur()
# O fecho vai junto do parágrafo anterior, para não ficar sozinho numa página.
st[-3:] = [KeepTogether(st[-3:])]
# ===================== DEPOIS DA PRIMEIRA CRUZ: DA OUTRA CHANCE =====================
SEC_NO_SUMARIO = False
st.append(PageBreak()); sp(30)
add("Depois da primeira cruz", LIV)
add("Da outra chance", LT); sumario(st[-1], 0, "Da outra chance")
add("<i>“Não se aborreça nem desanime se nem sempre conseguir agir segundo os seus princípios. Quando for derrubado, volte, e alegre-se se a maior parte do que você faz for digna de um homem.”</i>", ParagraphStyle('oc1', parent=PC, fontSize=12, spaceAfter=2))
add("Marco Aurélio, <i>Meditações</i>, V, 9", ParagraphStyle('oc2', parent=EPA, spaceAfter=20))
add("Você lê este capítulo na noite seguinte à primeira cruz, depois da marca, com o caderno ao lado, e sai dele com a lista das provas e a carta da outra chance escritas.", PI)

add("A frase do alto é de Marco Aurélio, numa das notas que ele escrevia para si mesmo. Ela diz que você vai falhar algumas vezes em agir segundo o que pensa, e que depois de cada queda se volta. Basta que a maior parte dos atos seja digna de um homem; para os estoicos, conforme à razão. A exigência de nunca cair acaba em desânimo, e o desânimo, em deixar de tentar. O que o imperador pede a si mesmo é a volta, e esta noite trata dela.", PI)
add("Se você tem este livro nas mãos, já tentou outras vezes. Já houve segundas-feiras em que tudo ia mudar, planos escritos com letra caprichada, livros comprados e deixados na estante, promessas feitas à noite e esquecidas de manhã. Cada tentativa, ao falhar, deixou um resíduo: uma frase cada vez mais firme, dita em voz cada vez mais baixa. <i>Eu não sou capaz. Comigo não funciona. Já tentei.</i>", PI)
add("Se uma dessas frases lhe veio agora, deixe que ela fique. O livro volta a ela aqui, com a primeira cruz na folha: nenhum método serve a quem já decidiu, em silêncio, que não vale a pena tentar de verdade. Daqui a pouco você vai escrever duas folhas no caderno, uma lista e uma carta. Antes delas, as razões.", PI)

sec("Da assimetria")
add("Ao amigo que falhou, você dá outra chance. Ao irmão que errou de novo, outra. Ao colega que prometeu e não cumpriu, à pessoa que você ama e que o decepcionou, você dá uma, duas, dez chances, e acha isso justo, porque sabe que ninguém é a soma dos seus piores dias. A si mesmo, não. Com você, cada queda é uma prova a mais num processo já encerrado.", PI)
add("O mecanismo é este. Depois da queda, a cabeça escreve uma sentença sobre o caráter, e a escreve depressa, porque ela já está pronta, gasta de tanto uso. <i>Sou um fracasso</i> leva um décimo de segundo; <i>havia um buraco ali, e eu não vi</i> exige parar e olhar. Com o tempo, a sentença chega antes de qualquer exame da queda.", PI)

sec("Do que custa não acreditar")
add("Quem deixou de acreditar em si continua tentando, mas pela metade. Começa o treino e não o faz de verdade. Abre o livro e não o termina. Se tentar com tudo e falhar, a sentença se confirma; se tentar pela metade, sempre resta a desculpa de que não deu tudo. A meia-força protege da dor de mais uma falha e torna essa falha mais provável. Os psicólogos chamam isso de autoincapacitação (<i>self-handicapping</i>).", PI)
proc("A reserva", [
 "Pense numa tentativa sua que ficou malfeita.",
 "Procure nela a reserva: a parte do esforço que você guardou porque já esperava falhar.",
])

sec("Por que mais uma vez")
add("Dar a si mesmo outra chance decorre de olhar as falhas com exatidão. As tentativas anteriores falharam em condições precisas: sem engrenagem, sem ordem, contra todas as distrações ao mesmo tempo, apoiadas só na vontade, que é a primeira coisa a faltar. Concluir delas que você é incapaz é concluir que um homem não sabe nadar porque se afogou no mar sem nunca ter aprendido a bater os braços. Essas falhas mostram que faltou método. Sobre a sua capacidade, ainda não dizem nada.", PI)
add("A dureza consigo mesmo se faz passar por exigência, e o efeito dela é a fuga. Quem se trata como réu tem medo de olhar para os próprios erros, porque cada erro é uma nova condenação, e quem não olha os erros não os corrige. Um estudo de Breines e Chen (2012) encontrou o contrário do que a intuição promete: quem se trata com compreensão depois de falhar se esforça mais para melhorar.", PI)
add("A conta das tentativas também tem uma história. Pedro quis saber quantas vezes devia perdoar o irmão que o ofendesse, e ofereceu um número que lhe parecia generoso: até sete? A resposta, no Evangelho de Mateus, foi: até setenta vezes sete, isto é, sem conta. Aplicado à chance que você dá a si mesmo, o número de tentativas não decide nada. Decide se a chance seguinte se parece com a anterior. Dez tentativas feitas nas mesmas condições valem, como prova, por uma só.", PI)
add("Uma tentativa nova muda ao menos uma condição: a medida, a ordem, o terreno, o que se faz quando faltam condições. Por isso a lista das provas, daqui a pouco, termina numa linha sobre o que falhou na maneira de tentar. Se este livro mudar essas condições, a décima chance é a primeira que você se dá em condições diferentes. As nove anteriores passam a servir de registro dos pontos em que a maneira de tentar falhou.", PI)

sec("Da firmeza e do perdão")
add("Dar-se outra chance parece complacência. Sêneca, que examinava a própria consciência todas as noites, terminava o exame assim: <i>cuide de não fazer mais isso; desta vez, eu o perdoo</i>. Na mesma frase, a exigência e o perdão. Ele não fingia que não tinha errado, e não fazia do erro uma sentença perpétua.", PI)
add("Ele conta o costume no terceiro livro de <i>Da ira</i>, e diz que o aprendeu com Séxtio, filósofo romano da geração anterior. Séxtio se perguntava a cada noite que mal tinha curado naquele dia, a que vício tinha resistido, em que estava melhor. Sêneca fazia o mesmo depois que a lâmpada era retirada e a mulher dele se calava: percorria o dia inteiro, ato por ato e palavra por palavra, sem esconder nada de si. E escreve que sono se segue a esse exame: tranquilo, profundo e livre. As faltas de que se acusa são miúdas, como ter repreendido alguém com tanta aspereza que o ofendeu em vez de corrigi-lo. Nenhuma das perguntas de Séxtio pergunta quanto se merece sofrer.", PI)
add("Existe um perdão que encolhe o erro até ele caber numa desculpa, ou baixa a régua até a queda deixar de contar como queda. Esse perdão não serve. O de Sêneca tem três partes: o erro nomeado com exatidão, a correção decidida (<i>cuide de não fazer mais isso</i>) e só então o passado liberado. A indulgência pula as duas primeiras. Assim entendido, o perdão obriga a uma correção, coisa que a condenação perpétua dispensa.", PI)
add("A epígrafe desta página junta as mesmas duas coisas: Marco Aurélio conta com a queda e exige de si mesmo a volta.", PI)
add("Na noite em que Jesus foi preso, Pedro, que jurara segui-lo até a prisão e até a morte, o seguiu de longe até o pátio da casa do sumo sacerdote e ficou se aquecendo com os criados junto de um braseiro. Três vezes lhe perguntaram se ele era um dos discípulos; três vezes ele negou. Então o galo cantou, e Lucas acrescenta um detalhe terrível: o Senhor se voltou e olhou para Pedro. Pedro saiu e chorou amargamente.", PI)
add("O Evangelho de João conta o que veio depois. Pedro voltou ao único ofício que conhecia antes de tudo aquilo: foi pescar no mar de Tiberíades, passou a noite no barco e não pegou nada. De madrugada, um homem na praia mandou lançar a rede do lado direito, e a rede se encheu. Em terra havia brasas acesas, com peixe e pão, e João usa para esse fogo a mesma palavra que usou para o braseiro do pátio. Depois que comeram, Jesus lhe perguntou três vezes, uma para cada negação: <i>Simão, filho de João, você me ama?</i> Na terceira, Pedro ficou triste e respondeu: <i>Senhor, tu sabes tudo; tu sabes que eu te amo.</i> E recebeu um ofício: <i>Cuide das minhas ovelhas.</i>", PI)
add("Ninguém, nessa praia, finge que a noite do pátio não existiu: as três perguntas lembram as três negações, uma a uma, e doem por isso. Ninguém pede a Pedro que se castigue, nem que prove o próprio valor antes de voltar. A queda é lembrada com exatidão, e na mesma conversa ele recebe trabalho. Essa é a forma da outra chance que você vai dar a si mesmo esta noite: a queda chamada pelo nome, e logo em seguida o que fazer amanhã. É também assim que você deixa o eu antigo: perdoa-o esta noite e segue sem lhe pedir desculpas.", PI)
add("O resto do livro está construído sobre isso. Entre as leis do Livro II, a quarta diz que nada volta ao começo e que o próximo momento é sempre seu; a quinta perdoa a primeira queda e só é severa com a segunda. No corte de um hábito, a frase é <i>caí; a linha continua</i>. Tudo o que vem depois supõe uma coisa que só você pode conceder: a permissão para tentar mais uma vez, sem guardar parte do esforço.", PI)

sec("Do exercício")
add("Agora, o caderno. Faça duas coisas, na ordem: a lista e a carta.", PI)
proc("A lista das provas", [
 "Abra o caderno na primeira página livre depois das páginas reservadas.",
 "Escreva tudo o que você já terminou na vida, por menor que seja.",
 "· O curso que concluiu, o trabalho que entregou, a pessoa que não abandonou, a dificuldade que atravessou, o que aprendeu sozinho.",
 "Continue até encher a página.",
 "Se vier a frase <i>isto é pouco; isto qualquer um fazia</i>, escreva a linha mesmo assim.",
 "Se vier <i>eu nunca termino nada</i>, olhe a página: essa frase é herdada, e ali estão os seus registros.",
 "Se a página não se encher esta noite, pare e deixe a carta para depois.",
 "Na noite seguinte, antes de qualquer outra coisa, continue a lista de onde parou.",
 "Com a página cheia, escreva na última linha o que falhou da última vez na maneira de tentar.",
 "Nessa linha, não escreva uma palavra sobre o seu caráter.",
 "· Exemplo: <i>comecei tudo ao mesmo tempo; dependia do entusiasmo; não havia o que fazer quando o dia corria mal</i>.",
 "Ao longo da leitura, confira se este livro muda essas condições.",
 "Se não mudar nenhuma, desconfie dele também.",
])
add("As primeiras linhas vêm depressa. Depois elas param, e nesse intervalo volta a frase de pouco antes, com outras palavras. A lista recolhe tudo o que você terminou, grande ou pequeno, e a página põe a frase herdada diante dos seus registros.", PI)
proc("A carta da outra chance", [
 "Abra o caderno na última página.",
 "Escreva uma carta a si mesmo, como a escreveria a um amigo que você respeita.",
 "· Esse amigo já tentou muitas vezes, falhou muitas vezes e quer tentar de novo. Você não diria a ele que é um fracasso, nem teria pena dele.",
 "Diga a ele, com exatidão, o que viu nele.",
 "Diga o que cada queda lhe ensinou.",
 "Diga por que vale a pena tentar mais uma vez.",
 "Se uma frase sair no tom em que você fala consigo mesmo, risque-a.",
 "Escreva-a de novo como a diria ao amigo: sem pena, sem sentença, com os fatos.",
 "Assine a carta.",
 "Escreva a data.",
 "Deixe a carta ali, no fundo do caderno.",
 "No dia em que quiser desistir, leia a carta.",
])
add("Sem pena e sem sentença, com os fatos: esse é o registro que o livro lhe pede todas as noites. A frieza que ele vai lhe pedir mais adiante é a do instante, diante da desculpa, e também ela dispensa a pena. O livro não sabe o que você escreveu numa folha nem na outra. Sabe que elas existem e onde estão, e voltará a elas.", PI)

sec("De acreditar o bastante")
add("Para começar, basta acreditar o suficiente para tentar por inteiro mais uma vez, sem guardar uma desculpa de reserva. A certeza de que você é capaz, ou de que desta vez vai dar certo, você não tem ao começar, e ela não lhe faz falta.", PI)
add("Uma crença mais firme, se vier, vem depois e se apoia nos atos. Cada traço na folha de marcas é o registro de uma coisa que você fez, e os registros se somam.", PI)
add("Quando você fechar o caderno esta noite, terá decidido tentar por inteiro mais uma vez. O capítulo seguinte dá sentido à frase que você já diz toda manhã.", PI)
add("“Cuide de não fazer mais isso; desta vez, eu o perdoo.”<br/>Sêneca, <i>Da ira</i>, III", BOX)

proc("Antes de seguir", [
 "Confira que a lista das provas enche uma página.",
 "Confira que a última linha dela diz o que falhou na maneira de tentar.",
 "Confira que a carta está assinada, datada e no fundo do caderno.",
])
# ===================== DO ESTRIBILHO =====================
st.append(PageBreak()); sp(30)
add("Depois da outra chance", LIV)
add("Do estribilho", LT); sumario(st[-1], 0, "Do estribilho")
st.append(KeepTogether([Paragraph(f"<i>“{ESTR}”</i>", ParagraphStyle('es1', parent=PC, fontSize=13.5, leading=20, spaceAfter=2)),
                        Paragraph(ESTR_A, ParagraphStyle('es1a', parent=EPA, spaceAfter=22))]))
add("Você lê este capítulo depois de <i>Da outra chance</i>, ou na manhã em que a frase soar alheia. A frase você já sabe de cor desde o dia zero.", PI)
add("Você escreveu a lista e a carta, e decidiu tentar por inteiro mais uma vez. Uma decisão tomada à noite enfraquece nos dias comuns que vêm depois. O estribilho serve para esses dias.", PI)
add("Estribilho é o verso que volta numa canção ou num poema, sempre igual, depois de cada estrofe. As estrofes mudam; o estribilho se repete, e quem canta acaba por sabê-lo sem ter decorado de propósito. Aqui, o estribilho é a frase de Sêneca do alto desta página. Ela abre o livro, aparece antes de cada parte e volta no fim. Você a diz todas as manhãs do ciclo, para lembrar, em dias que serão todos diferentes, a decisão desta noite.", PI)
add("A frase vem do começo da primeira carta de Sêneca ao amigo Lucílio, escrita nos últimos anos de vida dele. A carta trata de uma só coisa, o tempo, e do modo como ele se perde. É a primeira instrução que Sêneca dá a quem quer mudar de vida: antes de qualquer outro ensinamento, retomar as horas. A tradução é livre. Os colchetes marcam o que se pulou: o resto do primeiro parágrafo da carta.", PI)
est_intro = "Desde a manhã do dia um, cada parte da frase lhe pede uma coisa precisa:"
est3 = [
 ("Reivindique-se para si.", "Decida você a primeira hora do dia, antes que outra pessoa ou o que distrai decida por você. À noite, se houve queda, a linha da queda faz a divisão de Sêneca, numa palavra: a hora foi tirada, levada às escondidas ou deixada cair. Sêneca faz essa divisão logo depois da primeira frase da carta e chama a terceira, a do descuido, de a perda mais vergonhosa. Nas duas primeiras entram os outros; na terceira, só você. É dela que a sua linha da queda vai falar mais vezes."),
 ("Abrace todas as horas.", "Ninguém vigia todas as horas ao mesmo tempo, e o método não pede isso. A medida delas é a da vez, a microação que você treina, feita por inteiro na sua ocasião, todos os dias, até chegar. Abraçar a hora é fazê-la sem guardar ao lado uma saída. Se uma hora escapar, a ordem vale para a seguinte. A vontade de trocar por outra coisa vem antes da passagem, quando a novidade acabou e o gesto ainda não chegou. O estribilho é dito para esses dias."),
 ("Lançar mão do hoje.", "Esta parte corrige dois reflexos. O primeiro é adiar o começo: na manhã em que você disser a frase, o dia começa pela primeira tarefa, a que você evitaria. O segundo é juntar: se a da vez lhe parecer pouco e vier a vontade de acrescentar outra, ou outro método, a frase manda voltar ao que você tem nas mãos. O <i>Manual operacional</i> fica fora dessa proibição. Tudo o que o método pede cabe entre a manhã e a noite do mesmo dia, e nenhum balanço de fim de semana compensa a hora perdida hoje."),
]
st.append(KeepTogether([Paragraph(est_intro, PI), Paragraph(f"{rom(1)}. &nbsp;<b>{est3[0][0]}</b> {est3[0][1]}", LAW)]))
for i,(a_,b_) in enumerate(est3[1:],2):
    add(f"{rom(i)}. &nbsp;<b>{a_}</b> {b_}", LAW)


sec("Do uso")
add("A frase não se recita como um dever. O dia vacila num pensamento que chega antes de qualquer decisão, <i>hoje não</i> ou <i>desta vez também não vai dar</i>, e a frase entra antes da resposta. Ela está no alto do breviário, as duas páginas do fim do livro com tudo o que se pratica, e antes de cada livro.", PI)
proc("Quando dizer a frase", [
 "De manhã, diga a frase uma vez, em voz baixa.",
 "Se vier <i>hoje não</i> ou <i>desta vez também não vai dar</i>, diga a frase antes de responder.",
 "Se vier a vontade de largar o que está fazendo, diga a frase.",
 "Se a onda subir, diga a frase.",
 "· A onda é a vontade súbita daquilo que você decidiu deixar.",
 "Se a outra chance parecer a última, diga a frase.",
 "Se não estiver sozinho, diga-a por dentro.",
 "Depois, decida, com a decisão desta noite na lembrança.",
 "Se numa manhã a frase parecer alheia, não a troque por outra.",
 "Nessa manhã, releia a primeira carta de Sêneca a Lucílio, inteira.",
 "· Ver: <i>Comentário ao estribilho</i>.",
])
add("Haverá manhãs em que a frase lhe parecerá escrita por outro homem, em outro século, para outro leitor. A carta é curta, e as razões de cada parte estão nela. Numa manhã assim, faltava uma delas.", PI)
add("Agora você tem a lista, a carta e a frase.", PI)

proc("Antes de seguir", [
 "Diga a frase sem olhar, com os colchetes calados.",
 "Diga em uma linha o que cada parte da frase lhe pede.",
 "Se ainda não consegue, releia as três partes.",
])
# ===================== DA MÁSCARA =====================
estribilho_pagina()
st.append(PageBreak()); sp(30)
add("Quando a voz antiga ganhar", LIV)
QUANDO["Da máscara"] = "quando a voz antiga ganhar"
add("Da máscara", LT); sumario(st[-1], 0, "Da máscara")
LBP = ParagraphStyle('lbp', **{**base, 'textColor': GRAY}, fontSize=9.5, leading=12, spaceBefore=6, spaceAfter=2, keepWithNext=1)
add("<i>“I will never know myself until I do this on my own.<br/>[...]<br/>I will never be anything till I break away from me.<br/>I will break away, I’ll find myself today.”</i>", ParagraphStyle('ps1', parent=PC, fontSize=12, spaceAfter=2))
add("Linkin Park, <i>Somewhere I Belong</i> (2003)", ParagraphStyle('ps2', parent=EPA, spaceAfter=20))
SEC_NO_SUMARIO = True

sec("Da máscara")
add("Leia este capítulo na noite em que a voz antiga ganhar. A pergunta você já diz desde o dia um; aqui ela ganha as razões.", PI)
add("A teoria é curta. Seja X o que você quer. Em algum lugar existe, ou existiu, alguém que conseguiu X. Essa pessoa acordava a certas horas, recusava certas coisas, fazia outras sem discuti-las e aguentava o que custa a você. Você pergunta o que ela faria agora, no seu lugar, e faz isso. Dela você tira os meios, os atos e as recusas; o X é seu, escolhido no dia zero.", PI)
add("Você age como ela antes de ser como ela, porque é agindo que você vem a ser. Os latinos tinham uma palavra para isso. <i>Persona</i> era a máscara do ator em cena, e por ela passava a voz da personagem. A palavra deu depois <i>pessoa</i>: quem você é, literalmente, é a máscara por onde você fala. Este capítulo ensina você a escolher a máscara e a usá-la até o rosto tomar a forma dela.", PI)
add("Quem usa a máscara sente o medo, o tédio, a preguiça, e faz o gesto sem discutir com eles. Na hora da obra, não se demora com pena de si nem com desculpas ao eu antigo. Vê o que quer, vê o que custa, e paga. A frieza aponta para as suas desculpas e para a parte de você que prefere o conforto à obra. Ela serve enquanto o gesto custa.", PI)
add("Encarnar quem conseguiu X custa alguma coisa que hoje é querida para você: horas de sono mal gastas, conversas que não levam a nada, a imagem de si como alguém que tenta. Quem conseguiu X largou parte disso, e você também vai largar. Primeiro vem o que você faz. Depois, quem pensou isso antes, para que você saiba o que está fazendo.", PI)

sec("Da pergunta")
add("A máscara já está escrita no seu caderno: é a visão, o segundo ponto da folha do dia zero, a vida que você quer daqui a três anos, descrita em atos. Esses atos são de alguém. Esse alguém é <i>ele</i>, o rosto da máscara. Até hoje você leu a visão como um futuro. A partir de amanhã, leia-a como o retrato de quem está sentado à sua mesa.", PI)
add("Quem desenhou o retrato foi o eu antigo, num só dia, com os desejos que tinha. As marcas medem se você o cumpre e nada dizem sobre se você o escolheu bem. Dentro do ciclo, um erro dessa escolha só entra por uma porta, a resistência que fala. Mantenha essa porta aberta.", PI)
add("Se a visão lhe parece vaga para dar um rosto à máscara, dê a ela atos.", PI)
proc("Se a visão é vaga", [
 "Esta noite, escreva embaixo da visão, numa linha, três atos dele que você ainda não faz.",
 "Na mesma linha, escreva uma coisa que ele não faz e você faz.",
 "Escreva atos: <i>acorda às seis sem discutir</i>. Uma qualidade, como <i>é disciplinado</i>, não serve.",
 "Se você conhece alguém real que conseguiu o que você quer, leia como ele vivia.",
 "Tire de lá os atos que servem à sua visão.",
 "Passe cada ato pelo teste do dia zero: <i>quero isto, ou quero ser visto com isto?</i>",
 "· Você copia os meios dele. Os fins são seus.",
])
add("Com um homem real e estudado, a pergunta informa: diz o que ele fazia e você não sabia fazer. Com um <i>ele</i> tirado só da visão, ela responde sempre a mesma coisa: faz a coisa. Aí a pergunta é a lei com um rosto, e serve para pôr você para fazer. Se o que você quer nunca foi feito por ninguém, é só isso que ela pode ser.", PI)
add("O que ele faria agora?", VOICE)
sp(6)
proc("A pergunta", [
 "De manhã, ao escrever a obra de hoje, diga a pergunta por dentro.",
 "Diga a pergunta na entrada da obra.",
 "Diga a pergunta toda vez que a voz antiga falar fora da obra.",
 "· A voz antiga fala ao sentar, na onda, quando a cama pesar.",
 "Faça o que a resposta escolher, e diga <i>Isto</i>.",
 "Depois de dito <i>Isto</i>, cale a pergunta até o fim do passo. Diga a frase.",
 "Se, no fim do passo, há outro a escolher, diga a pergunta de novo.",
 "Se a vontade de parar vier antes da hora de parar, diga a linha II.",
 "Se a hora de parar chegou, termine o passo e feche a obra.",
 "· Ver: <i>Da assentada</i>.",
])
add("A hora de parar é dele: você a escreveu de manhã, de cabeça fria. Antes dela, a vontade de parar é do eu antigo. Depois dela, ficar é que seria fuga.", PI)
add("Perguntar no meio do passo quem você é seria olhar para si quando a obra pede que você se esqueça de si. A pergunta e a frase são a mesma coisa vista de dois lados: ele se senta, e ele não se levanta antes de acabar.", PI)
add("Você não precisa se sentir ele. Nos primeiros dias você se sente um impostor, fazendo de conta. Faça assim mesmo. O livro promete os atos e deixa o sentimento sem garantia. Sartre achava que ninguém coincide com o papel que faz; para ele, o fazer de conta não acaba. As marcas medem os atos.", PI)
add("À noite, a marca e a linha da queda mostram onde você foi ele e onde voltou a ser o antigo. A linha da queda não pergunta o que isso diz de você. Pergunta onde estava o buraco.", PI)
add("A pergunta também chega, como os gestos, sem coluna nem marca novas. Ela chegou no dia em que, na entrada, você fez o que ele faria sem dizê-la. Quem lembrou você foi a ocasião: a mesa vista ao sentar, a hora. A voz antiga não teve tempo de falar.", PI)
proc("Se a pergunta chegou", [
 "Confira só na noite de passagem, com as folhas de marcas à frente.",
 "Leia o <i>chegou</i> desta noite: na ocasião que mais pesou, o gesto veio sem o caderno e sem a pergunta.",
 "Leia as linhas da queda das semanas anteriores.",
 "Veja se a voz antiga ainda ganhava nas entradas ou se deixou de ganhar.",
 "Se há dúvida, a pergunta não chegou.",
 "Não escreva isso em lugar nenhum.",
 "Onde ela chegou, continue a dizê-la de manhã e sempre que a voz antiga falar.",
])
add("Onde a pergunta chegou, a frieza já não tem trabalho, porque o ato deixou de custar. A máscara chega assim, entrada a entrada, gesto a gesto.", PI)
add("Isso divide o tempo. A cabeça decide em poucos pontos: no dia zero, na entrada de cada obra e de cada passo, e à noite, diante da marca. Nos intervalos trabalha a mão, e a mão faz o que ficou decidido. A disposição se forma depois, nos intervalos que a mão preenche. Por isso um erro num desses pontos corre semanas sem dar sinal.", PI)
add("Se a ocasião foi mal escolhida, ou se a obra de hoje sai pequena demais para a obra em curso, a mão a cumpre bem. As marcas se enchem de traços, porque a marca só pergunta se você fez o gesto. Quem mostra esse erro é a linha do dia.", PI)
proc("Erro de decisão", [
 "Na noite de passagem, releia as linhas do dia ao lado da coluna de marcas.",
 "Se, noite após noite, a linha do dia diz pouco ou <i>nada</i> ao lado de traços: o erro é de decisão.",
 "Escreva a suspeita na folha de captura, com a data.",
 "· A suspeita espera pela passagem, como toda emenda.",
])

sec("De onde vem a voz antiga")
add("Saiba contra o que a pergunta trabalha. A voz que diz <i>hoje não</i>, <i>cinco minutos</i>, <i>amanhã faço</i> fala com a sua voz e traz razões; por isso parece juízo. Ela tem força por três motivos, e em nenhum deles entra a razão que ela possa ter.", PI)
add("O primeiro: ela foi aprendida, e quem a ensinou foi você. Cada vez que você adiou, o desconforto caiu na hora, e esse alívio funcionou como recompensa. Você recebeu essa recompensa centenas de vezes, na mesma mesa, na mesma hora. Está demonstrado que uma resposta repetida no mesmo contexto passa a ser disparada pelo contexto, sem o objetivo que a criou; Wood e Neal descreveram isso. A voz antiga é um hábito que aprendeu a falar.", PI)
add("O segundo: ela protege você de um custo imediato, e o ganho do outro lado vem tarde. A obra custa agora e paga em meses; o adiamento paga agora e cobra em meses. Está demonstrado que, para quem decide, um bem distante vale menos do que o mesmo bem ao alcance da mão. A voz antiga fala no instante em que a balança pende para ela.", PI)
add("O terceiro: ela fala primeiro. A pista dispara, e o impulso já está ali quando você começa a pensar. As razões vêm depois, feitas sob medida para defender o que o impulso escolheu. No debate, ela tem a vantagem do tempo. Por isso a pergunta se prepara de manhã, de cabeça fria, e se diz na entrada, no lugar exato em que a voz antiga falaria primeiro.", PI)
add("O que a repetição ensinou, a repetição desensina, no mesmo ritmo lento. Cada vez que a voz fala e você não obedece, a resposta antiga fica sem o alívio que a fixou. Ela continua a falar, mais baixo depois de muitas vezes. Um dia ela volta inteira. Para esse dia existem a cruz e a linha da queda.", PI)

sec("Das quatro máscaras")
add("Cícero escreveu no fim da vida, em 44 antes de Cristo, um tratado para o filho, <i>Dos deveres</i>, e nele retomou o estoico Panécio. Cada homem, diz ele, veste quatro <i>personae</i>. A primeira é comum a todos: a razão. A segunda é a natureza de cada um: o corpo, o temperamento, o talento. A terceira é a que as circunstâncias impõem: o nascimento, a riqueza, o acaso. A quarta é a que escolhemos pelo nosso juízo: o gênero de vida, o ofício, quem decidimos ser.", PI)
add("As três primeiras você recebe. A quarta você escolhe, e escolhe dentro da segunda. Nada convém, diz Cícero, contra a vontade de Minerva, isto é, contra o próprio feitio; e ninguém mantém a coerência de uma vida imitando a natureza de outro. Os atores escolhem as peças que mais lhes convêm, mesmo que não sejam as melhores. A máscara tem de servir ao rosto que você tem, ou cai.", PI)
add("Você já aplicou essa medida no dia zero, no teste da ambição verossímil. A folha que você escreveu foi a escolha da sua quarta máscara. Este capítulo trata de vesti-la.", PI)
proc("Se os meios não servem", [
 "Se os meios dele pedem o que o seu corpo ou o seu temperamento não aguentam, mantenha o X.",
 "Procure, para esses meios, quem chegou a X com uma natureza parecida com a sua.",
 "Copie os meios dessa pessoa.",
])
add("Uma fábula diz o resto. Em 1896, o inglês Max Beerbohm publicou o conto <i>O hipócrita feliz</i>. Lorde George Hell é um devasso com um rosto que mostra tudo o que ele fez. Apaixona-se por Jenny Mere, que só se casará com um homem de rosto de santo. Ele cola no rosto uma máscara de cera de santo, muda de nome e vive como viveria o homem da máscara. Mais tarde, uma antiga amante, La Gambogi, arranca a máscara em público, e por baixo está o rosto da máscara.", PI)
add("A fábula mostra que o ato vem antes do rosto: você põe a máscara, vive segundo ela, e o rosto vem depois. Ela não mostra que isso se faça a frio. O que muda Lorde George é o amor por Jenny, vivido com humildade. Em grego o ator se chamava <i>hypokritḗs</i>, de onde vem o hipócrita do título. O livro toma da fábula a ordem e põe nela outro motor.", PI)

sec("Do mostrador")
add("Kevin Dutton, psicólogo britânico, pesquisou a psicopatia em Oxford. Por anos entrevistou pessoas com os traços do psicopata: pacientes de hospitais de segurança máxima, mas também cirurgiões, soldados de forças especiais, advogados, operadores da bolsa. Em 2012 publicou <i>A sabedoria dos psicopatas</i>. A tese dele: os traços que tornam o psicopata perigoso produzem, em outra dose e com outro alvo, as pessoas que funcionam melhor sob pressão. São a impiedade, o encanto, o foco, a dureza mental, a ausência de medo, a atenção ao presente e a ação, que é a recusa de adiar.", PI)
add("A imagem dele é uma mesa de som, com um botão para cada traço. O psicopata dos tribunais tem todos os botões no máximo e travados, contra todo mundo. O que Dutton chama de psicopata funcional sobe os botões quando a situação pede e os abaixa depois. O cirurgião não sente nada pelo paciente enquanto corta, e em casa é um pai como os outros. Para Dutton, a frieza é ferramenta; quem a faz boa ou má é a mão que a usa e o lugar para onde ela aponta.", PI)
add("O nome é o mais duro que a máscara pode ter. A escala de Robert Hare, feita para prisões e hospitais, mede também a impulsividade, o tédio fácil, a falta de planos realistas de longo prazo, a irresponsabilidade e a recusa da culpa. É o retrato de quem não aguenta <i>Isto, até acabar</i> nem escreve uma linha da queda sem culpar outro. Nesses traços o método pede o contrário do psicopata. Por isso o livro toma de Dutton só a mesa de som.", PI)
proc("O botão", [
 "Na hora da obra, suba o botão ao máximo.",
 "Quando a voz antiga falar, suba o botão ao máximo.",
 "Diante do <i>amanhã faço</i> e dos cinco minutos a mais, não deixe a pena decidir.",
 "Fora disso, desça o botão.",
 "À noite, diante da marca, seja exato.",
 "· A frieza do instante não tem trabalho na marca.",
])

sec("Do papel")
add("Epicteto pensava a vida como um conjunto de papéis: o de filho, o de pai, o de cidadão, o do ofício. Cada papel traz o que cabe a ele fazer. Diante de qualquer escolha, Epicteto perguntava: isto está de acordo com o meu papel? No <i>Manual</i>, quem distribui os papéis é o autor da peça, e a você cabe representar bem o que lhe deram. Alguns papéis são escolhidos, como o do atleta ou o do filósofo. Esses se decidem primeiro e depois se cumprem, sem voltar a perguntar se há vontade.", PI)
add("A sua visão é dessa espécie, e quem aceitou o papel foi você. É o que diz a frase de Epicteto no alto do Prólogo, tirada dos <i>Discursos</i>: diga primeiro a si mesmo quem você quer ser, e depois faça o que tem de fazer.", PI)
add("Nos mesmos <i>Discursos</i>, Epicteto conta a história de Helvídio Prisco, senador romano. O imperador Vespasiano mandou lhe dizer que não fosse ao senado. Helvídio respondeu que estava no poder do imperador tirá-lo do senado, mas que, enquanto fosse senador, tinha de ir. Então vá, disse Vespasiano, mas fique calado.", PI)
add("Não me pergunte nada, e eu me calo. Mas eu tenho de perguntar e de dizer o que me parece justo. Se o disser, eu o mato. E Helvídio: quando foi que eu lhe disse que era imortal? A sua parte é matar; a minha é morrer sem tremer. Vespasiano mandou executá-lo.", PI)
add("Helvídio não calculou o que lhe convinha, nem o que sentia, nem se havia saída honrosa. Perguntou o que faz um senador, e fez isso, até o fim. É o que o livro chama de não negociar. Epicteto acrescenta que cada um conhece o preço e a máscara que lhe cabem, o seu <i>prosōpon</i>, a palavra grega da <i>persona</i> de Cícero. Ele não será Mílon, o lutador, e nem por isso descuida do corpo. Você também copia os meios do homem de X na sua medida.", PI)
add("No <i>Manual</i>, Epicteto mostra o preço. Se você quer vencer nos Jogos Olímpicos, diz ele, considere o que vem antes: comida medida, nenhum doce, treino na hora marcada, no calor e no frio. E o que vem depois: deslocar a mão, torcer o tornozelo, engolir poeira, levar chicotadas, e às vezes perder. Considere tudo isso e, se ainda quiser, vá. Do contrário, você será como as crianças, que brincam ora de lutador, ora de ator, e não são nada com a alma inteira.", PI)
add("Examine primeiro a coisa, e depois a sua natureza, para ver se pode carregá-la: olhe para os seus braços, para as suas coxas. O seu exame foi o dia zero. O preço se paga inteiro, e às vezes se perde mesmo assim. As vidas de quem conseguiu X não contam os que pagaram o mesmo e não chegaram. E a calma de quem já chegou é efeito de X; ela não se copia antes de chegar.", PI)

sec("Do se mágico")
add("Konstantin Stanislávski, ator e encenador russo, fundou com outros o Teatro de Arte de Moscou. Passou a vida procurando como um ator deixa de fingir e passa a viver a personagem em cena. Escreveu o que encontrou como diário de um aluno; o primeiro volume se chama, nas traduções, <i>A preparação do ator</i>. A chave que deu aos atores tem duas letras: <i>se</i>. O ator não diz a si mesmo <i>eu sou Otelo</i>, porque sabe que é mentira. Pergunta <i>se eu estivesse nestas circunstâncias, o que eu faria agora?</i>, e faz.", PI)
add("Stanislávski chamou isso de se mágico. Ele leva o ator às circunstâncias da peça sem obrigá-lo a crer que é outro, e põe o corpo dele em movimento. Num exercício, o mestre esconde um broche na cortina e manda uma aluna, Maria, procurá-lo. Ela corre pela sala com gestos de drama. Só quando procura de verdade a procura ganha vida. A personagem entra pelos atos.", PI)
add("O se de Stanislávski fica na primeira pessoa: o ator pergunta o que ele mesmo faria. A pergunta deste livro passa para a terceira. O autor acha que quem decide de fora do próprio estado decide melhor: Platão entregou a Espeusipo o castigo de um escravo porque o próprio Platão estava irado. Por isso, nesta manhã, neste estado, você pergunta o que faria quem já conseguiu o que você quer.", PI)
add("A terceira pessoa é antiga. Sêneca transmite a Lucílio um conselho de Epicuro: escolher um homem bom, tê-lo diante dos olhos e viver como se ele nos visse. Aristóteles define a virtude pela regra com que o homem prudente, o <i>phrónimos</i>, a determinaria. Este livro põe diante de você um homem que conseguiu X. O valor de X ficou para a escolha que você fez no dia zero.", PI)
add("O teatro também deu o patrono do <i>a frio</i>, rival de Stanislávski. Denis Diderot escreveu na década de 1770 o <i>Paradoxo do comediante</i>. O grande ator, diz ele, não sente o que representa: interpreta a sangue-frio um modelo que imaginou e estudou, e por isso é igual todas as noites. O ator que sente é grande num dia e fraco no seguinte. Mas o ator de Diderot nunca se torna a personagem; fica frio por baixo até o fim.", PI)
add("Este capítulo precisa dos dois, em ordem. A frieza é andaime: dura enquanto o gesto custa e sai quando ele deixa de custar. Nos primeiros dias você é o ator de Diderot, faz o gesto certo sem senti-lo, com o botão de Dutton no máximo. Quando o ato já não custa, ou até dá prazer, o rosto tomou a forma da máscara naquele gesto. Aristóteles chama de <i>héxis</i> esse modo de ser que os atos repetidos deixam. Se um gesto pedir frieza para sempre, o rosto ainda não se formou nele.", PI)

sec("Do corpo primeiro")
add("Aristóteles põe o ato antes do caráter: tornamo-nos justos praticando atos justos. Tudo o que este capítulo pede se apoia nisso.", PI)
add("Pascal foi mais longe, no fragmento da aposta: fazer como se cresse embrutece, <i>vous abêtira</i>. A palavra é dele e diz a coisa sem enfeite. O costume cala a parte de você que resiste ao que você já decidiu. Em Pascal ele humilhava o orgulho; aqui serve à ambição de X.", PI)
add("William James disse coisa parecida como psicólogo, em 1899, na conferência <i>O evangelho do relaxamento</i>. A ação parece seguir o sentimento, escreve ele, mas os dois andam juntos. Regulando a ação, que a vontade alcança, regulamos indiretamente o sentimento, que ela não alcança. Nos <i>Princípios de psicologia</i>, de 1890, está o <i>a frio</i>: quem quer vencer uma tendência tem de fazer, a sangue-frio, os movimentos exteriores da disposição contrária. James não promete quando o sentimento chega.", PI)
proc("A frio", [
 "Escolha uma disposição dele que você não tem: a calma, o gosto pela obra.",
 "Faça os movimentos exteriores dela, a sangue-frio, na ocasião deles.",
 "Não espere o sentimento para fazer o gesto.",
])

sec("Do estilo")
add("Nietzsche tem um nome para essa operação. Na <i>Gaia ciência</i>, aforismo 290, escreve que uma coisa é necessária: dar estilo ao próprio caráter. Pratica essa arte quem vê o que a própria natureza tem de forte e de fraco e o encaixa num plano. Aqui se acrescenta segunda natureza, ali se tira um pedaço da primeira, e o que não se pôde tirar é escondido ou reinterpretado. As naturezas fortes, diz ele, encontram a maior alegria no constrangimento de um único gosto.", PI)
add("O estilo se dá à matéria que você tem. Em <i>Schopenhauer como educador</i>, de onde vem a frase da capa, os verdadeiros educadores são libertadores. O educador é uma escada, e Nietzsche logo deixou a de Schopenhauer. No <i>Zaratustra</i> escreveu que se paga mal a um mestre quando se continua sempre aluno. O homem de X é um educador: usa-se e deixa-se.", PI)
add("No <i>Ecce Homo</i> Nietzsche faz à máscara a objeção mais funda. Tornar-se o que se é supõe não ter a menor ideia do que se é; a ideia que organiza cresce embaixo, e a superfície da consciência deve ficar limpa dos grandes imperativos. A pergunta deste capítulo é um grande imperativo posto na superfície. O livro responde com o Nietzsche da <i>Gaia ciência</i>, o do estilo feito por longa prática. A tensão permanece, porque é do próprio Nietzsche.", PI)
add("No começo do <i>Zaratustra</i> estão as três metamorfoses do espírito: o camelo, que se ajoelha e carrega; o leão, que diz não ao dragão chamado <i>Tu deves</i>; e a criança, que começa de novo. Nos termos dele, a máscara é coisa de camelo, e a pergunta é um <i>Tu deves</i> com rosto. O livro aceita o nome e lhe dá um fim. O leão vem em <i>Do retorno</i>, no novo dia zero, quando você recusa por escrito o que na máscara antiga era do eu antigo. A imitação é uma etapa.", PI)

add("D O &nbsp; P O R Q U Ê", LBP)
add("<b>A ideia.</b> Os autores deste capítulo concordam num ponto: o ato vem antes do rosto, e a máscara se escolhe dentro da natureza que se tem. Sêneca e Aristóteles punham diante dos olhos um homem bom. Este livro põe um homem que conseguiu.", PI)
add("<b>O mecanismo.</b> Primeiro, a pergunta muda a voz que decide. A voz que diz <i>hoje não</i> fala por você; a pergunta põe para falar outra, sem as suas desculpas. Quem decide continua a ser você, em nome dele, e não há ninguém atrás da máscara a quem passar a culpa. Sartre, em <i>O ser e o nada</i>, descreve o garçom que faz o papel com gestos precisos demais para fugir da própria liberdade, e chama isso de má-fé: é o modo errado de usar a máscara. Segundo, os atos repetidos formam o hábito e o caráter.", PI)
add("Nenhum estudo testou esta pergunta tal como o livro a usa. Há indícios em dois. Em 2014, Ethan Kross e colegas pediram a adultos que, antes de falar em público, pensassem em si pelo próprio nome, e a angústia diminuiu. Em 2017, Rachel White e colegas viram que crianças que faziam o papel de uma personagem, o Batman entre outras, persistiam mais numa tarefa entediante. A pergunta é a parte menos testada do livro. O que a sustenta é o primado do ato: Lally mediu que um gesto repetido na mesma ocasião se torna quase automático.", PI)
add("<b>Por isso.</b> <i>Pergunto o que ele faria porque a voz dele não tem minhas desculpas, e quem decide sou eu.</i>", PI)
fleur()
# O ornamento vai junto do parágrafo anterior, para não ficar sozinho numa página.
st[-2:] = [KeepTogether(st[-2:])]
SEC_NO_SUMARIO = False

# ===================== DA ASSENTADA =====================
estribilho_pagina()
st.append(PageBreak()); sp(30)
add("Quando a sessão se perder", LIV)
QUANDO["Da assentada"] = "quando a sessão se perder; antes de cada obra nova"
add("Da assentada", LT); sumario(st[-1], 0, "Da assentada")
# LBX só é definido no Livro III; este capítulo vem antes e precisa do mesmo rótulo.
LBA = ParagraphStyle('lba', **{**base, 'textColor': GRAY}, fontSize=9.5, leading=12, spaceBefore=6, spaceAfter=2, keepWithNext=1)
add("<i>“Pureza de coração é querer uma só coisa.”</i>", ParagraphStyle('as1', parent=PC, fontSize=12, spaceAfter=2))
add("Søren Kierkegaard", ParagraphStyle('as2', parent=EPA, spaceAfter=20))
SEC_NO_SUMARIO = True

sec("Da assentada")
add("Leia este capítulo na noite do primeiro dia em que a sessão se perder, e de novo antes de cada obra em curso nova. A frase você já diz desde o dia um.", PI)
add("Pense em duas pessoas. Uma decide aprender álgebra. Compra três livros, procura o melhor curso, faz um plano de seis meses com cores diferentes. Um mês depois, sabe muito sobre como se aprende álgebra e quase nada de álgebra. A outra se senta num sábado de manhã com um livro e um lápis, e à noite resolve equações que de manhã não sabia ler. Ela não é especialista, mas tem a base que faltava à primeira.", PI)
add("O que separa as duas está no modo de pensar à mesa. A segunda tem uma coisa à frente, nenhuma outra, e fica com ela até essa coisa estar feita. Ela planejou menos e contou menos, e não parecia estar se forçando. Há em português uma expressão antiga para isso: fazer de uma assentada, isto é, de uma vez, sentado, sem levantar até estar feito. Este capítulo trata desse modo de pensar e da frase que o protege.", PI)
add("Esse é o estado que dá nome ao livro. Conhece-o quem já o teve numa tarde inteira sem ter tomado nada. Os outros capítulos tiram da mesa e dos dias o que o impede. Este dá a frase que, cada vez que você se senta, prepara o lugar onde ele aparece, e o modo de conduzir a sessão.", PI)
add("Franz Kafka deixou desse estado um registro com data. Na noite de 22 para 23 de setembro de 1912, sentou-se às dez e escreveu <i>O veredicto</i> até as seis da manhã, <i>in einem Zug</i>, de uma assentada. No diário, anotou que mal conseguia tirar de debaixo da mesa as pernas rígidas, e falou do esforço terrível e da alegria de ver a história se desenvolver diante dele. Concluiu que só assim se pode escrever, com essa abertura completa do corpo e da alma. Kafka passava os dias num escritório de seguros, e muitas noites dele à mesa não davam nada. Aquela foi rara para ele também.", PI)

sec("Da frase")
add("A frase é esta, e se diz por dentro:", PI)
add("Isto, até acabar.", VOICE)
sp(6)
add("Ela tem duas metades. <i>Isto</i> pergunta o que você tem à frente: uma coisa só, presente, que se possa apontar. Este capítulo, este problema, esta página, esta carta: o que está nas suas mãos agora. <i>Até acabar</i> põe o fim na própria coisa. Acaba quando o capítulo estiver lido, quando o problema sair, quando a página estiver escrita. A vontade que passa, a outra coisa que chama e o corpo que pesa não acabam nada.", PI)
add("A frase não promete nada. Não diz nada sobre amanhã nem sobre quem você é; não se assina, não se cumpre nem se quebra. Se você a disser e, cinco minutos depois, se levantar, ela volta a ser dita quando você se sentar outra vez. Por isso serve para todos os casos. As nove linhas do Livro I respondem cada uma a um instante; esta fica por trás de todas.", PI)
proc("A frase nos casos que mais custam", [
 "Se você não sabe o que fazer, escolha uma coisa que se possa apontar. Essa é <i>isto</i>.",
 "Se você adia, olhe <i>isto</i>, que está aqui, agora, e comece.",
 "Se você planeja em vez de fazer, pergunte o que o plano acaba. A resposta é nada.",
 "Se outra coisa chama, diga que ela não é <i>isto</i>. Deixe-a esperar.",
 "Se você quer trocar de livro ou de método no meio, acabe antes de trocar.",
 "Se o corpo pesa, acabe o passo em que você está. Depois veja.",
])
add("D O &nbsp; P O R Q U Ê", LBA)
add("<b>A ideia.</b> Vários dos que pensaram o trabalho bem feito disseram, cada um a seu modo, alguma coisa sobre ter uma coisa só à frente: Dōgen, Descartes, Kierkegaard, Aristóteles, Simone Weil. Nenhum escreveu esta frase. As seções seguintes contam o que cada um pensava e onde o livro se afasta dele.", PI)
add("<b>O mecanismo.</b> Primeiro, a voz que tira você da obra pede que você faça outra coisa no lugar, mais fácil e parecida com a obra. A frase a reconhece sem discutir, porque essa coisa não é <i>isto</i>. Segundo, um fim posto na coisa se vê e se aproxima; um fim posto no humor muda a cada minuto. Quem sabe onde a coisa acaba deixa de decidir, a cada minuto, se continua. Nenhum estudo testou esta frase: o autor acha, pelo raciocínio e pelo que esses autores contam.", PI)
add("<b>Por isso.</b> <i>Digo a frase porque, com uma coisa só à frente, paro de decidir a cada minuto se continuo.</i>", PI)

sec("Do cozinheiro")
add("Dōgen, monge japonês que viveu entre 1200 e 1253, levou para o Japão a escola zen Sōtō. Aos vinte e três anos atravessou o mar até a China em busca de um mestre e passou alguns anos no mosteiro do monte Tiantong. Já velho, escreveu umas <i>Instruções ao cozinheiro</i>, e conta nelas um encontro dessa época.", PI)
add("Era verão, depois do almoço. O cozinheiro do mosteiro, um velho curvado de sobrancelhas brancas, estava ao sol, sem chapéu, pondo cogumelos para secar sobre as pedras que escaldavam. Dōgen lhe perguntou por que não deixava aquilo para um ajudante. O velho respondeu: os outros não são eu. Dōgen insistiu: mas por que agora, com este calor? E o velho: se não agora, quando?", PI)
add("Dōgen se calou, e escreve que ali começou a entender o ofício do cozinheiro. Na escola dele, a prática estava inteira em cada coisa feita com o espírito todo: cozinhar, varrer, lavar o arroz. Prática e realização são uma coisa só; nenhuma chegada adiante dá valor ao gesto. <i>Os outros não são eu</i>: isto é meu, e entregá-lo a outro seria largar a parte de vida que ele é. <i>Se não agora, quando?</i>: o tempo disto é este.", PI)
add("A frase deste capítulo toma do velho a primeira metade, e só essa. A segunda já não é de Dōgen, para quem cada instante é completo e estudar o eu é esquecer o eu (<i>Genjōkōan</i>); um caderno que conta dias limpos seria o contrário disso. A pergunta da máscara também não briga com o velho: ela escolhe na entrada e, dito <i>Isto</i>, se cala até o fim do passo.", PI)

sec("Da floresta")
add("O caso mais comum de quem não começa é não saber o que fazer. Você se senta, e na cabeça há uma nuvem: <i>tenho de estudar, tenho de pôr aquilo em dia, tenho de aprender francês, tenho de mudar de vida</i>. A nuvem pesa e não se pode fazer, porque não tem começo. Quem está nela diz que lhe falta motivação. O que falta é saber qual é <i>isto</i>.", PI)
add("Descartes passou por uma nuvem dessas e deixou escrito, no <i>Discurso do método</i>, de 1637, o que fez. Enquanto reconstruía as próprias opiniões, precisava continuar a viver e a agir, e fixou umas poucas máximas provisórias. A segunda era ser o mais firme e resoluto que pudesse nas ações, e seguir as opiniões mais duvidosas, uma vez decididas, como se fossem muito certas. Os viajantes perdidos numa floresta, diz ele, não devem andar em círculos nem parar num lugar. Devem caminhar sempre o mais reto possível para um mesmo lado, ainda que só o acaso tenha escolhido esse lado. Assim chegam pelo menos a algum lugar melhor do que o meio da floresta.", PI)
add("Para Descartes, quando a razão não consegue escolher, a pior escolha é não escolher: quem anda em círculos gasta a força sem sair do lugar. A clareza vem de caminhar depois da escolha, porque só quem anda descobre como é a floresta. E a máxima é provisória: Descartes revia o caminho quando tinha razões para isso. No seu caderno, o tempo de rever tem lugar marcado: a noite de passagem.", PI)
proc("Na nuvem", [
 "Diga a linha I: o que tem de existir quando você se levantar?",
 "Se há três coisas igualmente urgentes, diga a linha VII: qual delas você evitaria se pudesse?",
 "Escolha essa.",
 "Se continuam empatadas, escolha a primeira e pare de escolher.",
 "Escreva o que ficou de fora na folha de captura.",
])
add("A primeira metade da frase pede só uma coisa. Uma tarde de verbos parece pouco para quem quer aprender francês. Mas <i>aprender francês</i> é uma frase verdadeira que não se pode começar; serve de direção, e a direção você já escreveu no dia zero. A pessoa da álgebra não se sentou para aprender álgebra. Sentou-se diante da primeira coisa que a álgebra pede, até dominá-la, e depois diante da seguinte. A álgebra foi o que ficou.", PI)

sec("Do ânimo dobre")
add("A epígrafe deste capítulo é o título de um discurso de Kierkegaard, de 1847, <i>Pureza de coração é querer uma só coisa</i>. Ele parte da Epístola de Tiago, que chama de inconstante o homem de ânimo dobre, literalmente, de duas almas.", PI)
add("Para Kierkegaard, a pessoa dividida quer uma coisa e, ao lado, outra: o bem e a recompensa, o bem e não ser castigada, o bem para brilhar com ele. A forma mais difícil de ver é querer o bem até certo ponto. Quem quer até certo ponto tem sempre, para mostrar, a parte que quis, e por isso nunca se acusa. Entre as formas da divisão ele põe também a pressa ocupada: a vida em que cada afazer puxa para um lado, nenhum chega ao fim, e que se escolhe para não ter de se recolher.", PI)
add("Para ele, a unidade de uma pessoa se faz querendo uma coisa inteira e se desfaz querendo-a pela metade. Só que, para Kierkegaard, só o Bem é uma coisa só, e quem quisesse o estado que dá nome a este livro seria de ânimo dobre. O livro toma do discurso só a forma do querer inteiro e a figura do <i>até certo ponto</i>.", PI)
add("Na escala de uma obra que acaba numa tarde, <i>até acabar</i> responde ao <i>até certo ponto</i>. Quem lê o capítulo até a parte difícil e para ali quis o capítulo até certo ponto. À noite a diferença se sente: o que ficou feito está inteiro ou pela metade. <i>Ele</i> é alguém que não quer até certo ponto.", PI)
add("No meio de uma obra, outra obra, outro livro, outro método parecem mais promissores, porque você ainda não chegou à parte difícil deles. Kierkegaard chamaria isso de ânimo dobre: querer isto e, ao lado, a saída.", PI)
proc("Se outra coisa parece melhor", [
 "Escreva-a na folha de captura, numa linha.",
 "Volte a <i>isto</i> e acabe.",
 "À noite, decida sobre a linha.",
 "· Se ela for melhor de verdade, continuará melhor depois que você acabar <i>isto</i>.",
])

sec("Das duas portas")
add("Você chama de sabotagem uma coisa estranha: você quer fazer, sabe que quer, e você mesmo impede. Os gregos chamavam isso de <i>akrasía</i>: saber o que é melhor e fazer o pior. Aristóteles, no sétimo livro da <i>Ética a Nicômaco</i>, distingue duas formas dessa falta de domínio, e elas são as duas maneiras de você se tirar da obra.", PI)
add("Uma é a precipitação, <i>propéteia</i>: a pessoa não chega a deliberar e é levada pela primeira coisa que aparece. A outra é a fraqueza, <i>asthéneia</i>: a pessoa delibera, decide bem e depois não se mantém no que decidiu. Os que veem a tentação chegar e se preparam, observa Aristóteles, não são tão arrastados, como quem faz cócegas primeiro já não as sente.", PI)
add("A frase tem um remédio para cada falha. A primeira metade fecha a porta da precipitação: quem diz <i>isto</i> teve de olhar e escolher antes de fazer. A segunda metade fecha a porta da fraqueza: põe o fim fora do alcance do que chega depois. O que chega, vontade, peso do corpo ou boa ideia, não acaba <i>isto</i>.", PI)
add("A observação das cócegas explica por que a sabotagem chega disfarçada de outra coisa, mais fácil e parecida com a obra. Preparar em vez de fazer. Rever o que você já sabe em vez de enfrentar o que não sabe. Ler mais um pouco em vez de tentar. Ver só uma coisa e já voltar. Quem conhece esses disfarces de antemão já não é pego por eles, e a frase reconhece todos: nenhum é <i>isto</i>.", PI)
add("A preparação tem lugar marcado neste livro: a folha das quatro perguntas da linha VIII, a de quando você começa algo novo. Essa folha se faz numa sessão com prazo e acaba ali.", PI)

sec("Da atenção")
add("Quem passa bem uma tarde numa matéria nova não descreve o dia como esforço contra si. Descreve-o com surpresa: o tempo passou depressa, esqueceu de comer, no fim da tarde estava mais acordado do que de manhã. Uma filósofa e um psicólogo pensaram esse estado com cuidado.", PI)
add("Simone Weil ensinou filosofia em liceus do interior da França e trabalhou um ano como operária em fábricas metalúrgicas. Em 1942 escreveu para estudantes um texto curto, <i>Reflexões sobre o bom uso dos estudos escolares em vista do amor de Deus</i>. Morreu no ano seguinte, aos trinta e quatro anos. O texto parte de uma confusão que ela via nas escolas. Diz-se a um aluno <i>preste atenção</i>, e ele franze a testa, prende a respiração, contrai os músculos. Vinte minutos depois, não sabe dizer em que esteve atento: esteve fazendo força.", PI)
add("A vontade que aperta os dentes, escreve Weil, é a arma do aprendiz no trabalho manual e quase não tem lugar no estudo. A inteligência só se conduz pelo desejo, e o desejo pede prazer e alegria no trabalho. A atenção verdadeira suspende o próprio pensamento e o deixa vazio, à espera, aberto ao objeto. É como quem, do alto de uma montanha, vê ao mesmo tempo as florestas e as planícies sem olhar para elas. Em francês, espera é <i>attente</i>, parente de <i>attention</i>, e Weil pensava as duas juntas.", PI)
add("Para Weil, um esforço de atenção verdadeiro nunca se perde, mesmo que o problema de geometria fique sem solução. O fim que ela dava a essa atenção vai além do estudo: a oração e o próximo. O texto termina no infeliz e na pergunta que só a atenção sabe fazer a ele: qual é o seu tormento?", PI)
add("Mihaly Csikszentmihalyi chegou perto disso por outro caminho. Começou estudando pintores que passavam horas diante da tela esquecidos de comer e perdiam o interesse pelo quadro assim que ele ficava pronto. Depois estudou alpinistas, jogadores de xadrez, cirurgiões, operários. Em 1990 reuniu o que viu em <i>Flow</i>, palavra que os entrevistados usavam: a atenção toda na coisa, a consciência de si desaparecendo, o tempo passando de outra maneira.", PI)
add("Ele observou que o estado aparece quando a pessoa sabe com clareza o que faz, quando a própria coisa diz a cada passo se vai bem, e quando a dificuldade pede um pouco mais do que a pessoa tem. Muito menos dá tédio; muito mais dá ansiedade. As distrações desfazem o estado. Csikszentmihalyi descreveu as condições, sem um modo de ligar o estado, e há dias em que ele não vem. A frase também não o chama. Ela põe você no lugar onde ele aparece, com uma coisa só à frente e sem outra para onde ir.", PI)
add("A atenção de Weil diz respeito à qualidade da presença diante da coisa. <i>Até acabar</i> diz respeito à perseverança, que os monges do deserto chamavam de <i>hypomoné</i>, ficar até o fim. Pode-se perseverar desatento: o aluno de testa franzida ficou vinte minutos e esteve atento a nada. A frase tira do caminho a pergunta, a cada minuto, sobre se você continua, e deixa livre o lugar da atenção. Dita de dentes cerrados, ela dá a perseverança e imita mal a atenção.", PI)
add("A divisão é do livro. A disciplina serve ao começo, à hora de sentar, e a sexta linha trata dela. A perseverança protege a duração. A atenção, Weil a pedia como espera, e nem a disciplina nem a perseverança a garantem. Por isso a palavra disciplina não basta.", PI)
add("Pascal faria uma objeção. Nos <i>Pensamentos</i>, o divertimento inclui a ocupação séria: o rei cercado de afazeres, o caçador atrás da lebre, quem pretende um cargo e imagina que depois repousaria. Uma tarde inteira esquecido de si seria, para ele, o divertimento mais bem-acabado. Quem encarna o homem de X para chegar a X é esse caçador, com uma razão melhor. O livro o escolhe sabendo disso: a pergunta que o divertimento evita, quem você é e para quê, você respondeu por escrito no dia zero.", PI)

sec("Do que acaba")
add("Acabar pertence à coisa. Uma coisa que se aponta com <i>isto</i> tem um fim que se vê: o capítulo tem a última página, o problema tem a solução, a carta tem a assinatura. A frase não manda você nunca se levantar. Há coisas que não cabem num dia, e a hora de parar que você escreve de manhã continua a valer.", PI)
proc("Quando acabar", [
 "Se o que você apontou não tem fim que se veja, como <i>a álgebra</i>, volte à primeira metade.",
 "Se a hora de parar chega antes do fim, <i>isto</i> passa a ser o passo em que você está.",
 "Acabe esse passo.",
 "Responda à linha V: está feito ou quase? Qual é a primeira coisa de amanhã?",
 "Amanhã, comece ali.",
 "Se a vontade de parar vier no meio, diga a linha II: <i>até o fim deste passo</i>.",
 "Se, no fim do passo, o corpo não dá mais, sem pergunta sobre o valor da obra, feche-a sem culpa.",
 "Se nada em você quer começar, <i>isto</i> é a versão de dois minutos da linha VI.",
 "· Ver: <i>Do pêndulo</i>.",
])
add("A mulher de <i>Do primeiro dia</i> quis fazer o primeiro capítulo do programa num sábado livre. Sentou-se às nove. Às onze e meia, na parte dos prazos, que não entendia, lembrou-se de um manual mais recente, recomendado por uma colega. Já estava com meio corpo fora da cadeira quando disse a frase. O manual não era <i>isto</i>; foi para a folha de captura, numa linha. A parte dos prazos tomou a hora seguinte inteira.", PI)
add("Às cinco, a hora de parar, ela estava no meio do terceiro dos cinco exercícios do capítulo. Acabou esse, que era o passo em que estava, escreveu que amanhã começaria pelo quarto e se levantou. Não estava tão cansada quanto esperava; estava desperta. No dia seguinte sentou-se diante do quarto exercício sem nada a decidir. À noite, riscou o manual da folha de captura.", PI)

sec("Da sessão")
add("O estado que dá nome ao livro, quando vem, vem dentro de uma sessão. A sessão tem três tempos: a entrada, a duração e a volta depois de uma saída. O que segue prepara os três, e nenhum deles liga o estado. Há dias em que, cumpridas todas as condições, ele não vem. Nesses dias a sessão vale do mesmo modo: a obra anda, e a marca da noite mede os atos.", PI)
proc("A entrada", [
 "Tire da mesa o que distrai, em cinco minutos no máximo.",
 "Ponha a folha de captura ao lado.",
 "Diga a pergunta e escolha a coisa que a resposta der.",
 "Diga a linha I: o que tem de existir quando você se levantar, e qual é o primeiro movimento.",
 "Comece.",
 "Começada a obra, diga a frase: <i>Isto, até acabar</i>.",
 "Escreva na folha de captura, numa linha, o que chamar para outra coisa.",
 "Entre um passo e o seguinte, diga a pergunta de novo para escolher o próximo.",
 "Ao se levantar, ponha a mesa em ordem.",
 "Faça tudo sempre do mesmo modo e na mesma ordem.",
])
add("O valor do ritual está em ser igual: uma mesa que se reconhece não pede decisão. John Forster conta, na <i>Vida de Charles Dickens</i>, que sobre a mesa do romancista havia sempre os mesmos pequenos objetos, entre eles dois sapos de bronze que duelavam de florete. Estavam ali para que o olho tivesse onde pousar entre uma frase e outra. O homem que encheu o século de personagens não buscava novidade na mesa. O olho encontrava coisas conhecidas, que não contavam história nenhuma, e voltava à página.", PI)
add("Os primeiros minutos custam, e o custo não diz nada sobre a sessão. A cabeça resiste de três modos conhecidos.", PI)
proc("Os primeiros minutos", [
 "Se nada em você quer começar, diga a linha VI e faça a versão de dois minutos.",
 "Se você começa e a coisa não sai, escreva uma frase verdadeira, a mais verdadeira que souber.",
 "Se a voz oferece outra coisa parecida com a obra, diga a frase: essa coisa não é <i>isto</i>.",
 "Não espere sentir que entrou.",
 "· Dez minutos de obra feita contra a resistência são a entrada.",
])
proc("A duração", [
 "Marque o começo e o fim da sessão antes de começar.",
 "No início, marque de vinte e cinco a quarenta e cinco minutos.",
 "Quando ficar fácil, marque mais.",
 "Se você já se levantou por dentro, termine a sessão no fim do passo.",
 "Se você volta ao mesmo passo sem mudar nada, termine a sessão no fim do passo.",
 "Se a testa franze e a respiração fica presa, termine a sessão no fim do passo.",
 "Ao terminar, responda à linha V por escrito.",
 "Não arraste a sessão até a hora marcada à espera de que o estado volte.",
 "· Somadas, as sessões na parte difícil chegam a quatro horas por dia, no máximo.",
])
add("Há indícios desse teto: um estudo com violinistas de Berlim encontrou umas quatro horas diárias de prática difícil em todos os grupos. O sinal da testa franzida é de Weil: a atenção virou força, e você está atento a nada.", PI)
add("Dentro da sessão, o estado se reconhece depois, porque quem repara que está absorto já saiu um pouco. Humphrey Newton, secretário de Isaac Newton em Cambridge nos anos dos <i>Principia</i>, contou como era vê-lo trabalhar. Newton esquecia as refeições, e o prato voltava intocado. Dando uma volta no jardim, parava de repente, subia correndo a escada e escrevia de pé, sem puxar uma cadeira. Os sinais de fora servem a você de dentro: a hora que surpreende, a refeição que passou, a pergunta <i>quanto falta?</i> que deixou de vir. Newton não é modelo de duração; a hora de parar existe para que o estado não cobre do corpo o que o corpo não tem.", PI)
proc("A volta", [
 "Se quem saiu foi você, diga a linha III: <i>saí</i>, <i>onde eu estava?</i>",
 "Volte à última linha escrita.",
 "Se alguém chama e há um minuto, escreva na folha de captura onde parou e o próximo movimento.",
 "Ao voltar, não refaça a entrada inteira.",
 "Leia a linha deixada.",
 "Diga a frase.",
 "Faça o primeiro movimento que a linha manda.",
 "Se o estado não voltou, siga a sessão até o fim marcado.",
])
add("Há indícios de que essa linha ajuda. Em 2018, Sophie Leroy e Theresa Glomb viram que quem era interrompido e largava a tarefa sem mais nada levava para a seguinte um resíduo de atenção e se saía pior. Quem gastava um minuto anotando onde estava levava menos resíduo. O estudo mediu a tarefa que interrompia; o efeito sobre a volta é aposta do livro.", PI)
add("Três sessões da mulher de <i>Do primeiro dia</i>, no segundo capítulo do programa, mostram os três tempos. Numa terça, às oito e meia, ela levou o telefone para o quarto e pôs a folha de captura ao lado do livro. A resposta da pergunta foi a parte dos recursos, que ela adiava havia dois dias. Escreveu a linha I: <i>quando eu me levantar, os recursos numa página; primeiro movimento, reler o artigo.</i> Marcou trinta e cinco minutos e começou.", PI)
add("Quando a sessão terminou, ela estava no meio de um parágrafo e não tinha olhado o relógio. Acabou o parágrafo, respondeu à linha V e marcou a segunda sessão igual à primeira. Só às quinze para as dez reparou no que tinha havido, pelos sinais de fora: a xícara de chá cheia e fria, a pergunta <i>quanto falta?</i> que não tinha vindo. A marca da noite mediu a da vez, e o estado não entrou nela.", PI)
add("Na quinta, ela tinha dormido mal, e o capítulo chegara às nulidades, que ela não entendia. Fez a entrada do mesmo modo e na mesma ordem. Em vinte minutos leu a mesma página três vezes. A vontade de trocar as nulidades pelos recursos foi para a folha de captura, porque os recursos não eram <i>isto</i>. Voltar ao mesmo passo sem mudar nada era o sinal da linha V, e a sessão terminou no fim daquele passo. Então ela disse a linha IV e escreveu o que não sabia: a diferença entre as duas espécies de nulidade.", PI)
add("A menor parte que podia fazer agora era um quadro de duas colunas. A segunda sessão foi o quadro, feito devagar e sem gosto. À noite, a linha do dia disse <i>quadro das nulidades, pela metade</i>, e a marca foi traço, porque na ocasião que mais pesou ela fez o gesto. Na sessão seguinte, começou pelo quadro.", PI)
add("Num sábado, uma hora depois de começar, ela estava no estado da terça quando a irmã telefonou. Deixou tocar enquanto escrevia na folha uma linha: <i>parei no terceiro requisito; próximo, o exemplo da página 84</i>. Na volta, a vontade era recomeçar o capítulo do princípio. Ela leu a linha deixada, disse a frase e abriu a página 84. O estado não voltou, e a sessão seguiu sem gosto até o fim marcado.", PI)
add("Ao meio-dia, o terceiro requisito estava entendido e o exemplo, resumido em quatro linhas. Antes de se levantar, respondeu à linha V: quase; amanhã, o quarto requisito. À noite, riscou a linha da folha de captura, que já tinha servido.", PI)
add("Das três sessões, só a da terça ela chamaria de boa, e foi a única em que o estado veio. Na folha de marcas as três ficaram iguais, e o capítulo andou nas três. No fim do mês, ao reler as linhas do dia, ela já não sabia dizer quais tinham saído das sessões boas. Você não sai de uma assentada mestre de nada. O mestre se faz em anos de obra, nas estações do Livro III. A frase dá um começo: uma coisa feita inteira, e depois outra.", PI)
fleur()
# O ornamento vai junto do parágrafo anterior, para não ficar sozinho numa página.
st[-2:] = [KeepTogether(st[-2:])]
SEC_NO_SUMARIO = False

# ===================== DA TÉCNICA =====================
st.append(PageBreak()); sp(30)
add("À mão, a qualquer hora", LIV)
QUANDO["Da técnica"] = "a seção do obstáculo, quando ele se repetir"
add("Da técnica", LT); sumario(st[-1], 0, "Da técnica")
add("<i>“Faça da postura de combate a postura de todos os dias, e da postura de todos os dias a postura de combate.”</i>", ParagraphStyle('tc1', parent=PC, fontSize=12, spaceAfter=2))
add("Miyamoto Musashi, <i>O livro dos cinco anéis</i>, Livro da Água (tradução livre)", ParagraphStyle('tc2', parent=EPA, spaceAfter=20))
SEC_NO_SUMARIO = True

# O EBG-B.ttf sai com o peso regular, então o rótulo se distingue em maiúsculas menores.
def tec(nome, texto, faca, pratica=None, primeiro=False):
    marca = " <i>(primeiro gesto)</i>" if primeiro else ""
    add(f"<font size=9.5>{nome.upper()}</font>{marca} {texto} <i>Faça assim:</i> {faca}", PI)
    if pratica:
        add(f"<i>Na prática.</i> {pratica}", PI)

sec("Da técnica")
add("Você só precisa deste capítulo quando um obstáculo se repetir: o medo antes de entrar numa sala, a raiva que sobe, a cabeça que trava no meio da obra. Cada seção é um desses momentos. Cada gesto vem de alguém que viveu o momento antes de você e deixou dito o que fazia. Quando a pergunta da máscara não responde, porque você não sabe o que ele faria diante do medo, da dor ou da página em branco, estes são máscaras de bolso.", PI)
proc("Como usar este capítulo", [
 "Antes de o obstáculo se repetir, pule este capítulo.",
 "No dia em que ele se repetir, leia a seção dele.",
 "Leia a caixa de cada gesto na noite em que abrir a seção.",
 "No instante, use só o <i>Faça assim</i> do primeiro gesto, sem consultar o resto.",
 "Se o primeiro gesto falhou duas vezes no mesmo tipo de momento, use o segundo.",
 "Feito o gesto, diga a frase e volte à obra.",
 "Não marque os gestos. A da vez continua a única microação em treino.",
])
add("Cada gesto diz o que se sabe dele. Onde a história é lenda ou atribuída, isso vem dito. Um estudo citado sustenta o princípio do gesto; quando testou o gesto mesmo, ou quando caiu, isso também vem dito.", PI)
add("A chave é esta. Ela basta para escolher; o resto do capítulo ensina a fazer.", PI)
CHAVE = [
    ("Você percebe o que está fazendo da sua vida", "James: um ato físico em menos de um minuto"),
    ("A cabeça está cheia demais", "Os contêineres: a pendência na folha, o pensamento na esteira"),
    ("Você evita começar", "Hemingway: uma frase verdadeira"),
    ("Você se dispersa no meio", "A cavilha: o próximo passo, já escrito"),
    ("Você está confuso", "Feynman: o que eu não sei"),
    ("Você tem de falar ou executar diante de alguém", "Douglass: três frases de cor"),
    ("O medo do ridículo segura você", "Diógenes: um pedido por dia, sujeito a um não"),
    ("O corpo treme antes", "O suspiro duplo"),
    ("A raiva sobe", "Sentar antes de responder"),
    ("Você está travado entre opções", "A moeda; se a decisão é grande, Franklin"),
    ("O cansaço bate no meio da obra", "Vinte minutos até um ponto visível"),
    ("A tentação já está na mão", "Alexandre: descartar à vista"),
    ("O desconforto escolhido aperta", "Ou acaba, ou eu aguento"),
    ("Chega um golpe", "Uma pergunta só, e a coroa de volta"),
    ("O perigo físico já chegou", "Meu, e a ordem de Sullenberger"),
    ("Você precisa decorar", "Por partes, recitar antes de olhar, e a noite no meio"),
]
CH_A = ParagraphStyle('cha', parent=CX, fontSize=10, leading=13)
CH_B = ParagraphStyle('chb', parent=CH_A, fontName='G-I')
t = Table([[Paragraph(a, CH_A), Paragraph(b, CH_B)] for a, b in CHAVE], colWidths=[(W-2*M)*0.48, (W-2*M)*0.52])
t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'), ('LINEBELOW',(0,0),(-1,-2),0.3,GRAY),
                       ('LEFTPADDING',(0,0),(-1,-1),2), ('RIGHTPADDING',(0,0),(-1,-1),6),
                       ('TOPPADDING',(0,0),(-1,-1),3), ('BOTTOMPADDING',(0,0),(-1,-1),3)]))
st.append(KeepTogether([st.pop(), Spacer(1, 4), t, Spacer(1, 12)]))

sec("No instante em que você percebe")
add("Este é o momento mais importante do capítulo. Ele chega sem aviso: no sinal vermelho, no banho, às duas da manhã, no meio de uma conversa à toa. De repente você vê, com uma nitidez que não pediu, o que está fazendo da sua vida. O livro inteiro começou num momento assim, a noite em que você o abriu. Se o momento passa sem ato, a lucidez dói um pouco e no dia seguinte a vida continua igual. Os gestos desta seção fazem a lucidez deixar uma marca no mundo antes de ir embora.", PI)
tec("James e o brilho que evapora.", "No capítulo sobre o hábito dos <i>Princípios de psicologia</i>, William James escreveu que uma resolução que evapora sem dar fruto prático é pior do que uma chance perdida: atrapalha as resoluções seguintes de chegarem ao ato. A lucidez que não vira ato ensina você a ter lucidez sem agir, e a próxima chega mais fraca.",
    "em menos de um minuto, faça um ato físico pequeno na direção do que você viu, antes que se forme a segunda frase interior.",
    primeiro=True)
proc("James, na prática", [
 "Escolha um ato que muda um pouco o mundo e que se vê amanhã.",
 "· Servem: escrever a primeira linha, mandar a mensagem, apagar o aplicativo, calçar o tênis. Pensar, planejar, contar, comprar ou prometer não servem.",
 "Se o que você viu é a vida inteira, faça o menor pedaço da resposta que cabe neste minuto.",
 "Se é o corpo, faça dez agachamentos agora.",
 "Se é a obra, abra o arquivo e escreva uma linha.",
 "Se é uma pessoa, mande a mensagem agora.",
 "Se não há como agir, escreva em papel a data, o que viu e o primeiro ato de amanhã e a hora.",
 "· Essa linha é o ato.",
 "À noite, passe essa linha para a folha de captura.",
 "No dia seguinte, confira se o ato existe e se vê.",
 "Se a lucidez passou sem ato, não se acuse.",
 "Escreva o ato padrão para a próxima vez: <i>quando eu perceber, eu ___</i>.",
])
tec("Nansen e a costa sem volta.", "Em <i>A primeira travessia da Groenlândia</i>, Fridtjof Nansen conta por que, em 1888, cruzou o gelo a partir da costa leste, deserta, rumo às aldeias do oeste: quem saía do oeste podia voltar para o conforto. Na costa leste, não haveria recuo. A ordem, escreveu, era a morte ou a costa oeste.",
    "pergunte <i>o que me deixa voltar atrás?</i> e faça o ato de James que corta essa volta: a mensagem enviada, o valor pago, o aviso dado a quem vai cobrar.")

sec("Para limpar a mente")
add("Aqui você não quer resolver nem entender nada. A cabeça está cheia, barulhenta, com dez coisas rodando ao mesmo tempo, e você quer limpá-la, recomeçar do zero no meio do dia.", PI)
tec("Os contêineres.", "Tudo o que roda na cabeça é de dois tipos: pendência, que é algo a fazer, e pensamento, que só passa. Há indícios de que a pendência sossega quando ganha um plano escrito (Masicampo e Baumeister, 2011); daí a folha de captura. O pensamento passa quando você o deixa passar: é o exercício das folhas no rio da terapia de aceitação e compromisso (Hayes e colegas, 1999).",
    "numa folha, ponha cada pendência numa linha, com o verbo e o destino. Cada pensamento vai num contêiner de uma esteira que passa diante de você: veja-o entrar, diga o nome dele, deixe a esteira levá-lo.",
    primeiro=True)
proc("Os contêineres, na prática", [
 "Escreva primeiro todas as pendências, até a cabeça não ter mais nada para lembrar.",
 "· Exemplos: <i>pagar a conta: amanhã, nove horas</i>; <i>responder o João: hoje, depois do almoço</i>.",
 "Se você não sabe quando vai fazer, ponha como destino <i>decidir quando: sexta à noite</i>.",
 "Feche os olhos para a esteira, de três a cinco minutos.",
 "Veja os contêineres passarem da esquerda para a direita.",
 "Ponha cada pensamento que vier num contêiner, com o nome escrito do lado.",
 "Não empurre a esteira. Não segure o contêiner.",
 "Se o mesmo pensamento voltar, ponha-o em outro contêiner.",
 "Se a esteira fica vazia por alguns segundos e você percebe o silêncio: funcionou.",
 "Se um pensamento volta sem parar, abra os olhos e escreva-o na folha, com destino: era uma pendência.",
])
tec("Churchill e a pintura.", "Em 1915, depois do desastre de Galípoli e da saída do Almirantado, Churchill começou a pintar. No ensaio <i>A pintura como passatempo</i>, explicou que as partes cansadas da mente descansam quando se usam outras partes. A mudança, escreveu, é a chave mestra.",
    "quando a cabeça estiver gasta por um assunto, não se deite com o celular. Faça algo que use outra parte de você: as mãos, o corpo, a cor, o som. Quanto mais longe do assunto, melhor.")

sec("Para começar")
tec("Hemingway e a frase verdadeira.", "Em <i>Paris é uma festa</i>, Hemingway conta que, quando uma história não começava, dizia a si mesmo: basta escrever uma frase verdadeira; escreva a frase mais verdadeira que você sabe. Escrita essa, seguia dali.",
    "diante da página em branco, escreva uma única frase que você sabe ser verdadeira sobre o assunto, sem adjetivo. A seguinte sai dela.",
    primeiro=True)
proc("Hemingway, na prática", [
 "Use quando estiver diante da obra há mais de um minuto sem começar.",
 "Escreva algo que você viu, sabe ou mediu.",
 "· Exemplos: <i>as vendas caíram doze por cento em março</i>; <i>faz dois anos que não falamos</i>.",
 "Se a frase sai ruim, deixe-a. Corrija no fim, com o resto.",
 "Se a segunda não vem, escreva outra frase verdadeira sobre o mesmo assunto, e depois outra.",
 "Se você está na quinta frase sem ter decidido começar: funcionou.",
 "Se nem a primeira vem, você ainda não sabe o que pensa. Use o gesto de Feynman.",
])
tec("Demóstenes e a cabeça raspada.", "Plutarco conta que Demóstenes construiu um estúdio debaixo da terra para treinar a voz e descia lá todos os dias, às vezes por dois ou três meses seguidos. Raspava metade da cabeça, para que a vergonha o impedisse de sair, mesmo que quisesse.",
    "antes da sessão, ponha um custo de vergonha na saída: diga a alguém que você só responde depois de certa hora, ou entregue o celular a outra pessoa. A porta continua aberta, e sair por ela passa a custar.")

sec("Para não sair da obra")
tec("A cavilha do carpinteiro.", "Um sermão do cânone budista, atribuído ao Buda, ensina ao monge o que fazer quando um pensamento o tira do objeto. O primeiro recurso é trocar o pensamento por outro, como o carpinteiro que tira uma cavilha grossa batendo nela com uma fina. O último, cerrar os dentes e dominar a mente com a mente, fica em último de propósito. Há indícios do mesmo princípio: Wegner e colegas (1987) viram que tentar não pensar numa coisa a faz voltar, e que um pensamento substituto diminui essa volta.",
    "quando um pensamento puxar você para fora, ponha no lugar dele o próximo passo mínimo da obra, a próxima frase, o próximo número: a resposta pronta ao <i>Onde eu estava?</i> da linha III.",
    primeiro=True)
proc("A cavilha, na prática", [
 "Ao fim de cada passo, escreva qual é o próximo, em menos de dez palavras.",
 "· Exemplos: <i>reescrever a segunda frase</i>, <i>somar a coluna C</i>, <i>testar a lista vazia</i>.",
 "Quando o pensamento puxar, volte os olhos para essa linha e faça só ela.",
 "Se o pensamento é uma pendência real, escreva-o em meia linha na folha de captura e volte.",
 "Se, minutos depois, você percebe que esqueceu o pensamento: funcionou.",
 "Se ele voltar três vezes na sessão, diga o que ele custou: <i>me levou o último quarto de hora</i>.",
])
tec("Clausewitz e o atrito.", "No primeiro livro de <i>Da guerra</i>, Clausewitz escreve que na guerra tudo é muito simples, mas o mais simples é difícil. As pequenas dificuldades se somam, e agir na guerra é como andar dentro da água. Ele chama isso de atrito, e diz que só há um lubrificante para ele, o costume.",
    "antes de sentar para a obra, pergunte <i>o que vai emperrar nos primeiros cinco minutos?</i> e tire uma coisa do caminho: o arquivo já aberto, o carregador na tomada, a senha à mão, o material sobre a mesa. Se emperrar mesmo assim, siga: o atrito é o meio, e cada dia feito apesar dele é o costume que Clausewitz prescreve.")

sec("Para pensar com clareza")
tec("Feynman e o que ele não sabia.", "James Gleick conta que Feynman, estudante em Princeton, antes dos exames orais abriu um caderno com o título <i>Caderno das coisas que eu não sei</i>, e passou semanas desmontando cada ramo da física à procura das próprias falhas. Há indícios de que a página desfaz uma ilusão: Rozenblit e Keil (2002) viram que as pessoas acham que entendem um mecanismo até tentarem explicá-lo passo a passo.",
    "abra uma página com o título <i>O que eu não sei sobre isto</i>. Escreva uma lacuna por linha, como pergunta que tem resposta, e comece pela que sustenta as outras.",
    primeiro=True)
proc("Feynman, na prática", [
 "Troque o vago por perguntas. <i>Não entendo busca binária</i> não serve.",
 "· Exemplo: <i>por que posso descartar metade da lista? quando o laço para? e se o número não está nela?</i>",
 "Tente responder a cada pergunta em voz alta, sem olhar a solução.",
 "Ache a que você não consegue nem começar e da qual as outras dependem. Estude essa primeiro.",
 "Para cada lacuna, olhe a resposta por dez segundos e feche.",
 "Se a resposta volta inteira, era esquecimento: revise.",
 "Se continua opaca, era ignorância: estude.",
 "Se você explica a primeira lacuna em voz alta e as outras parecem pequenas: funcionou.",
])
tec("Lichtenberg e o caderno de rascunho.", "Lichtenberg, físico de Göttingen, tomou dos comerciantes ingleses o <i>waste book</i>, o livro onde se anota no dia, do jeito que vier, tudo o que se compra e vende, antes de passar a limpo. Fez dele os seus <i>Sudelbücher</i>, os cadernos de rascunho, onde por mais de trinta anos pôs cada ideia no minuto em que ela vinha.",
    "quando uma ideia vier, anote-a no ato, crua, numa linha, sem decidir se presta. À noite, passe a limpo só o que sobreviveu, para o caderno ou para a obra. O rascunho é sujo por regra; o juízo vem depois.")

sec("Para entrar e falar")
tec("Douglass em Nantucket.", "Em agosto de 1841, numa convenção em Nantucket, Frederick Douglass, que tinha fugido da escravidão três anos antes, foi chamado a falar a uma plateia de brancos. Ele conta que tremia em todos os membros e mal conseguia ficar de pé. Falou só alguns instantes, escreveu depois, sentiu certo grau de liberdade e disse o que queria com bastante facilidade.",
    "saiba as três primeiras frases de cor, para que a boca as diga enquanto o corpo ainda treme. A confiança chega depois delas.",
    primeiro=True)
proc("Douglass, na prática", [
 "Na véspera, escreva as três frases, curtas, do jeito que você fala.",
 "Decore-as recitando sem olhar: diga, confira, diga de novo.",
 "Pare quando saírem duas vezes seguidas sem erro.",
 "Ensaie com algum desconforto: de pé, depois de subir uma escada, com alguém olhando ou gravando.",
 "No dia, diga-as uma vez no caminho, sem papel.",
 "Se a terceira frase sai e você percebe que já está falando: funcionou.",
 "Se travar no meio de uma, diga a próxima. Não volte ao começo.",
 "· Ninguém na sala conhece as frases; só você sabe que pulou uma.",
])
tec("César e o Rubicão.", "Suetônio conta, na <i>Vida dos doze Césares</i>, que em janeiro de 49 a.C., à beira do Rubicão, Júlio César parou e hesitou: ainda podemos voltar, disse aos que estavam com ele; passada esta pequena ponte, tudo terá de ser decidido pelas armas. Depois atravessou, dizendo que a sorte estava lançada.",
    "com a mão na maçaneta, diga por dentro: <i>a sorte está lançada</i>. O ensaio acabou, e do outro lado da porta não há volta. Entre.")

sec("Para atravessar o ridículo")
add("O medo do ridículo segura a mão antes de qualquer coisa nova feita diante dos outros: a primeira aula, o primeiro texto publicado, o primeiro treino numa academia cheia, a pergunta em voz alta na reunião. A sensação parece um aviso para parar. O autor acha que ela mede só a falta de costume.", PI)
tec("Diógenes e a estátua.", "Diógenes Laércio conta que Diógenes, o cínico, pedia esmola a uma estátua no meio de Atenas. Quando lhe perguntaram por quê, respondeu que estava se exercitando a ser recusado.",
    "uma vez por dia, faça de propósito um pedido pequeno, sujeito a um não, e receba o não sem explicar nem insistir.",
    primeiro=True)
proc("Diógenes, na prática", [
 "Faça um pedido real, curto e de custo baixo para os dois lados.",
 "· Exemplos: um desconto no caixa, uma mesa melhor, cinco minutos de alguém que você admira.",
 "Antes de cada pedido, dê ao medo uma nota de zero a dez.",
 "Ouvido o não, diga <i>obrigado</i> e vá embora.",
 "À noite, escreva na folha de captura quantos pedidos fez e as notas.",
 "Se a nota cai de uma semana para outra: funcionou.",
 "Se fica no mesmo lugar, suba um degrau: pedidos maiores ou mais diferentes entre si.",
])
tec("Catão e os pés descalços.", "Plutarco conta, na <i>Vida de Catão, o Jovem</i>, que Catão, quando a moda em Roma era a púrpura viva, vestia de propósito a escura, e saía à rua depois da refeição sem sapatos e sem túnica. Com isso, diz Plutarco, acostumava-se a ter vergonha só do que é de fato vergonhoso. As terapias de exposição para a ansiedade social se apoiam no mesmo princípio.",
    "uma vez por semana, escolha uma dose pequena de ridículo sem dano a ninguém e fique nela um minuto inteiro, sem se explicar. Fique até o fim do minuto, sem rir de si para aliviar.")

sec("Para tirar o nervosismo")
tec("O suspiro duplo.", "Este gesto não tem padrinho antigo e vem primeiro porque é o mais direto. Há indícios a favor: Balban e colegas (2023) compararam cinco minutos diários de suspiro com outras respirações e com meditação, e o suspiro foi o que mais melhorou o humor e mais desacelerou a respiração. Como dose de um minuto antes da fala, há menos indícios.",
    "duas inspirações pelo nariz, a segunda curta, para encher o resto do pulmão, e uma expiração lenta e longa pela boca, mais longa que as duas inspirações juntas. Duas ou três vezes. Você pegou o jeito quando os ombros descem na expiração sem que você mande.",
    primeiro=True)
tec("Crasso e o tremor.", "No diálogo <i>Do orador</i>, Cícero põe na boca de Crasso, o maior orador da geração anterior, uma confissão: ele empalidece no começo de cada discurso e treme com todo o espírito e com todos os membros. Na mesma conversa se diz que os melhores oradores são os que mais temem, porque sabem o que está em jogo. Há indícios a favor: Brooks (2014) viu que dizer <i>estou animado</i>, em vez de <i>estou calmo</i>, muda o que a pessoa sente; sobre o desempenho, o efeito é menos firme.",
    "quando o coração disparar na porta, diga por dentro: <i>é o tremor de Crasso; estou pronto para isto</i>. Comece com o tremor dentro da primeira frase.")

sec("Para conter a raiva")
tec("Sentar e deitar.", "Uma tradição registrada por Abu Dawud atribui a Maomé este conselho: quem se irritar de pé, que se sente; se a raiva não passar, que se deite. Há indícios a favor: Harmon-Jones e Peterson (2009) viram que, sob insulto, o cérebro de quem estava reclinado não mostrava o padrão de quem se prepara para avançar; o estudo é pequeno e mediu o cérebro, sem medir a conduta.",
    "de pé, sente-se. Se continuar fervendo, encoste-se para trás. Só fale depois de mudar de postura, também ao telefone ou numa mensagem.",
    primeiro=True)
tec("Marco Aurélio e o próprio erro.", "Marco Aurélio anotou: quando a falta de alguém o ofender, volte-se logo para si e pense em que você erra de modo parecido; atento a isso, você logo esquecerá a raiva. Há indícios a favor: Mischkowski, Kross e Bushman (2012) viram que quem pensava na provocação de um ponto de vista distanciado ficava menos irritado e menos agressivo.",
    "sentado, complete por dentro uma frase só: <i>eu também já...</i> Ele me interrompeu; eu também interrompo quando tenho pressa. Responda só depois de completá-la.")

sec("Para decidir")
tec("A moeda de Piet Hein.", "O dinamarquês Piet Hein, matemático e poeta, deixou num poema curto este conselho: quando você precisar decidir e não tiver decisão nenhuma, jogue uma moeda; no instante em que ela está no ar, você sabe o que espera. Há indícios a favor: Levitt (2021) acompanhou pessoas que deixaram uma moeda decidir uma mudança grande; as que tiraram <i>mudar</i> mudaram mais e, seis meses depois, diziam-se mais felizes. O próprio autor chama o resultado de sugestivo.",
    "dê a cada opção um lado e jogue. No instante em que a moeda cai, repare no alívio ou na decepção, e decida por esse sinal. Se não sentir nada, as duas se equivalem: fique com a da moeda e siga.",
    primeiro=True)
proc("A moeda, na prática", [
 "Use em escolhas entre opções parecidas e que têm volta: qual passo primeiro, qual caminho, se aceita o convite.",
 "Para uma decisão grande, use a folha de Franklin.",
 "Jogue a moeda no fim, para ver se o resultado da folha alivia você.",
])
tec("A álgebra de Franklin.", "Em 1772, Joseph Priestley pediu conselho a Franklin sobre um cargo. Franklin respondeu que não podia dizer o que ele devia decidir, só como. Dividia meia folha em duas colunas, a favor e contra, e ia anotando durante três ou quatro dias, porque as razões não aparecem todas ao mesmo tempo. Depois riscava as que se equivaliam e chamou isso de álgebra moral. Há indícios de um limite: Wilson e colegas (1993) viram que quem listou razões antes de escolher um cartaz ficou menos satisfeito com ele semanas depois.",
    "divida a folha, anote as razões ao longo de alguns dias, risque os pares de mesmo peso. O lado que sobrar decide.")
proc("Franklin, na prática", [
 "No alto da folha, escreva o que importa nesta decisão: três ou quatro critérios no máximo.",
 "· Exemplos: dinheiro, tempo, o que você aprende, o risco.",
 "Risque a razão que não toca nenhum critério.",
 "Marque de modo diferente o que é fato e o que é preferência.",
 "Junte as razões que são a mesma dita duas vezes.",
 "Dê a cada razão um peso de um a três.",
 "Risque os pares de mesmo peso.",
 "Se uma condição elimina sozinha uma das opções, como um prazo impossível, deixe a folha de lado.",
 "Se a escolha é de gosto, deixe a folha de lado.",
 "Se a decisão não tem volta, espere uma noite a mais.",
 "Se o lado vencedor alivia você, decida.",
 "Se abate você, procure o critério que falta na folha e escreva-o.",
])

sec("Para continuar quando o cansaço bate")
tec("Joe Simpson e os vinte minutos.", "Em 1985, nos Andes peruanos, o alpinista Joe Simpson caiu numa fenda com a perna quebrada e foi dado como morto. Levou três ou quatro dias para se arrastar até o acampamento. Escolhia um ponto, aquela fenda, aquela pedra vermelha, e se dava vinte minutos para chegar lá, de olho no relógio. Quando deixava de olhar o relógio, achava que tinha descansado cinco minutos e tinham passado quarenta e cinco. Há indícios a favor: Bandura e Schunk (1981) viram que metas próximas fazem avançar mais do que metas distantes.",
    "quando o peso vier, escolha um ponto visível da obra, o fim desta seção, a página doze, e marque vinte minutos. Ao chegar, escolha o próximo ponto antes de levantar os olhos.",
    primeiro=True)
proc("Os vinte minutos, na prática", [
 "Escolha o ponto que você alcança em vinte minutos trabalhando sem parar.",
 "Se chegou em cinco minutos, faça o próximo ponto maior.",
 "Se o alarme toca e você ainda está longe, faça o próximo ponto menor.",
 "Quando o alarme tocar, escolha o próximo ponto antes de qualquer pausa.",
 "Se o peso vem de uma noite sem dormir, pare na hora de parar que escreveu de manhã.",
 "· O relógio corrige o que o corpo diz sobre o tempo.",
])
tec("Shackleton e os cinco minutos.", "Em maio de 1916, Shackleton, Worsley e Crean atravessaram a pé as montanhas da Geórgia do Sul para buscar socorro, umas trinta e seis horas sem dormir. Numa parada, Shackleton deixou os dois dormirem e ficou acordado. Depois de cinco minutos, acordou-os dizendo que tinham dormido meia hora, porque, naquele frio, dormir mais seria não acordar. O que se copia dele é a regra de parada. Cinco minutos não recuperam ninguém exausto, e a história não prova isso.",
    "no meio da obra, faça uma pausa curta com fim marcado, cinco minutos no relógio, e ao levantar declare que foi o bastante. Ao volante, numa máquina, no mar ou na estrada, se o sono fecha os olhos, pare de vez.")

sec("Para resistir a um impulso")
tec("Alexandre e o capacete.", "Arriano conta que Alexandre, atravessando com o exército o deserto da Gedrósia, recebeu dos soldados um pouco de água num capacete. Diante de todos, derramou-a no chão sem beber, e cada soldado, diz Arriano, se sentiu como se tivesse bebido aquela água. Ulisses se amarrava antes; Alexandre fechava a questão no instante, para que ela não ficasse aberta à negociação.",
    "quando a tentação já estiver na mão, jogue fora, devolva, derrame, à vista. Não a guarde para mais tarde.",
    primeiro=True)
tec("Mischel e a moldura.", "Nos estudos de Walter Mischel em Stanford, nos anos 1970, crianças diante de uma guloseima esperavam muito mais quando aprendiam a vê-la como uma foto, com uma moldura em volta, ou a pensar nela pela forma e pela cor. Os estudos eram pequenos. As réplicas de Watts e colegas (2018) derrubaram só a ideia de que a espera aos quatro anos prevê o futuro de alguém.",
    "quando não puder descartar, olhe para o objeto e diga por dentro: <i>é uma foto</i>. Descreva-o como quem faz um inventário: forma, cor, material.")

sec("Para aguentar o desconforto")
add("Esta seção é para o desconforto que você escolheu ou já conhece: o frio do banho, o treino, a fome do jejum, a cãibra do esforço, a cadeira depois de três horas.", PI)
proc("Antes destes gestos", [
 "Se a dor é nova, forte ou súbita, pare e procure um médico.",
 "Se há dor no peito, falta de ar ou dor que piora em repouso, pare e procure um médico.",
 "Se a dor veio depois de uma queda ou de uma pancada, pare e procure um médico.",
 "· Nenhum destes gestos serve para calar um sinal.",
])
tec("Marco Aurélio e a medida.", "Nos acampamentos do Danúbio, Marco Aurélio anotou sobre a dor: a insuportável nos leva embora; a que dura é suportável. Há indícios a favor: Sullivan e colegas (1995) criaram uma escala para medir o hábito de ampliar e ruminar a dor e viram que quem mais faz isso relata sentir mais dor.",
    "no pico do frio, da cãibra ou da fome, diga: <i>ou ela acaba, ou eu aguento</i>. Depois ponha nela uma fronteira, onde ela está e até onde vai, <i>é a mão, só a mão</i>, sem acrescentar o futuro, <i>e se piorar, e se não passar</i>.",
    primeiro=True)
tec("Epicuro no último dia.", "No último dia, morrendo de uma doença na bexiga e de disenteria, Epicuro escreveu a um amigo: <i>escrevo-lhe neste dia feliz, que é também o último da minha vida</i>. As dores não podiam ser maiores, mas a tudo isso se opunha a alegria da alma pela lembrança das conversas que tinham tido. E pediu que cuidassem dos filhos de um amigo morto.",
    "no desconforto, ponha ao lado dele uma lembrança precisa e boa, uma conversa, um lugar, um rosto, com os detalhes. E faça um ato pequeno por alguém.")

sec("Para aguentar um golpe")
tec("Xenofonte e a coroa.", "Diógenes Laércio conta que Xenofonte oferecia um sacrifício, com uma coroa na cabeça, quando chegou a notícia de que o filho, Grilo, tinha morrido na batalha de Mantineia. Tirou a coroa e perguntou como ele tinha morrido. Ao saber que caíra lutando bem, pôs a coroa de volta e terminou o sacrifício.",
    "recebida a notícia, pare de verdade o que tem nas mãos. Faça uma pergunta só, a que decide o que é preciso saber agora. Respondida, devolva a coroa: volte ao que fazia e termine, ainda que pela metade. Se a notícia pede que você vá a algum lugar ou faça algo agora, isso passa à frente, e a coroa espera.",
    primeiro=True)
tec("Marie Curie e o diário.", "Em abril de 1906, Pierre Curie morreu atropelado por uma carroça em Paris. Poucos dias depois, Marie começou um caderno escrito a ele, em segunda pessoa, com os fatos como foram, e o manteve por um ano; a filha Ève cita trechos na biografia da mãe. Há indícios a favor: Pennebaker e Beall (1986) viram que escrever assim melhora a saúde nos meses seguintes.",
    "no dia do golpe, escreva no caderno, por quinze minutos e sem parar, o que aconteceu e o que você sente, com os fatos e os nomes. Repita nos três dias seguintes.")

sec("Diante do perigo")
add("Os gestos desta seção são para o medo diante de um perigo que já chegou e que você não pode evitar: a cirurgia marcada, a turbulência, a água que virou o barco. Eles não servem para entrar num perigo que você poderia recusar.", PI)
tec("Sullenberger e as duas palavras.", "Em janeiro de 2009, logo depois de o avião perder os dois motores ao bater num bando de gansos sobre Nova York, o comandante Sullenberger disse ao copiloto duas palavras, <i>meu avião</i>, e assumiu os comandos, enquanto o copiloto corria a lista de emergência. Poucos minutos depois pousaram no rio Hudson, e todos sobreviveram. Os pilotos aprendem uma ordem fixa para esses instantes: primeiro voar, depois navegar, por último comunicar.",
    "diante do perigo físico, tome o comando com uma palavra, <i>meu</i>, e siga a ordem: primeiro o que mantém você vivo nos próximos dez segundos, depois a direção, por último avisar alguém. A ordem funciona porque foi aprendida antes: se o seu ofício ou a sua casa têm um perigo provável, escreva hoje os três passos dele.",
    primeiro=True)
tec("Montaigne e a queda.", "Montaigne conta, no ensaio <i>Do exercício</i>, que um criado montado num cavalo forte o derrubou, e que foi levado para casa como morto, vomitando sangue. Por dentro, escreve, o estado era doce, uma languidez sem medo; a dor só veio quando voltou a si.",
    "quando vier o medo da anestesia, da queda ou da água, lembre Montaigne: o meio do perigo foi mais calmo do que a espera dele. Ponha a atenção no corpo presente, longe do filme do que vai acontecer.")

sec("Para memorizar")
tec("Quintiliano e a noite.", "Quintiliano, que ensinava retórica em Roma, mandava decorar o discurso longo por partes, ensaiar em voz baixa e decorar do próprio manuscrito, porque a memória guarda o lugar na página. E notou que uma noite de intervalo dá força ao que se aprendeu: o que não se conseguia repetir de manhã aparece firme depois do sono. Há indícios a favor da noite no meio (Rasch e Born, 2013).",
    "divida em partes de sentido. Ensaie cada uma em voz baixa, primeiro olhando o papel, depois sem olhar. Faça a última recitação antes de dormir e teste de manhã, sem reler antes.",
    primeiro=True)
proc("Quintiliano, na prática", [
 "Faça cada parte do tamanho de um fôlego: três a cinco frases.",
 "Recite sempre antes de olhar: tente, erre, confira, tente de novo.",
 "Se uma parte sai duas vezes seguidas sem erro, passe à seguinte.",
 "A cada três partes, recite as três juntas.",
 "Se um ponto falha sempre, marque-o no papel e comece a próxima rodada por ele.",
 "Se você recita o todo de manhã, sem reler, e de novo no dia seguinte: está decorado.",
])
tec("Mozart e o Miserere.", "Numa carta à mulher, de abril de 1770, Leopold Mozart conta que o filho, aos catorze anos, ouviu na Capela Sistina o <i>Miserere</i> de Allegri, música que o papa não deixava copiar, e a escreveu inteira de memória. Há indícios a favor: Roediger e Karpicke (2006) viram que tentar lembrar fixa mais do que reler.",
    "logo depois da aula ou da reunião, antes de falar com alguém ou olhar as notas, escreva de memória tudo o que guardou. Depois confira com a fonte e marque o que faltou.")

proc("Na noite em que abrir este capítulo", [
 "Escolha o obstáculo que mais se repete na sua vida.",
 "· O homem que você mais admira e o gesto mais grandioso não entram na escolha.",
 "Ache esse obstáculo na chave.",
 "Escreva no caderno, ao lado dele, o primeiro gesto da seção, numa linha curta.",
 "Deixe essa linha fora da folha de marcas.",
 "No dia em que o obstáculo vier, não decida de novo.",
 "Faça o gesto e volte à obra.",
])
st[-2:] = [KeepTogether(st[-2:])]
SEC_NO_SUMARIO = False

# ===================== LIVRO I =====================
livro("I", "Do pensamento")
st.append(KeepTogether([Paragraph("<i>“Dimidium facti qui coepit habet: sapere aude, incipe.”</i>", ParagraphStyle('livro1e1', parent=PC, fontSize=12, spaceAfter=2)),
                        Paragraph("Horácio, <i>Epístolas</i>, I, 2", ParagraphStyle('livro1e2', parent=EPA, spaceAfter=18))]))
add("Este livro guarda os instantes em que o dia se decide: o começo, a vontade de parar, a saída, o impasse, o fim, a falta de vontade, a escolha, o que é novo, a onda. Para cada instante há uma linha de pensamento. Cada linha é, para o seu instante, uma forma da frase que <i>Da assentada</i> ensina: <i>Isto, até acabar.</i>", PI)
proc("Como ler este livro", [
 "Na noite do dia zero, decore as frases das linhas I e VI, no breviário.",
 "Leia cada outra linha na noite em que entrar o exercício que a traz.",
 "Se uma linha soar vazia, leia <i>Da forma</i> e o <i>Do sentido</i> dela.",
])
add("As nove linhas não pesam igual no dia. A primeira e a sexta acompanham você desde o dia um: a primeira cada vez que você se senta diante da obra, a sexta quando nada em você quer começar. A oitava serve desde o começo, sempre que algo novo for começar. A segunda, a quinta e a sétima chegam com o exercício do terminar; a terceira, com o da absorção; a quarta, com o da prática deliberada. A nona só serve depois do primeiro corte.", PI)
add("O verso no alto é de Horácio e diz: quem começou tem metade do feito; ouse saber, comece. Ele abre o livro das linhas porque todas tratam do instante em que se começa, ou se deixa de começar. Na manhã do dia um, a folha do dia zero está escrita, a linha da manhã também, e a mesa está sob a microação da ordem. Tudo o que se podia decidir no papel está decidido. Falta o instante.", PI)
add("No começo do quinto livro das <i>Meditações</i>, Marco Aurélio, senhor de Roma, escreve a si mesmo que, ao amanhecer, quando lhe custar levantar-se, tenha à mão este pensamento: eu me levanto para a obra de homem. E discute consigo, ainda debaixo das cobertas, se terá nascido para ficar deitado e aquecido. Não lhe faltavam razões nem deveres. Faltava, naquele minuto, a frase certa, e ele a escrevia para tê-la à mão no minuto seguinte. No minuto do custo não há tempo para refazer o argumento. As nove linhas servem a você do mesmo modo.", PI)
add("No dia um você vai se sentar diante da obra de hoje. Entre sentar e o primeiro movimento da mão se abre um intervalo de poucos segundos, e nesse intervalo algo fala por dentro. É a voz antiga. Fala baixo. Diz <i>daqui a pouco</i>, diz <i>primeiro arrume isto</i>, diz <i>hoje não é o melhor dia, amanhã se começa direito</i>. A folha do dia zero dá direção, e a direção não governa o instante.", PI)
add("As tentativas antigas não morriam no dia em que se decidia mudar de vida. Morriam dias depois, às nove e dez de uma manhã qualquer, numa conversa de três segundos que ninguém ouviu. Este livro trata dessas conversas. Para cada uma há duas, três ou quatro frases curtas que você diz por dentro, em silêncio, no instante em que ela chega, sem discuti-las.", PI)
sec("Da forma")
add("Nesse intervalo, a voz fala, e você responde; ela replica, e você pondera; ao fim de um minuto, você delibera se a obra de hoje deve ser feita hoje, coisa que decidiu ontem. Entre perceber e agir, você abriu um tribunal. As nove linhas têm todas a mesma forma, e essa forma serve para que o tribunal nem chegue a abrir. Ela tem quatro tempos:", PI)
add("<i>perceber &nbsp;·&nbsp; nomear &nbsp;·&nbsp; o próximo movimento &nbsp;·&nbsp; mover</i>", ParagraphStyle('f2', parent=PC, fontSize=13, spaceBefore=8, spaceAfter=12))
proc("A forma", [
 "Perceba: a mão parou, o olhar foi à janela, veio uma frase que pede outra coisa.",
 "Nomeie o que veio com a palavra da linha: <i>é vontade</i>, <i>saí</i>, <i>é a onda</i>.",
 "Diga o próximo movimento que a linha traz: um gesto pequeno e visível.",
 "Mova a mão antes que outra frase se forme.",
 "Não argumente. Não se examine. O exame fica para a noite, com o caderno.",
 "Para decorar uma linha, leia-a em voz baixa até dizê-la sem olhar.",
])
add("A forma vem dos estoicos. Eles descreveram o caminho que vai do mundo até o ato. Primeiro chega a impressão, <i>phantasía</i>: uma coisa vista, uma lembrança, um desejo. Depois o espírito concorda ou não com o que ela afirma. Só então vem o impulso, <i>hormé</i>, e com ele o movimento. Entre a impressão e o impulso há um ponto em que o homem ainda é senhor de si.", PI)
add("Epicteto ensinava a guardar esse ponto com uma frase. No primeiro capítulo do <i>Manual</i>, aconselha o discípulo a dizer a toda impressão áspera: você é uma impressão, e de modo algum aquilo que parece. Isso é o nomear. A vontade de largar a obra se apresenta como verdade sobre o mundo, <i>isto está difícil demais</i>. Nomeada, volta ao tamanho que tem, o de um estado que passou pelo espírito.", PI)
add("Os estoicos examinavam cada impressão antes de lhe dar assentimento, e faziam disso a vida inteira. Você tem uma obra à frente e poucos segundos. Por isso a forma toma deles só o nomear, reduz o nomear a uma palavra e acrescenta o próximo movimento, decidido antes. Nomear sem mover não basta. Quem diz <i>é vontade, não fato</i> e continua sentado reconheceu o estado e deixou que ele decidisse.", PI)
add("A deliberação continua, em outra hora. No dia zero você delibera um dia inteiro sobre quem quer ser; depois, todas as noites, diante da folha de marcas, e com mais vagar em cada noite de passagem. O que a forma recusa é reabrir às nove e dez da manhã, com a preguiça como advogado, o processo julgado de cabeça fria. Um tribunal que reabre a causa a cada hora dá razão a quem fala por último, e no meio da manhã quem fala por último é o desejo do mais fácil.", PI)
add("Por isso as linhas são curtas. Uma frase longa convida à réplica; uma frase de três palavras já acabou antes que a réplica se forme. Você entende a linha antes, ao ler com calma o sentido dela. No instante, você só a diz, no tempo de uma respiração.", PI)

sec("As nove linhas")
add("Cada linha segue a mesma ordem: o título e o momento em que ela chega; as frases que você diz por dentro e decora; o que você faz em seguida, num quadro; <i>Do porquê</i>, com a ideia, o mecanismo e a frase que você diz ao usá-la; e <i>Do sentido</i>, com o instante como você vai vivê-lo e o que outros viveram nesse ponto do caminho.", PI)
add("O sentido se lê com calma, uma vez, fora das horas da obra, e se relê quando a linha parecer vazia.", PI)

LBL = ParagraphStyle('lbl', **{**base, 'textColor': GRAY}, fontSize=9.5, leading=12, spaceBefore=8, spaceAfter=4, keepWithNext=1)
# O quadro de procedimento de cada linha fica logo abaixo das frases, onde o leitor age.
PASSOS = {}
def linha(num, nome, quando, preludio, vozes, corpo, sentido, nota=None, porque=None):
    blk = [sumario(Paragraph(f"{num}. &nbsp;{nome}", ParagraphStyle('hh', parent=HEAD, fontSize=13.5, spaceBefore=16)), 1, f"{num}. {nome}"),
           Paragraph(quando, WHEN)]
    if preludio: blk.append(Paragraph(preludio, BODY))
    for v in vozes: blk.append(Paragraph(v, VOICE))
    blk.append(Paragraph(corpo, BODY))
    st.append(KeepTogether(blk))
    if num in PASSOS: proc(f"Linha {num}", PASSOS[num])
    if porque:
        st.append(Paragraph("D O &nbsp; P O R Q U Ê", LBL))
        for par in porque: st.append(Paragraph(par, PI))
    st.append(Paragraph("D O &nbsp; S E N T I D O", LBL))
    for par in sentido: st.append(Paragraph(par, PI))
    if nota: st.append(Paragraph(nota, NOTE))

PASSOS["I"] = [
 "Sente-se diante da obra de hoje. Tire da mesa o que distrai.",
 "Repouse os olhos num ponto fixo, em silêncio, até o ruído das horas anteriores assentar.",
 "Pergunte por dentro: <i>o que deve existir quando eu me levantar daqui?</i>",
 "Responda com um objeto que se possa ver e tocar ao fim da sessão.",
 "Escreva a resposta na margem da folha de captura ou no canto do caderno.",
 "Se a resposta é a obra inteira ou uma intenção, como <i>avançar</i>, corte-a até caber nesta sessão.",
 "Pergunte: <i>qual é o primeiro movimento da mão?</i>",
 "Veja-se por um instante fazendo os primeiros cinco minutos.",
 "Diga <i>comece</i>.",
 "Mova a mão sem esperar outro pensamento.",
 "Se passaram mais de cinco minutos sem a mão se mover, faça a segunda pergunta e mova a mão.",
]
linha("I", "Do começar", "Quando você for iniciar o que importa.",
 "Sente-se, afaste de você o que distrai e repouse os olhos num ponto fixo, em silêncio. Então, nesta ordem:",
 ["O que deve existir quando eu me levantar daqui?", "Qual é o primeiro movimento da mão?",
  "<font color='#6b6b6b'>(Veja-se, por um instante, fazendo os primeiros cinco minutos.)</font>", "Comece."],
 "E a mão se move.",
 ["No dia um, à mesa, você vai fazer isto pela primeira vez. A obra de hoje vai parecer, nesse instante, maior e mais vaga do que na linha da manhã. Vem a primeira voz do dia: <i>primeiro vejo só uma coisa</i>, ou <i>preciso pensar melhor por onde pegar isto</i>. Você está à mesa, a obra está à frente, e a mão ainda não fez nada. É o começar.",
  "A obra adiada continua por fazer, e amanhã pesa mais: à névoa se soma o atraso. A primeira pergunta transforma <i>trabalhar no relatório</i> em <i>a segunda seção escrita</i>. Quando a mão se move, a linha fez o que tinha a fazer, e o resto da sessão pertence à obra.",
  "Na Inglaterra de meados do século XIX, um funcionário dos correios chamado Anthony Trollope se tornou um dos romancistas mais lidos de seu tempo sem deixar o emprego. Às cinco e meia estava à mesa, com o relógio diante de si, e exigia de si mesmo duzentas e cinquenta palavras a cada quarto de hora. Escrevia três horas e depois ia trabalhar. Um velho criado o acordava de madrugada, com café, e Trollope escreveu que devia a esse homem, mais do que a qualquer outro, o êxito que tivera.",
  "Trollope não começava o dia decidindo se escrevia, nem o quê. A obra da manhã tinha contorno, e o primeiro movimento era sempre o mesmo, a pena no papel. Duzentas e cinquenta palavras num quarto de hora são um passo que se cumpre em qualquer manhã. Quem responde à primeira pergunta com <i>o livro inteiro</i> trocou uma névoa por outra, maior.",
  "Quando a <i>Autobiografia</i> saiu, em 1883, muitos leitores não perdoaram o romancista por ter confessado o relógio. Ele já respondera no próprio livro: o sapateiro, acabado um par de botas, não se senta à espera da musa para começar o seguinte. Os romances de Trollope continuam sendo lidos.",
  "Horácio escreveu o verso que abre este livro numa carta a um jovem amigo, Lólio. <i>Sapere</i>, em latim, é também ter juízo, e Horácio pede ao rapaz que comece desde já a viver com juízo. Dá a imagem: quem adia a hora de viver bem é o camponês que espera, à beira do rio, que a água acabe de passar para atravessá-lo; e o rio continua correndo. O <i>incipe</i> do fim do verso é um imperativo de uma palavra, como o <i>comece</i> desta linha."],
 "Mais de cinco minutos entre sentar e começar já são adiamento.",
 porque=[
  "<b>A ideia.</b> Aristóteles diz, na <i>Ética a Nicômaco</i>, que o princípio parece ser mais da metade do todo. Numa sessão, o começo pesa pela névoa: enquanto a obra não tem contorno, não há por onde pegá-la, e quem adia foge dessa névoa.",
  "<b>O mecanismo.</b> Um objeto que se pode ver ao fim da sessão diz por onde começar e quando você acabou; uma intenção não diz nenhuma das duas coisas. O primeiro movimento é tão pequeno que não deixa nada para deliberar, e, feito, mostra o passo seguinte. Nenhum estudo testou esta linha: este livro aposta nela pela razão e pela experiência de quem trabalhou assim.",
  "<b>Por isso.</b> Faço as duas perguntas porque um primeiro gesto pequeno não me deixa nada para discutir."])

PASSOS["II"] = [
 "Reconheça o momento: a vontade de parar chegou junto com o trecho difícil.",
 "Diga por dentro: <i>é vontade, não fato</i>.",
 "Diga: <i>até o fim deste passo</i>.",
 "Termine só o passo: a frase, a série, o parágrafo.",
 "Não se levante da cadeira antes do fim do passo.",
 "No fim do passo, olhe de novo para a vontade.",
 "Se ela passou, siga na obra.",
 "Se ela continua inteira, pare nesse ponto fechado. Amanhã você retoma sem névoa.",
 "Se o peso vem sem causa, com <i>vale a pena?</i>, trate-o como pêndulo.",
 "Se a hora de parar chegou, termine o passo e feche a obra.",
 "· Ver: <i>Do pêndulo</i>.",
]
linha("II", "Da vontade de parar", "Quando, no meio da obra, vier o desejo de largá-la.", None,
 ["É vontade, não fato.", "Até o fim deste passo."],
 "Termine a frase, a série, o parágrafo. A mão não sai do lugar.",
 ["Esta linha chega com o exercício do terminar, depois da primeira passagem. Até lá, você vai sentir este momento sem lhe dar nome. A obra anda, e depois chega um trecho que resiste: uma frase que não sai, uma série que pesa, um cálculo que não fecha. A mão desacelera. Vem uma voz sensata: <i>você já fez bastante por hoje</i>, <i>vou só me levantar um minuto</i>, <i>amanhã, com a cabeça fresca, isto sai</i>.",
  "A vontade de parar aparece onde a obra resiste. Por isso ela marca o ponto que importa.",
  "Um homem teve essa vontade com todos os motivos. Entre 1508 e 1512, Michelangelo pintou a abóbada da Capela Sistina, por encomenda do papa Júlio II. Não queria a encomenda: considerava-se escultor. Passou quatro anos nos andaimes, com a cabeça dobrada para trás. Numa folha desses anos escreveu um soneto a um amigo, Giovanni da Pistoia. Diz que tem a barba virada para o céu e a nuca colada às costas; que o pincel pinga na cara dele e faz dela um pavimento de cores; que o corpo se curvou como um arco sírio. E pede ao amigo que defenda a honra dele, porque ele não está no lugar certo, e não é pintor.",
  "O corpo doía de verdade, e a obra não era a que ele escolhera. Michelangelo pôs a vontade por escrito, deu a ela rima e humor, e voltou ao teto. O soneto é um <i>é vontade, não fato</i> de catorze versos: a queixa nomeada para que a mão pudesse continuar. A abóbada foi descoberta em 1512.",
  "Os gregos chamavam isto de <i>akrasía</i>: saber o que é melhor e fazer o pior. Aristóteles, no sétimo livro da <i>Ética a Nicômaco</i>, diz que o acrático tem o saber como o bêbado que recita versos de Empédocles sem que as palavras lhe digam nada. O desejo não apaga o saber; adormece-o no instante em que seria preciso. No trecho difícil, você não esquece que a obra importa. Durante alguns segundos, isso deixa de estar presente.",
  "A linha é uma prova barata: dê um passo e veja o que sobra. Uma resistência verdadeira não se dissolve no fim de uma frase; continua lá, e pode ser ouvida com calma depois. A vontade passageira se dissolve. Para a resistência que volta, há o Livro V."],
 "Esta linha vale para a vontade. Depois de horas de obra, a pausa planejada faz parte da obra; dela trata <i>Do descanso</i>.",
 porque=[
  "<b>A ideia.</b> É a <i>akrasía</i> dos gregos: o desejo adormece o saber no instante em que seria preciso. A vontade de parar aproveita esses segundos.",
  "<b>O mecanismo.</b> Um estado passa sozinho; uma razão pode ser escrita numa linha. Se você não consegue escrevê-la, era o estado. O fim do passo é tão pequeno que o saber acordado o cumpre sem ganhar a discussão inteira. Nenhum estudo testou esta linha; este livro aposta nela pela razão.",
  "<b>Por isso.</b> Termino o passo porque esta vontade passa, e um passo pequeno se faz mesmo com ela."])

PASSOS["III"] = [
 "Reconheça o momento: você se percebe fora da obra, sem lembrar de ter decidido sair.",
 "Diga por dentro só: <i>saí</i>. Sem adjetivo.",
 "Diga: <i>onde eu estava?</i>",
 "Feche o que abriu.",
 "Releia a última linha escrita, ou o último passo feito.",
 "Continue dali.",
 "Se vier à cabeça algo que não pertence à obra, escreva-o numa linha na folha de captura.",
 "Não pergunte por quê durante a obra.",
 "Se a mesma distração volta na mesma hora, procure a causa à noite, com a folha de captura.",
 "· Cada volta conta como uma repetição do treino.",
]
linha("III", "Da dispersão", "Quando você perceber que saiu.", None,
 ["Saí.", "Onde eu estava?"],
 "Feche o que abriu, releia a última linha e continue. Não pergunte por quê.",
 ["Esta linha chega com o exercício da absorção, e o momento dela vem desde o primeiro dia. Você está na obra e se percebe em outro lugar: olhando pela janela, pensando numa conversa de ontem, com a distração na mão sem lembrar de ter ido buscá-la. Logo depois vem uma segunda voz, que faz mais estrago do que a saída: <i>outra vez</i>, <i>nunca consigo manter a atenção</i>, <i>esta manhã já está perdida</i>.",
  "Numa manhã você pode sair e voltar trinta vezes. Com os dias, encurta o tempo entre sair e perceber que saiu.",
  "No século IV, nos desertos do Egito, homens iam viver sozinhos numa cela, e o que lhes cabia era ficar. Evágrio Pôntico chamou o pensamento mais pesado que os assaltava de <i>acédia</i>, o demônio do meio-dia. Ele faz parecer que o sol mal se move, que o dia tem cinquenta horas. Obriga o monge a olhar pela janela, a sair da cela, a calcular quanto falta para a refeição. Por fim, faz o monge odiar o lugar e lhe sussurra que em outro lugar tudo seria mais fácil. As distrações do seu tempo têm outros objetos; o movimento é o do monge à janela.",
  "O conselho dos padres do deserto era não sair da cela e voltar ao trabalho das mãos. João Cassiano conta a história do abade Paulo, que vivia a sete dias de caminho de qualquer cidade, sustentado por tâmaras e por uma horta. Não precisava trabalhar para comer, nem tinha a quem vender. Ainda assim, todos os dias, trançava cestos de folhas de palmeira; ao fim do ano, com a gruta cheia, queimava tudo e recomeçava. Sem o trabalho das mãos, diz Cassiano, o monge não consegue ficar no próprio lugar. A última linha escrita é o seu monte de folhas de palmeira: ela prende você à mesa antes que a obra ande.",
  "No meio da manhã, o espírito é um mau detetive de si mesmo: explica tudo pelo caráter. À noite, com a folha de captura na mão, as provas estão escritas: a hora, o lugar, o que veio. É ali que a causa aparece, e ela aparece no ambiente."],
 porque=[
  "<b>A ideia.</b> A atenção se desvia sozinha, dezenas de vezes por hora, e nenhum mestre esteve livre disso. A saída vem de qualquer modo. Esta linha treina o modo da volta e o tempo que ela leva.",
  "<b>O mecanismo.</b> Julgar a si mesmo por ter saído gasta a atenção que devia voltar à obra: <i>de novo</i> é uma segunda saída, e <i>saí</i> nomeia sem condenar, numa palavra. Está demonstrado que cada troca de atividade custa tempo e erros, mesmo prevista; Stephen Monsell reuniu esses estudos. Voltar à última linha reduz o que você tem de reconstruir.",
  "<b>Por isso.</b> Digo só <i>saí</i> e volto à última linha porque cada atividade nova me obriga a reconstruir onde estava."])

PASSOS["IV"] = [
 "Reconheça o giro: há algum tempo você não faz nada diferente do que fazia.",
 "Pare de girar.",
 "Pergunte por dentro: <i>o que exatamente eu não sei?</i>",
 "Escreva a resposta numa linha, em forma de pergunta, no caderno ou na folha de captura.",
 "Pergunte: <i>qual é a menor parte que posso fazer agora?</i>",
 "Escolha um caso particular, um pedaço do problema, ou a parte que você já sabe resolver.",
 "Faça essa parte.",
 "Se o impasse continua depois de algumas voltas assim, peça a crítica de quem sabe mais.",
 "Ou faça uma pausa, com a pergunta escrita à vista.",
 "· Abandonar não está entre as saídas.",
]
linha("IV", "Do impasse", "Quando o problema não andar.", None,
 ["O que exatamente eu não sei?", "Qual é a menor parte que posso fazer agora?"],
 "Escreva a pergunta numa linha. Faça a menor parte.",
 ["Esta linha chega com o exercício da prática deliberada, na segunda estação. Ali a obra passa a ser fazer o que você ainda não sabe, e os impasses se multiplicam. Uma prática que nunca trava está abaixo do seu limite. Você relê o mesmo parágrafo pela terceira vez, tenta a saída que já falhou, olha para o todo à espera de que ele ceda. O tempo passa com a aparência de trabalho.",
  "A voz tem duas formas: <i>não tenho jeito para isto</i>, ou <i>preciso ler mais antes de continuar</i>. A primeira é uma sentença sobre o caráter e nada diz sobre o problema. A resposta a ela é a menor parte, feita.",
  "Henri Poincaré contou, em <i>Ciência e método</i>, como fez uma de suas primeiras descobertas. Durante quinze dias tentou provar que não podia existir certa classe de funções. Sentava-se todos os dias à mesa por uma ou duas horas, experimentava combinações e não chegava a nada. Depois deixou Caen para uma excursão geológica e esqueceu o problema. Em Coutances, no instante em que punha o pé no estribo de uma carruagem, a ideia lhe veio: as transformações que usara eram idênticas às da geometria não euclidiana. Não a verificou ali; retomou a conversa. De volta a Caen, verificou-a com calma.",
  "Poincaré tirou da cena a conclusão que esta linha leva a sério. As iluminações súbitas, escreveu, só vêm depois de dias de esforço voluntário que pareceram inúteis, e pedem trabalho consciente depois, para verificar o que veio. Ele largou depois de quinze dias sabendo exatamente o que procurava e onde falhava. A pergunta escrita faz esse papel. A pausa desta linha vem depois da pergunta e nunca toma o lugar dela. <font color='#6b6b6b'>(Lição III)</font>"],
 porque=[
  "<b>A ideia.</b> George Pólya, em <i>A arte de resolver problemas</i>, aconselha a quem trava: se você não consegue resolver um problema, resolva primeiro um menor que seja parente dele. O impasse vem de um problema mal definido, ou grande demais para ser tomado inteiro.",
  "<b>O mecanismo.</b> Escrever o que você não sabe transforma uma ignorância vaga numa pergunta, e uma pergunta tem resposta possível. No papel, a dúvida deixa de voltar sempre ao mesmo ponto. A menor parte faz a obra avançar e mostra por onde o problema cede. Nenhum estudo controlado testou esta linha; este livro aposta nela pela razão de quem passou a vida resolvendo problemas.",
  "<b>Por isso.</b> Escrevo a pergunta porque uma lacuna com nome tem resposta, e a menor parte me mostra onde cede."])

PASSOS["V"] = [
 "Reconheça o momento: você já se levantou por dentro, ou volta ao mesmo passo sem mudar nada.",
 "Pergunte: <i>está feito, ou está quase?</i>",
 "Compare uma vez, só uma, com a resposta que você deu à primeira pergunta da linha I.",
 "Se o objeto prometido existe, está feito.",
 "Se falta um pedaço, está quase: termine o pedaço agora.",
 "Pergunte: <i>o que faço primeiro amanhã?</i>",
 "Escreva a resposta numa linha.",
 "À noite, copie essa linha como primeira tarefa, na terceira linha da noite.",
 "Levante-se.",
]
linha("V", "Do fim", "Quando você julgar que terminou.", None,
 ["Está feito, ou está quase?", "O que faço primeiro amanhã?"],
 "Confira uma vez com o que você definiu ao começar. Escreva o primeiro passo de amanhã. Levante-se.",
 ["Esta linha chega com o exercício do terminar, depois da primeira passagem: quem aprende a não largar no meio aprende também a não largar no fim. A obra tem a aparência de feita, e vem a voz: <i>está bom assim</i>, <i>o resto reviso amanhã</i>, <i>falta tão pouco que não vale a pena agora</i>. Ou a contrária, se você é dos que nunca terminam: <i>ainda não está bom, mais uma volta</i>.",
  "Há dois perigos no fim. O primeiro é parar no quase: a obra oitenta por cento pronta, que parece feita e não está. O último passo, a revisão, a conferência, é o mais tedioso, e é o que fica por fazer. O segundo é parar sem saber como recomeçar, e então a manhã seguinte começa com névoa. Hemingway conta, em <i>Paris é uma festa</i>, que parava quando sabia o que ia acontecer em seguida, para ter certeza de continuar no dia seguinte.",
  "Virgílio passou os últimos onze anos da vida escrevendo a <i>Eneida</i>. Ditava de manhã muitos versos e passava o resto do dia reduzindo-os a muito poucos; dizia que dava forma ao poema como a ursa às crias, lambendo-as. No ano 19 antes de Cristo, partiu para a Grécia decidido a passar três anos polindo o poema. Adoeceu na viagem e morreu em Brindisi. Antes de morrer, pediu que queimassem a <i>Eneida</i>, porque não estava acabada. Augusto proibiu a queima e mandou publicá-la como estava. Por isso ainda hoje se leem nela versos cortados no meio.",
  "Virgílio sabia o que faltava e tinha um plano para fazê-lo; deixou o acabamento para uma viagem, e a viagem não terminou. O poema se salvou porque um imperador desobedeceu ao poeta. Uma obra comum não conta com essa intervenção.",
  "Leonardo errou do outro lado. Vasari conta que ele começou muitas coisas e não acabou nenhuma, porque a mão não alcançava a perfeição que ele imaginava; trabalhou quatro anos no retrato da mulher de Francesco del Giocondo e o deixou inacabado. Ele comparava cada pincelada com uma perfeição imaginada, e nenhuma pincelada aguenta essa comparação. A linha I dá ao fim outra medida: o que você prometeu ao sentar. O perfeccionismo e a pressa erram do mesmo modo: nenhum dos dois compara a obra com o que foi prometido."],
 porque=[
  "<b>A ideia.</b> Os gregos chamavam o fim de <i>télos</i>, palavra que quer dizer ao mesmo tempo o término e o propósito. A sessão termina quando alcança aquilo para que foi começada, e esse propósito ficou escrito na resposta a <i>o que deve existir quando eu me levantar daqui?</i>",
  "<b>O mecanismo.</b> Comparar uma vez com um objeto que você mesmo definiu dá ao fim uma medida fechada: o objeto existe, ou lhe falta um pedaço. Essa medida impede o quase e a volta sem fim ao mesmo passo. Escrever o primeiro passo de amanhã deixa o recomeço decidido. Está demonstrado que decidir antes que ação concreta você fará num momento concreto aumenta a probabilidade de fazê-la; Peter Gollwitzer e Paschal Sheeran reuniram esses estudos.",
  "<b>Por isso.</b> Comparo e escrevo o passo de amanhã porque assim sei se acabei e não decido nada de manhã."])

PASSOS["VI"] = [
 "Reconheça o momento: você espera sentir vontade antes de se mexer.",
 "Diga por dentro: <i>não preciso de vontade; preciso do primeiro movimento</i>.",
 "Pergunte: <i>qual é a versão de dois minutos?</i>",
 "Responda com o menor gesto da obra de hoje: abrir o caderno na página, escrever a primeira frase.",
 "Faça esse gesto.",
 "Se você parar ao fim dos dois minutos, cumpriu a linha.",
 "Se continuar, o <i>isto</i> da frase passa a ser o objeto da linha I.",
 "Se hoje é dia de piso, comece o piso pela versão de dois minutos.",
 "· A permissão de parar é verdadeira. As linhas não se marcam: a marca é só da da vez.",
]
linha("VI", "Da falta de vontade", "Quando nada em você quiser começar.", None,
 ["Não preciso de vontade. Preciso do primeiro movimento.", "Qual é a versão de dois minutos?"],
 "Faça a versão de dois minutos: abra o caderno, calce o tênis, abra o livro na página marcada. Depois disso, você pode parar.",
 ["Esta é a outra linha do dia um. Você se senta, a distração sai da mesa, e nada em você quer começar. Você ainda não trabalhou e tudo pesa, sem objeto preciso. O peso vem com uma frase razoável: <i>não estou com cabeça para isto</i>, ou <i>se começar assim vai sair ruim; espere até ter vontade</i>.",
  "<i>Não preciso de vontade</i> tira da vontade o direito de voto. Ela pode estar presente, e é bem-vinda; já não decide. Se você continuou depois dos dois minutos, repare, sem fazer disso vitória, quando a vontade apareceu: depois que você começou. Nos dias seguintes, observe quantas vezes a permissão de parar fica sem uso.",
  "Piotr Tchaikóvski trabalhou a vida inteira sem esperar a vontade, e disse isso por carta a Nadejda von Meck, a viúva rica que o sustentou durante treze anos e que ele nunca encontrou. Em 1878 ela lhe perguntou se esperava pela inspiração. Ele respondeu que a inspiração é uma visita que não gosta de visitar os preguiçosos; que se sentava ao trabalho todas as manhãs, quisesse ou não; e que quem espera a disposição sem ir ao encontro dela cai depressa na indolência (paráfrase das cartas). Tchaikóvski viveu atormentado pela melancolia e por dúvidas sobre o próprio valor, e por isso o testemunho dele pesa.",
  "Pascal levou a ideia a um lugar mais desconfortável, no fragmento da aposta dos <i>Pensamentos</i>. Ao homem que a razão já convenceu e que mesmo assim não consegue crer, ele responde: faça como os que começaram tomando água benta e mandando dizer missas, como se cressem. Somos autômato tanto quanto espírito, e o costume dobra o que o argumento não alcança. O fim de Pascal era a fé. Aqui o costume serve à obra que você escolheu: o gesto de abrir o caderno, repetido nas manhãs sem vontade, ensina ao corpo o caminho da obra.",
  "O que se sente parece o autêntico, e o resto parece máscara. Aceite a palavra. <i>Persona</i> era a máscara por onde passava a voz do ator, e deu origem a <i>pessoa</i>. Ao escrever sem vontade, você veste a máscara do homem da sua visão, para que o rosto tome a forma dela. A folha do dia zero foi escrita de cabeça fria, durante um dia inteiro; a falta de vontade é um estado de algumas horas. Obedecer ao humor contra a folha é trair o que você escreveu naquele dia."],
 porque=[
  "<b>A ideia.</b> William James contou como se levantava nas manhãs frias: deliberava debaixo das cobertas e, a certa altura, se via com os pés no chão, antes que a mente acabasse de decidir. A vontade chega depois do começo. Quem espera estar disposto para se mexer espera o efeito antes da causa.",
  "<b>O mecanismo.</b> A maior parte da resistência está no começo, e a versão de dois minutos reduz o custo de entrada a quase nada. A permissão de parar tira da falta de vontade o argumento de que o dia inteiro está em jogo. Ela tem de ser verdadeira, ou o espírito não acredita nela. Nenhum estudo testou esta regra; este livro aposta nela pela razão.",
  "<b>Por isso.</b> Faço a versão de dois minutos porque posso mesmo parar depois dela."])

PASSOS["VII"] = [
 "Reconheça o momento: várias coisas pedem atenção, e a comparação entre elas não acaba.",
 "Pergunte por dentro: <i>qual delas eu evitaria, se pudesse?</i>",
 "Diga <i>essa</i>.",
 "Volte à linha I: o que deve existir ao se levantar, e o primeiro movimento.",
 "Comece.",
 "Se há uma urgência real, com prazo, faça-a primeiro. Depois faça a pergunta.",
 "Se a que você escolhe é preparação da obra temida, confira se ainda serve a ela.",
 "· Nenhum desconforto vira dever só por ser desconfortável.",
]
linha("VII", "Da escolha", "Quando muitas coisas pedirem e você não souber qual.", None,
 ["Qual delas eu evitaria, se pudesse?", "Essa."],
 "E volte à primeira linha.",
 ["Esta linha chega com o exercício do terminar, quando as coisas começadas se acumulam. O momento vem de manhã, ou depois de uma interrupção. Cinco coisas pedem atenção ao mesmo tempo. Você anda de uma para outra, abre uma, se lembra de outra, compara. A voz tem o tom de um bom administrador: <i>despacho primeiro as pequenas, para ficar com a cabeça livre</i>, ou <i>antes de tudo, uma lista de prioridades</i>.",
  "A resposta à pergunta vem depressa, e é desagradável. Diga <i>essa</i>, e a comparação acabou.",
  "Charles Darwin teve a ideia central de sua vida no outono de 1838, aos vinte e nove anos. Em 1844 tinha um ensaio de mais de duzentas páginas e deixou à mulher uma carta pedindo que o publicasse se ele morresse. Depois guardou o ensaio. Nos anos seguintes fez de tudo: livros de geologia, a revisão do diário do <i>Beagle</i> e oito anos estudando cracas, até escrever que odiava uma craca como nenhum homem jamais odiara. Tudo era trabalho sério, e tudo o afastava do livro que temia escrever. A Joseph Hooker confessara que dizer que as espécies não são imutáveis era como confessar um assassinato.",
  "Em junho de 1858, chegou pelo correio uma carta de Alfred Russel Wallace, do arquipélago malaio, com um manuscrito curto. Era a mesma teoria. Darwin, que adiara vinte anos, escreveu então em pouco mais de um ano <i>A origem das espécies</i>. Quando há muitas coisas boas a fazer, o adiamento dispensa a preguiça: basta escolher sempre outra coisa boa, e a mais temida fica esperando. A pergunta desta linha teria apontado para a gaveta de Darwin em qualquer manhã daqueles anos.",
  "Há uma velha imagem para a indecisão, o asno de Buridano: igualmente faminto e igualmente distante de dois montes de feno iguais, ele morreria de fome entre os dois. A linha desfaz o asno recusando a igualdade. Entre as coisas que lhe pedem atenção há uma que pesa mais, por assustar mais. Quem está diante de muitas coisas se perde de outro modo: escolhe sempre o monte mais perto, como Darwin escolhia as cracas, e chama isso de prioridade."],
 "A bússola vale entre coisas que importam. Uma urgência real, com prazo, vence.",
 porque=[
  "<b>A ideia.</b> Entre coisas que parecem igualmente boas, a comparação não tem fim natural, porque cada uma tem razões a seu favor. Enquanto se compara, nada se faz, e a mais temida fica esperando.",
  "<b>O mecanismo.</b> A pergunta troca um critério que empata por um que não empata. A importância e a urgência se discutem sem fim; a resistência se sente numa resposta rápida. O que pesa é o que importa, porque o fácil já teria sido feito; e <i>essa</i>, uma palavra, fecha a deliberação. Nenhum estudo testou esta pergunta; este livro aposta nela pela razão.",
  "<b>Por isso.</b> Escolho a que evitaria porque a resistência desempata depressa, e o que pesa é o difícil adiado."])

PASSOS["VIII"] = [
 "Reconheça o momento: você quer começar algo novo já, ou quer saber tudo antes de começar.",
 "Pegue uma folha.",
 "Escreva as quatro perguntas, com uma resposta curta para cada uma.",
 "Marque o prazo da pesquisa antes de abrir a primeira página sobre o assunto.",
 "· Para coisas pequenas, o prazo é uma sessão, uma hora no máximo.",
 "Quando o prazo vencer, faça o primeiro movimento com o que você sabe.",
 "Aprenda o resto no terreno.",
 "Se o que está à frente é a obra já decidida, use a linha I.",
]
linha("VIII", "Da estratégia", "Quando você for começar algo novo: um projeto, um estudo, um ofício, até um passatempo.",
 "<font color='#6b6b6b'><i>“O guerreiro vitorioso vence primeiro, e só depois vai à guerra.” &nbsp;— Sun Tzu</i></font><br/>Nada avulso. Antes de entrar, uma folha e quatro perguntas:",
 ["O que exatamente eu quero com isto?", "Qual é o terreno?", "Qual é o sistema?", "Qual é o primeiro movimento, e até quando pesquiso?"],
 "Marque o prazo da pesquisa antes de abrir a primeira página. Vencido o prazo, faça o primeiro movimento com o que você sabe.",
 ["Esta linha serve desde os primeiros dias, porque ninguém sabe quando vai querer começar uma coisa nova. O momento tem um calor particular: você leu, ouviu ou pensou em alguma coisa e quer começá-la já. A voz é entusiasta: <i>comece hoje, depois você vê</i>. Ou prudente, se você é do outro feitio: <i>antes de começar, preciso saber tudo sobre isto</i>. As duas levam à primeira dificuldade que ninguém previu, ou ao começo que nunca chega.",
  "O impulsivo começa muitas coisas e as abandona na primeira dificuldade, porque não sabia que ela viria. <i>Qual é o terreno?</i> pergunta o que já existe, quem faz isso bem, quais são as regras, e poupa erros que outros já cometeram por você. A quarta pergunta amarra a estratégia ao ato. A estratégia termina num movimento; o adiamento termina em outro plano.",
  "No verão austral de 1911, duas expedições partiram para o polo sul. A do norueguês Roald Amundsen chegou em 14 de dezembro e voltou sem perder um homem. A do inglês Robert Falcon Scott chegou em 17 de janeiro de 1912, encontrou a barraca dos noruegueses e morreu inteira no caminho de volta, a dezoito quilômetros de um depósito de provisões. Coragem não faltou a nenhum dos dois. A diferença esteve no conhecimento do terreno.",
  "Amundsen passara um inverno junto dos inuítes netsilik, no Ártico canadense, e aprendera com eles a vestir peles e a conduzir cães. Copiou os meios de quem já vivia no gelo, sem discuti-los; o fim continuou sendo dele: os netsilik viviam no Ártico, e ele queria o polo. Assim se copiam os meios de quem domina o terreno: os atos que levam aonde você decidiu ir, nunca o fim dele. Para o sul, Amundsen levou cães e esquiadores e marcou os depósitos com fileiras de bandeiras atravessadas na rota. Scott confiou em pôneis, que não aguentaram o frio, e acabou puxando os trenós com a força dos homens.",
  "O próprio caderno começou assim. O dia zero foi a folha de estratégia da sua vida: a anti-visão e a visão disseram o que você quer, as alavancas e a da vez são o sistema, e o dia um é o primeiro movimento. Esta linha é a mesma folha em ponto pequeno."],
 "Pesquisa sem prazo é adiamento. Esta linha vale para o que é novo; para o que já foi decidido, vale a primeira.",
 porque=[
  "<b>A ideia.</b> A frase de Sun Tzu vem de <i>A arte da guerra</i>. Ali o exército vitorioso primeiro se põe em condições de vencer e só depois procura a batalha; o derrotado combate primeiro e procura a vitória depois. A folha das quatro perguntas é essa preparação: o fim, o terreno, o sistema, e o primeiro movimento com o prazo que fecha a pesquisa.",
  "<b>O mecanismo.</b> Fixar o fim antes dos meios impede a deliberação em círculos e separa o objetivo da excitação do começo. O prazo dá à pesquisa um fim que ela não tem por natureza. A pergunta do sistema dá à prática uma hora e um lugar. Wendy Wood mediu que os hábitos são respostas disparadas pelas pistas do contexto: a prática repetida no mesmo lugar e na mesma hora se faz quase sozinha.",
  "<b>Por isso.</b> Escrevo as respostas e marco o prazo porque pesquisa com data acaba, e prática com hora sobrevive ao entusiasmo."])

PASSOS["IX"] = [
 "Reconheça a onda: um desejo súbito do que você cortou, com pressa e com razões prontas.",
 "Diga por dentro: <i>é a onda</i>.",
 "Não responda às razões dela.",
 "Diga: <i>ela sobe, e passa</i>.",
 "Pergunte: <i>o que faço com as mãos agora?</i>",
 "Faça já o gesto que você pôs no lugar do hábito no dia do corte.",
 "Levante-se, mude de cômodo, vá à paixão contrária.",
 "Se o caderno está à mão, leia a frase da anti-visão, na primeira página.",
 "Diga o estribilho.",
 "Quando notar que pensa em outra coisa, não volte a olhar para a vontade. Continue o que as mãos faziam.",
 "Se você obedeceu, escreva à noite <i>caí; a linha continua</i>. Amanhã, nenhuma queda.",
 "· Ver: Livro IV.",
]
linha("IX", "Da onda", "Quando vier a vontade daquilo que você cortou.", None,
 ["É a onda.", "Ela sobe, e passa.", "O que faço com as mãos agora?"],
 "Faça o gesto que você pôs no lugar. Levante-se, mude de cômodo, vá à paixão contrária. Não discuta com a vontade: espere que ela passe, fazendo outra coisa.",
 ["Esta é a última linha, e serve só depois do primeiro corte: deixar de uma vez um hábito que desfaz o que os exercícios fazem. Você a lê agora para conhecê-la antes de precisar dela. Horas ou dias depois do corte, você está fazendo outra coisa e, sem aviso, a vontade do que deixou está ali. Ela vem na hora que o hábito ocupava, num lugar que o lembra, ou no tédio e na contrariedade em que ele era o seu consolo.",
  "A onda começa no corpo antes de chegar às palavras: uma inquietação nas mãos, a atenção que se estreita, o olhar que vai ao lugar onde a coisa estava. Depois chegam as palavras, das mais hábeis que você vai ouvir: <i>só hoje</i>; <i>uma vez não conta</i>; <i>você já aguentou tantos dias, merece</i>; <i>isto não vai passar, mais vale acabar com isto já</i>. A vontade sobe, e tudo nela afirma que vai continuar subindo. Ela chega ao alto e desce. Você percebe isso depois, quando nota que há algum tempo pensa em outra coisa.",
  "Aulo Gélio conta, nas <i>Noites áticas</i>, uma travessia de Corcira para Brindisi. No mar Jônio, de noite, levantou-se uma tempestade, e o navio se encheu de água. Viajava a bordo um filósofo estoico, e Gélio o viu pálido e assustado, embora não gritasse como os outros. Mais tarde, quando Gélio lhe perguntou a sério como um filósofo podia ter tido medo, ele tirou da bagagem um livro dos <i>Discursos</i> de Epicteto e mostrou uma passagem. As impressões do espírito não dependem da vontade. Diante de algo terrível, até o sábio empalidece por um instante, por movimentos rápidos que se antecipam à razão. O sábio não aprova essas impressões; o insensato as aprova e as confirma com seu juízo.",
  "O filósofo empalidecera e não se envergonhava disso. O que ele não fizera era concordar com a palidez. Quando a vontade do que você cortou vier e o corpo inteiro a pedir, não conclua, por sentir, que o corte falhou. Você estará no lugar do filósofo no navio, abalado e sem obedecer.",
  "Sêneca, no segundo livro <i>Da ira</i>, chama isso de primeiros movimentos: o arrepio de quem é salpicado de água fria, o cabelo que se eriça com uma má notícia, a vertigem de quem olha de um precipício. O primeiro movimento não se evita; o segundo, o consentimento, sim, e é nele que mora a responsabilidade. A onda é um primeiro movimento. <i>É a onda</i> é a frase de quem o reconhece como tal, sem confundi-lo com uma decisão já tomada.",
  "Quem reprime está tenso, de olhos fixos na vontade. Quem atravessa a onda admite que ela está ali, dá nome a ela e tem as mãos ocupadas em outra coisa."],
 "Quando a onda não passa, ou passa e vence sempre, vale aqui a nota com que fecha o Livro IV.",
 porque=[
  "<b>A ideia.</b> Alan Marlatt, psicólogo que estudou recaídas nas dependências, descreveu a vontade de voltar a um hábito como uma onda: sobe, chega a um pico e desce em minutos, embora, enquanto sobe, pareça que vai subir para sempre. Ele ensinou a <i>surfar o impulso</i>: observá-lo no corpo, sem obedecer e sem lutar, até que passe.",
  "<b>O mecanismo.</b> Chamar a vontade de onda a trata como um estado que passa: você não precisa vencê-la, só não obedecer a ela durante alguns minutos. Há indícios a favor: num estudo de Sarah Bowen e Marlatt com estudantes fumantes, quem aprendeu a observar a vontade fumou menos nos sete dias seguintes. As mãos ocupadas dão à atenção outro objeto.",
  "<b>Por isso.</b> Faço o gesto que pus no lugar porque, com as mãos ocupadas, a vontade desobedecida passa em minutos."])

sec("Da ordem das linhas")
add("Uma linha está aprendida quando você a percebe em si sem ter precisado se lembrar dela. Na primeira passagem, você terá dito a primeira e a sexta linhas dezenas de vezes, e algumas vezes elas terão funcionado sem que você percebesse. Outras vezes, não. Você vai começar bem às nove e largar às dez; voltar de uma dispersão para cair em outra; ter um dia em que as frases vêm sozinhas e, no seguinte, nenhuma.", PI)
add("Baudelaire conheceu essa irregularidade por dentro. Nos cadernos íntimos, em páginas que chamou de <i>Higiene</i>, escritas por volta de 1862, ele jura tomar por regras eternas coisas simples: trabalhar todos os dias e preferir o trabalho imediato, mesmo ruim, ao devaneio. Escreve que uma série de pequenas vontades faz um grande resultado (paráfrase). O homem que escreveu isso refez poemas d’<i>As flores do mal</i> verso a verso durante anos; sabia governar o instante. O que nunca teve foi o dia. Mudava de quarto para fugir dos credores, perdia semanas, e as mesmas resoluções voltam nos cadernos com as mesmas palavras. Tinha as frases certas, e faltava a elas uma moldura que as trouxesse de volta todas as manhãs.", PI)
add("As linhas governam o instante, e o dia é feito também do que liga os instantes: a hora em que se acorda, o que se faz primeiro, o que se marca à noite, o que acontece depois de uma queda, quando se dorme. Um instante bem governado num dia sem forma se perde como uma frase certa numa conversa confusa. Os instantes precisam de uma moldura: uma lei que diga o que nunca se faz, e um dia que diga quando cada coisa acontece. É dela que trata o livro seguinte.", PI)


# ===================== LIVRO II =====================
livro("II", "Da lei e do dia")

add("As leis e o dia arrumam o tempo em volta da obra, para que, na hora em que você se sentar, tenha uma coisa só à frente e nada que a interrompa. A assentada precisa de um dia assim para caber.", PI)
proc("Como ler este livro", [
 "Na noite do dia zero, leia <i>Do dia</i>, de <i>De manhã</i> até o fim de <i>À noite</i>.",
 "Leia cada lei na noite em que o livro a citar. Leia as nove antes da primeira passagem.",
 "Leia <i>Do piso</i>, <i>Do descanso</i> e <i>Do bloco de obra</i> na manhã em que o estado do dia os chamar.",
 "· Você sai deste livro fazendo a manhã e a noite sem abri-lo.",
])
add("Por volta do ano 529, num monte entre Roma e Nápoles, Bento de Núrsia reuniu alguns monges sobre as ruínas de um templo antigo e escreveu uma regra para eles. Deu-lhes duas coisas que quem tenta mudar sozinho não tem: umas poucas leis que não se discutem, e um horário que diz quando cada coisa acontece. O monge de Monte Cassino não decidia a cada manhã se ia rezar, nem lembrava a que horas: a lei o poupava da deliberação, e o sinal o poupava da memória. Quinze séculos depois, a regra ainda governa mosteiros.", PI)
add("Este ponto do caminho é plano e longo, e nele você aprende a andar todos os dias no mesmo passo. Ele lhe dá o que Bento deu aos monges: nove leis, curtas, para serem lembradas sem esforço e cumpridas sem discussão; o dia, com seus momentos fixos; e o que sustenta os dois: o descanso, o piso, o bloco de obra e a companhia dos livros. Quando uma lei lhe parecer dura, procure o que ela protege: é o que se perdeu nas tentativas anteriores.", PI)
st.append(CondPageBreak(5*cm))  # a § 1 não se parte; sem isto o título fica sozinho no pé da página
sec("Da lei")
add("Uma lei, neste livro, é uma frase que não se discute durante o dia: ela se discute aqui, uma vez, de cabeça fria. Cada uma vem em negrito, para que você a encontre depressa quando estiver cedendo. Embaixo vêm <i>Do porquê</i>, com a ideia, o mecanismo e a frase que você diz ao cumpri-la; o quadro com o que fazer; e a história de onde ela vem.", PI)
leis = [
 ("Uma só microação nova de cada vez, e na ordem.",
  "A ordem é a dos exercícios, e a que está em treino é a da vez.",
  ["A da vez é a da ordem, e a ordem parece pouco: tirar o que distrai ao sentar, dois minutos ao levantar. No terceiro ou no quarto dia, folheando o Livro III, vem a vontade de somar outra coisa: o treino, uma hora de leitura, a primeira hora do dia longe das distrações. Com ela vem a frase <i>isto é pouco, posso mais</i>. É a essa frase que esta lei responde.",
   "Em Filadélfia, por volta de 1730, um tipógrafo de vinte e poucos anos chamado Benjamin Franklin decidiu chegar à perfeição moral e logo descobriu a dificuldade: enquanto vigiava uma falta, outra o surpreendia. Escolheu então treze virtudes e deu a cada uma, por uma semana, atenção estrita, deixando as outras à sorte de costume. Comparou-se ao jardineiro que não tenta arrancar de uma vez todas as ervas daninhas: limpa um canteiro e só passa ao seguinte quando termina. Franklin dava a cada virtude uma semana certa; este livro não dá prazo a nenhuma microação, e a seguinte só entra quando a da vez chegou. <font color='#6b6b6b'>(Lição I)</font>",
   "A ordem de Franklin não era arbitrária. A temperança vinha primeiro porque dá a clareza de cabeça de que as outras precisam. A ordem deste livro segue o mesmo princípio: a ordem vem antes do terminar, o terminar antes da prática deliberada, e a crítica só vem quando há obra para criticar.",
   "Se alguma tentativa antiga sua começou com quatro gestos de uma vez, num primeiro de janeiro, você conhece o desenho. Na primeira semana o entusiasmo paga a conta de todos os gestos. Na segunda, um falha, e a falha contamina os outros, presos ao mesmo fio: <i>se o dia já falhou num ponto, por que não nos restantes?</i> No fim do mês não resta nenhum dos quatro."]),
 ("Percebeu, aja, antes que se forme a segunda frase interior.",
  "Quem age antes da segunda frase não precisa vencê-la, porque ela não chegou a existir.",
  ["Você acorda, e a primeira frase vem limpa: <i>levante-se</i>. A segunda vem logo atrás: <i>cinco minutos</i>. Se você lhe dá o assentimento, vem uma terceira, <i>já que vai se atrasar, abra o caderno depois</i>, e uma quarta, <i>a linha da manhã se escreve no almoço</i>. Cada uma é mais razoável que a anterior, porque parte da derrota da outra como de um fato consumado. Às oito, o dia foi decidido por uma fileira de concessões que, sozinhas, pareciam nada.",
   "Em Atenas, no Pórtico Pintado, Zenão de Cício ensinava essa diferença com a mão; Cícero conta a cena. Zenão mostrava a mão aberta, os dedos estendidos: assim é a impressão. Dobrava um pouco os dedos: assim é o assentimento. Fechava o punho: assim é a compreensão. O que aparece no espírito não está em nosso poder. Dobrar os dedos está.",
   "A segunda frase interior é um pedido de assentimento. <i>Mas talvez depois</i> chega como proposta razoável, numa voz parecida com a sua, e espera que os dedos se dobrem. O exame foi feito de manhã, quando você escolheu o gesto. Agir na primeira frase é não reabrir no instante o que você decidiu de cabeça fria, como Ulisses, que se fez amarrar ao mastro antes de ouvir as sereias."]),
 ("A vontade não é condição. Sem ela, faz-se igual.",
  "Quando a vontade vem, ela ajuda (sexta linha); quando não vem, o que há para fazer continua o mesmo.",
  ["No Liceu, Aristóteles chamava de <i>héxis</i> a disposição que os atos repetidos deixam em quem os pratica. O prazer que acompanha um ato é o sinal da disposição já formada: quem se abstém dos prazeres do corpo e se alegra com isso é temperante; quem se abstém e se aborrece ainda não é. A vontade de agir chega no fim, como sinal de que a disposição nasceu. Pedi-la antes é exigir, como condição para começar, o que só a repetição produz. Com a mesma régua se mede a frieza com que você veste a máscara: ela é necessária enquanto o gesto custa.",
   "Se você deixar a vontade decidir, a folha de marcas mostra o resultado em poucas semanas: os traços agrupados nos dias de ânimo, as cruzes espalhadas pelos outros, e nenhum <i>chegou</i>. A disposição que se forma assim é a de agir só quando se tem vontade."]),
 ("Você falhou: o próximo momento é seu. Nada se compensa; nada volta ao começo.",
  "Compensar é fazer em dobro amanhã; voltar ao começo é declarar perdidos os traços que você já marcou. A lei recusa os dois.",
  ["Siga o que acontece se você obedecer à primeira frase. Você falha numa terça a hora de leitura que pôs entre as alavancas. Na quarta, para compensar, lê duas horas e se deita tarde. Na quinta, sem forças, falha de novo, agora com uma dívida de três horas. No domingo você faz a conta das culpas, quase não vê os traços, e a saída mais limpa que encontra é a da segunda frase: declarar o caderno perdido e recomeçar na segunda. Assim terminam muitas tentativas.",
   "Nos séculos em que o Templo estava de pé, o Dia da Expiação era o dia do jejum de todo o povo. Os mestres da Mishná escreveram, no tratado sobre esse dia, uma regra de exatidão notável: o Dia da Expiação apaga as faltas do homem para com Deus, e não apaga as faltas para com o próximo enquanto o próximo não tiver sido apaziguado. O rito não substitui o ato de ir até quem foi ferido.",
   "Dessa regra sai a distinção de que esta lei precisa. Compensar é pagar ao caderno, sozinho, à noite, para que a folha fique bonita, e por isso engana. Reparar é responder a quem sua falha atingiu, e exige o outro. A reparação se faz no próximo momento, que é o que esta lei lhe dá. A cruz fica onde está.",
   "Marco Aurélio lembrava que ninguém perde outra vida senão a que está vivendo agora <font color='#6b6b6b'>(<i>Meditações</i>, II, 14)</font>. O dia de ontem, com a falha dele, já não se pode perder nem ganhar de novo, e por isso não há nada a pagar por ele. Nenhum prazo se perdeu, porque não havia nenhum: a da vez continua sendo a da vez, e espera seu <i>chegou</i> como esperava antes."]),
 ("Nunca dois dias seguidos de queda.",
  "Queda é uma cruz ou, numa das que ficaram, ceder na ocasião. O ponto não separa: cruz, ponto, cruz contam como duas seguidas. No dia seguinte a uma cruz, a da vez é sagrada e, se for preciso, cumpre-se o piso.",
  ["Na manhã seguinte à primeira cruz, ao abrir o caderno, fala uma voz que você já ouviu em outras tentativas: <i>já há uma cruz, que diferença faz outra?</i> Foi assim que ela falou à mulher de <i>Do primeiro dia</i>, e a mulher fez o que a lei pede. Se a segunda cruz vier mesmo assim, a lei foi quebrada, e o caminho continua, porque nada volta ao começo.",
   "No primeiro livro da <i>Ética a Nicômaco</i>, Aristóteles recorre a um provérbio: uma andorinha não faz a primavera, nem um só dia. Escreveu isso para conter o entusiasmo de quem julga que um bom ato basta. Lido ao contrário, o provérbio contém o desespero. Uma cruz também é um dia só, e não faz de você alguém sem disposição. O que forma a disposição contrária é a repetição, e a repetição começa no segundo dia. Por isso a lei é tolerante com o primeiro e guarda a manhã seguinte.",
   "O número dois foi escolhido pelo método; nenhum estudo o descobriu. Três seria mais confortável. O livro ficou com o menor número que ainda separa o acidente do começo de um costume, porque é o único que põe a manhã seguinte inteira sob a lei."]),
 ("Nada se abre antes que o anterior se feche. Um livro por vez, até a última página.",
  "Fechar quer dizer terminar, ou encerrar por decisão, por escrito, com a razão. O que não se pode é deixar a coisa aberta, pesando em silêncio.",
  ["O momento desta lei vem fora da obra, no fim do dia: a vontade de começar um livro novo, com o anterior marcado pela metade na mesa de cabeceira. Quando a coisa nova chegar durante a obra, o gesto treinado para ela é a segunda microação, a do terminar. Até lá, você tem esta lei, a folha de captura e a frase que reconhece a coisa nova sem discuti-la: ela não é <i>isto</i>.",
   "Sêneca, já passado dos sessenta anos e retirado da corte de Nero, previne Lucílio, na segunda carta, contra a inquietação das leituras. Ler muitos autores tem algo de vago e instável; é preciso demorar-se em certos espíritos e alimentar-se deles. Quem passa a vida viajando tem muitos anfitriões e nenhum amigo. O alimento devolvido logo não nutre. A planta mudada de lugar a toda hora não ganha força. Na sua mesa de cabeceira, o livro novo é mais um anfitrião, e o que está marcado pela metade é o que ainda pode ficar.",
   "Samuel Taylor Coleridge deu a esta lei a demonstração contrária. Tinha talento para várias vidas e anunciou obras para outras tantas, sobretudo uma grande obra de filosofia de que falou durante décadas. Começava, prometia, abria outra coisa. Quando morreu, em 1834, essa obra era um monte de fragmentos. Cada obra nova que ele abria tirava força das que já estavam abertas, e a que ele mais queria ficou em pedaços."]),
 ("Fala-se do que está feito, nunca do que se fará.",
  "Anunciar um plano também expõe a obra ao olhar dos outros antes de ela estar pronta para isso. Pedir ajuda ou crítica sobre a obra faz parte da obra. <font color='#6b6b6b'>(Epicteto, <i>Manual</i>, 46)</font>",
  ["A primeira conversa depois do dia zero: alguém pergunta como você vai, e dá vontade de contar o dia, a folha, a visão, o alvo do ano. Você pode dizer que passou um dia escrevendo, porque isso está feito. O que você decidiu nesse dia fica no caderno.",
   "Epicteto, na passagem que esta lei cita, pede ao discípulo que nunca se chame de filósofo e não discorra sobre princípios diante de quem não os pratica; que faça, antes, o que deles decorre. E dá a imagem das ovelhas: elas não vomitam a erva diante do pastor para mostrar quanto comeram; digerem-na por dentro e dão por fora lã e leite. O plano contado é a erva devolvida. A obra feita é a lã."]),
 ("O quarto é para dormir: nada que distraia entra nele à noite. O sono, de sete a oito horas, não se negocia.",
  "Um homem sem dormir negocia consigo mesmo o dia inteiro, e dormir pouco não tem mérito nenhum. Por isso a disciplina de cada dia começa na noite anterior.",
  ["A regra de Bento era escrita para monges que se levantavam de noite para rezar, e seria de esperar que tratasse o sono como inimigo. Ela faz o contrário. Fixa a hora de levantar para que os irmãos repousem um pouco mais da metade da noite e se levantem com a digestão feita. Manda que cada um durma na própria cama, vestido, para estar pronto ao sinal. E, depois das Completas, a última oração do dia, ninguém mais fala.",
   "A regra tira a conversa do dormitório em vez de pedir ao monge força para resistir a ela. É o princípio desta lei: à noite, com sono, ninguém vence o que tem ao alcance da mão. Quando a lei se quebra, quebra sem barulho. Você fica acordado mais uma hora, e depois outra. Na manhã seguinte a primeira linha custa o dobro, a segunda frase interior chega mais forte e, às quatro da tarde, tudo se negocia. A cruz que vem disso é posta na conta da fraqueza."]),
 ("Este método não se emenda no meio do caminho: só numa passagem.",
  "A emenda se faz por escrito, com base nas marcas. A lei vale também para a folha do dia zero, e o domínio só é revisto numa passagem.",
  ["O momento desta lei vem no quinto ou no sexto dia. A da vez já não é novidade, o gesto ainda não chegou, e você vê, ou julga ver, um defeito: a ocasião mal escolhida, uma alavanca longa demais, uma marca que deveria contar de outro modo. A mulher de <i>Do primeiro dia</i> viu um no oitavo dia e o escreveu na folha de captura sem mudar nada.",
   "O caminho entre duas passagens é a sua moral provisória: não há outra maneira de saber se a ocasião e o gesto estão errados. Quem emenda a cada dificuldade troca o gesto no quinto dia, alarga a ocasião no nono, muda a maneira de marcar no décimo segundo. Depois de duas semanas tem um método melhor no papel e nenhuma marca que diga coisa alguma, porque cada traço foi medido com uma régua diferente."]),
]
PROC_LEIS = [
 ("A da vez", [
  "Treine uma microação por vez: a da vez.",
  "Siga a ordem dos exercícios do Livro III.",
  "Se vier a vontade de somar outro gesto, note a frase: <i>isto é pouco, posso mais</i>.",
  "Não some nada. O exercício seguinte entra quando a da vez chegar.",
  "Continue as que ficaram, cada uma na sua ocasião, sem marca própria.",
  "· Nunca há mais de uma da vez, nem quando uma das que ficaram volta à folha de marcas.",
  "· Ver: <i>Da medida</i>.",
 ]),
 ("A primeira frase", [
  "Quando vier a primeira frase, <i>levante-se</i> ou <i>comece</i>, aja nela.",
  "Se vier a segunda, <i>cinco minutos</i> ou <i>depois</i>, não lhe dê assentimento.",
  "Se a segunda traz um fato, verifique-o em segundos: olhe, toque, pergunte.",
  "Se o fato se confirma, faça já o que cabe nele. O joelho que dói decide o tamanho da corrida.",
  "Se falta um dado que só outra pessoa tem, comece pelo passo que não depende dele.",
  "· Para o que é novo e grande, use a linha VIII.",
 ]),
 ("Sem vontade", [
  "Se vier <i>hoje não estou com vontade</i>, note a frase antes de obedecer.",
  "Diga a linha VI e faça a versão de dois minutos.",
  "Se, três manhãs seguidas, nem a obra nem o que antes dava gosto veio por vontade, declare piso.",
  "Se isso dura sete dias seguidos ou mais, leia <i>Do escrúpulo</i>.",
 ]),
 ("Na noite da cruz", [
  "Marque a cruz.",
  "Escreva a linha da queda.",
  "Se vier <i>amanhã faço em dobro</i>, não faça em dobro.",
  "Se vier <i>estragou tudo; recomeço na segunda</i>, não recomece. Os traços continuam valendo.",
  "Se a falha atingiu alguém, vá até essa pessoa e diga o que falhou, sem discurso.",
  "Faça por ela o que ainda cabe: a parte entregue hoje, a leitura amanhã.",
  "Deixe a cruz onde está.",
  "Tome o próximo momento.",
 ]),
 ("Dia sagrado", [
  "Na manhã depois de uma cruz, cumpra a da vez, com o piso do exercício se preciso.",
  "Não declare dia de ócio nesse dia.",
  "Se vier <i>já há uma cruz, que diferença faz outra?</i>, cumpra o gesto assim mesmo.",
  "Conte cruz, ponto, cruz como duas cruzes seguidas.",
  "Se você está de cama, declare o piso de manhã.",
  "Se a ocasião não chega porque você não sai da cama, marque ponto.",
  "Se ela chega e você não consegue, marque cruz.",
  "No dia seguinte a essa cruz, faça o gesto uma vez, mesmo da cama.",
 ]),
 ("Fechar", [
  "Antes de abrir um livro ou uma obra nova, feche o anterior.",
  "Feche terminando, ou encerrando por decisão: uma linha escrita, com a razão.",
  "Se o livro é ruim, feche-o assim, por escrito, com a razão.",
  "Se a coisa nova chega durante a obra, escreva-a numa linha na folha de captura.",
  "· Dicionário, manual de consulta e texto exigido pelo emprego ficam fora desta lei.",
 ]),
 ("Falar", [
  "Se perguntarem como você vai, conte o que está feito.",
  "Guarde no caderno o que você decidiu fazer.",
  "Ao parceiro que cobra, leve as marcas da folha, a passagem que veio, a obra entregue.",
  "Leve as cruzes à vista.",
  "Não leve o plano do que virá.",
  "Peça ajuda ou crítica sobre a obra quando precisar.",
 ]),
 ("O quarto", [
  "Depois de fechar o caderno, deixe fora do quarto tudo o que distrai.",
  "Deite-se numa hora que deixe sete a oito horas até acordar.",
  "Se uma noite não foi assim, mude hoje o lugar onde a distração dorme.",
  "Se um filho pequeno acorda à noite, deite-se mais cedo.",
  "Divida as noites com quem as compartilha com você.",
  "Se você trabalha em turnos, guarde o quarto nas horas do seu sono, caiam quando caírem.",
  "· Levantar-se para um filho é circunstância. Negociar o sono consigo mesmo é o que a lei proíbe.",
 ]),
 ("Antes de emendar", [
  "Se você vê um defeito no método entre duas passagens, escreva-o na folha de captura.",
  "Escreva a data e a razão.",
  "Não mude nada.",
  "Na próxima noite de passagem, confira a observação com as marcas.",
  "Se as marcas a confirmam, emende por escrito.",
  "Se a prática fere a sua saúde ou quem depende de você, leia o Livro V.",
  "Se a passagem não vem, use a passagem por decisão.",
  "· Ver: <i>Da medida</i>.",
 ]),
]
LAWT = ParagraphStyle('lawt', parent=P, fontSize=12, leading=16, spaceBefore=10, spaceAfter=3, keepWithNext=1)
PORQUE_LEIS = [
 ["<b>A ideia.</b> Um gesto novo, enquanto não é hábito, só acontece se for lembrado na ocasião, e lembrar gasta atenção.", "<b>O mecanismo.</b> Dois gestos novos disputam a mesma atenção, e a memória falha na ocasião em que se precisa dela. Um gesto leva tempo para se tornar automático: um estudo de Phillippa Lally encontrou de três semanas a mais de meio ano. Quem junta quatro gestos tem quatro coisas a lembrar durante meses, e o entusiasmo dos primeiros dias não basta para tanto.", "<b>Por isso.</b> Treino um gesto por vez porque na ocasião só lembro de um, e cada um leva semanas."],
 ["<b>A ideia.</b> Esta lei é uma regra de pré-compromisso: escolher de cabeça fria de modo a restringir as escolhas do momento fraco. A primeira frase interior, <i>tenho de começar</i>, lembra a decisão; a segunda, <i>mas talvez depois</i>, propõe reabri-la.", "<b>O mecanismo.</b> O gesto foi decidido de manhã, com a ocasião prevista. Quando a ocasião chega, não há nada novo a examinar, e qualquer exame reabre o que estava fechado. Cada concessão torna a seguinte mais razoável. Agir na primeira frase corta a fileira antes que ela comece.", "<b>Por isso.</b> Ajo na primeira frase porque o gesto está decidido, e a primeira concessão abre a fileira."],
 ["<b>A ideia.</b> O gosto de agir chega no fim, como sinal de que a disposição já se formou, e por isso não pode ser condição para começar.", "<b>O mecanismo.</b> O humor muda de uma manhã para outra por razões que nada têm a ver com a obra. O que se repete fica ligado àquilo que o dispara: os estudos de Wendy Wood mostram que os hábitos são respostas a pistas do contexto, independentes da intenção do momento. O gesto feito na ocasião, com ou sem vontade, se liga à ocasião; o gesto feito só com vontade se liga à vontade.", "<b>Por isso.</b> Faço igual sem vontade porque a vontade vem depois da repetição, e o gesto repetido se prende à ocasião."],
 ["<b>A ideia.</b> Sêneca observa, em <i>Da brevidade da vida</i>, que das três partes do tempo o passado é a única certa: a fortuna já não tem poder sobre ele. A falha de ontem não se desfaz, e os traços de ontem também não. O que depende de você é o próximo momento.", "<b>O mecanismo.</b> Compensar faz da falha uma dívida, e a dívida se paga com excesso e nova falha, até que abandonar parece a saída limpa. Há indícios do contrário: num estudo de Juliana Breines e Serena Chen, quem se tratou com compreensão depois de um mau resultado estudou mais para o teste seguinte. Recomeçar do zero apaga o registro dos traços, e está demonstrado que registrar o progresso aumenta a chance de chegar ao objetivo; Benjamin Harkin e colegas reuniram esses estudos.", "<b>Por isso.</b> Não compenso nem recomeço porque a dívida acaba em abandono, e os traços já marcados continuam contando."],
 ["<b>A ideia.</b> Uma queda isolada não forma a disposição contrária; duas seguidas já são o começo de uma repetição.", "<b>O mecanismo.</b> A severidade cai sobre o único dia em que ainda é barato frear a repetição: depois da segunda cruz, a terceira custa menos. A manhã seguinte à queda traz a voz mais perigosa, <i>já há uma cruz, que diferença faz outra?</i> Alan Marlatt observou, em quem tinha deixado um hábito, que uma queda decidia pouco por si; decidia o que a pessoa dizia a si mesma logo depois. Nenhum estudo testou esta lei; este livro aposta nela pela razão.", "<b>Por isso.</b> Cumpro a da vez na manhã depois de uma cruz porque duas quedas seguidas começam a repetição contrária."],
 ["<b>A ideia.</b> Começar dá prazer, e terminar custa. Quem tem muitas coisas abertas escolhe sempre o prazer de começar, adia sempre o custo de terminar, e fica com muitas obras pela metade e nenhuma inteira.", "<b>O mecanismo.</b> Cada coisa aberta pede para ser lembrada, e cada pedido é uma pequena saída da obra; fechar, terminando ou encerrando por escrito, cala esse pedido. Alternar entre várias obras custa tempo e erros a cada troca.", "<b>Por isso.</b> Fecho antes de abrir porque o que fica aberto me puxa, e cada troca custa tempo e erros."],
 ["<b>A ideia.</b> Os objetivos que dizem quem queremos ser se alimentam de sinais de que se está chegando lá, e ser visto declarando a intenção já conta como um desses sinais. O espírito registra a intenção anunciada como em parte conquistada, e afrouxa.", "<b>O mecanismo.</b> O anúncio dá antes do tempo uma parte da satisfação que só a obra deveria dar. Há indícios disso: em 2009, Peter Gollwitzer e colegas viram que estudantes cuja intenção foi anotada por outra pessoa trabalharam menos e se sentiram mais perto da meta. O que está feito é um fato que outro pode verificar, e mostrá-lo ajuda.", "<b>Por isso.</b> Falo do que fiz e calo o que farei porque o plano anunciado já me satisfaz como feito."],
 ["<b>A ideia.</b> A lei protege duas coisas: a quantidade, sete a oito horas, e o quarto, onde nada que distraia entra à noite. Do sono depende o resto, porque a falta dele corrói primeiro o juízo e depois a vontade.", "<b>O mecanismo.</b> O sono curto degrada a atenção sem que se perceba. Num estudo de Hans Van Dongen e David Dinges, catorze noites de seis horas produziram déficits de atenção iguais aos de uma a duas noites sem dormir, e os participantes subestimaram o próprio déficit. À noite, com sono, o que está ao alcance da mão leva a melhor; por isso a distração tirada do quarto vale mais do que a força para resistir a ela.", "<b>Por isso.</b> Durmo as sete a oito horas, sem distração no quarto, porque dormir pouco me rouba atenção sem aviso."],
 ["<b>A ideia.</b> É a moral provisória de Descartes, que <i>Da floresta</i> lhe contou: a ocasião e o gesto que você definiu valem como certos até as marcas dizerem o contrário.", "<b>O mecanismo.</b> Só uma régua fixa permite saber se um gesto funciona; um gesto leva semanas, ou meses, para chegar. O dia em que a prática custa é aquele em que o defeito parece mais claro, e a dificuldade se apresenta como prova de erro. A observação escrita espera a passagem e então é confrontada com as marcas, que a desmentem com frequência. Nenhum estudo testou esta lei; este livro aposta nela pela razão.", "<b>Por isso.</b> Escrevo o defeito e espero a passagem porque, no dia em que a prática custa, eu julgaria o método pelo peso do dia."],
]
assert len(PORQUE_LEIS) == len(leis) == len(PROC_LEIS)
for i, ((l, e, mais), pq, (pt, pl)) in enumerate(zip(leis, PORQUE_LEIS, PROC_LEIS), 1):
    st.append(KeepTogether([Paragraph(f"§ {i}. &nbsp;<b>{l}</b>", LAWT), Paragraph("D O &nbsp; P O R Q U Ê", LBL), Paragraph(pq[0], PI)]))
    for par in pq[1:]: add(par, PI)
    add(e, PI)
    proc(pt, pl)
    for par in mais:
        add(par, PI)

sec("Do dia")
st.append(KeepTogether([Paragraph("<i>“Omnes horas complectere.”</i>", ParagraphStyle('r3dia1', parent=PC, fontSize=12, spaceAfter=2)),
                        Paragraph("Sêneca, <i>Cartas a Lucílio</i>, 1", ParagraphStyle('r3dia2', parent=EPA, spaceAfter=14))]))
add("A frase latina no alto é de Sêneca e quer dizer <i>abrace todas as horas</i>: tome posse de cada hora do dia, em vez de deixá-la passar sem perceber. Você dependerá menos do amanhã, escreve ele na carta do estribilho, se puser a mão no dia de hoje; enquanto se adia, a vida passa correndo.", PI)
add("Num monte da Galileia, o sermão que o Evangelho de Mateus conta chegou ao mesmo ponto por outro caminho. Depois de mandar olhar as aves do céu e os lírios do campo, fecha assim: não vos inquieteis com o dia de amanhã, porque o dia de amanhã cuidará de si; basta a cada dia o seu mal <font color='#6b6b6b'>(Mateus 6, 34)</font>. Um estoico rico e um pregador da Galileia concordam nisto: a unidade em que a vida se pode segurar é o dia.", PI)
add("Por isso este livro não tem semanas nem prazos. A direção foi escrita no dia zero: a visão, o alvo e a obra em curso, relidos em cada passagem. Todas as manhãs a obra de hoje desce da obra em curso, e cada dia traz a direção inteira, reduzida ao tamanho de uma linha. A semana só acrescentava um prazo mais largo e, com ele, mais espaço para adiar.", PI)
add("O seu dia tem três momentos: a manhã, o tempo que corre entre ela e a noite, e a noite. A manhã e a noite pedem o caderno, cerca de dez minutos cada uma. Enquanto um exercício é a da vez, a noite ganha a escrita curta que ele pedir. No resto do tempo você vive, e o método se cumpre nas ocasiões que esse tempo traz. Quando um gesto chega, a noite se alonga um pouco: é a passagem.", PI)
add("Franklin, na <i>Autobiografia</i>, copiou o horário que se impunha. Levantava-se às cinco e, no alto das primeiras horas, escreveu uma pergunta: <i>Que bem farei hoje?</i> No alto das horas da noite, a pergunta gêmea: <i>Que bem fiz hoje?</i> Confessou que a ordem foi a virtude que mais lhe custou. As duas perguntas são as duas pontas do seu dia: a linha da manhã, que diz a obra, e a linha do dia, que pergunta o que existe agora que não existia.", PI)
add("A obra de hoje é o objeto do dia: a coisa que existirá à noite e de manhã não existe. A primeira tarefa é o primeiro passo dessa obra, o que você evitaria, escolhido na noite anterior e confirmado de manhã.", PI)
proc("Se a obra não cabe na manhã", [
 "Se o emprego ocupa as horas até a noite, faça de manhã primeiro o que você evitaria no emprego.",
 "Comece a obra na hora dela, pelo passo que deixou escrito na véspera.",
 "Se você trabalha à noite e acorda às duas da tarde, faça a manhã nessa hora.",
 "· Exemplo: <i>A obra de hoje é o mês de março lançado e conferido</i>, às nove da noite.",
])
MOM = ParagraphStyle('mom', parent=HEAD, fontSize=12.5, spaceBefore=14)
st.append(Paragraph("De manhã &nbsp;<font size=10 color='#6b6b6b'>cerca de dez minutos, antes de qualquer distração</font>", MOM))
add("Você lê isto na noite do dia zero. Os passos começam na manhã do dia um.", PI)
proc("Passos da manhã", [
 "Abra o caderno antes de qualquer outra coisa.",
 "Se abriu outra coisa antes, feche-a já. Amanhã o caderno vem primeiro.",
 "Diga o estribilho, uma vez, em voz baixa, com os colchetes calados.",
 "Escreva a linha da manhã: <i>Posso morrer hoje. A obra de hoje é ____.</i>",
 "Escreva como obra de hoje um objeto que existirá à noite, tirado da obra em curso.",
 "Se você escreveu uma intenção, como <i>trabalhar no projeto</i>, corte-a até virar um objeto.",
 "Se você anda frágil, escreva <i>O meu tempo é limitado</i> no lugar da primeira metade.",
 "Leia no breviário a linha da da vez.",
 "Percorra o dia por dentro e escolha a ocasião que vai pesar mais.",
 "Escreva a hora de parar.",
 "Confira o estado do dia, no quadro abaixo.",
 "Confirme a primeira tarefa escrita ontem.",
 "Feche o caderno e vá à primeira tarefa.",
 "Se uma urgência chega antes, como um filho que chora, atenda-a. Abra o caderno logo depois.",
])
proc("O estado do dia", [
 "Confira nesta ordem. Pare no primeiro sim.",
 "Se o caderno tem <i>suspenso</i> escrito e não foi retomado, o dia está suspenso.",
 "Se um sinal de <i>Do escrúpulo</i> está presente há sete dias seguidos ou mais, leia <i>Do escrúpulo</i>.",
 "Se ontem à noite você declarou hoje dia de ócio por escrito, hoje é dia de ócio.",
 "Se há febre ou doença que impede sentar à mesa da obra, é dia de piso.",
 "Se uma viagem tira você de casa antes da hora da obra, ou ocupa o dia em deslocamento, é dia de piso.",
 "Se uma prova, um plantão ou um compromisso marcado por outro ocupa as horas da obra, é dia de piso.",
 "Se alguém da casa está doente ou em crise e precisa de você hoje, é dia de piso.",
 "Se hoje está entre o primeiro e o último dia de um bloco de obra, é dia de bloco.",
 "Se hoje está na semana depois do último dia do bloco, é dia de descarga.",
 "Se nada disso, é dia comum.",
 "Em qualquer estado, se ontem foi cruz, hoje é também dia sagrado.",
 "Se é dia de piso, escreva agora <i>hoje, piso</i>. Não declare piso à tarde.",
 "· Falta de vontade, uma noite mal dormida e o humor não fazem dia de piso.",
 "· Ver: <i>Do piso</i>; <i>Do descanso</i>; <i>Do bloco de obra</i>.",
])
add("A primeira metade da linha da manhã lembra que o tempo é limitado; a segunda diz em que este dia se gasta. Marco Aurélio recomendava regular cada ato como quem pode deixar a vida a qualquer momento: quem sabe que o dia pode ser o último não o gasta com o que não importa. Os estoicos faziam dessa lembrança um exercício diário, e Epicteto pede no <i>Manual</i> que a morte esteja todos os dias diante dos olhos.", PI)
add("Marco Aurélio começava o dia prevendo o intrometido e o ingrato que ia encontrar, para responder a eles como tinha decidido de manhã <font color='#6b6b6b'>(<i>Meditações</i>, II, 1)</font>. Você prevê o momento em que o gesto vai ser posto à prova. A hora de parar se marca de manhã pela mesma razão: de cabeça fria. O que se abre primeiro ocupa a manhã, e o que se faz na primeira hora define o que se faz no resto do dia.", PI)
st.append(Paragraph("Durante o dia", MOM))
add("Depois, o dia corre como correm os dias. As linhas atravessam os instantes em que são chamadas; a da vez acontece quando chega a ocasião dela, e as que ficaram, cada uma na sua. Fora das ocasiões, o método não lhe pede nada. Não interrompa a vida para pensar nele.", PI)
proc("A folha de captura", [
 "Deixe a folha de captura ao lado da obra.",
 "Se surge algo que não pertence à obra, escreva-o numa linha.",
 "Volte à obra.",
 "· Escrever a linha não obriga você a nada. Tira a coisa da cabeça.",
])
add("A folha tem antepassados. Os gregos e romanos letrados mantinham <i>hypomnémata</i>, cadernos onde anotavam o que liam, ouviam ou pensavam, para reler depois. A folha de captura é mais humilde e guarda o que interrompe. O gesto é o mesmo: o que passa pelo espírito vai para o papel para que o espírito o solte. Enquanto não está escrita, a ideia pede para ser lembrada, e cada pedido é uma pequena saída da obra.", PI)
st.append(Paragraph("À noite &nbsp;<font size=10 color='#6b6b6b'>cerca de dez minutos, longe de toda distração</font>", MOM))
proc("Passos da noite", [
 "Faça a marca na folha de marcas, sobre a da vez, pela ocasião que mais pesou.",
 "Escreva a linha do dia: <i>o que existe agora que não existia de manhã?</i>",
 "Se a resposta é nada, escreva <i>nada</i>, sem enfeite.",
 "Na mesma linha, escreva sim ou não para as alavancas de hoje.",
 "Escreva a linha da queda: numa palavra, tirada, levada ou deixada cair.",
 "Na mesma linha, escreva onde foi e o que você fará diferente. Ou escreva <i>nenhuma</i>.",
 "Percorra a folha de captura e decida cada linha: amanhã, marcada para um dia, ou riscada.",
 "Escreva a primeira tarefa de amanhã.",
 "Se a quinta linha deixou escrito o primeiro passo de amanhã, copie-o aqui.",
 "Se a obra em curso ficou pronta, escreva logo a seguinte, descendo de novo do ano.",
 "Feche o caderno.",
 "Vá para o quarto, sem nada que distraia.",
 "Se hoje foi dia de piso, faça só a marca e a primeira tarefa.",
 "· Ver: <i>Da medida</i>.",
])
add("A linha da queda pergunta onde estava o buraco e deixa de fora o juízo sobre você. Ela guarda a ordem do exame de Sêneca, em que o perdão vem depois da correção: primeiro o que você fará diferente, e só então o caderno fechado, sem sentença. <font color='#6b6b6b'>(Lição XII)</font> As alavancas não têm marca própria: a marca é só da da vez. Nas noites de passagem, os sins e os nãos mostram se alguma alavanca pede emenda.", PI)
add("Esta escrita da noite é das mais antigas que se conhecem. Os <i>Versos de ouro</i>, poema que os antigos ligavam à escola de Pitágoras, pedem que não se deixe o sono descer sobre os olhos antes de repassar cada ato do dia com três perguntas: em que falhei? que fiz? que dever deixei de cumprir? A sua noite herda as três e as encolhe: a marca e a linha da queda respondem à primeira, a linha do dia à segunda, a primeira tarefa à terceira. Uns dez minutos, porque uma escrita que custa uma hora é abandonada depois de poucos dias.", PI)
add("A linha do dia vem de um pintor. Plínio, o Velho, conta que Apeles, o mais célebre dos pintores gregos, não deixava passar um dia, por mais ocupado que fosse, sem traçar ao menos uma linha. Daí o provérbio latino <i>nulla dies sine linea</i>, nenhum dia sem linha. Bastava-lhe uma linha, desde que estivesse na tábua à noite e de manhã não estivesse. É a pergunta da sua noite, respondida com o pincel.", PI)

st.append(Paragraph("Na noite de passagem", MOM))
add("Numa noite que este livro não sabe dizer qual será, ao fazer a marca, você vai reconstruir a ocasião que mais pesou e encontrar o gesto feito sem encontrar a decisão de fazê-lo: a ocasião o lembrou, e não o caderno. Você vai escrever <i>chegou</i> ao lado do traço. Essa noite e a manhã seguinte formam a passagem, o único momento em que o método se emenda.", PI)
proc("Passos da passagem", [
 "Faça a noite de sempre.",
 "Leia a Lição que fecha o exercício que chegou. O da discrição não tem Lição.",
 "Releia a folha do dia zero.",
 "Na primeira noite de passagem, copie <i>Do homem</i> à mão. Nas seguintes, releia a página.",
 "Na primeira, copie também o breviário nas páginas 3 e 4, se ainda não o imprimiu e colou.",
 "Leia a frase da anti-visão, o primeiro ponto da folha do dia zero.",
 "Faça por escrito as emendas que as marcas pedirem: ao método, à folha do dia zero ou ao domínio.",
 "Se as marcas não pedem emenda, não emende nada.",
 "Leia, no Livro III, o exercício da microação que entra amanhã.",
 "Preveja onde a ocasião dela vai aparecer.",
 "· A anti-visão se lê só nestas noites e na onda.",
])

sec("Do descanso")
add("<i>“É preciso dar descanso ao espírito: repousado, ele se levanta melhor e mais vivo.”</i> &nbsp;<font color='#6b6b6b'>— Sêneca, <i>Da tranquilidade da alma</i></font>", ParagraphStyle('dq', parent=P, alignment=TA_CENTER))
add("Sêneca compara o espírito ao campo fértil, que se esgota se nunca o deixam repousar. Por isso, neste livro, o descanso tem regras, como a obra as tem. Um esforço sem repouso não se mantém. Quem passa semanas no limite para de uma vez e, com essa parada, abandona também o que tinha conseguido. O descanso pertence à disciplina, como o intervalo entre as séries pertence ao treino.", PI)
proc("A hora de parar", [
 "De manhã, escreva a hora de parar na página do dia.",
 "Quando ela chegar, termine o passo em que estiver.",
 "Feche a obra aí. O que ficou por fazer espera a manhã seguinte.",
 "Depois dela, não há obra nem culpa.",
 "Faça a noite e a marca como sempre. As microações continuam.",
])
add("Max Weber viveu a parada por inteiro. Nos anos noventa do século XIX, professor jovem e já célebre em Heidelberg, ele dava aulas, examinava, escrevia pareceres e estudos, e trabalhava noite adentro, sem pausa, como conta Marianne Weber, a mulher dele. Em 1898 a máquina parou de uma vez. Ele já não conseguia ler, nem escrever, nem dar aula. Viajou para a Itália, tentou voltar mais de uma vez, e em 1903 renunciou à cátedra. Quando voltou a escrever, saiu <i>A ética protestante e o espírito do capitalismo</i>, e Weber nunca mais teve a capacidade de trabalho de antes. O limite que ele não quis marcar, o corpo marcou por ele, e cobrou anos.", PI)
add("Em 1947, em Bonn, numa Alemanha em ruínas onde tudo pedia reconstrução, o filósofo Josef Pieper lembrou uma palavra grega. <i>Scholé</i> era o tempo livre, de onde vem a nossa escola; o trabalho se dizia pela negativa, <i>ascholía</i>, falta de ócio. Aristóteles escreve no último livro da <i>Ética a Nicômaco</i> que trabalhamos para ter ócio, como fazemos a guerra para ter paz. Uma vida feita só de trabalho toma o meio pelo fim. E Pieper avisava contra o descanso que serve só para render mais: quem descansa pensando no dia seguinte já trouxe o trabalho para dentro do tempo livre.", PI)
add("O método guarda o ócio de duas maneiras. A primeira é diária e pequena: a hora de parar. Ela se marca de manhã, de cabeça fria, porque à noite, com o peso ou com o entusiasmo da obra, ninguém julga bem a hora de parar. A segunda é maior e mais rara: o dia de ócio. Ele não tem frequência fixa.", PI)
proc("O dia de ócio", [
 "Faça a prova do sono: depois de sete a oito horas de sono, confira de manhã o peso da véspera.",
 "· A prova do sono falha se o peso continua igual ou maior.",
 "Se a prova do sono falhou três manhãs seguidas, com a hora de parar cumprida, declare na véspera um dia de ócio.",
 "Escreva a declaração no caderno: o dia seguinte é dia de ócio.",
 "Não declare no próprio dia.",
 "Não declare dois dias seguidos.",
 "Não declare no dia seguinte a uma cruz: é dia sagrado.",
 "No dia de ócio, não faça obra. Caminhe, converse, leia por prazer, durma.",
 "Faça as microações e a marca da noite.",
 "Antes de cada coisa, pergunte: <i>faço isto para ter feito, ou porque é bom fazê-lo?</i>",
 "Se é para ter feito, é obra: deixe para amanhã.",
 "· O dia de ócio não é dia de recaída, nem de distração sem fim.",
 "· Ver: Livro V.",
])
add("Abraham Joshua Heschel, rabino nascido em Varsóvia que acabou ensinando em Nova York, escreveu em 1951 um livro breve, <i>O sábado</i>, sobre o sétimo dia da tradição dele. Chamou-o de palácio no tempo. As outras civilizações, dizia, santificaram lugares; a Bíblia santificou um tempo, e o fiel entra nele toda semana como num edifício, com hora certa para as portas se abrirem e se fecharem. Ao seu ócio, este livro pede só o que fazia daquele dia um palácio: as paredes. A hora de parar é a parede de cada dia; o dia de ócio tem as suas desde a véspera.", PI)
add("O ócio e a preguiça podem ocupar as mesmas horas com as mesmas coisas. O ócio foi decidido antes e tem fim marcado; a preguiça começa sem decisão e termina quando calha. Quando o dia de ócio vier, guarde-o como guardaria uma consulta marcada. E quando a trégua vier sem ter sido merecida, num dia em que tudo pesa menos sem razão aparente, aceite-a. A clareza vem também fora das horas da obra, numa caminhada ou no banho, depois que se deixou de procurá-la. <font color='#6b6b6b'>(Lição III)</font>", PI)

sec("Do piso")
add("Há dias em que faltam condições, e não vontade: doença, viagem, um período de provas, um peso na família. Para esses dias existe o piso, o mínimo de cada coisa, declarado de manhã. O piso se define agora, de cabeça fria, e não na manhã em que tudo parece justificar o abandono.", PI)
proc("Dia de piso", [
 "De manhã, antes de abrir qualquer outra coisa, confira estes quatro fatos.",
 "Se há febre ou doença que impede sentar à mesa da obra, é dia de piso.",
 "Se uma viagem tira você de casa antes da hora da obra, ou ocupa o dia em deslocamento, é dia de piso.",
 "Se uma prova, um plantão ou um compromisso marcado por outro ocupa as horas da obra, é dia de piso.",
 "Se alguém da casa está doente ou em crise e precisa de você hoje, é dia de piso.",
 "Escreva no caderno <i>hoje, piso</i>, de manhã, ainda na cama se preciso.",
 "Faça a da vez ao menos uma vez, no piso que o exercício dela dá.",
 "Leia uma página.",
 "Dê ao corpo dez minutos, ou uma caminhada.",
 "Dê ao domínio quinze minutos na parte difícil.",
 "À noite, faça a marca e só a terceira linha, a primeira tarefa de amanhã.",
 "· Cumprido o piso da da vez, a marca é traço. O corte não tem piso.",
 "· Ver: <i>Do piso e do sinal</i>.",
])
add("O dia de piso se declara de manhã, nunca à tarde: à tarde, quem o escolhe é o peso do dia. Só o piso da da vez decide a marca. As outras linhas da lista são o mínimo do dia, e valem para quem já tem a leitura, o corpo ou o domínio nos dias comuns. O piso é para a circunstância; para a falta de vontade há a sexta linha. O corte não tem piso porque um corte reduzido deixaria entrar de novo, aos poucos e com licença, aquilo que se cortou.", PI)
add("A meia-força finge fazer a obra e a faz pela metade, para que reste a desculpa de não ter dado tudo; estraga a obra e protege só a sentença sobre você. O piso não promete a obra. Guarda a ocasião, que o gesto continua encontrando no dia em que tudo pedia que ela passasse sem ele, e guarda quem faz isto todos os dias, também nos de febre. Ele se escreve de manhã, com o tamanho dito, e se cumpre inteiro nesse tamanho: a página lida até o fim, os dez minutos de corpo feitos de verdade.", PI)
add("Matisse viveu um piso que durou anos. Em 1941, aos setenta e um, foi operado de um câncer e saiu da cirurgia sem forças para ficar muito tempo de pé diante do cavalete; passou boa parte do que lhe restava de vida na cama ou numa cadeira de rodas. Não parou, e também não fingiu que nada tinha mudado. Os assistentes cobriam folhas de papel com guache, e ele recortava as formas com uma tesoura grande, sentado, e indicava onde prendê-las na parede. Assim fez <i>Jazz</i>, publicado em 1947, e os vitrais da capela de Vence. O gesto ficou menor, e a obra não se interrompeu.", PI)

sec("Do bloco de obra")
add("Há semanas em que a obra pede mais do que o dia comum lhe dá: o livro que precisa estar pronto antes do outono, a prova de um concurso, a obra que tem data. Para elas existe o <b>bloco de obra</b>, um período declarado, de quatro a oito semanas, em que a obra passa à frente de tudo o que o método não protege. O dia comum segue o ritmo; o piso atravessa os dias sem condições; o bloco dá à obra um período só dela, com começo e fim escritos.", PI)
proc("Declarar o bloco", [
 "Numa noite de passagem, escreva a obra do bloco, a data do primeiro dia e a do último.",
 "No alto da mesma página, escreva as três paredes.",
 "Parede 1: o sono do §8, de sete a oito horas.",
 "Parede 2: a hora de parar, marcada de manhã e cumprida à noite.",
 "Parede 3: um tempo diário com as pessoas da sua vida, sem a obra na mesa nem na conversa.",
 "Se a descarga do bloco anterior e quatro semanas comuns não passaram, não declare.",
])
proc("No bloco", [
 "Escreva sempre a obra do bloco como obra de hoje.",
 "Abaixo da linha do dia, escreva a linha do bloco: horas reais na parte difícil e o que foi entregue.",
 "· Exemplo: <i>bloco: duas horas e meia; o capítulo quatro revisto</i>.",
 "Não some as linhas do bloco nem as compare. Releia-as uma vez, na noite do último dia.",
 "Continue a da vez e as que ficaram. Se a da vez chegar, faça a passagem.",
 "Não abra coisa nova, nem corte, nem ações do apêndice.",
 "Não adie nem antecipe o fim.",
 "Se a obra não coube, ela volta ao ritmo comum.",
 "Se o sono cai ou as pessoas da sua vida se ferem, leia <i>Dos dois lados</i>.",
 "Se a hora de parar passa sete noites seguidas, leia <i>Dos dois lados</i>.",
])
proc("A descarga", [
 "Na semana depois do último dia, faça a obra no piso: quinze minutos na parte difícil.",
 "Marque a hora de parar mais cedo do que no dia comum.",
 "Faça o resto do método inteiro.",
 "Não escreva mais a linha do bloco.",
])
add("A linha do bloco é um fato registrado, como <i>a obra de hoje, feita</i>. A descarga é a semana em que o corpo e as pessoas recebem de volta o que o bloco lhes tomou; quem a pula entra no ritmo comum já devendo. A obra manda dentro das horas dela; fora delas, não tem voto.", PI)
add("Balzac mostra o que acontece quando a temporada não tem paredes. Durante anos ele se deitava no começo da noite, levantava-se de madrugada e escrevia até a manhã seguinte, sustentado por café forte, regime que ele mesmo descreveu no <i>Tratado dos excitantes modernos</i>, de 1839. Deixou em vinte anos a obra de várias vidas e morreu em 1850, aos cinquenta e um anos; os biógrafos ligam a esse regime parte do desgaste que o matou. A obra ficou. O bloco deste livro quer a intensidade dessas temporadas, com o fim que elas não tinham.", PI)

sec("Da companhia")
add("Boas companhias são raras, e não se escolhem como se escolhe um livro. As obras, sim. Os livros dos melhores autores estão à mão a qualquer hora e custam pouco.", PI)
add("Sêneca, em <i>Da brevidade da vida</i>, diz que só estão vivos de verdade os que dedicam tempo aos sábios: podem discutir com Sócrates, duvidar com Carnéades, repousar com Epicuro, e nenhum deles os despedirá de mãos vazias. Maquiavel, exilado da política, escreveu a Francesco Vettori, em dezembro de 1513, que ao anoitecer tirava a roupa do dia, enlameada, vestia-se com dignidade e entrava nas antigas cortes dos homens antigos. Ali perguntava, e eles respondiam; e por quatro horas não sentia tédio nem temia a pobreza. Tratava a leitura como um encontro, e por isso, exilado e pobre, tinha uma companhia que o exílio não lhe tirava.", PI)
add("Montaigne fez da companhia um lugar. Em 1571, aos trinta e oito anos, retirou-se para a torre do castelo dele, onde tinha a biblioteca, uma sala redonda com os livros em volta. Nas vigas do teto mandou gravar dezenas de sentenças gregas e latinas: ao levantar os olhos da página, dava com outra voz. Os livros, escreveu, são a companhia mais constante e a que está sempre à mão.", PI)
proc("O livro da vez", [
 "Escolha seus companheiros entre os autores. O livro da vez é o companheiro da vez.",
 "Leia com a caneta na mão.",
 "Escreva na margem de cada livro ao menos uma discordância sua, mesmo torta.",
 "Copie numa folha duas ou três frases do livro da vez.",
 "Ponha a folha onde você a veja ao levantar os olhos da obra.",
 "Troque a folha quando o livro se fechar. Guarde as folhas numa gaveta.",
 "Antes de uma decisão difícil, pergunte o que faria Marco Aurélio, ou o que diria Sêneca.",
 "Ouça as razões dele. Depois decida você.",
])
add("Essa pergunta é a da máscara feita a um rosto que deixou escrito como pensava, e por isso a resposta vem com as razões dele. Schopenhauer avisava que ler é pensar com a cabeça de outro, e que quem só lê acaba sem cabeça própria: enquanto você lê, pensa o autor. O seu pensamento só trabalha quando você responde. No fim de um ciclo, a gaveta terá as vozes que acompanharam você, na ordem em que vieram. <font color='#6b6b6b'>(Lição VI)</font>", PI)
add("Um livro não corrige você em tempo real, nem vê a sua obra. Para isso, o exercício da crítica continua necessário, e uma pessoa que saiba mais, mesmo distante, vale como mestre.", NOTE)
add("Às vezes esse mestre está do outro lado do mundo. Em janeiro de 1913, Srinivasa Ramanujan, escriturário de vinte e cinco anos no porto de Madras, sem diploma, que aprendera matemática quase sozinho num livro de fórmulas, mandou a G. H. Hardy, em Cambridge, uma carta com umas dez páginas de teoremas. Hardy quase a pôs de lado; à noite, leu-a com Littlewood, e os dois concluíram que estavam diante de um matemático de primeira ordem. A carta trazia também erros, e quase nenhuma demonstração. Nenhum livro podia dizer isso a Ramanujan. Hardy disse, e passou anos em Cambridge ensinando-lhe a prova rigorosa sem apagar o resto.", PI)
add("Agora você tem a moldura inteira. A folha do dia zero diz para onde você vai; as linhas dizem o que pensar no instante; as leis dizem o que não se discute; o dia diz quando cada coisa acontece; o piso e o descanso dizem como atravessar os dias sem condições e o peso que se acumula; o bloco dá à obra um período só dela; e os livros lhe dão com quem falar pelo caminho. Tudo isso serve a uma só hora, aquela em que você se senta diante de uma coisa e fica com ela até acabar. Falta o gesto, e o gesto tem uma ordem. Você já o começou na manhã do dia um, com a microação da ordem. O livro seguinte entrega os exercícios, estação após estação, até o décimo terceiro.", PI)
add("Se a manhã e a noite de hoje ainda lhe pediram o livro aberto, releia <i>Do dia</i> a partir de <i>De manhã</i> e faça amanhã os passos com ele aberto. Se a da vez não chega há muitas noites, leia <i>O que está acontecendo?</i> antes de mudar seja o que for. Daqui em diante você abre o livro nas noites de passagem, e o caderno todas as manhãs e todas as noites.", PI); fleur()
# O fecho vai junto do parágrafo anterior, para não ficar sozinho numa página.
st[-3:] = [KeepTogether(st[-3:])]
# As Lições de M Castro fecham os exercícios: cada uma se lê na noite em que o seu exercício chega.
import json
LIC = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'licoes.json')))
NOTA = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nota.txt')).read().split("\n\n")
LBL5 = ParagraphStyle('lbl5', **{**base, 'textColor': GRAY}, fontSize=9.5, leading=12, alignment=TA_CENTER, spaceBefore=16, spaceAfter=8, keepWithNext=1)
QQ = ParagraphStyle('qq', fontName='G-I', textColor=INK, fontSize=12, leading=16.5, alignment=TA_CENTER, leftIndent=20, rightIndent=20, spaceAfter=2)
QAu = ParagraphStyle('qau', **{**base, 'textColor': GRAY}, fontSize=10, leading=13, alignment=TA_CENTER, spaceAfter=10)
def citas(t):
    out = []
    for m in re.finditer(r"“(.*?)”\s*—\s*(.*?)(?=“|$)", t, re.S):
        q = re.sub(r"\s*\n\s*", " ", m.group(1)).strip()
        a = re.sub(r"\s*\n\s*", " ", m.group(2)).strip()
        out.append((q, a))
    return out
NOMES = {"O exemplo real":"O &nbsp;EXEMPLO &nbsp;REAL","A crítica":"A &nbsp;CRÍTICA","O que diz o autor":"O &nbsp;QUE &nbsp;DIZ &nbsp;O &nbsp;AUTOR","A meditação":"A &nbsp;MEDITAÇÃO"}
def licao(i):
    Lc = LIC[i]
    # A Lição abre página nova; sem isto, a última linha do exercício pode ficar sozinha na página anterior.
    if isinstance(st[-1], Paragraph): st[-1] = KeepTogether([st[-1]])
    st.append(PageBreak()); sp(24)
    add(f"L I Ç Ã O &nbsp; {Lc['num']}", LIV)
    add(Lc['title'], ParagraphStyle('lt5', parent=LT, fontSize=21, spaceAfter=4))
    sumario(st[-1], 1, f"Lição {Lc['num']} · {Lc['title']}")
    add("por M Castro", ParagraphStyle('l5a', parent=EPA, spaceAfter=16))
    if i == 0:
        add("As Lições que fecham os exercícios são de outro autor, M Castro, e a voz muda nelas de propósito. O livro mede e dá de cada caso só o que serve ao gesto; M Castro afirma, e conta a história inteira. A noite em que um gesto chega é a única em que o método não lhe pede nada novo, e é a hora de ouvir alguém que não precisa medir as palavras. Na manhã seguinte, o livro volta a falar baixo. Cada Lição dá o porquê do gesto que acabou de chegar. Nenhuma traz regra, nem lhe pede ato ou escrita, e cada uma se lê em menos de dez minutos, depois da marca. O exercício da discrição é o único sem Lição: o que ele treina é o silêncio.", PI)
        add("N O T A &nbsp; I N I C I A L", LBL5)
        for par in NOTA: add(par, PI)
    for k in ["O exemplo real","A crítica","O que diz o autor","A meditação"]:
        if k == "O que diz o autor":
            # O rótulo vai no bloco da primeira citação: o keepWithNext do LBL5
            # não segura um KeepTogether na mesma página.
            rotulo = [Paragraph(NOMES[k], LBL5)]
            for q, a in citas(Lc['secs'][k]):
                st.append(KeepTogether(rotulo + [Paragraph(f"“{q}”", QQ), Paragraph(f"— {a}", QAu)]))
                rotulo = []
            st.extend(rotulo)
        else:
            add(NOMES[k], LBL5)
            add(Lc['secs'][k], PI)
    add(Lc['secs']["A lição"], BOX)

# ===================== LIVRO III =====================
livro("III", "Dos exercícios")

add("Os treze gestos deste livro preparam, um de cada vez, o lugar onde aparece o estado de foco que dá nome ao livro. Os primeiros tratam da mesa, do terminar, da atenção e do corpo. Os do meio tratam da obra. Os últimos tratam do ânimo que sustenta a obra: as conversas, as opiniões, o conforto, a vontade de contar. Cada gesto, quando chega, tira um obstáculo entre você e o que está à sua frente.", PI)
proc("Como ler este livro", [
 "Na tarde do dia zero, leia o exercício da ordem: o gesto do alto, <i>Do começo</i> e <i>Da marca</i>.",
 "Na primeira noite de passagem, leia esta abertura e o resto do exercício da ordem.",
 "Em cada noite de passagem, leia a Lição do exercício que chegou.",
 "Na mesma noite, leia só o exercício seguinte.",
 "Se um exercício adiante parece mais urgente, fique no da vez. A ordem não se pula.",
 "Leia a estação zero numa noite antes do próximo dia zero.",
 "· Você sai das estações com as treze microações entre as que ficaram e o ciclo pronto para <i>Da prova</i>.",
])
add("Um exercício treina um gesto até ele ser feito sem esforço de decisão. Cada um se reduz a uma microação: um gesto central, curto, na sua ocasião. Alguns trazem práticas que servem ao gesto; só o gesto central se marca. Você treina uma de cada vez, a da vez, até a noite em que escreve <i>chegou</i>. Na manhã seguinte ela passa a ficar, e entra a seguinte.", PI)
add("Os exercícios se agrupam em estações. A estação zero é a do domínio; a primeira treina as condições da obra; a segunda entra na obra; a terceira trata do que você faz quando a obra, as pessoas e as circunstâncias contrariam você. Os nomes das três vêm das fases com que Robert Greene descreve, em <i>Maestria</i> (2012), a formação num ofício. Quanto tempo leva cada estação, ninguém sabe de antemão: o gesto chega quando chega.", PI)
add("Todo exercício tem a mesma forma, para você achar depressa o que procura. No alto, o número, o nome e a letra H ou J; embaixo, a frase de um autor; depois, em negrito, o gesto, que o breviário resume numa linha e sobre o qual você faz a marca. Seguem as partes, sempre nesta ordem:", PI)
add("<b>Do porquê</b>: a ideia, o mecanismo e uma frase para dizer por dentro.<br/><b>Do começo</b>: o primeiro dia, num quadro, e a linha <b>Você sai com</b>, o que tem de existir na primeira noite.<br/><b>Do modo</b>: os passos, num quadro, para reler de pé.<br/><b>Da marca</b>: o que conta como traço, cruz e ponto, e quando se escreve <i>chegou</i>. As regras de <i>Da medida</i> valem acima disso.<br/><b>Dos erros</b>: os modos de cumprir por fora sem cumprir.<br/><b>Do piso e do sinal</b>: o mínimo do dia de piso e o retrato do gesto maduro, que não decide a passagem.<br/><b>Do sentido</b>: de onde vem o gesto e quem o praticou antes de você.<br/><b>Do que se sabe</b>: o que os estudos sustentam, com o grau de certeza.", PI)
add("Depois de cada exercício vêm um parágrafo que adapta o gesto a outras vidas e um quadro, <b>Se o gesto falha</b>, com linhas começadas por <i>Se</i>. É esse quadro que você procura quando o gesto falha sempre do mesmo modo.", PI)
add("<b>H</b> quer dizer hábito: com a repetição, o gesto acontece sem decisão, como acender a luz ao entrar num quarto escuro. <b>J</b> quer dizer juízo: o gesto fica mais rápido e mais leve, mas pede sempre que você pense, porque a situação nunca se repete igual. Os quatro da primeira estação são H. Num exercício J, <i>chegou</i> quer dizer que o gesto veio na ocasião sem o breviário; ele continua pedindo cabeça.", PI)
add("A estação zero vem a seguir e não é para esta noite. Passe à primeira estação e ao exercício da ordem.", PI)


PEND = []
def estacao(t, sub):
    PEND.extend([Paragraph(t.upper().replace(" ", " &nbsp;"), SEC), Paragraph(sub, ParagraphStyle('ss', parent=EXQ, alignment=TA_CENTER, spaceAfter=8))])
LBX = ParagraphStyle('lbx', **{**base, 'textColor': GRAY}, fontSize=9.5, leading=12, spaceBefore=6, spaceAfter=2, keepWithNext=1)
# Nas listas de parágrafos do exercício, uma tupla (título, linhas) sai como quadro de procedimento.
def _blocos(itens):
    for it in itens:
        if isinstance(it, tuple): proc(*it)
        else: st.append(Paragraph(it, PI))
def exe(n, nome, tipo, frase, autor, texto, sentido=None, como=None, erros=None, piso=None, sinal=None, comeco=None, marca=None, sai=None, porque=None, saber=None):
    pre = PEND[:]; PEND.clear()
    st.append(KeepTogether(pre + [
        sumario(Paragraph(f"{n}. &nbsp;{nome} <font size=9.5 color='#6b6b6b'>&nbsp;{tipo}</font>", ParagraphStyle('exh', parent=EXE, fontSize=13.5, spaceBefore=20)),
                1, f"{n}. {nome}"),
        Paragraph(f"“{frase}” &nbsp;— {autor}", EXQ),
        Paragraph(f"<b>{texto}</b>", P)]))
    if porque:
        st.append(Paragraph("D O &nbsp; P O R Q U Ê", LBX))
        _blocos(porque)
    if comeco or sai:
        st.append(Paragraph("D O &nbsp; C O M E Ç O", LBX))
        _blocos(comeco or [])
        if sai: st.append(Paragraph(f"<b>Você sai com:</b> {sai}", PI))
    if como:
        proc("Do modo", como)
    if marca:
        st.append(Paragraph("D A &nbsp; M A R C A", LBX))
        st.append(Paragraph(marca[0], P))
        for par in marca[1:]: st.append(Paragraph(par, PI))
    if erros:
        st.append(Paragraph("D O S &nbsp; E R R O S", LBX))
        st.append(Paragraph(erros, PI))
    if piso or sinal:
        blk=[Paragraph("D O &nbsp; P I S O &nbsp; E &nbsp; D O &nbsp; S I N A L" if piso else "D O &nbsp; S I N A L", LBX)]
        if piso: blk.append(Paragraph(f"<b>Piso:</b> {piso}", P))
        if sinal: blk.append(Paragraph(f"<b>Sinal de consolidação:</b> {sinal}", P))
        st.append(KeepTogether(blk))
    if sentido:
        st.append(Paragraph("D O &nbsp; S E N T I D O", LBX))
        _blocos(sentido)
    if saber:
        st.append(Paragraph("D O &nbsp; Q U E &nbsp; S E &nbsp; S A B E", LBX))
        st.append(Paragraph(saber, PI))

estacao("Estação zero", "Do domínio. Uma vez por ciclo.")
st.extend(PEND); PEND.clear()
add("Leia esta estação no dia zero, se a lista do que você amou não mostrou nada e você veio procurar o porquê. Ou leia numa noite do caminho, antes do próximo dia zero, para entender com calma o que fez às pressas. O exercício zero diz para onde vão os outros treze. Volta-se a ele uma vez por ciclo, em cada dia zero.", PI)
exe("0", "Da vocação", "", "O que você amou verdadeiramente até agora?", "Nietzsche",
 "Faz-se no dia zero, descrito no prólogo.",
 ["No inverno de 1902, Franz Xaver Kappus, aluno da escola militar de Wiener Neustadt, mandou alguns poemas a Rainer Maria Rilke e pediu que ele dissesse se valiam alguma coisa. Rilke respondeu de Paris, em fevereiro de 1903, e começou por uma recusa: não ia julgar os versos. O rapaz olhava para fora, comparava seus poemas com os de outros, sofria com as recusas das revistas. Rilke lhe deu um só caminho: entrar em si e perguntar, na hora mais silenciosa da noite, se morreria caso fosse proibido de escrever. Se a resposta fosse um sim simples e forte, que ele construísse a vida segundo essa necessidade.",
  "Rilke não pergunta pelo talento nem pelo futuro da poesia. Pergunta pela necessidade, e manda procurá-la numa hora sem plateia. A lista do que você amou responde a ele sem esperar uma voz no escuro: em vez de perguntar uma vez se morreria sem aquilo, você procura os momentos em que, fazendo aquilo, esqueceu o tempo. Repetidos na página, eles mostram o desenho.",
  "Quase ninguém responde a Rilke com um sim limpo, aos vinte ou aos quarenta. Por isso o exercício pede uma lista: um gosto fraco também deixa rastro, e os rastros juntos mostram o que se repete. Meses depois, Rilke pediu a Kappus que amasse as próprias perguntas como quartos fechados, e que as vivesse até entrar um dia na resposta sem perceber. O domínio do dia zero é uma pergunta assim, vivida durante um ciclo. No fim dele, você o escreve de novo, e só então sabe se era resposta."],
 ["Na manhã do dia zero, depois das oito perguntas, liste à mão tudo o que você amou fazer ou estudar desde criança.",
  "Não filtre pela utilidade.",
  "Ao lado de cada item, escreva o momento em que você esqueceu o tempo fazendo aquilo.",
  "Sublinhe o que se repete.",
  "Escreva o domínio numa frase. Uma combinação de campos serve.",
  "Embaixo, escreva o porquê com rosto: o que tira você da cama numa terça-feira, sem plateia."],
 "Os dois erros aparecem enquanto a lista se escreve. O primeiro é escolher pelo prestígio: a mão hesita diante de um item que dá vergonha e escreve no lugar dele o que soaria bem em voz alta. Escreva o que a mão ia escrever. O segundo é esperar certeza antes de escrever a frase. Ninguém tem certeza no dia zero. O domínio muda no ciclo seguinte, se for o caso; em branco ele não fica.",
 None, "você consegue explicá-lo em trinta segundos sem hesitar.",
 comeco=[
  "O exercício zero é escrever, numa frase, o domínio em que você vai até o fundo neste ciclo, e embaixo o porquê. Ele não tem microação nem ocasião diária. Faz-se uma vez, na manhã do dia zero, depois das oito perguntas da escavação, e de novo no começo de cada ciclo.",
  "Domínio é o campo de trabalho ou de estudo a que você vai dar as melhores horas: um ofício, uma arte, uma ciência, uma parte da sua profissão. Para uma enfermeira, o cuidado de doentes graves; para um marceneiro, os móveis de encaixe sem pregos; para quem criou os filhos e agora tem as tardes livres, a pintura abandonada aos vinte anos.",
  ("Na noite do dia zero", [
   "Se um item ficou fora da lista porque veio a pergunta <i>para que serve isto?</i>, escreva-o agora.",
   "Diga o domínio em voz alta, em trinta segundos.",
   "Se você hesitou, reescreva a frase nesta mesma noite, antes de fechar o caderno.",
   "Se a frase não saiu limpa, fique com a melhor que você tem e trabalhe com ela.",
   "Depois desta noite, reveja o domínio só numa passagem, por escrito, diante das marcas, ou no próximo dia zero.",
   "· Este exercício não tem marca, nem <i>chegou</i>, nem passagem. O teste dos trinta segundos faz as vezes de marca.",
  ]),
 ], sai="o domínio numa frase no terceiro ponto da folha do dia zero, com o porquê com rosto embaixo, e a lista do que você amou com o que se repete sublinhado.",
 porque=[
  "<b>A ideia.</b> Nietzsche, em <i>Schopenhauer como educador</i> (1874), dá um caminho indireto a quem quer saber quem é: olhar para trás e perguntar o que amou de verdade até agora, o que elevou a alma, o que a dominou e a fez feliz, e pôr esses objetos em fila. A fila mostraria a lei fundamental do seu ser, que, segundo ele, está muito acima de você. Aqui o uso é outro: na fila entram coisas feitas, com os momentos em que você esqueceu o tempo, e dela se tira o domínio. Esse ser de cima continua seu; o domínio diz em que campo você vai procurá-lo.",
  "<b>O mecanismo.</b> A pergunta direta, <i>o que devo fazer da vida?</i>, recebe o que soa bem em voz alta. A pergunta pelos momentos em que você esqueceu o tempo recebe lembranças de coisas feitas, que o prestígio distorce menos; isto o autor acha, sem estudo. Os treze exercícios seguintes são planos do tipo <i>quando acontecer isto, faço aquilo</i>, e Gollwitzer e Sheeran mediram efeitos maiores desses planos quando a pessoa quer de fato o objetivo. Sem domínio, os gestos não servem a obra nenhuma.",
  "<b>Por isso.</b> Faço esta lista porque os outros gestos só pegam se servirem a uma coisa que eu queira."])
add("Quem tem a vida presa a um ofício que não escolheu faz o exercício sem demolir nada. O domínio pode ser o campo que se cultiva nas margens do ofício, ou a parte dele que você faria de graça. Quem chega com muitos anos procura também nos anos de trabalho, porque há amores que aparecem tarde. Quem cuida de outros escreve o domínio ao lado desse cuidado, com a pequena hora que sobra.", PI)
proc("Se o gesto falha", [
 "Se a lista tem cinco itens respeitáveis, você filtrou. Recomece pelo inútil: os jogos da infância, o que lia escondido.",
 "Se a lista é longa e nada se repete, procure o verbo: ordenar, consertar, explicar, contar, cuidar.",
 "Se a frase junta três coisas que não se tocam, procure o que as une.",
 "Se nada as une, escolha uma para este ciclo e guarde as outras para o seguinte.",
 "Se, semanas depois, o domínio parecer errado, escreva a dúvida na folha de captura.",
 "Leve a dúvida à próxima passagem. Não corrija o domínio no meio do caminho (§9).",
])

estacao("Primeira estação", "Do aprendizado, segundo Robert Greene.")
st.extend(PEND); PEND.clear()
add("A primeira estação começa na tarde do dia zero. Do domínio escrito passa-se ao chão em que ele será servido: o lugar da obra, a recusa de abrir o que não se fecha, a atenção que fica, o corpo que sustenta tudo. Esses quatro gestos quase não aparecem na obra de hoje; servem para que ela se sustente nos meses que vêm. Greene chama de aprendizado esse tempo em que se aceita a disciplina antes de ter algo para mostrar. No meio da estação, numa noite de marca, vai parecer que você avança pouco. Conta o que você já faz sem esforço, e é nisso que a estação seguinte se apoia.", PI)
exe("1", "Da ordem", "H", "Algumas coisas dependem de nós, outras não.", "Epicteto",
 "Quando você se sentar à mesa: tudo o que distrai sai dela. Quando você se levantar dela: a mesa volta à ordem.",
 ["Os monges do deserto egípcio viviam em celas quase vazias: uma esteira, um jarro de água, as folhas de palmeira com que trançavam cestos. Um irmão foi a Scete pedir uma palavra ao abade Moisés, e o velho respondeu: vá, sente-se na sua cela, e a sua cela lhe ensinará tudo. Num lugar onde nada chama, a mente, depois de se agitar, não tem para onde ir senão para aquilo que veio fazer ali.",
  "Quinze séculos depois, em Londres, Auguste Escoffier dirigia as cozinhas do Savoy e organizava os cozinheiros em brigadas. A regra da <i>mise en place</i>, pôr no lugar, governava a hora antes do serviço: cada um preparava a bancada sempre na mesma ordem, para que a mão achasse tudo sem procurar. A limpeza se fazia durante o serviço, porque a bancada suja de uma hora é a confusão da seguinte. No meio do serviço, nenhum cozinheiro decide onde está o sal. Decidiu antes.",
  "A sua mesa é as duas coisas. É cela, porque nela a distração não tem onde morar. É bancada, porque nela a obra está pronta para a mão. A lista da mesa é a sua <i>mise en place</i>, e os dois minutos ao se levantar são o fechamento do serviço: a manhã seguinte começa sem nada a decidir.",
  "As mesas de alguns grandes espíritos ficaram famosas pela desordem. Essa desordem se acumulava em volta de uma só obra. O exercício deixa na mesa o papel da sua obra e tira dela o que chama você para fora."],
 ["No dia zero, à tarde, arrume a mesa e o que está ao alcance dela por completo, num único esforço.",
  "Escreva no caderno a lista da mesa: o mínimo que fica nela quando você não está na obra.",
  "Ao se sentar, antes de abrir a obra, tire da mesa e do alcance tudo o que distrai.",
  "Ao se levantar, use dois minutos: devolva a mesa ao que diz a lista."],
 "O primeiro erro tem ar de zelo. Numa manhã de obra difícil, a arrumação se alonga: o pó, as canetas, uma gaveta, e meia hora depois a obra continua fechada. A ordem tem um limite de cinco minutos. O segundo erro é buscar a mesa perfeita e corrigir a lista todas as tardes. Basta a ordem da lista que você escreveu.",
 "ao se sentar, só tirar a distração.", "a mesa está neutra e a distração ausente sem que você tenha precisado se lembrar.",
 comeco=[
  "Você lê isto na tarde do dia zero. O gesto do alto é a primeira microação do livro, e a partir desta tarde é a da vez. A mesa vazia fecha a saída mais curta da assentada: o que está à vista chama a mão, e cada ida até ele deixa o <i>isto</i> esperando.",
  "A ocasião é sentar no lugar onde você trabalha ou estuda, e levantar dele. Mesa é qualquer lugar assim, inclusive o do emprego: a escrivaninha do escritório, o balcão onde o comerciante faz as contas. Num dia comum a ocasião vem várias vezes. A que mais pesa é a sessão da obra de hoje, com o sentar que a abre e o levantar que a fecha.",
  ("Na tarde do dia zero", [
   "Faça a arrumação grande: a mesa e o que está ao alcance dela, de uma vez.",
   "Termine escrevendo no caderno a lista da mesa.",
   "Se tem mesa fora de casa, escreva a lista dela no primeiro dia em que se sentar lá.",
   "Passe essa lista para o caderno na mesma noite.",
   "Na síntese, tire a distração antes de abrir o caderno.",
   "Ao se levantar, devolva a mesa à lista.",
   "Faça a primeira marca na folha de marcas, sobre a síntese.",
   "· Nesta noite não se escreve <i>chegou</i>: no dia em que uma microação entra, nunca.",
  ]),
  "Na primeira ocasião vem uma frase pequena e razoável: <i>isto pode ficar, não incomoda</i>. É a segunda frase interior (§2), e o gesto existe para que você não a discuta: a distração sai antes de a obra abrir. Ao se levantar, vem outra, mais lenta: <i>arrumo amanhã</i>. São dois minutos.",
 ],
 marca=["<i>Traço:</i> na sessão da obra, a distração saiu quando você se sentou e a mesa ficou neutra quando você se levantou, mesmo que você tenha falhado na volta do almoço.<br/><i>Cruz:</i> você falhou nessa sessão, mesmo que tenha cumprido todas as outras vezes. Cumprir o sentar e falhar o levantar, ou o contrário, é cruz.<br/><i>Ponto:</i> você não se sentou a mesa nenhuma, por viagem ou doença de cama.<br/><i>Chegou:</i> ao reconstruir a sessão, você acha a mesa limpa e não acha a decisão de limpá-la; foi a mesa, ao ser vista, que lembrou você.<br/><i>Fora da marca:</i> as outras vezes do dia em que você se sentou ou se levantou.", "Sentar só para pagar contas ou escrever uma carta já é ocasião. No dia em que não houver outra, é ela a que mais pesa."], sai="a lista de cada mesa escrita no caderno, o quarto e a mesa arrumados de uma vez, e a primeira linha da folha de marcas com o número um. No <i>Manual operacional</i>, as ações do grupo <i>Ordem</i>.",
 porque=[
  "<b>A ideia.</b> Epicteto abre o <i>Manual</i> com a frase do alto: algumas coisas dependem de nós, outras não. A mesa está no segundo grupo. O seu ato de arrumá-la, e a escolha de não ir atrás do que está à vista, estão no primeiro, e é nesse ato que o exercício põe a força. Cada objeto sobre a mesa é um convite, e quem trabalha cercado de convites passa a sessão recusando-os com a força que devia ir para a obra.",
  "<b>O mecanismo.</b> O ambiente dispara muito do que fazemos. David Neal, Wendy Wood e colegas observaram em 2011 que um hábito continua agindo contra a preferência enquanto a pista está presente: no cinema, quem tinha o hábito comia a pipoca velha quase tanto quanto a fresca. Tirar a distração tira a pista. E um gesto repetido num momento fixo vai saindo sem pensar, como observou Lally; por isso o gesto se prende ao sentar e ao levantar, que voltam todos os dias.",
  "<b>Por isso.</b> Tiro a distração porque o que está à vista me chama antes de eu decidir, e arrumo para amanhã."],
 saber="Há indícios, no estudo das pipocas de Neal e Wood, de que uma pista à vista dispara o hábito mesmo contra a preferência. Há indícios, no estudo de Lally, de que um gesto repetido num momento fixo se torna automático; os números dele têm as ressalvas de <i>Da medida</i>. Nenhum estudo testou a mesa neutra nem os dois minutos ao se levantar: a passagem dos estudos para este gesto é aposta do autor.")
add("O gesto é o mesmo para quem não tem mesa. O carpinteiro tem a bancada; o músico, a estante e a cadeira; o estudante da mesa da cozinha tem uma caixa onde a obra mora e de onde ela sai inteira quando ele se senta. Quem trabalha numa sala compartilhada ou numa biblioteca leva a <i>mise en place</i> na bolsa. Quem trabalha com o corpo aplica o gesto às ferramentas, e a lista da mesa é a parede onde cada uma tem seu prego.", PI)
proc("Se o gesto falha", [
 "Se a mesa está neutra de manhã e cheia à tarde, dê a cada coisa um lugar fora dela.",
 "Se a arrumação passa de cinco minutos, pare no quinto minuto e comece com a mesa imperfeita.",
 "Se o que mais distrai volta à mesa sem você ver como, ponha-o longe: outro cômodo, uma gaveta fechada.",
 "Se, depois do <i>chegou</i>, a ordem cai na coluna das que ficaram, tire mais uma coisa da lista da mesa.",
])
licao(0)
exe("2", "Do terminar", "H", "Até quando você vai adiar exigir de si o melhor?", "Epicteto",
 "Quando vier o desejo de abrir algo novo: volte ao que está aberto e dê o próximo passo.",
 ["Epicteto faz a pergunta do alto no fim do <i>Manual</i>, a um discípulo que já recebeu os princípios e espera um dia melhor para praticá-los. Você já não é um rapaz, lembra ele, e não há outro mestre por quem esperar. O adiamento se apresenta como preparação, e a forma mais comum de adiar é começar outra coisa.",
  "Em Berlim, nos anos vinte, contava-se no círculo do psicólogo Kurt Lewin a observação de um garçom: ele lembrava sem anotar tudo o que cada mesa pedira enquanto a conta estava por pagar, e esquecia tudo quando a mesa pagava. Uma aluna de Lewin, Bluma Zeigarnik, levou isso ao laboratório, e em 1927 publicou que as tarefas interrompidas voltavam à memória mais vezes do que as terminadas. Cada coisa da sua lista é uma conta por pagar. O exercício aceita duas maneiras de fechá-la: terminá-la, ou encerrá-la por escrito, com a razão.",
  "Edward Gibbon teve a ideia da sua história de Roma em 15 de outubro de 1764, sentado entre as ruínas do Capitólio, enquanto os frades cantavam as vésperas. Terminou-a em Lausanne, na noite de 27 de junho de 1787, entre as onze e a meia-noite. Pousou a pena e andou por uma alameda de acácias, de onde se viam o lago e as montanhas sob a lua. Confessou a alegria da liberdade recuperada e, logo depois, uma melancolia sóbria por se despedir de um velho e agradável companheiro.",
  "Entre a ideia e a última linha passaram vinte e três anos, com o parlamento, as dívidas e a mudança para a Suíça. Gibbon terminou porque sempre voltou ao que estava aberto. A melancolia daquela noite mostra que terminar custa também por dentro: quem fecha uma obra perde a companhia dela. O autor acha que parte do desejo do novo, no ponto difícil, vem da vontade de evitar essa perda.",
  "O livro ruim começado por engano não precisa ser terminado: encerra-se numa linha, <i>paro aqui, porque não me ensina o que procuro</i>. O que o exercício não permite é a coisa nem viva nem morta, que continua cobrando atenção como a conta por pagar."],
 ["No primeiro dia, liste à mão tudo o que está aberto: livros, obras começadas, pendências, promessas.",
  "Quando vier o desejo do novo, escreva-o na folha de captura. Ele espera ali.",
  "Volte ao que está aberto e dê o próximo passo dele, por menor que seja.",
  "À noite, se uma coisa da lista já não pede nada de você, encerre-a por escrito, com a razão."],
 "Dois erros aparecem cedo. No fim de um dia longo, você olha uma coisa quase pronta e a dá por terminada, porque o que falta é pouco e chato; a quinta linha pergunta se está feito ou quase. O outro é confundir encerrar com abandonar. Encerrar é uma decisão escrita, com a razão, que fecha a conta. Abandonar é deixar a coisa apodrecer em silêncio, ainda na lista.",
 "um passo de uma coisa aberta.", "a lista de coisas abertas encolhe, e o novo já não puxa você como antes.",
 comeco=[
  "Você está na noite da primeira passagem e escreveu há pouco <i>chegou</i> ao lado do traço da ordem. Se não escreveu, esta página ainda não é sua: a ordem continua a da vez. Amanhã a ordem passa a ficar, e entra a segunda microação. Ela guarda a obra da fuga mais bem disfarçada: a coisa nova, aberta no meio da sessão, leva a assentada consigo e deixa a outra pela metade, ainda ocupando a cabeça.",
  "Daqui em diante, o número de uma passagem conta só as que trazem um exercício novo. Quando uma das que ficaram volta e chega de novo, a noite também é passagem, com a sua Lição, e esse número não muda.",
  "A ocasião é o desejo de começar uma coisa nova quando outras estão por acabar. A estudante, no meio de um capítulo árduo, quer o livro mais leve que lhe recomendaram. O homem que pinta a casa quer começar a cozinha antes de terminar a sala. A dona de uma pequena loja, no meio de uma encomenda difícil, quer cuidar já de um produto novo. O desejo vem no ponto difícil do que está aberto, com ar de boa ideia e um pequeno alívio.",
  ("O primeiro dia", [
   "Esta noite, releia as linhas II, V e VII do Livro I.",
   "Amanhã, depois do caderno, faça à mão a lista do que está aberto. Completa, sem enfeite.",
   "Guarde a lista na página do caderno reservada a ela.",
   "Quando vier <i>e se eu começasse aquilo agora?</i>, escreva a ideia na folha de captura.",
   "Se você não sabe a que coisa aberta voltar, diga a linha VII e escolha a que você evitaria.",
   "Dê o próximo passo dela.",
   "À noite, ao decidir a folha de captura, deixe as coisas novas esperando (§6).",
   "Olhe a lista. Se uma coisa já não pede nada de você, encerre-a por escrito, com a razão.",
   "· Se o desejo vem várias vezes, pesa mais o do trecho difícil da obra de hoje.",
  ]),
 ],
 marca=["<i>Traço:</i> na vez que mais pesou, você escreveu o desejo e voltou ao que estava aberto, com um passo dado.<br/><i>Cruz:</i> nessa vez, você abriu a coisa nova.<br/><i>Ponto:</i> o desejo do novo não veio o dia inteiro.<br/><i>Chegou:</i> o desejo veio no trecho difícil, e a mão o pôs na folha de captura e voltou ao que estava aberto antes de você se lembrar do caderno. Você percebe isso à noite, ao achar a linha escrita sem lembrar de ter decidido escrevê-la.<br/><i>Fora da marca:</i> o encerramento da noite; uma noite sem nada a encerrar não é falha.", "Depois do <i>chegou</i> fica: o desejo na folha de captura, o passo numa coisa aberta e o encerramento da noite, sempre que a lista o pedir."], sai="a lista à mão de tudo o que está aberto, guardada no caderno; cada desejo do novo numa linha da folha de captura; e o que você encerrou, por escrito, com a razão. No <i>Manual operacional</i>, as ações do grupo <i>Ordem</i>.",
 porque=[
  "<b>A ideia.</b> Kurt Lewin, em Berlim, nos anos vinte, dizia que cada intenção deixa na mente uma tensão, que só se desfaz quando a coisa acaba. Enquanto a coisa fica aberta, a tensão puxa a atenção para ela. A experiência de Zeigarnik foi feita no círculo dele para pôr essa ideia à prova.",
  "<b>O mecanismo.</b> Cada coisa aberta pede atenção enquanto você faz outra; abrir uma nova soma mais uma tensão, por mais alívio que dê. E. J. Masicampo e Roy Baumeister observaram em 2011 que os pensamentos intrusivos sobre uma pendência diminuem quando se faz para ela um plano concreto, antes mesmo de cumpri-la. Por isso o desejo vai para a folha de captura, e cada encerramento leva a razão escrita.",
  "<b>Por isso.</b> Escrevo o desejo e volto ao que está aberto porque o que fica escrito deixa de me interromper."],
 saber="Há indícios, num só artigo de Masicampo e Baumeister com poucos experimentos pequenos, de que um plano concreto para a pendência reduz os pensamentos intrusivos sobre ela. O efeito de Zeigarnik se replicou de modo irregular desde 1927; aqui ele serve de imagem. Nenhum estudo mediu se voltar ao que está aberto faz a obra andar mais depressa: isso é aposta do autor.")
add("Quem tem uma única obra enorme, uma tese, uma casa por construir, tem uma lista curta, e o gesto se aplica dentro dela: o capítulo aberto, a parede começada, a peça na bancada. Quem vive de muitas pendências pequenas, num ofício de atendimento ou no governo de uma casa, dá o próximo passo na mais antiga. Nos estudos, cada livro conta como uma coisa aberta (§6). As promessas feitas a outros se fecham quando cumpridas, ou quando se diz com franqueza que não serão; nesse caso, o encerramento escrito vai também a quem esperava.", PI)
proc("Se o gesto falha", [
 "Se a lista cresce, você abriu o que só devia anotar. Deixe a captura dormir alguns dias antes de decidir.",
 "Se a lista encolhe só por encerramentos, pergunte antes de cada um se a razão convenceria um amigo exigente.",
 "Se o próximo passo é sempre o mesmo e não acaba, corte-o até caber numa sessão, como a linha IV.",
 "Se o desejo do novo segue forte depois de semanas, anote a hora em que ele chega.",
 "· Essa hora é a do trecho difícil.",
])
licao(1)
exe("3", "Da absorção", "H", "Quem está em toda parte não está em lugar nenhum.", "Sêneca",
 "Quando você perceber que se dispersou: a terceira linha. E a primeira hora do dia longe das distrações do seu tempo.",
 ["Em Down, no condado de Kent, Darwin mandou abrir nos anos quarenta do século XIX um caminho de areia em volta de um bosque nos fundos da casa, o Sandwalk. Percorria-o todos os dias, sozinho ou com o cachorro. O filho Francis lembra que ele deixava um monte de pedras na entrada e derrubava uma a cada volta, para saber quantas dera sem contar. As melhores horas da manhã eram do trabalho. Doente boa parte da vida, Darwin trabalhava poucas horas por dia, mas horas inteiras.",
  "Darwin deu ao corpo a conta das voltas para não pensar nela. A sessão com começo e fim marcados faz o mesmo: tira de você a pergunta <i>quanto falta?</i>. E o caminho era sempre o mesmo, sem nada novo para ver, para que a atenção só tivesse o problema. A primeira hora longe das distrações é o seu Sandwalk.",
  "Guilherme de Tocco, que conheceu Tomás de Aquino, conta que em Paris Tomás foi convidado à mesa do rei Luís IX. Trabalhava então contra os maniqueus, e no meio da refeição ficou calado, preso ao problema. De repente bateu na mesa e disse que estava concluído contra os maniqueus. O prior lembrou-lhe que estava à mesa do rei da França. Tomás pediu desculpas, e o rei mandou chamar um secretário para que o argumento fosse escrito antes que se perdesse. Diante da distração mais nobre de Paris, a atenção ficou no problema.",
  "Os estoicos chamavam de <i>prosoché</i> a atenção que permanece, o estar voltado para. Epicteto avisa que quem afrouxa a atenção não a recupera quando quer: o descuido de hoje facilita o de amanhã, e assim se forma o hábito de não prestar atenção. Nunca errar é impossível, diz ele; estar sempre voltado para não errar, não. A dispersão vem, e por isso o exercício pede a volta. O que se forma, se você não vigiar, é o hábito de não voltar logo."],
 ["Trabalhe em sessões com começo e fim marcados.",
  "Comece com sessões de vinte e cinco a quarenta e cinco minutos. Alongue-as quando ficarem fáceis.",
  "Antes de cada sessão, escreva a única coisa em que você vai estar nela.",
  "Quando perceber que se dispersou, diga a linha III: <i>saí; onde eu estava?</i>",
  "Releia a última linha da obra.",
  "Escreva o pensamento que puxou você na folha de captura, numa linha.",
  "Continue.",
  "Passe a primeira hora do dia, do acordar em diante, longe das distrações do seu tempo."],
 "No fim de uma sessão em que você saiu vinte vezes, vem a vontade de fazer a conta e lê-la como sentença. Contar as voltas como fracassos é o primeiro erro: cada volta é uma repetição do exercício. O segundo é começar com sessões longas demais, uma hora e meia na primeira manhã, e desanimar no primeiro dia.",
 "uma sessão de vinte e cinco minutos.", "você volta mais depressa e as sessões se alongam sem esforço.",
 comeco=[
  "Você está na noite da segunda passagem. O terminar chegou e amanhã passa a ficar, ao lado da ordem. Amanhã entra a terceira microação, e com ela a linha III, a da dispersão; releia-a esta noite. Ela fecha o vazamento que ninguém decide: o pensamento que leva a atenção para longe do <i>isto</i> enquanto você continua sentado.",
  "O exercício treina a volta. A linha III diz para onde você volta; <i>Isto, até acabar</i> diz até quando fica. O fim marcado da sessão é a medida mínima, o tempo que você dá à coisa antes de se levantar. O fim de <i>isto</i> pertence à coisa.",
  "A ocasião é o instante em que você percebe que saiu. O instante de sair não se nota; nota-se o de depois, segundos ou minutos mais tarde. O estudante descobre que leu a mesma página três vezes. A costureira percebe que a mão parou na bainha e o pensamento foi para uma conversa da véspera. Ou você percebe que a mão foi buscar o que distrai sem ordem sua.",
  ("O primeiro dia", [
   "Esta noite, ao escrever a primeira tarefa, escreva também o que você fará na primeira hora de amanhã.",
   "Amanhã de manhã, decida quantas sessões fará, a que horas e de que tamanho.",
   "Comece a primeira hora pelo caderno, antes de qualquer distração.",
   "Na primeira hora, comece a primeira tarefa.",
   "Quando perceber que saiu, diga <i>saí; onde eu estava?</i>",
   "Se vier <i>de novo, não aguento nem dez minutos</i>, diga a linha III outra vez.",
   "· Essa frase também é dispersão, agora contra você mesmo.",
   "Se a sessão acaba e <i>isto</i> não, termine o passo em que está.",
   "Escreva a mesma coisa antes da sessão seguinte.",
   "· Pesa mais a sessão da obra de hoje. Nos primeiros dias, as saídas vêm às dezenas.",
  ]),
 ],
 marca=["<i>Traço:</i> na sessão da obra de hoje, você voltou com a linha III em vez de seguir a dispersão.<br/><i>Cruz:</i> nessa sessão, você ficou fora.<br/><i>Ponto:</i> só num dia sem obra nenhuma que peça atenção, como um dia de cama. Pular as sessões marcadas para não ter de voltar não dá ponto.<br/><i>Chegou:</i> na sessão da obra, <i>onde eu estava?</i> veio sozinha no instante em que você percebeu que saiu, e você voltou antes de se lembrar do exercício. Se precisou se lembrar da linha para voltar, não chegou.<br/><i>Fora da marca:</i> quantas vezes você saiu; a primeira hora e a única coisa escrita antes de cada sessão, que servem à volta.", "A linha da primeira hora, escrita à noite, acompanha o exercício enquanto ele é a da vez e acaba quando ele chega. Depois basta a primeira tarefa.", "Depois do <i>chegou</i> fica: a volta com a linha III na sessão da obra."], sai="a primeira hora do dia longe das distrações, escrita na véspera; sessões com começo e fim marcados, cada uma com a sua única coisa escrita antes; e a volta com a linha III quando você percebe que saiu. No <i>Manual operacional</i>, as ações do grupo <i>Atenção e obra</i>.",
 porque=[
  "<b>A ideia.</b> Sêneca escreve a Lucílio que quem está em toda parte não está em lugar nenhum, e que o espírito que pula de coisa em coisa não cria raízes. Nunca se dispersar é impossível. O que se treina é a volta, cada vez mais rápida, e uma hora por dia em que nada puxa você para fora.",
  "<b>O mecanismo.</b> Está demonstrado que cada troca de atividade custa tempo e erros, mesmo prevista; Stephen Monsell reviu esses estudos em 2003. A sessão com uma só coisa e a volta rápida reduzem as trocas. E a linha III é um plano decidido antes, <i>quando eu perceber que saí, digo isto</i>. Os estudos mostram, na revisão de Peter Gollwitzer e Paschal Sheeran (2006), que planos assim aumentam a chance de a ação acontecer: no instante da dispersão, já não há o que decidir.",
  "<b>Por isso.</b> Digo <i>saí; onde eu estava?</i> e releio a última linha porque a frase pronta me poupa a decisão."],
 saber="Está demonstrado que a troca de atividade custa, em frações de segundo, em tarefas de laboratório; levar isso a uma manhã de obra é aposta do autor. Os estudos mostram que os planos <i>se... então</i> funcionam, com efeito médio e muita variação de um comportamento para outro. Nenhum estudo testou a linha III nem a primeira hora longe das distrações.")
add("Quem trabalha com pessoas, no balcão, na sala de aula, junto de um doente, tem conversas, aulas e plantões no lugar de sessões solitárias. O gesto é o mesmo: antes de cada um, a única coisa que deve acontecer nele; durante, a linha III sempre que o espírito se afastar da pessoa à sua frente. Quem faz obra manual mede a sessão pela peça, pela parede, pelo canteiro, com começo e fim marcados antes de pegar a ferramenta. Quem estuda senta com o livro, a caneta e a folha de captura, e mais nada.", PI)
proc("Se o gesto falha", [
 "Se a dispersão chega sempre perto do mesmo minuto, encurte a sessão em cinco minutos.",
 "Alongue-a só depois de três sessões seguidas sem esforço.",
 "Se você volta e não sabe para onde, escreva a única coisa antes da sessão.",
 "Se as voltas não encurtam em semanas, olhe o sono das noites (§8).",
 "Se o que puxa você vem dos objetos, confira na coluna das que ficaram se a ordem anda caindo.",
 "Se a primeira hora se desfaz em dez minutos, escolha na véspera o que fazer nela, com começo e fim.",
])
licao(2)
exe("4", "Do corpo", "H", "É vergonha envelhecer sem conhecer a força do próprio corpo.", "Sócrates",
 "Quando você chegar ao treino: nada que distraia vai com você, a ficha de papel vai na mão, e a ficha é cumprida inteira.",
 ["Para os gregos, a ginástica fazia parte da formação da alma. Platão abriu a sua escola num ginásio junto ao bosque de Academo, e Aristóteles ensinou em outro, o Liceu. Na <i>República</i>, Platão diz que a ginástica e a música foram dadas ao homem, as duas, por causa da alma: quem só faz ginástica fica bruto, quem só faz música fica mole, e a educação acerta quando afina uma contra a outra, como as cordas de um instrumento. Por isso um exercício do corpo entra num livro sobre a obra.",
  "De Crotona vem a lenda do lutador Mílon, vencedor em Olímpia. Quando rapaz, ele carregava um bezerro nos ombros todos os dias, e continuou carregando à medida que o animal crescia, até levar nas costas um touro. É lenda. Ela diz em imagem a regra de progressão deste exercício: a carga sobe tão devagar que o corpo não percebe, e cada dia leva um pouco mais que o anterior.",
  "No <i>Banquete</i>, Alcibíades conta o que viu de Sócrates na campanha de Potideia. Quando faltava comida, Sócrates aguentava a fome melhor que todos. No inverno terrível daquela região, andava descalço sobre o gelo com a capa de sempre. Num dia de verão ficou de pé, da madrugada à madrugada seguinte, pensando num problema. A obra dele era de cabeça, como a sua. O corpo treinado lhe dava disponibilidade: o frio, a fome e a vigília não decidiam por ele.",
  "Na passagem de Xenofonte de onde vem a frase do alto, Sócrates lembra ao jovem Epígenes que muitos falham no próprio pensamento por causa da saúde ruim, com o esquecimento, o desânimo e o mau humor que ela traz. A ficha anotada é um lugar onde é difícil se enganar: ela diz o que você levantou. E o corpo é onde o hábito fica. Por isso a máscara inclui o corpo de <i>ele</i>: a postura com que se senta para a obra, o passo com que chega ao treino, a respiração entre as séries. Você os copia como copia os outros meios; o livro não promete que mudem o que você sente."],
 ["Antes de sair, escreva a ficha: exercícios, séries, repetições, carga.",
  "No treino, anote cada série feita, com a carga real.",
  "Se cumpriu todas as repetições de um exercício em dois treinos seguidos, aumente um pouco a carga ou as repetições.",
  "No fim do treino, compare com a ficha anterior.",
  "Mude no máximo uma coisa."],
 "Há três erros. Treinar sem plano faz de cada treino uma negociação nova. Mudar a ficha inteira numa noite de entusiasmo apaga a comparação com o treino anterior. E buscar a exaustão no lugar da progressão: sair destruído não mostra que o treino foi bom.",
 "dez minutos de movimento, ou uma caminhada.", "a ficha é cumprida sem negociação e os números sobem devagar.",
 comeco=[
  "Você está na noite da terceira passagem. A absorção chegou, e amanhã serão três as que ficaram. Entra o último exercício da primeira estação, o único feito longe da mesa. De longe, ele serve à mesa: o corpo parado chega à assentada com a inquietação que encurta a sessão antes que o <i>isto</i> acabe.",
  "A ocasião é a chegada ao treino, nos dias e na hora que a ficha marca: a sala de musculação, a pista, a piscina, o parque onde um aposentado caminha todas as manhãs, o canto da sala onde uma mãe estende um tapete depois de pôr os filhos para dormir. Com ela vêm a vontade de levar a distração, de improvisar, de cortar as duas últimas séries.",
  ("O primeiro dia", [
   "Amanhã de manhã, se ainda não tem a ficha, escreva-a.",
   "Escreva os dias da semana e a hora do treino.",
   "Para cada treino, escreva os exercícios, as séries, as repetições e a carga.",
   "Se você não sabe por onde começar, comece com pouco.",
   "Se você tem lesão, doença ou muitos anos, escreva a ficha com quem entende do seu caso.",
   "Num dia de treino, preveja de manhã a hora da chegada.",
   "Se a ficha não marca treino para amanhã, a noite leva ponto.",
   "Na chegada, deixe a distração para trás e cumpra a ficha inteira.",
   "· A voz antiga pechincha: <i>levo isto só para o intervalo</i>; <i>as duas últimas séries não fazem diferença</i>.",
  ]),
  "O preço do atleta de Epicteto, a hora marcada, o calor e o frio, não se pechincha. As frases ficam sem resposta. A ocasião vem uma vez por dia de treino, e por isso ela mesma é a que mais pesa. Cada série que você pensa em pular faz parte dela.",
 ],
 marca=["<i>Traço:</i> num dia de treino, você chegou sem o que distrai, com a ficha, e a cumpriu inteira.<br/><i>Cruz:</i> você cortou a ficha, levou a distração ou não foi no dia e na hora marcados; a ocasião chegou na hora marcada, mesmo que você não tenha chegado.<br/><i>Ponto:</i> nos dias em que a ficha não marca treino.<br/><i>Chegou:</i> você saiu para o treino com a ficha na mão e a distração deixada para trás sem pensar nisso, como quem pega as chaves ao sair de casa; foi a hora do treino que lembrou você.<br/><i>Fora da marca:</i> a anotação das séries, a progressão e a comparação com o treino anterior.", "Depois do <i>chegou</i> fica: chegar ao treino sem o que distrai, com a ficha, e cumpri-la inteira."], sai="a ficha escrita, com dias, hora, exercícios, séries, repetições e carga; cada treino anotado com a carga real; e uma só mudança de cada vez, decidida no fim do treino. No <i>Manual operacional</i>, as ações do grupo <i>Corpo</i>, e antes delas <i>Dos cuidados</i>.",
 porque=[
  "<b>A ideia.</b> Sócrates, nas <i>Memoráveis</i> de Xenofonte, diz a um jovem que descuidava do corpo que é vergonha envelhecer sem ver a força e a beleza de que o corpo é capaz. Para ele o corpo fazia parte da formação de quem pensa. O exercício toma a ideia pela maneira: um plano escrito antes, cumprido inteiro, sem distração, anotado.",
  "<b>O mecanismo.</b> Os estudos mostram que um treino melhora o humor e, um pouco, o desempenho mental logo depois; Yu-Kai Chang e colegas reuniram em 2012 os estudos de treinos únicos e acharam um efeito real e pequeno. Benjamin Harkin e colegas mediram que registrar o progresso aumenta a chance de alcançar o objetivo, mais ainda quando o registro é físico. A ficha anotada é esse registro: diz se você cumpriu e se a carga sobe.",
  "<b>Por isso.</b> Anoto cada série porque o corpo treinado sustenta a cabeça da obra, e o papel mostra se avanço."],
 saber="Está demonstrado que o exercício melhora o humor. Há indícios de um ganho pequeno no desempenho mental logo depois de um treino, na revisão de Chang. Há indícios de um efeito moderado do registro físico do progresso, na de Harkin. Nenhum estudo testou a ficha cumprida inteira nem a regra de não levar distração. Que o treino melhora a obra do dia é aposta do autor.")
add("A ficha é sua, e o gesto se adapta a qualquer corpo. Quem tem lesão, doença crônica ou muitos anos progride no que pode progredir: amplitude, equilíbrio, distância, tempo. Quem não pode sair treina em casa, e a ocasião é a chegada ao canto da sala. Quem trabalha com o corpo o dia inteiro, na obra ou no campo, faz uma ficha para o que o ofício deixa parado. Quem corre, nada ou luta escreve as séries em distâncias, tempos ou assaltos.", PI)
proc("Se o gesto falha", [
 "Se os números param três ou quatro semanas, confira o sono e a comida.",
 "Se, com sono e comida em ordem, eles ainda param, faça um aumento menor.",
 "Se aparece uma dor diferente da do músculo trabalhado, volte à carga anterior.",
 "Se a dor continua, procure quem saiba avaliá-la antes de voltar à ficha.",
 "Se você cumpre a ficha e esquece de anotar, deixe em casa a distração que foi junto.",
 "Se você falta sempre nos mesmos dias, mude a hora do treino antes de pôr em dúvida a vontade.",
])
licao(3)
estacao("Segunda estação", "Da ação criativa.")
st.extend(PEND); PEND.clear()
add("Você está na noite da quarta passagem. Escreveu <i>chegou</i> ao lado do traço do corpo, leu a Lição, releu a folha do dia zero e <i>Do homem</i>, fez as emendas que as marcas pediam. Na folha de marcas, o número subiu quatro vezes desde o dia um, e cada subida foi uma noite como esta. Se os quatro gestos chegaram, a mesa se arruma quase sozinha, as coisas abertas diminuíram, as sessões se alongaram e a ficha se cumpre sem negociação. É sobre esse chão que <i>Isto, até acabar</i> se sustenta por uma tarde inteira.", PI)
add("Aqui o caminho começa a subir. A segunda estação entra na obra: a hora no domínio, o que dela fica na memória, a crítica de quem sabe mais, as pessoas com quem se trabalha. Ninguém treina no limite numa mesa cheia, com seis coisas abertas e a atenção fugindo; por isso a primeira estação veio antes. Antes de fechar o caderno, leia o exercício que entra amanhã.", PI)
exe("5", "Da prática deliberada", "H", "Sem pressa, mas sem pausa.", "Goethe",
 "Quando você começar a obra no seu domínio: pela parte mais difícil, sem preâmbulo. À noite, anote as horas reais.",
 ["Benjamin Franklin conta na <i>Autobiografia</i> como aprendeu a escrever, ainda aprendiz de tipógrafo em Boston. Achou um volume do <i>Spectator</i>, o jornal de Addison e Steele, e achou a escrita excelente. Pegava um ensaio, anotava em poucas palavras o sentido de cada frase e deixava as notas de lado alguns dias. Depois, sem olhar o original, reescrevia o ensaio com as suas palavras, comparava com o jornal e corrigia as falhas. Quando lhe faltaram palavras, passou os ensaios a verso e de volta a prosa. Para aprender a ordem, embaralhava as notas e as reordenava. Fazia isso à noite, de madrugada e aos domingos.",
  "Franklin arranjou um modelo melhor que ele, um modo de se medir contra o modelo e uma dificuldade precisa em cada fase: o sentido, depois o vocabulário, depois a ordem. É a máscara feita na página: copiou os meios de um modelo real, mediu a distância, e a distância encurtou. Sem um alvo, a hora na parte difícil é só sofrimento. Com ele, cada sessão termina com uma resposta a <i>consegui ou não consegui</i>. Um alvo claro, um modo de saber se você vai bem e uma dificuldade um pouco acima do que você tem: Csikszentmihalyi descreve essas condições como as do estado de foco que dá nome a este livro.",
  "Em 1993, Anders Ericsson, Ralf Krampe e Clemens Tesch-Römer estudaram os violinistas de uma escola superior de música de Berlim. Por volta dos dezoito anos, os melhores tinham acumulado milhares de horas a mais de prática solitária dirigida a uma dificuldade, que eles mesmos apontavam como a mais útil e a menos agradável. Os melhores dormiam mais, e quase nenhum sustentava mais de umas quatro horas por dia daquela prática. Vinte e um anos depois, Brooke Macnamara, David Hambrick e Frederick Oswald mediram que essa prática explica uma parte modesta das diferenças de desempenho, e menor nas profissões. A hora no ponto de falha é a parte do caminho que depende de você.",
  "Quem quer oito horas por dia de prática no limite acaba fazendo oito horas de ocupação. A soma das noites de passagem só serve se for verdadeira, mesmo pequena. A comparação que conta é com você mesmo, com e sem esta prática."],
 ["Antes da sessão, escolha a parte mais difícil da obra, a que você evitaria se pudesse.",
  "Escreva o melhor de hoje: o que você vai conseguir no fim da sessão e não consegue agora.",
  "Comece a sessão por ela. Sem preparação, sem coisas menores antes.",
  "À noite, anote as horas reais, sem as pausas.",
  "Na noite de passagem, some as horas do caminho."],
 "Há dois modos de falhar que parecem obra. No primeiro, você passa a tarde no domínio, sempre ocupado, e à noite as horas são muitas e nada ficou mais difícil: a tarde foi no que você já sabia fazer. No segundo, você faz o fácil primeiro para aquecer, e a sessão acaba antes de chegar ao difícil.",
 "quinze minutos na parte difícil.", "as horas se mantêm ao longo dos meses e a dificuldade do que você faz aumenta.",
 comeco=[
  "A quinta microação treina o começo da obra no domínio. Sem ela, a sessão começa pelas coisas menores, que parecem obra e gastam a melhor hora, e a parte difícil fica para quando falta força.",
  "A ocasião é o momento em que você começa a obra no domínio do terceiro ponto da sua folha. Para quem escreve, é abrir o manuscrito; para o violinista, tirar o violino do estojo; para o carpinteiro, pegar a primeira peça do dia; para a médica que estuda uma especialidade, abrir o capítulo que vem adiando. Com ela vem a tentação: arrumar antes, rever o feito, despachar o fácil para aquecer.",
  ("O primeiro dia", [
   "Amanhã de manhã, depois da linha da manhã, escolha a parte difícil.",
   "Escreva numa linha o melhor de hoje.",
   "Na folha de marcas, dê à linha de amanhã o número cinco.",
   "Se a obra de hoje é no domínio e abre a manhã, faça da parte difícil a primeira tarefa.",
   "Se a obra começa mais tarde, abra a sessão por ela, na hora dela.",
   "Se vier <i>primeiro reviso o que fiz ontem</i>, diga a linha VII e comece.",
   "Se a parte difícil travar e você não souber por quê, diga a linha IV.",
   "Escreva a pergunta numa linha e faça a menor parte.",
   "À noite, antes da marca, anote as horas reais.",
   "· Se você está no domínio mais de uma vez por dia, pesa mais a sessão principal.",
  ]),
  "Com este exercício chega a linha IV, a do impasse: <i>O que exatamente eu não sei? Qual é a menor parte que posso fazer agora?</i> A linha VII você conhece desde as primeiras semanas: <i>Qual delas eu evitaria, se pudesse? Essa.</i>",
 ],
 marca=["<i>Traço:</i> na sessão principal no domínio, você começou pela parte difícil, sem preâmbulo.<br/><i>Cruz:</i> a sessão começou pelo fácil. Se você só chegou à parte difícil depois de rever um pouco e hesita, é cruz.<br/><i>Ponto:</i> só num dia em que a circunstância impediu a obra no domínio. Um dia sem domínio por adiamento não dá ponto: a ocasião estava nas suas alavancas.<br/><i>Chegou:</i> ao se sentar para o domínio, a mão foi direto à parte que você evitaria, sem preparação, antes de você se lembrar do exercício.<br/><i>Fora da marca:</i> o melhor de hoje, escrito de manhã, e as horas reais, anotadas à noite.", "Depois do <i>chegou</i> fica: começar a sessão principal pela parte difícil, e as horas reais anotadas todas as noites, sem arredondar. A soma das noites de passagem e o sinal dependem delas."], sai="a parte mais difícil escolhida de manhã, com o melhor de hoje escrito numa linha; a sessão principal começada por ela; e as horas reais anotadas a cada noite e somadas nas noites de passagem. No <i>Manual operacional</i>, as ações do grupo <i>Atenção e obra</i>.",
 porque=[
  "<b>A ideia.</b> A frase do alto é de Goethe, que em versos curtos da velhice pede que cada um gire em volta do próprio fardo como um astro, sem pressa, mas sem pausa. A pressa gasta em semanas a força que os anos pedem; a pausa perde o que se ganhou. É o passo das horas reais, poucas e verdadeiras. Prática deliberada é o nome que Anders Ericsson deu em 1993 a um tipo preciso de obra: a sós, no ponto em que você ainda falha, com um alvo e um modo de saber se o atingiu. As horas que repetem o que já se sabe enchem o dia e deixam a habilidade onde estava.",
  "<b>O mecanismo.</b> Os violinistas de Ericsson apontavam a prática dirigida a uma dificuldade como a que mais os fazia melhorar; por isso se escolhe a parte que você evitaria e se escreve o melhor de hoje. Essa prática é pouco agradável, tem limite e gasta a energia que houver. Por isso vem primeiro, sem esperar vontade (§3). As horas reais mostram quanto dela houve.",
  "<b>Por isso.</b> Começo pela parte que evitaria porque só melhoro onde falho, e isso pede a cabeça fresca."],
 saber="Há indícios, no estudo de 1993, de que os melhores violinistas de uma escola tinham praticado mais a sós; o estudo compara grupos com horas lembradas pelos músicos e não prova que uma coisa produz a outra. Os estudos mostram, na revisão de Macnamara, Hambrick e Oswald (2014), que essa prática explica uma parte modesta do desempenho, que muda de um domínio para outro. A regra de começar pelo mais difícil não foi testada: é aposta do autor.")
add("No ofício manual, a parte difícil é o corte que sai torto, a junta que abre; o modelo é a peça do mestre, posta ao lado da sua. Na música e no esporte, é o compasso ou o movimento que se evita, isolado e repetido devagar. Em ofícios de pessoas, ensinar, vender, cuidar, é a conversa que se adia ou a situação em que você falha, treinada antes por escrito ou em voz alta, como Franklin treinava o ensaio. Quem tem o domínio nas horas vagas, ao lado de outro emprego, faz menos horas e o mesmo gesto.", PI)
proc("Se o gesto falha", [
 "Se as horas sobem e a dificuldade não, escreva um melhor de hoje que você ainda não consegue cumprir.",
 "· O sinal disso é que você nunca erra.",
 "Se as horas caem dia após dia, desça um degrau: algo que você consegue uma vez em três tentativas.",
 "Se, dez minutos depois de começar, você está em outra coisa, diga a linha II ou a linha IV.",
 "Se as horas somadas parecem poucas, escreva-as como são.",
 "· Arredondadas, elas deixam de mostrar se aumentam.",
])
licao(4)
exe("6", "Do aprender", "H", "Enquanto ensinamos, aprendemos.", "Sêneca",
 "Quando você fechar o livro ou terminar o estudo: um ou dois minutos, e diga ou escreva o essencial, de memória.",
 ["Na carta 84, Sêneca escreve a Lucílio que devemos imitar as abelhas: andam de flor em flor, escolhem o que serve ao mel e depois o misturam nos favos até que já não se reconheça a flor. O que se juntou da leitura deve ser separado e depois fundido pelo nosso engenho num só sabor. O alimento que fica inteiro no estômago pesa; só nutre digerido. Ler é recolher, e o saber vem depois, quando quem leu dá ao que leu a sua forma. Escrever de memória, ao fechar o livro, é a forma mais curta dessa digestão.",
  "Durante séculos, os estudantes da Europa fizeram essa digestão num caderno. Erasmo de Roterdã, no <i>De copia</i>, mandava preparar um livro com títulos, as virtudes, os vícios, os grandes temas, e copiar embaixo de cada um o melhor que se lia. O valor estava na escolha do título, que obrigava a decidir de que tratava o que se acabara de ler. As três ideias que você escreve ao fechar o livro pedem a mesma decisão.",
  "A frase do alto vem da sétima carta: fuja da multidão e conviva com quem pode tornar você melhor e com quem você pode tornar melhor, porque os homens, enquanto ensinam, aprendem. Explicar em voz alta é a recordação mais exigente, porque o ouvinte, mesmo imaginado, não aceita saltos. Onde quem explica hesita, ali estava o que não entendeu.",
  "Em 1812, Michael Faraday, aprendiz de encadernador em Londres, ganhou de um freguês entradas para as conferências de Humphry Davy na Royal Institution. Tomou notas e, em casa, reescreveu-as por extenso, com o que ouvira e o que entendera, e com desenhos dos aparelhos. Encadernou o volume e o mandou a Davy, pedindo emprego. Em março de 1813 era assistente de laboratório na mesma casa. Anos depois criou ali as conferências de Natal para os jovens; a mais conhecida, sobre a história química de uma vela, não pulava nenhum passo. Reescrever de memória e depois explicar: são as duas metades deste exercício."],
 ["Ao fechar o livro, antes de se levantar, escreva de memória as três ideias principais. Não olhe.",
  "Abra o livro e confira.",
  "Corrija o que você esqueceu ou entendeu mal.",
  "Uma vez por dia, explique em voz alta, por um minuto, algo que estudou hoje, como numa aula.",
  "Na margem de cada livro, escreva pelo menos uma discordância sua. <font color='#6b6b6b'>(Lição VI)</font>"],
 "O erro comum tem ar de zelo: no lugar de recordar, você relê, e a releitura dá a sensação de saber sem que você saiba. O outro é resumir copiando o texto, frase por frase, com o livro aberto ao lado.",
 "uma frase de memória.", "você explica o que estudou nos últimos dias sem consultar nada.",
 comeco=[
  "É a noite da quinta passagem. Você escreveu <i>chegou</i> ao lado do traço da prática deliberada, e são cinco as que ficaram. O exercício do aprender cabe em um ou dois minutos no fim de cada estudo. Ele tira da obra a ilusão de saber: a página relida parece aprendida, e o que não ficou só aparece no meio da assentada, quando o <i>isto</i> precisa dele.",
  "A ocasião é o fim de uma leitura ou de um estudo: fechar o livro, terminar a aula, sair de uma lição. O operário que lê no caminho do emprego a tem ao chegar; o aprendiz, quando o mestre acaba de lhe mostrar um movimento. Com ela vem o impulso de fechar e seguir, ou de voltar a ler o que acabou de ler.",
  ("O primeiro dia", [
   "Amanhã de manhã, veja quando você vai ler ou estudar.",
   "Ponha ao lado do livro uma folha e uma caneta.",
   "Escolha a hora do minuto em voz alta. O fim do último estudo do dia serve.",
   "Ao fechar o livro, deixe-o fechado.",
   "Escreva as três ideias como vierem.",
   "No minuto em voz alta, diga a aula inteira, mesmo que se sinta um impostor.",
   "· Se você estuda várias vezes, pesa mais o estudo mais longo, ou o do assunto que mais custa.",
  ]),
  "As três ideias vêm piores do que você esperava, e é por virem piores que a conferência tem o que ensinar. O minuto em voz alta parece ridículo na primeira vez, numa sala vazia, dando aula para ninguém.",
 ],
 marca=["<i>Traço:</i> no estudo principal, ao fechar o livro, você recordou de memória antes de reler.<br/><i>Cruz:</i> você fechou e seguiu, ou releu no lugar de recordar. Se não sabe se escreveu de memória ou com um olho na página, é cruz.<br/><i>Ponto:</i> nos dias sem leitura nem estudo.<br/><i>Chegou:</i> ao fechar o livro, você já dizia por dentro as ideias principais antes de se lembrar do caderno. Se foi a folha ao lado do livro que lembrou você, não chegou.<br/><i>Fora da marca:</i> a conferência, o minuto em voz alta e a discordância na margem.", "Depois do <i>chegou</i> fica: recordar de memória ao fechar o livro, antes de reler."], sai="as três ideias de cada estudo escritas de memória e corrigidas, um minuto por dia em voz alta sobre o que você estudou, e uma discordância sua na margem de cada livro. No <i>Manual operacional</i>, as ações do grupo <i>Aprender</i>.",
 porque=[
  "<b>A ideia.</b> Quem explica algo a outra pessoa põe em ordem o que sabe, sem saltos, e descobre nesse esforço onde o saber lhe falta. Escrever de memória ao fechar o livro é dar essa aula a você mesmo. O psicólogo Henry Roediger passou anos mostrando que recordar já é aprender: cada vez que você tira uma ideia da memória, ela fica mais fácil de achar na vez seguinte.",
  "<b>O mecanismo.</b> Está demonstrado que testar-se retém mais que reler. Em 2006, Roediger e Jeffrey Karpicke mediram que, uma semana depois de estudar um texto, quem tentou recordar lembrava muito mais, e quem só releu estava mais confiante de que ia lembrar. Recordar custa, e esse custo engana: a releitura parece fácil porque o texto ficou familiar, e a familiaridade passa por saber. A conferência logo depois corrige o resto.",
  "<b>Por isso.</b> Fecho o livro e escrevo de memória porque o que tiro dela fica, e o relido só parece sabido."],
 saber="Está demonstrado, em centenas de experimentos e em salas de aula, que recordar retém mais que reler; as revisões de Rowland (2014) e de Dunlosky e colegas (2013) o confirmam. Os estudos usaram sobretudo textos, listas e matéria escolar; para habilidades do corpo e obras longas, os indícios são mais fracos. O gesto de um ou dois minutos é uma versão curta do que se testou, sem ensaio próprio.")
add("Quem aprende um ofício com as mãos repete de memória, sem o mestre olhando, o movimento que acabou de aprender, e só depois confere. Quem aprende ouvindo faz a recordação ao sair, em três frases ditas por dentro e escritas ao chegar. Quem lê pouco recorda a cada capítulo. O minuto em voz alta aceita um ouvinte de verdade: um filho, um colega, um amigo paciente.", PI)
proc("Se o gesto falha", [
 "Se nada vem ao fechar o livro, diga a linha III durante a leitura.",
 "Recorde ao fim de cada capítulo, e não só ao fim do estudo.",
 "Se vêm só detalhes, pergunte primeiro <i>o que o autor quer que eu pense?</i> e escreva isso.",
 "Se a conferência mostra sempre os mesmos erros, releia só a parte mal entendida.",
 "Se a aula em voz alta parece ridícula, escreva-a como carta a alguém. A carta também não aceita saltos.",
 "Se as discordâncias na margem são todas de forma, procure uma de fundo.",
 "· Sem discordância de fundo, você ainda lê para concordar.",
])
licao(5)
exe("7", "Da crítica", "J", "Viva como se alguém que você respeita o observasse.", "Sêneca",
 "Quando você entregar a obra a quem sabe mais: peça a crítica, ouça sem se defender, corrija.",
 ["Horácio, já poeta celebrado, escreveu aos Pisões a carta que depois se chamou <i>Arte poética</i>. Perto do fim, lembra um amigo morto, Quintílio. Se você lesse algo para ele, Quintílio dizia: <i>corrija isto, e isto</i>. Se você respondesse que já tentara duas e três vezes, ele mandava riscar e devolver à bigorna os versos mal torneados. Se você preferisse defender o defeito a emendá-lo, ele não gastava nem mais uma palavra: deixava você amar, sozinho e sem rival, a si mesmo e à sua obra. No mesmo poema, Horácio manda guardar o escrito até o nono ano, porque o que fica em casa ainda se risca. Por isso o exercício leva a obra ao crítico inacabada.",
  "O castigo de Quintílio é parar de falar. Quem se defende de toda crítica recebe de todos esse silêncio, e fica sem ninguém que lhe aponte os defeitos da obra.",
  "Plutarco escreveu um tratado inteiro sobre como distinguir o bajulador do amigo. O bajulador imita tudo, como o camaleão, que toma todas as cores menos o branco: imita seus gostos, seus defeitos, seu riso, e só não imita o que você tem de bom. Não preciso de um amigo que muda quando eu mudo e acena quando eu aceno, diz ali; minha sombra faz isso melhor. O amigo se reconhece pela franqueza, que age como remédio: dói, pede o momento certo, é dada a sós e nunca para humilhar.",
  "Às vezes quem sabe mais está longe. Em outubro de 1705, Johann Sebastian Bach, com vinte anos e organista em Arnstadt, pediu quatro semanas de licença e foi a pé a Lübeck, a uns quatrocentos quilômetros, ouvir Dietrich Buxtehude. Ficou cerca de quatro meses. Na volta, o consistório lhe pediu contas da ausência e reclamou das variações estranhas que ele passara a pôr nos corais. A música dele já não era a mesma.",
  "O crítico também erra: há quem critique por inveja, por pressa ou pelo gosto de ferir. Por isso o gesto tem duas metades separadas no tempo. No instante, você ouve inteiro e anota. O juízo vem à noite, longe do calor, quando a vaidade já não está de guarda. A defesa no instante não protege da crítica injusta e impede você de ouvir a justa que vem logo atrás dela."],
 ["Escolha a quem pedir: alguém que saiba mais e que diga a verdade.",
  "Pergunte <i>o que está mais fraco aqui?</i> Não pergunte <i>o que você acha?</i>",
  "Ouça até o fim.",
  "Não explique nem justifique. Agradeça.",
  "Anote a crítica.",
  "Corrija.",
  "Mostre a correção a quem criticou você.",
  "· Mostrar a correção é o que faz o crítico voltar a falar."],
 "Há três erros, e o primeiro engana quem o comete: pedir elogio disfarçado de crítica, com uma pergunta ampla, a quem gosta de você. O segundo é ficar se explicando enquanto o outro fala. O terceiro é aceitar tudo sem examinar: o juízo da noite existe para isso.",
 "releia sua obra como o crítico a leria e escreva três fraquezas.", "pedir crítica deixou de custar, e corrigir se tornou o passo seguinte natural.",
 comeco=[
  "Você está na noite da sexta passagem, com a prática deliberada e o aprender entre as que ficaram. Este é o primeiro exercício J. A obra feita no limite tem defeitos que o autor não vê, porque os olhos que a fizeram são os que a julgam. O defeito que ninguém aponta vira alicerce: cada assentada constrói por cima dele, e quanto mais tarde aparece, mais obra leva consigo.",
  "A ocasião é a entrega da obra a alguém capaz de julgá-la melhor que você: o capítulo ao orientador, a peça ao mestre da oficina, o relatório a uma chefe exigente, o prato que o cozinheiro novo põe diante do chefe de cozinha. Esta ocasião passa dias sem vir, porque a obra fica guardada à espera de estar pronta, e ela nunca está.",
  ("O primeiro dia", [
   "Amanhã de manhã, escreva a quem você vai mostrar o quê, e quando, mesmo inacabado.",
   "Escolha alguém que saiba mais que você e diga a verdade. Escreva o nome no caderno.",
   "Prepare a pergunta: <i>o que está mais fraco aqui?</i>",
   "Quando subir à boca <i>isso foi de propósito</i>, guarde a frase até o outro acabar.",
   "À noite, longe do calor, julgue o que ouviu.",
   "Guarde o que é verdadeiro. Descarte o resto por escrito, com a razão.",
   "· Se você mostra várias coisas no dia, pesa mais a entrega a quem mais sabe.",
  ]),
 ],
 marca=["<i>Traço:</i> na entrega que mais pesou, você pediu a crítica precisa e a ouviu até o fim sem se defender. Num dia com uma correção a mostrar, mostrá-la faz parte do gesto.<br/><i>Cruz:</i> você se explicou enquanto o outro falava, pediu elogio disfarçado ou deixou a correção na gaveta. Também é cruz quando você não sabe se a sua frase foi pergunta ou defesa, e quando escolheu de manhã a quem mostrar e não mostrou: a ocasião veio na hora que você marcou.<br/><i>Ponto:</i> hoje não houve entrega nem crítica.<br/><i>Chegou:</i> numa entrega, a pergunta estreita e o silêncio enquanto o outro falava vieram sem o breviário; foi a entrega que lembrou você.<br/><i>Fora da marca:</i> a escolha da manhã e o juízo da noite.", "Aqui os pontos pedem vigilância: nenhum treina nada, e eles se sucedem noite após noite enquanto você guarda a obra.", "Depois do <i>chegou</i> fica: pedir a crítica precisa e ouvi-la até o fim, e o juízo da noite, nas noites em que houve crítica."], sai="o nome de quem sabe mais e lhe diz a verdade, a pergunta estreita preparada, cada crítica anotada e julgada por escrito à noite, e a correção levada a quem a fez. No <i>Manual operacional</i>, as ações do grupo <i>Pessoas</i>.",
 porque=[
  "<b>A ideia.</b> A frase do alto resume o conselho de Epicuro que Sêneca passa a Lucílio: ter diante dos olhos um homem melhor e viver como se ele nos visse. A crítica pedida a quem sabe mais é esse olhar tornado real. Robert Greene, em <i>Maestria</i>, dedica um capítulo ao mestre, a quem está mais adiante no mesmo ofício. O mestre lhe dá um par de olhos que você não tem: o defeito que nasceu do que você ainda não sabe fica invisível para você e aparece para ele na primeira leitura.",
  "<b>O mecanismo.</b> A crítica só dá o que você não vê se você a ouvir inteira. A defesa vem depressa e sem decisão, e enquanto você a prepara deixa de ouvir o resto, onde está a parte justa quando a primeira frase foi injusta. E quem critica só volta a fazê-lo se vir que a crítica serviu: a correção mostrada é a prova, e cada defesa ensina ao crítico que não vale a pena falar.",
  "<b>Por isso.</b> <i>Faço isto porque sozinho não vejo o que não sei, e só segue falando quem me vê corrigir.</i>"],
 saber="Há indícios de um efeito médio favorável do retorno sobre o desempenho, com uma ressalva: na revisão de Avraham Kluger e Angelo DeNisi (1996), cerca de um terço dos retornos piorou o desempenho, sobretudo quando desviava a atenção da obra para a pessoa. Isso apoia ouvir a crítica como notícia sobre a obra. A regra de não se defender vem do ofício, sem estudo: é aposta do autor.")
add("Se ninguém perto de você sabe mais no seu domínio, o mestre está longe: uma carta com a peça e a pergunta estreita cumpre o gesto, e a resposta se lê até o fim antes de qualquer réplica. A crítica que vem sem pedido, de um chefe, de um colega, de quem vive com você, também é ocasião: ouça, agradeça, anote, e o juízo fica para a noite. Se você tem um crítico fiel, não faça dele o único; um só par de olhos acaba vendo só os defeitos que já conhece. Se a obra é grande demais para mostrar inteira, mostre uma página, um movimento, uma série.", PI)
proc("Se o gesto falha", [
 "Se há muitos pontos e poucos traços, escreva de manhã a quem vai mostrar o quê.",
 "Mostre a obra inacabada.",
 "Se há traços e nenhuma correção mostrada, mostre a próxima correção a quem criticou.",
 "· Na terceira vez sem correção, o crítico começa a se calar, como Quintílio.",
 "Se cada crítica pesa sobre você por dias, peça a crítica de uma parte, com uma pergunta estreita.",
 "Leia a resposta como juízo sobre essa parte da obra.",
])
licao(6)
exe("8", "Das pessoas", "J", "Temos duas orelhas e uma só boca.", "Zenão",
 "Quando alguém falar com você: deixe a pessoa terminar. Pergunte antes de opinar.",
 ["Plutarco escreveu <i>Sobre como ouvir</i> para o jovem Nicandro, quando este vestia a roupa de homem feito e deixava os preceptores. Livre dos mestres, avisa Plutarco, o rapaz cai sob senhores piores, os próprios desejos, e a primeira defesa contra eles é aprender a ouvir. Os conselhos são concretos: não interromper, não saltar sobre a primeira frase com uma objeção, esperar o fim e só então perguntar, sobre o que o outro disse. É dele a imagem do espírito como lenha que pede uma faísca para arder. A pergunta que nasce das últimas palavras do outro é o sinal de que a faísca pegou.",
  "Na primavera de 1889, em Viena, Sigmund Freud tratava uma senhora que nos <i>Estudos sobre a histeria</i> chamou de Emmy von N. Interrogava muito, querendo saber de onde vinha cada sintoma. Numa nota daquelas semanas, conta que ela lhe pediu, aborrecida, que parasse de perguntar de onde vinha isto ou aquilo e a deixasse contar o que tinha a dizer. Freud a deixou falar até o fim. Pense o que quiser da teoria que ele construiu depois; a correção da paciente vale para qualquer conversa. Quem pergunta cedo demais leva o outro para onde ele não ia, e só ouve o que esperava ouvir.",
  "Anotar à noite o que alguém disse, para usar na conversa seguinte, é também a técnica de quem quer agradar ou vender. A diferença está no que se guarda. O bajulador de Plutarco lembra só o que lhe serve para agradar. Quem escuta lembra o que importa ao outro: o nome do filho doente, a prova que ele ia fazer, a obra de que falou de passagem. Se, ao reler as notas, você acha só o que lhe convinha, o exercício mostrou o que a sua escuta escolhe."],
 ["Deixe o outro terminar a frase.",
  "Conte um instante antes de falar.",
  "Faça uma pergunta antes de dar a sua opinião.",
  "À noite, anote um detalhe que alguém lhe disse hoje.",
  "Na próxima conversa com essa pessoa, use esse detalhe."],
 "O erro mais sutil é a escuta fingida: você se cala, conta o instante e, enquanto isso, prepara a resposta. O mais visível são as perguntas em fila, de interrogatório, feitas para ganhar.",
 None, "você interrompe menos e lembra mais do que as pessoas lhe dizem.",
 comeco=[
  "Na noite da sétima passagem, com a crítica entre as que ficaram, você lê este. A crítica treinou você a ouvir quando o assunto era você e quando você tinha pedido. Este exercício leva a escuta à conversa comum, à mesa, no trabalho, em casa, onde nada obriga você a se calar e a vontade de falar não tem freio. Ele poupa obra refeita: o pedido ouvido pela metade, do cliente ou do colega, volta à assentada como coisa errada a consertar, e o <i>isto</i> da sessão passa a ser o conserto.",
  "A ocasião é alguém falando com você, e ela vem o dia inteiro: o colega que conta o que fez na véspera, o filho que explica uma briga na escola, o cliente que descreve o que quer, a vizinha na escada, a mulher ou o marido no jantar. Você a reconhece por dentro: a resposta já está pronta antes de o outro acabar, e vem a vontade de entrar na frase dele.",
  ("O primeiro dia", [
   "Amanhã de manhã, antecipe as conversas do dia.",
   "Escolha a que mais lhe custa ouvir. Em casa, a interrupção é costume de anos.",
   "Quando a sua boca se abrir antes do tempo, conte o instante.",
   "Se vier uma pergunta que é ponte para a sua opinião, <i>mas você não acha que...?</i>, deixe-a passar.",
   "Faça a pergunta que nasce das últimas palavras do outro.",
   "À noite, anote um detalhe.",
   "Nas manhãs seguintes, releia o detalhe antes do próximo encontro com essa pessoa.",
   "· Pesa mais a conversa escolhida de manhã. Se o dia trouxe uma mais pesada, é essa.",
  ]),
 ],
 marca=["<i>Traço:</i> na conversa que mais pesou, você deixou o outro acabar e perguntou antes de opinar.<br/><i>Cruz:</i> você interrompeu, ou a sua pergunta serviu só de caminho para a sua resposta. Se você não lembra o que o outro disse depois da sua pergunta, é cruz: você não estava ouvindo.<br/><i>Ponto:</i> num dia sem conversa nenhuma.<br/><i>Chegou:</i> na conversa que mais pesou, o instante de silêncio e a pergunta vieram antes da sua resposta sem o breviário; foi a voz do outro que lembrou você.<br/><i>Fora da marca:</i> o detalhe anotado à noite e usado na conversa seguinte.", "A linha do detalhe se escreve todas as noites enquanto este exercício é a da vez, e acaba quando ele chega.", "Depois do <i>chegou</i> fica: deixar acabar e perguntar antes de opinar."], sai="um detalhe de alguém escrito a cada noite e usado na conversa seguinte com essa pessoa, e a pergunta feita antes da sua opinião. No <i>Manual operacional</i>, as ações do grupo <i>Pessoas</i>.",
 porque=[
  "<b>A ideia.</b> Diógenes Laércio conta que Zenão disse a um rapaz que falava sem parar: temos duas orelhas e uma só boca para ouvirmos mais e falarmos menos. Numa conversa, a parte maior é ouvir, e quem só espera a vez de falar a deixa por fazer. Robert Greene, em <i>Maestria</i>, chama de inteligência social a capacidade de ver as pessoas como são. Para Greene, autor também de <i>As 48 leis do poder</i>, essa leitura é estratégica e serve para você se mover entre os outros a seu favor. O primeiro passo dela é saber o que o outro disse, com as palavras dele, antes de saber o que você pensa disso.",
  "<b>O mecanismo.</b> Enquanto você prepara a sua frase, não ouve a dele: quem interrompe responde à frase que imaginou, e a que foi dita fica sem resposta. O instante de silêncio e a pergunta feita das últimas palavras do outro só são possíveis se você as ouviu, e por isso obrigam você a ouvi-las. E o que alguém diz de passagem se perde em poucos dias; o detalhe escrito e usado fica, e mostra ao outro que ele foi ouvido.",
  "<b>Por isso.</b> <i>Faço isto porque o que me disseram e não escrevi eu já terei perdido no encontro seguinte.</i>"],
 saber="Nenhum estudo citado neste livro mede o gesto de deixar terminar e perguntar antes de opinar. Está demonstrado que a atenção dividida entre ouvir e preparar a resposta perde parte do que foi dito, e que o que não se escreve se esquece depressa, como Ebbinghaus mediu com listas de sílabas. Sobre essa base, o gesto é aposta do autor.")
add("Numa conversa de várias pessoas, o gesto vale para quem está falando: deixe essa pessoa terminar mesmo que outro a tenha interrompido, e a sua pergunta devolve a ela a palavra. Com quem fala demais, o instante continua valendo; a pergunta traz a conversa de volta ao ponto. Com quem desagrada a você, perguntar antes de opinar pesa mais, porque é aí que se responde com mais certeza à frase imaginada. Em casa, com os mais próximos, está a ocasião mais difícil e a mais importante, e é por ela que se decide a marca.", PI)
proc("Se o gesto falha", [
 "Se você marca traço e continua sem lembrar o que as pessoas disseram, a escuta é fingida.",
 "Faça a pergunta nascer das últimas palavras do outro. Se não consegue, você não estava ouvindo.",
 "Se você anota o detalhe e nunca o usa, releia-o de manhã, antes do encontro.",
 "Se o outro se fecha, você perguntou demais. Faça uma pergunta e depois dê a sua opinião.",
 "· A opinião vem depois da pergunta, e continua sendo dita.",
])

licao(7)
estacao("Terceira estação", "Da maestria.")
st.extend(PEND); PEND.clear()
add("Na noite da oitava passagem você escreve <i>chegou</i> ao lado do traço das pessoas, e a segunda estação fica para trás com quatro gestos: começar pela parte difícil e anotar as horas reais; fechar o livro e dizer de memória o essencial; levar a obra a quem sabe mais e ouvir a crítica até o fim; deixar o outro terminar e perguntar antes de opinar. Com os da primeira estação, são oito, feitos todos os dias, sem marca. Os dois últimos puseram você diante dos outros, e diante deles a obra começou a pesar de outra maneira.", PI)
add("Greene chama de maestria a última fase da formação num ofício. Aqui ela começa pelo que você faz quando a obra, as pessoas e as circunstâncias deixam de obedecer: a irritação que sobe, a opinião contrariada, o conforto que pede, a vontade de contar, a coisa que deu errado. Quatro dos cinco exercícios desta estação são J. Ficam mais rápidos e mais leves; nenhum se fará sozinho.", PI)
exe("9", "Da serenidade", "J", "Seja como o rochedo contra o qual as ondas quebram.", "Marco Aurélio",
 "Quando vierem a irritação ou a pressão: faça uma pausa; separe o que aconteceu do que você pensa; responda depois do pico.",
 ["Sêneca escreveu ao irmão Novato três livros sobre a ira. Alguns sábios, lembra ele, a chamaram de loucura breve: os olhos acesos, o rosto vermelho, a voz que sobe, a mesma surdez à razão. O remédio que ele mais repete é a demora. O primeiro ímpeto é violento e curto, e quem lhe dá tempo o encontra mais fraco. Platão, irritado com um escravo, levantou a mão para bater nele e a deteve no ar, e assim ficou, parado, até um amigo perguntar o que fazia. Estou castigando um homem irado, respondeu.",
  "Platão reconheceu que, irado, não estava em condições de julgar, e tirou a decisão das mãos da ira. A mão parada no ar é a pausa do modo. <i>O que ele faria agora?</i> faz o mesmo com o eu antigo. Quem decide continua sendo você, com a voz de quem não está no pico.",
  "A mulher de <i>Do primeiro dia</i> conheceu este obstáculo antes do gesto. Numa reunião da tarde, uma colega apontou diante do chefe um número errado no relatório dela; ela sentiu o rosto quente e não disse nada. Às nove da noite, no meio de um capítulo, ela se pegou compondo a réplica que não dera, e virou duas páginas sem saber o que diziam. Meses depois, com a serenidade como a da vez, a colega a corrigiu de novo. Ela respirou duas vezes e separou por dentro: <i>ela corrigiu um número</i>; <i>eu acho que ela quis me diminuir</i>. Na manhã seguinte, passado o pico, mandou-lhe duas linhas com o número certo e a hora da versão nova. À noite, o capítulo teve a mesa só para ele.",
  "Em julho de 1863, dias depois de Gettysburg, Lincoln soube que o exército de Lee tinha atravessado o Potomac e escapado, quando o general Meade poderia tê-lo capturado contra o rio. Lincoln escreveu a Meade uma carta dura: a oportunidade de ouro estava perdida, e ele se sentia aflito além de qualquer medida. Depois guardou a carta. Ela foi achada entre os papéis dele, com uma nota de próprio punho: nunca enviada, nem assinada. Lincoln pôs no papel cada linha da irritação e não deixou o pico decidir a entrega.",
  "Diante de um perigo, o corpo age antes do juízo, como deve. O exercício governa a palavra e a réplica, que perdem pouco esperando alguns minutos. No pico se perde a frase que não se desdiz e a carta que já não se recolhe. A resposta depois do pico pode ser dura, se for justa."],
 ["Aprenda o seu sinal no corpo: o calor no rosto, a mandíbula, a pressa na voz.",
  "Quando o sinal vier, faça uma pausa.",
  "Respire devagar duas vezes.",
  "Separe por dentro: <i>o que aconteceu</i> e <i>o que eu acho do que aconteceu</i>.",
  "Responda depois do pico, com o que você vai fazer.",
  "Se a resposta é por escrito, escreva-a e espere antes de entregar."],
 "O primeiro erro é confundir serenidade com engolir: a irritação que deve ser dita se diz, depois do pico e com calma. O segundo se parece com o gesto e fica aquém dele: calma por fora, fervura por dentro, sem pausa e sem separação.",
 None, "o intervalo entre o golpe e a resposta aumentou, e suas respostas são mais calmas.",
 comeco=[
  "O exercício que entra amanhã começa onde o anterior se rompe. Quando o que o outro diz fere você, deixar terminar já não basta: por dentro você respondeu antes de ele acabar. A serenidade treina o intervalo entre o golpe e a resposta. O pico é o ponto mais alto da irritação, os segundos ou minutos em que ela decide por você. O gesto tira do caminho da obra a ruminação: a réplica dada no pico volta à assentada seguinte como conversa que não acabou, e ocupa o lugar do <i>isto</i>.",
  "A ocasião é a irritação ou a pressão, e ela aparece no corpo antes de ter nome: o calor no rosto, a mandíbula apertada, a voz subindo. Vem com o colega que corta você na reunião, o filho que não se veste quando já é tarde, o vizinho que faz barulho de madrugada, o funcionário que pede o mesmo papel pela terceira vez, a obra que falha e irrita você consigo mesmo.",
  ("O primeiro dia", [
   "Amanhã de manhã, anote onde e com quem a irritação vem.",
   "Na primeira irritação do dia, note em que parte do corpo ela se mostrou.",
   "Se vier uma frase com certeza de fato, <i>ela faz isso de propósito</i>, ponha-a na segunda metade.",
   "Diga as duas metades por dentro: <i>ela me interrompeu</i>; <i>eu acho que ela não me leva a sério</i>.",
   "Respire duas vezes. Deixe a resposta esperar.",
   "Se você só percebeu a irritação depois de responder, reconstrua o episódio à noite, de trás para a frente.",
   "Pare a reconstrução no primeiro sinal do corpo.",
   "· Pesa mais a ocasião de mais consequência: a pessoa de quem você depende, a palavra que não se desdiz.",
  ]),
 ],
 marca=["<i>Traço:</i> na vez que mais pesou, você fez a pausa e respondeu depois do pico.<br/><i>Cruz:</i> você respondeu no pico. Calar por fora e ferver por dentro, sem pausa e sem separação, é cruz; na dúvida, também.<br/><i>Ponto:</i> o dia passou sem irritação nem pressão.<br/><i>Chegou:</i> na vez que mais pesou, o corpo deu o sinal e as duas respirações vieram atrás dele sem o breviário; foi o calor no rosto que lembrou você.<br/><i>Fora da marca:</i> a reconstrução da noite, que acaba quando o gesto chega; e voltar à pessoa para reparar o que a pressa estragou, que é devido e não muda a marca da noite.", "A separação entre o que aconteceu e o que você pensa disso será sempre um juízo, feito ali, no momento.", "Depois do <i>chegou</i> fica: a pausa e a resposta depois do pico."], sai="seu sinal no corpo identificado, as duas respirações quando ele vem, a separação entre o que aconteceu e o que você pensa disso, e a resposta dada depois do pico. No <i>Manual operacional</i>, as ações do grupo <i>Pensamento</i>.",
 porque=[
  "<b>A ideia.</b> Nas <i>Meditações</i>, Marco Aurélio descreve o rochedo à beira-mar: as ondas batem sem parar, ele fica de pé, e em volta a água acaba se aquietando. A irritação é a onda e continuará vindo; o gesto treina o que fica de pé enquanto ela quebra. Epicteto ensina, no <i>Manual</i>, que o que nos perturba é o juízo que fazemos das coisas. Para os estoicos, esse juízo é a única coisa que depende inteiramente de nós. Ele chega colado ao fato, rápido demais para ser notado, com a mesma certeza.",
  "<b>O mecanismo.</b> O pico é curto, como Sêneca observou, e as duas respirações compram os segundos em que ele perde força. Dizer lado a lado o que aconteceu e o que você pensa disso tira da segunda metade a aparência de fato. Os psicólogos chamam isso de desfusão; há indícios, numa meta-análise de estudos de laboratório (Levin e colegas, 2012), de um efeito favorável.",
  "<b>Por isso.</b> <i>Faço isto porque o pico passa, e o juízo dito ao lado do fato deixa de parecer fato.</i>"],
 saber="Há indícios de um efeito favorável da desfusão, em testes curtos de laboratório, longe das brigas reais (Levin e colegas). Que o pico passe em segundos vem de Sêneca, sem medida neste livro. A pausa não foi testada: é aposta do autor.")
add("A irritação consigo mesmo, quando a obra falha ou o corpo não obedece, é ocasião do mesmo gesto: o sinal, as duas respirações, a separação entre o que aconteceu e o que você diz de si. A pressão sem ninguém à frente, o prazo que aperta, a fila que não anda, também é; ali a resposta é o próximo ato. Com quem fere você sempre com a mesma frase, a pausa começa antes do encontro: de manhã você ouve por dentro a frase que vai doer, e o pico, quando vier, já terá sido visto uma vez.", PI)
proc("Se o gesto falha", [
 "Se as cruzes se juntam na mesma hora ou em volta da mesma pessoa, antecipe essa ocasião de manhã.",
 "Se elas se juntam depois de noites curtas, confira o sono (§8).",
 "Se a resposta sai igual depois da pausa, diga a separação em palavras, por dentro ou por escrito.",
 "· Sem a separação, a pausa só prepara melhor o ataque.",
 "Se você só nota a irritação com a voz já alta, faça a reconstrução da noite até achar o sinal.",
 "Se você percebeu só depois de responder, volte à pessoa, passado o pico, e diga o que vai fazer.",
 "Se a microação não chega e a resistência não cede, siga pela passagem por decisão.",
 "· Ver: <i>Da resistência que fala</i>, no Livro V.",
])
licao(8)
exe("10", "Da mente móvel", "J", "Se me mostrarem que erro, mudarei com alegria.", "Marco Aurélio",
 "Quando alguém contrariar você: <i>talvez você tenha razão</i>. Examine antes de defender; e, se o outro estiver certo, mude e diga isso.",
 ["No <i>Górgias</i> de Platão, antes de discutir com o retor diante de uma sala cheia, Sócrates avisa que espécie de homem é: dos que têm gosto em ser refutados quando dizem algo falso, e não menos gosto nisso do que em refutar. É um bem maior, diz, livrar a si mesmo do pior dos males, que é ter uma opinião falsa sobre o que se discute. Quem é refutado perde um erro que levaria consigo. Os gregos chamavam de <i>élenchos</i> essa prova: perguntas que levam uma opinião até as consequências dela, para ver se aguenta. Quem contraria você submete a sua opinião, sem saber, a essa prova.",
  "Em 1859, em <i>Sobre a liberdade</i>, John Stuart Mill escreveu que quem conhece só o próprio lado da questão conhece pouco dela. E exigiu mais: ouvir os argumentos contrários da boca de quem acredita neles, os defende a sério e faz por eles o melhor que pode. O modo pede isso quando manda repetir o argumento do outro até ele concordar que é esse.",
  "Darwin conta na <i>Autobiografia</i> a sua regra de ouro: todo fato ou ideia contrária aos seus resultados ele anotava na hora, sem falta, porque esses fatos fugiam da memória mais depressa que os favoráveis. Graças a isso, poucas objeções lhe foram feitas que ele já não tivesse notado. A crença que você escreve à noite, com o melhor argumento contra ela, é essa regra aplicada ao que você pensa de si, dos outros e do mundo.",
  "A mulher de <i>Do primeiro dia</i> perdeu assim uma sessão inteira. O chefe disse que o prazo que ela propusera não fechava, e ela o defendeu até o fim da reunião. À noite, em vez de ler, refez num papel as contas do prazo para provar que estava certa; às dez, o capítulo seguia na primeira página. Já com este exercício como a da vez, o chefe contestou outro prazo. Ela disse <i>talvez você tenha razão</i>, pediu o argumento e o repetiu com as próprias palavras: o fornecedor levava dez dias, e não cinco. Ele tinha razão, e ela disse isso ali mesmo. Naquela noite, a sessão foi do capítulo.",
  "Marco Aurélio escreveu <i>se me mostrarem</i>, e mostrar exige prova. A mente móvel se move por razão. Diante da insistência, do prestígio de quem fala ou da vontade de encerrar a conversa, ela fica onde estava. Sócrates morreu sem mudar de posição diante de um tribunal inteiro, porque ninguém lhe mostrou que estava errado."],
 ["Quando alguém contrariar você, diga primeiro <i>talvez você tenha razão</i>.",
  "Peça o melhor argumento do outro.",
  "Repita-o com as suas palavras, até ele concordar que é isso.",
  "Só então responda.",
  "Se mudou de ideia, diga isso em voz alta.",
  "À noite, escreva numa linha uma crença em que você se apoiou hoje e o melhor argumento contra ela."],
 "O erro que mais se confunde com o gesto é ceder para a conversa acabar, sem que o argumento tenha convencido você. Aqui só o argumento decide. O outro é fingir abertura: dizer a primeira frase e repetir o argumento só para rebatê-lo melhor.",
 None, "você muda de posição quando deve, e admitir isso já custa pouco.",
 comeco=[
  "Você está na noite da nona passagem, com a serenidade entre as que ficaram. Dela sobra uma pergunta: passado o pico, e se o outro tiver razão? A serenidade deu o intervalo; a mente móvel trata do que você faz nele quando a irritação vinha de orgulho ferido. À mesa, ela tira a defesa de uma ideia que já não serve: quem não solta uma opinião continua trabalhando nela depois que a obra mostrou o erro, e o <i>isto</i> da sessão vira provar que estava certo.",
  "A ocasião é ser contrariado: alguém discorda, corrige um número seu, põe em dúvida uma decisão, mostra que você se engana sobre um fato. Na reunião, à mesa da família, numa carta que contesta o seu relatório, com um filho adolescente certo de que você não entende nada. Ela se reconhece pela pressa de responder e pela resposta pronta antes de o outro acabar.",
  ("O primeiro dia", [
   "Amanhã de manhã, anote onde e por quem você será contrariado.",
   "Quando vier a contrariedade, diga <i>talvez você tenha razão</i>, mesmo baixo.",
   "Peça logo o argumento: <i>explique-me melhor por quê</i>.",
   "Repita-o com as suas palavras e pergunte se é isso.",
   "Deixe a voz de dentro esperar o fim da repetição.",
   "À noite, e em todas as noites daqui em diante, escreva a linha da crença.",
   "· Se ninguém contrariou você, a linha da crença continua, e a marca é ponto.",
   "· Pesa mais a contrariedade que toca o que mais importa, ou a de quem você menos queria ouvir.",
  ]),
  "A primeira frase custa a sair, e sai baixo, quase engolida, enquanto por dentro outra voz diz <i>não tem, e eu sei por quê</i>. Essa voz espera a repetição. Se ainda tiver razão depois dela, terá o argumento à frente para responder.",
 ],
 marca=["<i>Traço:</i> na contrariedade que mais pesou, você examinou antes de defender: a primeira frase, o argumento do outro repetido e, quando ele tinha razão, a mudança dita.<br/><i>Cruz:</i> você defendeu antes de examinar, ou mudou de ideia e não disse. Ceder para a conversa acabar também é cruz, e na dúvida entre razão e vontade de encerrar, é cruz.<br/><i>Ponto:</i> num dia em que ninguém contrariou você.<br/><i>Chegou:</i> numa contrariedade de fato, a primeira frase e o pedido do argumento vieram antes da réplica sem o breviário; foi a pressa de responder que lembrou você. A linha da noite, de caderno aberto, nunca dá <i>chegou</i> por si.<br/><i>Fora da marca:</i> a linha da crença, à noite.", "Depois do <i>chegou</i> fica: examinar antes de defender, e a linha da crença todas as noites."], sai="uma linha por noite com uma crença em que você se apoiou e o melhor argumento contra ela, e o argumento de quem contraria você repetido até ele concordar que é esse. No <i>Manual operacional</i>, as ações do grupo <i>Pensamento</i>.",
 porque=[
  "<b>A ideia.</b> Marco Aurélio escreve, nas <i>Meditações</i>, que, se alguém lhe mostrar que ele pensa ou age mal, mudará com alegria, porque busca a verdade, e ninguém jamais foi prejudicado por ela. O que trava a mente móvel é o orgulho, que sente a opinião contrariada como derrota de quem a tinha.",
  "<b>O mecanismo.</b> A pressa de defender ouve do argumento contrário só a parte que já sabe rebater, e responde a uma caricatura. Repetir o argumento até o outro concordar obriga você a ouvi-lo inteiro, e só um argumento ouvido inteiro mostra que você erra. E a memória guarda melhor o que nos dá razão; Darwin notou isso em si e passou a anotar na hora os fatos contrários. A linha da crença faz o mesmo.",
  "<b>Por isso.</b> <i>Faço isto porque esqueço mais depressa o que me contraria do que o que me dá razão.</i>"],
 saber="Está demonstrado o viés de confirmação, a tendência a procurar, notar e lembrar o que nos dá razão; Raymond Nickerson reviu os estudos em 1998. Ele sustenta a necessidade do gesto. Nenhum estudo citado aqui mostra que repetir o argumento do outro ou anotar o argumento contrário corrija esse viés: o remédio é aposta do autor, apoiada no exemplo de Darwin.")
add("Contrariado por escrito, o gesto é o mesmo, mais lento: leia o argumento até o fim, reescreva-o na margem com as suas palavras e só então responda. Se quem contraria sabe menos que você, a primeira frase vale do mesmo jeito: o argumento se pesa pela força dele. Se é você que se contraria, relendo o que pensava há um ano, anote a mudança e a razão, como Darwin. E quando, examinado tudo, o outro está errado, diga isso com a mesma calma, com o argumento à vista.", PI)
proc("Se o gesto falha", [
 "Se <i>talvez você tenha razão</i> sai irônica ou como tique, peça o argumento logo depois.",
 "· A frase vale só com a repetição do argumento atrás dela.",
 "Se em muitas noites você não mudou de ideia nem num ponto pequeno, procure de propósito o contrário.",
 "Escolha um livro, uma pessoa, um argumento a que você ainda não respondeu.",
 "Se você só conversa com quem pensa como você, reveja a quem pede crítica.",
 "Se você muda de ideia sempre, escreva antes, numa linha, o argumento que convenceu você.",
 "Se não consegue escrevê-lo, não mude.",
])
licao(9)
exe("11", "Da pobreza voluntária", "J", "É disto que eu tinha medo?", "Sêneca",
 "Quando vier o impulso do conforto: espere vinte e quatro horas. E uma recusa de conforto por dia, escolhida de manhã.",
 ["Sêneca escreve a carta do dia de pobreza em dezembro, com Roma inteira nas Saturnais e a cidade suando nos banquetes. Entre entrar na festa e fugir dela, propõe um terceiro caminho, mais duro: dias de comida pouca e barata e de roupa áspera, com a pergunta no fim. O soldado, lembra ele, faz manobras em tempo de paz e cava trincheiras sem inimigo à vista, para não se cansar quando o esforço for necessário. Quem quer que a escassez não o abale a ensaia enquanto ela está longe.",
  "Na mesma carta, Sêneca lembra que Epicuro tinha dias fixos em que matava a fome com pouco, para ver se faltava algo à alegria plena. O mestre do prazer vivia no Jardim a pão e água, e pediu certa vez a um amigo um potinho de queijo, para se banquetear quando quisesse. Desfruta mais da abundância quem menos precisa dela. O dia de pobreza protege o prazer do desgaste do costume.",
  "A mulher de <i>Do primeiro dia</i> levou semanas para ver de onde vinham as saídas da mesa. Diante de um parágrafo de prescrição que não entendia, ela foi buscar um chocolate, voltou, leu de novo e foi fazer um chá. Às dez tinha ido três vezes à cozinha, e o parágrafo continuava lá. Com este exercício como a da vez, o impulso veio no mesmo ponto de outro parágrafo difícil, com a mão já no braço da cadeira. Ela escreveu na folha <i>chocolate, nove e dez</i> e ficou. O parágrafo levou vinte minutos e se resolveu na página, o único lugar onde podia se resolver. Na noite seguinte, às nove e dez, ela releu a linha e já não quis o chocolate.",
  "Em 1845, Thoreau foi viver numa cabana que construiu à beira do lago Walden, porque queria viver deliberadamente. Conta que tinha sobre a mesa três pedaços de calcário e se assustou ao ver que precisava espaná-los todos os dias, enquanto a mobília do espírito seguia sem espanar; jogou as pedras pela janela. Um homem é rico, escreveu, na proporção das coisas de que pode prescindir. Cada coisa de que você depende cobra cuidado e atenção. A recusa de cada manhã procura uma delas por dia.",
  "Sêneca era um dos homens mais ricos de Roma quando escreveu a carta, e Thoreau ia jantar na casa da família, em Concord. Nenhum dos dois pede que você jogue fora o que tem. O exercício mede quanto do seu tempo e do seu juízo o conforto decide sem consultar você."],
 ["Quando vier o impulso de conforto, escreva-o com a data e a hora.",
  "Espere vinte e quatro horas.",
  "Se ainda o quiser e ele couber nas suas regras, faça.",
  "De manhã, escolha uma recusa de conforto para o dia, pequena e concreta.",
  "Cumpra a recusa.",
  "Uma vez por ciclo, declare na véspera o dia de pobreza: comida simples, nenhuma compra, nenhum entretenimento.",
  "Na noite desse dia, escreva o que você descobriu que não precisava."],
 "Há quem faça do exercício um castigo, e do dia de pobreza uma pena cumprida de dentes cerrados. E há a vaidade da austeridade: quem mostra o pouco recebe por ele o conforto de ser visto.",
 None, "o conforto deixou de decidir por você.",
 comeco=[
  "Na noite da décima passagem, com a mente móvel entre as que ficaram, você lê este. A mente móvel solta uma opinião quando deve; este exercício pede a mesma soltura diante das coisas, e começa pelo menor: um impulso de conforto adiado um dia. Ele tira da assentada o conforto que chama: cada impulso atendido na hora ensina que o desconforto se resolve fora da obra, e a sessão que aperta ganha uma saída a um gesto de distância.",
  "A ocasião é o impulso de conforto: comprar o que não estava previsto, comer sem fome, abrir uma distração que você não escolheu, pedir carona em vez de andar dez minutos, o doce no fim da tarde. Ele chega sem pedir licença, com a mão já no meio do gesto.",
  ("O primeiro dia", [
   "Amanhã de manhã, ponha uma folha onde o impulso aparece.",
   "Se ainda não tem as suas regras, escreva-as: o que cabe no seu dinheiro e no seu tempo, com números.",
   "Escolha a recusa do dia: o açúcar, o caminho a pé, a distração que não abre antes da obra.",
   "Quando vier <i>mereço</i> ou <i>é só desta vez</i>, escreva na folha só a data e a hora.",
   "Deixe a decisão para daqui a vinte e quatro horas.",
   "Declare o dia de pobreza na véspera, à noite. Nunca na própria manhã.",
   "Marque o dia de pobreza para enquanto este exercício é a da vez.",
   "· Pesa mais o impulso maior em dinheiro ou em tempo, ou o que volta todo dia à mesma hora.",
  ]),
 ],
 marca=["<i>Traço:</i> no impulso que mais pesou, você o escreveu e esperou as vinte e quatro horas. Fazer depois o que cabe nas suas regras faz parte do gesto.<br/><i>Cruz:</i> você cedeu na hora a esse impulso. Impulsos obedecidos sem ser vistos, descobertos à noite, contam como ocasião cedida.<br/><i>Ponto:</i> num dia sem impulso; um dia assim merece desconfiança.<br/><i>Chegou:</i> no impulso que mais pesou, a mão parou e foi à folha sem o breviário; foi o próprio impulso que lembrou você.<br/><i>Fora da marca:</i> a recusa da manhã, as regras de dinheiro e de tempo e o dia de pobreza; nesse dia, a marca continua sobre o impulso.", "Depois do <i>chegou</i> fica: escrever o impulso e esperar as vinte e quatro horas."], sai="a folha dos impulsos com data e hora, suas regras de dinheiro e de tempo escritas, uma recusa de conforto cumprida por dia e, do dia de pobreza, a linha do que você não precisava. No <i>Manual operacional</i>, as ações do grupo <i>Privação voluntária</i>.",
 porque=[
  "<b>A ideia.</b> Sêneca aconselha Lucílio a reservar alguns dias de pobreza, com comida pouca e barata e roupa áspera, e a perguntar no fim: é disto que eu tinha medo? Quem ensaia o pouco descobre que aguenta mais do que temia, e o conforto perde poder sobre ele. Quando decide por você, o conforto decide pelo adiamento.",
  "<b>O mecanismo.</b> O impulso chega com a mão já no meio do gesto, e quem decide nesse instante decide com a força dele. Escrevê-lo e esperar vinte e quatro horas leva a decisão para quando ele baixou. Há indícios, num estudo de Bowen e Marlatt, de que deixar a vontade passar sem obedecer reduz o ato. E você só sabe de quanto precisa quando passa sem isso: a recusa diária e o dia de pobreza respondem a Sêneca pela experiência.",
  "<b>Por isso.</b> <i>Faço isto porque o impulso adiado um dia perde a força, e só sem isso sei de quanto preciso.</i>"],
 saber="Há indícios, num só estudo curto e preliminar de Bowen e Marlatt com estudantes fumantes, de que observar a vontade sem obedecer reduziu o fumo na semana seguinte. A espera de vinte e quatro horas e a recusa diária não foram testadas. A ideia de Sêneca vem da experiência, sem medida: é aposta do autor.")
add("Se você vive com outras pessoas, o dia de pobreza é seu: não se impõe a ninguém a austeridade que você escolheu, e a comida simples é só o seu prato. A recusa se adapta à vida que você tem: quem não compra nada passa sem o doce, quem não come doce faz a pé o caminho curto, quem tem o dinheiro apertado recusa conforto de tempo, a distração aberta antes da obra.", PI)
proc("Se o gesto falha", [
 "Se a folha dos impulsos fica quase vazia, ponha-a onde o impulso aparece.",
 "Escreva assim que vier a primeira frase interior (§2).",
 "Se, passadas as vinte e quatro horas, você sempre faz o adiado, escreva as regras, com números.",
 "Se o dia de pobreza irrita você e o seguinte vira desforra, faça o próximo mais leve.",
 "· Nada se compensa (§4).",
 "Nesse dia, ponha a atenção na pergunta da noite: o que você descobriu que não precisava.",
 "Se a recusa da manhã é sempre a mesma e já não custa, escolha outra.",
])
licao(10)
exe("12", "Da discrição", "H", "As ovelhas não mostram quanto comeram; digerem e dão lã.", "Epicteto",
 "Quando vier a vontade de contar um plano: cale-se e volte à obra.",
 ["No Sermão da Montanha, tal como Mateus o conserva, Jesus fala dos que dão esmola tocando trombeta, nas sinagogas e nas ruas, para serem louvados, e diz deles: já receberam a sua recompensa. E dá a regra contrária: que a sua mão esquerda não saiba o que faz a direita. A frase descreve um mecanismo, para quem crê e para quem não crê. Quem anuncia o ato recebe o louvor antes de praticá-lo, e com ele parte da razão para praticá-lo.",
  "Epicteto, no mesmo <i>Manual</i> das ovelhas, dá o exercício na forma mais pura. Se quiser se treinar para suportar, faça isso para si: quando estiver com muita sede, tome um gole de água fresca, cuspa-o e não conte a ninguém. O treino feito para ser visto já recebeu o pagamento no olhar dos outros. O ato bom que ninguém saberá é esse gole de água cuspido.",
  "Carl Friedrich Gauss tinha por lema <i>pauca sed matura</i>, poucas coisas, mas maduras, gravado num selo com uma árvore de poucos frutos. Só publicava o que estava acabado e demonstrado sem lacuna. O resto ia para um pequeno caderno, começado em março de 1796, aos dezoito anos, com a construção do polígono de dezessete lados com régua e compasso. Ali anotou, sem contar a ninguém, resultados que outros só publicariam décadas depois, com o nome deles. O caderno só foi conhecido em 1898. Gauss pagou esse preço de olhos abertos: falava do que estava maduro, e o resto amadurecia calado, a salvo da conversa e do aplauso."],
 ["Quando vier a vontade de contar, cale-se.",
  "Escreva a vontade na folha de captura.",
  "Volte à obra.",
  "Fale só do que está concluído, e só se perguntarem.",
  "Faça por dia um ato bom, pequeno, que ninguém saberá."],
 "O erro mais sério é confundir discrição com isolamento ou com mentira: esconder dos seus o que eles precisam saber, ou dizer que não faz nada quando faz. Pedir crítica continua: levar a obra a quem sabe mais é o sétimo exercício, e ele fica.",
 None, "você fala apenas do que já está feito.",
 comeco=[
  "Você está na noite da décima primeira passagem, e a pobreza voluntária ficou entre as que ficaram. Lá você ensaiou o pouco nas coisas; aqui o ensaia nas palavras. Ser visto também é um conforto, e se obtém antes do tempo, sem obra feita, contando. Quem conta o plano recebe o aplauso que caberia à obra feita: a vontade que pedia o <i>isto</i> se gasta na conversa, e a sessão seguinte começa com a recompensa já recebida.",
  "A ocasião é a vontade de contar. Vem à mesa com amigos, quando alguém fala do que anda fazendo e você tem algo maior a dizer; vem no trabalho, com um plano seu ainda no papel; vem em casa, no fim do dia, com tudo o que você vai começar. Ela se reconhece pelo prazer antecipado, o gosto de ver a cara do outro antes de haver obra.",
  ("O primeiro dia", [
   "Amanhã de manhã, antecipe onde a vontade de contar vai aparecer: o encontro, a pessoa a quem você conta tudo.",
   "Quando vier <i>conte, ele vai gostar de saber</i>, escreva a vontade na folha de captura.",
   "Pergunte ao outro como vai a vida dele.",
   "Faça o ato bom do dia quando couber.",
   "Não o conte a ninguém.",
   "· Pesa mais a vontade que toca o plano que mais importa a você.",
  ]),
  "A frase da vontade é generosa. Quando o plano estiver feito, o outro vai gostar de saber o que você fez.",
 ],
 marca=["<i>Traço:</i> na vontade de contar que mais pesou, você se calou e voltou à obra.<br/><i>Cruz:</i> você contou esse plano. Deixar adivinhar com meias frases também é contar; na dúvida, é cruz.<br/><i>Ponto:</i> num dia em que a vontade de contar não veio.<br/><i>Chegou:</i> na vontade que mais pesou, você se calou sem o breviário; foi o prazer antecipado que lembrou você.<br/><i>Fora da marca:</i> o ato bom do dia, que ninguém saberá.", "Depois do <i>chegou</i> fica: calar a vontade de contar e voltar à obra."], sai="a vontade de contar posta na folha de captura em vez de dita, a resposta curta com o que está feito quando lhe perguntam, e um ato bom por dia que você não contou.",
 porque=[
  "<b>A ideia.</b> As ovelhas da frase do alto não mostram ao pastor quanto comeram; digerem e dão lã. O plano contado é o pasto mostrado antes de haver lã.",
  "<b>O mecanismo.</b> O anúncio paga adiantado; há indícios disso num estudo de Gollwitzer. E o plano contado põe a obra sob o olhar dos outros antes de ela estar pronta, e você passa a trabalhar também para esse olhar.",
  "<b>Por isso.</b> <i>Faço isto porque o plano contado me paga antes da obra, e o que falta se faz calado.</i>"],
 saber="Há indícios, num estudo de Gollwitzer com poucos experimentos pequenos, com estudantes e sem replicação larga, de que o anúncio paga adiantado; planos comuns não foram medidos. O segundo ponto, a obra sob o olhar dos outros, é aposta do autor.")
add("Se perguntam o que você anda fazendo, responda com o que está feito, em poucas palavras, e pare. Se outros dependem dos seus planos para organizar os deles, dê a informação necessária sem o brilho; a prova é perguntar se você diria aquilo caso ninguém fosse admirar você por isso. O ato bom muda de forma: um serviço feito sem contar a quem o recebe, uma dívida paga que ninguém cobrava, uma recomendação de que o recomendado nunca saberá a origem.", PI)
proc("Se o gesto falha", [
 "Se você deixa o plano ser adivinhado, <i>ando com uma coisa grande</i>, marque cruz.",
 "Se a folha se enche de vontades de contar o mesmo plano, olhe a obra: ela parou.",
 "Volte à obra pela linha I.",
 "· A discrição vale para os planos e o desejo de ser visto. O que os seus precisam saber, diga.",
])
exe("13", "Do amor ao destino", "J", "Não querer nada diferente, nem para a frente, nem para trás.", "Nietzsche",
 "Quando algo der errado: uma linha com a causa, e o próximo passo feito. Sem lamento.",
 ["Epicteto, escravo liberto e, segundo a tradição, coxo desde jovem, pôs no capítulo 8 do <i>Manual</i> uma regra que só parece fácil: não peça que as coisas aconteçam como você quer; queira que aconteçam como acontecem, e a sua vida correrá serena. A regra não manda deixar de agir. O que aconteceu já não depende de você. O próximo passo depende, e é só nele que a linha da noite põe a mão.",
  "Marco Aurélio, nos acampamentos do Danúbio, deixou a forma mais curta da ideia (<i>Meditações</i>, V, 20): os homens podem impedir a ação dele, mas não a disposição, porque o espírito converte o obstáculo em matéria. O que impede a ação faz a ação avançar, e o que está no caminho se torna caminho. É uma técnica: tomar o que bloqueou o plano e perguntar o que isso permite fazer agora.",
  "Nietzsche escreveu o aforismo que abre o quarto livro de <i>A gaia ciência</i> em janeiro de 1882, em Gênova. Tinha deixado a cátedra de Basileia por doença; passava dias fechado no escuro com dores de cabeça, e a vista lhe falhava. Escreveu que queria aprender a ver como belo o que é necessário nas coisas, e chamou isso de amor fati: que seja este, de agora em diante, o meu amor. Não queria acusar, nem sequer os acusadores; queria ser, algum dia, apenas alguém que diz sim. O livro toma dele só a metade que olha para trás: escrever o que aconteceu sem culpado e sem queixa. O próximo passo quer que amanhã seja diferente, e Nietzsche não chamaria isso de amor fati.",
  "John Milton ficou cego por volta de 1652, aos quarenta e poucos anos. Depois da Restauração, em 1660, escondeu-se, foi preso e perdeu boa parte do que tinha. Cego, compôs o <i>Paraíso perdido</i>, publicado em 1667. Os primeiros biógrafos contam que ele compunha de noite, de memória, e de manhã esperava quem escrevesse os versos; se a pessoa tardava, queixava-se de que precisava ser ordenhado. O obstáculo virou modo de trabalhar, e o próximo passo da sua linha pode ter essa forma, diferente da que você planejava.",
  "Numa segunda-feira, a mulher de <i>Do primeiro dia</i> recebeu a nota de um simulado: quatro em dez em contratos, a matéria que mais estudara. À noite, os primeiros quarenta minutos foram do lamento: a questão mal escrita, o mês gasto em resumos, o que aquilo dizia das chances dela no exame. O livro ficou aberto na mesma página. Semanas depois, com este exercício como a da vez, veio outro simulado ruim. Ela escreveu a linha antes de abrir o livro: <i>seis em dez em obrigações; o buraco, li e resumi e nunca resolvi questões; o próximo passo, dez questões hoje</i>. Às nove estava na quinta questão. A nota continuava ruim, e a sessão, desta vez, foi das questões.",
  "Inácio de Loyola, nos <i>Exercícios espirituais</i>, ensinava um exame dirigido a uma só falta: de manhã, propor-se guardar dela; depois do almoço e à noite, marcar numa linha as vezes em que caíra; depois comparar as linhas, dia com dia, semana com semana, para ver se diminuíam. O exame geral da noite começava dando graças. A folha de marcas e as linhas de queda descendem desse papel. Relidas, servem para procurar o padrão, e começar pelo que deu certo ajuda a ler o resto com a cabeça fria."],
 ["Quando algo der errado, escreva uma linha: <i>o que aconteceu, onde estava o buraco, qual é o próximo passo</i>.",
  "Escreva sem lamento e sem culpar ninguém.",
  "Faça o próximo passo no mesmo dia.",
  "Uma vez por ciclo, releia todas as linhas de queda.",
  "Procure o que se repete."],
 "O erro mais frequente é confundir este exercício com resignação: encolher os ombros e não fazer o passo. O outro é fingir que não dói, escrever a linha com uma calma que você não tem e pular o buraco. O exercício pede que se use o que aconteceu.",
 None, "as quedas passaram a ser lidas como dados sobre o que ajustar, e já não como razão para parar.",
 comeco=[
  "É a noite da décima segunda passagem, e você lê o último exercício. Atrás de você há muitas noites de marcas, e entre elas quedas: cruzes, noites em que a dúvida recusou o <i>chegou</i>, microações que já tinham ficado e voltaram a ser a da vez. Os doze exercícios anteriores trataram do que fazer; este trata do que fazer com o que não deu certo, e vem no fim porque agora há matéria para ele. Ele tira da assentada o lamento: a queda de ontem, revisitada, toma os primeiros minutos da sessão, e o <i>isto</i> espera atrás dela.",
  "A ocasião é algo que deu errado, à medida do dia: o plano que caiu porque choveu, a entrega devolvida cheia de emendas, a viagem perdida por minutos, a conversa que acabou mal, uma noite de cruz, uma das que ficaram que cedeu. A grande dor, a doença e o luto ficam fora dela: para eles nenhum exercício deste livro foi escrito, e o livro não pede marca nenhuma. A ocasião se reconhece pela voz que começa logo a contar a história, com culpados e queixas.",
  ("O primeiro dia", [
   "Amanhã de manhã, saiba onde está a folha em que vai escrever a linha.",
   "Quando algo der errado, escreva <i>o que aconteceu</i>: o fato, sem adjetivos.",
   "Escreva <i>onde estava o buraco</i>: um lugar.",
   "Escreva <i>qual é o próximo passo</i>: um ato que caiba no dia.",
   "Faça o passo hoje.",
   "À noite, faça a marca.",
   "· O que a queda diz de você não tem linha.",
   "· Pesa mais a coisa maior, ou a que mais puxa você para o lamento.",
  ]),
  "A história do que deu errado chega inteira e depressa, já contada por dentro: quem teve a culpa, como era evitável, o que isso diz de você. A linha em três partes deixa pouco espaço para ela, e é por isso que se escreve.",
 ],
 marca=["<i>Traço:</i> na coisa que mais pesou, você escreveu a linha sem lamento e fez o próximo passo no mesmo dia.<br/><i>Cruz:</i> o lamento venceu, ou o passo escrito ficou por fazer. Se a linha saiu com um culpado dentro e você hesita, é cruz.<br/><i>Ponto:</i> nada deu errado. Não se fabricam quedas para treinar o exercício.<br/><i>Chegou:</i> na coisa que mais pesou, a linha em três partes tomou o lugar do lamento sem o breviário; foi a própria queda que lembrou você.<br/><i>Fora da marca:</i> a releitura das linhas de queda, uma vez por ciclo, que não tem noite própria.", "Depois do <i>chegou</i> fica: a linha em três partes no lugar do lamento, com o próximo passo feito no mesmo dia."], sai="uma linha em três partes para cada coisa que deu errado, com o próximo passo feito no mesmo dia, e as linhas de queda do ciclo relidas uma vez, com o que se repete anotado. No <i>Manual operacional</i>, as ações do grupo <i>Pensamento</i>.",
 porque=[
  "<b>A ideia.</b> Nietzsche, em <i>Ecce Homo</i>, chama de amor fati amar o que é necessário, sem querer nada diferente, nem para a frente, nem para trás. O gesto segue a fórmula só na metade que olha para trás. O próximo passo vem da técnica estoica do obstáculo que se torna caminho (Marco Aurélio, <i>Meditações</i>, V, 20; Epicteto, <i>Manual</i>, 8). Diante do que deu errado, você lê o que a queda mostra e faz o passo que ela ainda permite. A queda diz onde a estrutura cedeu.",
  "<b>O mecanismo.</b> O lamento é uma sentença sobre o caráter, e vem depressa porque já está pronta; fecha o caso antes de a queda ser olhada. A linha pede um fato, um lugar e um ato, e um buraco com lugar se tapa. E quem se condena depois de falhar tem medo de olhar a falha. Há indícios, num estudo de Juliana Breines e Serena Chen (2012), de que quem se tratou com compreensão depois de falhar num teste estudou mais tempo para o seguinte.",
  "<b>Por isso.</b> <i>Faço isto porque o lamento fecha o caso, e só corrijo a queda que olho sem me condenar.</i>"],
 saber="Há indícios, no estudo de Breines e Chen, bem desenhado, feito com estudantes e ainda sem replicação independente, de que a compreensão consigo depois de uma falha aumenta o tempo de estudo seguinte. Nenhum estudo testou a linha em três partes, com fato, lugar e ato: a forma do gesto é aposta do autor.")
add("Quando o erro foi de outra pessoa, a linha continua sem culpado: o que aconteceu, onde estava o buraco que cabia a você, qual é o seu próximo passo. Há um buraco que cabia a você, mesmo pequeno, e é o único sobre o qual você pode agir. Quando o que deu errado é grande, o próximo passo é mínimo, a versão de dois minutos da linha VI, feita no mesmo dia.", PI)
proc("Se o gesto falha", [
 "Se as linhas crescem até virar parágrafos, volte à forma: uma linha, três partes.",
 "· Nenhuma das três partes pergunta quem você é.",
 "Se você escreve o passo e não o faz, diminua-o até caber no que resta do dia.",
 "Se, na releitura do ciclo, o mesmo buraco aparece cinco ou dez vezes, leve-o à manhã seguinte.",
 "Pergunte pelo desenho: o ambiente, a ordem da mesa, a ocasião mal definida.",
])

licao(11)
add("Numa noite que o livro não sabe qual será, a décima terceira microação chega. Na ocasião que mais pesou, a linha em três partes vem no lugar do lamento sem o caderno lembrar você, e você escreve <i>chegou</i> ao lado do último traço do ciclo. Nessa noite não há exercício seguinte para ler, e na manhã seguinte não entra nenhum. As treze estão entre as que ficaram, cada uma na sua ocasião, todos os dias. À mesa, quando você se senta e diz <i>Isto, até acabar</i>, o que vem buscar você continua vindo, e encontra treze gestos que já não pedem caderno.", PI)
add("O ciclo acaba aí. Antes de voltar à estação zero, você responde por escrito à prova do ciclo, em <i>Da prova</i>, no Livro V. Depois vêm o Interlúdio e <i>Do retorno</i>, um novo dia zero e o primeiro exercício outra vez: a mesa em ordem, a lista do que está aberto, a primeira hora longe das distrações, agora com a prática de um ciclo inteiro.", PI)
add("Se, em algum ponto das estações, você viu uma coisa que nenhum exercício resolveu, você conhece a forma dela: um hábito antigo que volta à mesma hora, no mesmo lugar, com o mesmo pagamento, e que nenhum gesto novo desaloja. Os exercícios acrescentam, e ele não se vence por acréscimo.", PI)
add("Para ele não há passagem nem estação, e não é preciso esperar as treze para enfrentá-lo. É dele que trata o livro seguinte.", PI)
fleur()
# O ornamento vai junto do último parágrafo, para não ficar sozinho numa página.
st[-2:] = [KeepTogether(st[-2:])]

# ===================== LIVRO IV =====================
livro("IV", "Do corte")
add("<i>“Dá-me a castidade e a continência, mas não ainda.”</i>", ParagraphStyle('c1', parent=PC, fontSize=12.5, spaceAfter=2))
add("Santo Agostinho, <i>Confissões</i>, VIII", ParagraphStyle('c2', parent=EPA, spaceAfter=18))
add("Há hábitos que desfazem o estado de foco antes que ele comece. Dão em um minuto o que a obra só dá em uma tarde inteira, e depois deixam a atenção incapaz de se fixar numa coisa só. O corte é para esses.", PI)
abertura([("Quando ler", "Na noite em que você percebe que um hábito antigo desfaz o que os exercícios fazem, em qualquer ponto das estações."),
          ("Se cair duas vezes", "Se você cair dois dias seguidos, ou se a linha cair uma vez e depois outra, leia a nota do fim de <i>Da contagem</i>.")],
         "<i>Dias limpos</i> começada: a linha datada e assinada no alto, a lista das pontes riscada e a paixão contrária escrita.")
add("Você está em algum ponto das estações. As noites são feitas como você aprendeu: a marca e as três linhas. Numa delas, ao percorrer a folha de marcas, você vê uma conta que não fecha. Os traços estão lá, a da vez avança, algumas já ficaram, e a vida, vista de um mês para o outro, quase não se mexe. O que o gesto tece de dia, alguma coisa desfaz quando ninguém está olhando. Você procura a falha na folha, e ela não está na folha.", PI)
add("A falha está num hábito antigo que nenhum exercício toca. Você sabe qual é o seu, e sabe há muito tempo: ele volta à mesma hora, no mesmo lugar, com o mesmo pagamento. Os gestos novos passam ao lado dele sem desalojá-lo. No instante em que você o reconhece, vem uma frase mansa: <i>disso cuido depois, quando os exercícios estiverem feitos</i>. Agostinho deu nome a essa frase na epígrafe: <i>mas não ainda</i>.", PI)
add("Agostinho foi professor de retórica antes de ser bispo de Hipona, e contou nas <i>Confissões</i> os anos em que quis deixar uma vida e não conseguia. Na juventude, rezava pedindo a castidade e acrescentava <i>não ainda</i>, porque temia ser atendido depressa demais. O corte vem encerrar esse adiamento.", PI)
add("Ninguém chega ao caminho como um terreno vazio. O Livro III ensinou você a pôr coisas onde não havia nada. O seu terreno já está ocupado por hábitos com suas horas e seus lugares, e eles não vão embora só porque chegaram vizinhos novos.", PI)
add("Para esse hábito o livro tem outra operação, o <b>corte</b>: deixar um hábito de uma vez, a partir de um dia certo, com uma linha escrita à mão, no presente, datada e assinada. Depois a linha se guarda com o corpo, pondo distância entre você e a ocasião. O corte corre ao lado dos exercícios: a da vez continua, e o corte segue junto, um de cada vez. Não tem passagem, nem <i>chegou</i>, nem piso. No lugar da passagem, tem a contagem dos <b>dias limpos</b>, na página 35 do caderno, <i>Dias limpos</i>.", PI)
proc("Esta noite", [
 "Leia até o fim de <i>Do modo</i>.",
 "Antes de fechar o caderno, faça só o primeiro passo: nomeie o hábito.",
 "Deixe a linha para amanhã de manhã.",
])

sec("Da decisão")
st.append(Paragraph("D O &nbsp; P O R Q U Ê", LBX))
for par in ["<b>A ideia.</b> Agostinho descreveu os degraus do hábito no livro oitavo das <i>Confissões</i>. Da vontade desviada nasce o desejo; o desejo atendido vira costume; o costume a que não se resiste vira necessidade. Nenhum degrau pede uma decisão grave, só repetição. Enquanto houver repetição, ela trabalha a favor do hábito, e por isso o corte o deixa de uma vez.", "<b>O mecanismo.</b> A linha absoluta tira a quantidade da discussão. Moderar obriga a decidir, em cada ocasião, quanto se concede, e essa decisão se toma no pior momento, com a coisa ao alcance da mão. E o hábito é disparado pelas pistas do lugar, da hora e da companhia. Por isso os passos de <i>Do modo</i> afastam a ocasião, em vez de pedir força diante dela.", "<b>Por isso.</b> Corto de uma vez porque moderar é negociar a cada ocasião, e afasto a ocasião, que dispara o hábito."]: add(par, PI)
add("O pedido de Agostinho era sincero, e o <i>não ainda</i> também. O hábito aceitava a mudança e a adiava por mais um dia razoável.", PI)
add("No verão de 386, em Milão, Agostinho tinha trinta e um anos e já não tinha dúvida sobre o que devia fazer. Não o fazia. Um conterrâneo, Ponticiano, veio visitá-lo e contou de dois funcionários do imperador que tinham lido a vida de Antão, o monge do deserto, e deixado tudo no mesmo dia. Agostinho escreve que foi como se o pusessem diante do próprio rosto.", PI)
add("Quando Ponticiano saiu, Agostinho foi para o jardim, e o amigo Alípio o seguiu. Arrancava os cabelos, batia na testa. O corpo, escreve, obedecia ao menor sinal da vontade; a vontade não obedecia a si mesma, porque não mandava por inteiro. Metade dele queria deixar aquela vida, a outra metade não. Os velhos hábitos o puxavam pela roupa de carne e murmuravam: <i>vai nos deixar? a partir deste momento, nunca mais?</i>", PI)
add("Deitou-se debaixo de uma figueira e chorou: <i>Até quando? Amanhã, e amanhã? Por que não agora?</i> De uma casa vizinha veio uma voz de criança que repetia, como numa cantiga, <i>tolle lege, tolle lege</i>, toma e lê. Ele abriu ao acaso as cartas de Paulo e leu: não cuideis da carne para satisfazer seus desejos. Não quis ler mais, escreve, nem era preciso.", PI)
add("Falta à cena um argumento novo: Agostinho sabia havia anos tudo o que precisava saber. Ela tem uma hora, um lugar, um gesto e uma frase que acaba com o <i>amanhã</i>. Não cuidar da carne é não lhe preparar o caminho, e isso é queimar as pontes. Para Agostinho, o que veio depois da voz foi graça; a leitura deste livro é secular, e ele a julgaria insuficiente. A linha que você vai traçar busca a ordem dada por inteiro, sem uma metade guardada para depois.", PI)
add("Ao nomear, vem uma proposta mais razoável que o <i>não ainda</i>: <i>e se eu só diminuir? Só nos dias bons, só um pouco.</i> É a última forma que o adiamento assume. Um gesto novo se forma aos poucos, por repetição; um hábito que se corta é deixado de uma vez.", PI)
add("Aristóteles pôs a virtude no meio-termo, entre o excesso e a falta. No mesmo capítulo (<i>Ética a Nicômaco</i> II, 6), avisa que nem toda ação admite meio: não há adultério bem feito, com a mulher devida, no momento devido. E o meio é relativo a nós. Para quem já desceu os três degraus de Agostinho, a medida justa daquele ato pode ser zero. Três capítulos adiante (II, 9), ele dá um conselho para o primeiro mês de um corte: quem quer chegar ao meio vai primeiro ao extremo contrário, como se faz com a vara torta que se quer endireitar.", PI)
add("Samuel Johnson, homem de letras do século XVIII inglês, de corpo enorme e apetites à altura, passou longos períodos sem vinho. Quando insistiam que bebesse só um pouco, respondia que não sabia beber pouco, e por isso não bebia: a abstinência lhe era fácil, a moderação seria difícil (paráfrase do que registram Boswell e Hannah More).", PI)
add("Há também o hábito com a forma de uma frase: <i>Eu nunca termino nada. Gente como a gente não chega lá.</i> Alguém a disse uma vez, numa cozinha qualquer, e já a esqueceu. Você continua a repeti-la como se ela descrevesse um fato. Uma frase herdada também se corta.", PI)
proc("Moderar ou cortar", [
 "Esta noite, lembre as vezes em que você tentou moderar esse hábito.",
 "Escreva como terminou cada uma.",
 "Se a moderação serviu e ainda serve, não corte. Feche este livro até precisar dele.",
 "Se a mesma tentativa terminou do mesmo modo várias vezes, você é da espécie de Johnson: corte.",
 "Se o hábito é uma frase herdada, nomeie-a por escrito, como nomearia um gesto.",
 "Toda noite, responda a essa frase com o que a folha de marcas mostra.",
])

sec("Do modo")
add("Os passos são sete. Os cinco primeiros se fazem entre esta noite e o fim de amanhã; os dois últimos começam amanhã e não terminam. Ficam aqui secos, para a hora da dúvida. Os quadros que vêm depois dizem quando fazer cada um.", PI)
corte = [
 ("Nomeie", "o que você vai deixar, com verbo e objeto, sem adjetivo: <i>faço X</i>, em vez de <i>sou um desastre</i>. Depois, a ocasião: lugar, hora, estado, companhia. E o pagamento: alívio, excitação, fuga, companhia."),
 ("Trace a linha", "à mão, numa frase absoluta, curta, no presente, com a data: <i>A partir de hoje, não ____.</i> Sem “vou tentar”, sem “vou diminuir”, sem “quase nunca”. Escreva-a numa hora fria, longe da ocasião. Assine. Copie-a para o alto de <i>Dias limpos</i>, a página 35 do caderno."),
 ("Queime as pontes", "no mesmo dia, enquanto a decisão está quente: jogue fora, afaste, tranque, entregue a chave a outra pessoa. Cada passo a mais entre o impulso e o ato é tempo a mais para a onda passar."),
 ("Mude o terreno", "onde o hábito morava. Se vivia num lugar, mude o lugar; se vivia numa hora, ocupe a hora; se vivia numa sequência, quebre a sequência."),
 ("Ponha algo no lugar:", "um gesto escrito antes, para o instante em que a ocasião chegar: <i>quando acontecer ____, eu faço ____</i>. Para o instante, basta um gesto; para a vida, a paixão contrária da seção seguinte."),
 ("Atravesse a onda", "com a nona linha, todas as vezes que a vontade vier: <i>É a onda. Ela sobe, e passa. O que faço com as mãos agora?</i>"),
 ("Conte os dias", "em <i>Dias limpos</i>: uma casa em cada noite em que você não cedeu. Se você cair, <i>caí; a linha continua</i>, e nunca dois dias seguidos."),
]
for i,(a,b) in enumerate(corte,1):
    add(f"{rom(i)}. &nbsp;<b>{a}</b> {b}", LAW)

proc("Esta noite: nomear", [
 "Numa página nova do caderno, escreva o comportamento, com verbo e objeto.",
 "Se saiu um adjetivo, risque e escreva de novo.",
 "Embaixo, escreva onde e quando ele aparece.",
 "Escreva em que estado você está e com quem.",
 "Escreva o que ele lhe paga.",
 "Se não achar o pagamento, lembre a última vez: o minuto antes e o minuto depois.",
 "Feche o caderno sem traçar a linha.",
 "Vá dormir.",
])
proc("Amanhã de manhã: a linha", [
 "Faça os minutos de sempre: caderno aberto, estribilho, linha da manhã, breviário.",
 "Longe da hora do hábito, escreva embaixo do nome: <i>A partir de hoje, não ____</i>.",
 "Escreva a data.",
 "Se a mão escrever <i>vou tentar</i> ou <i>quase nunca</i>, risque e recomece.",
 "· É o <i>não ainda</i> pedindo um lugar na frase.",
 "Assine.",
 "Copie a linha, a data e a assinatura para o alto de <i>Dias limpos</i>, a página 35.",
])
add("No canto XII da <i>Odisseia</i>, Circe avisa Ulisses: duas sereias cantam num prado à beira-mar, e em volta delas há um monte de ossos de homens. Quem ouve o canto não volta para casa. Para os companheiros, cera nos ouvidos. Para ele, se quiser ouvir, cordas: que o amarrem de pé ao mastro e, se ele pedir que o soltem, que apertem os nós.", PI)
add("Quando o navio passa, as sereias oferecem saber tudo o que se passou em Troia e tudo o que acontece sobre a terra. O que tenta Ulisses é uma coisa nobre posta no lugar errado. Ele pede com as sobrancelhas que o soltem; Perimedes e Euríloco o amarram com mais cordas. O navio passa.", PI)
add("A sua manhã copia três coisas dessa cena. A decisão foi tomada longe das sereias, em terra firme; ao alcance do canto não se decide nada de importante. Ulisses deu ordem para que desobedecessem às suas ordens futuras, porque sabia que, na hora, pediria com toda a convicção. A linha assinada é essa ordem. Quem decidiu em terra firme foi você, com o rosto dele; quem pede no meio do canto é a voz antiga, e ela já não tem autoridade sobre a linha.", PI)
add("E há duas maneiras de passar. A cera é não se expor; o mastro é se expor amarrado. Use a cera sempre que puder. O mastro fica para a ocasião que não se pode evitar, e mesmo então as cordas se põem antes.", PI)
add("No verão de 1830, Victor Hugo devia ao editor um romance que adiava havia muito, e o editor lhe deu um prazo final. Segundo Adèle, a mulher dele, Hugo comprou um frasco de tinta e um agasalho de lã que o cobria da cabeça aos pés. Trancou à chave a roupa de sair, para não pôr os pés na rua, e entrou no romance como numa prisão. Terminou <i>Notre-Dame de Paris</i> em janeiro de 1831, e o frasco de tinta, conta ela, acabou ao mesmo tempo.", PI)
add("O eu da manhã não estará presente quando o eu da noite quiser ceder. Só pode lhe deixar o terreno arrumado. O esforço se gasta uma vez, de antemão, para não ter de ser pedido todas as noites.", PI)
proc("No resto do dia: as pontes", [
 "Faça a lista das pontes: cada objeto, caminho, hora e companhia que deixam o hábito ao alcance.",
 "Procure a sua roupa de sair: a ponte que, trancada, fecha o caminho.",
 "Ao lado de cada ponte, escreva o que vai fazer com ela.",
 "Faça.",
 "Risque cada ponte feita.",
 "Se uma ponte não sai hoje, afaste-a e escreva o dia em que vai removê-la.",
 "Se o hábito morava num lugar, não se sente lá esta noite.",
 "Se morava numa hora, ponha outra coisa nessa hora.",
 "Se morava numa sequência (um jantar, um caminho), quebre-a num ponto à sua escolha.",
])
proc("Antes da primeira ocasião: o gesto", [
 "Embaixo das pontes, escreva: <i>quando acontecer ____, eu faço ____</i>.",
 "Escolha um gesto curto, feito com as mãos, possível em qualquer lugar.",
 "· Exemplos: levantar e mudar de sala, sair para andar, abrir a obra.",
])
add("Dostoiévski desafiava o leitor a não pensar num urso branco. Em 1987, um estudo de Daniel Wegner levou o desafio ao laboratório e encontrou o rebote: quem tentava não pensar no urso pensava nele mais de uma vez por minuto, e depois mais ainda. No mesmo estudo, quem recebeu uma imagem alternativa, definida de antemão, teve rebote muito menor. Um corte feito só de <i>não</i> alimenta o que proíbe. O gesto que você escreveu é a imagem definida de antemão.", PI)
add("A primeira onda vem na hora de sempre ou fora dela. Ela não diz <i>quebre a linha</i>. Diz <i>só hoje</i>, ou <i>só para ver como é</i>, ou <i>já decidi, posso ficar perto sem ceder</i>. A partir deste dia, a nona linha do Livro I é sua.", PI)
proc("Na onda", [
 "Diga a nona linha: <i>É a onda. Ela sobe, e passa. O que faço com as mãos agora?</i>",
 "Não discuta com ela.",
 "Faça o gesto que escreveu.",
 "Se ela vier com muita força, abra o caderno e leia a frase da anti-visão.",
 "Se ela disser que você está seguro perto da ocasião, levante-se e saia de onde está.",
])
add("Sobre a terceira frase, a de quem se julga seguro perto da ocasião, Agostinho conta de Alípio. Em Roma, colegas o arrastaram ao anfiteatro num dia de gladiadores, espetáculo que ele detestava. Ele lhes disse: podeis levar o meu corpo; estarei ausente, mesmo estando presente. Sentou-se e fechou os olhos.", PI)
add("Um homem caiu na arena, a multidão rugiu, e o grito entrou pelos ouvidos dele. Seguro de que saberia desprezar o que visse, abriu os olhos. Viu o sangue e bebeu com ele a crueldade. Saiu de lá como um da multidão, e voltou depois, e levava outros. A decisão era firme, dita diante de testemunhas; ele caiu porque confiou nela num lugar onde ela não podia valer.", PI)
add("A nona linha tem uma antepassada. Epicteto dizia aos alunos (<i>Discursos</i> II, 18): quando a impressão pegar você, diga a ela <i>espere um pouco por mim, impressão; deixe-me ver quem você é</i>. Não a deixe desenhar a cena seguinte, e a seguinte. Traga para o lugar dela outra impressão, bela e nobre. Um intervalo, um exame, uma substituição: é a nona linha, e é o quinto passo.", PI)
proc("À noite: a primeira casa", [
 "Depois da marca, abra <i>Dias limpos</i>.",
 "Se você não cedeu, preencha a primeira casa.",
 "Se você cedeu, deixe a noite sem casa.",
 "Se você cedeu, leia <i>Da queda</i> esta noite, antes de dormir.",
])

sec("Da paixão contrária")
add("<i>“Um afeto não pode ser refreado nem suprimido senão por um afeto contrário e mais forte.”</i>", ParagraphStyle('sp1', parent=PC, fontSize=12, spaceAfter=2))
add("Espinosa, <i>Ética</i>, IV, proposição 7", ParagraphStyle('sp2', parent=EPA, spaceAfter=14))
add("Depois de alguns dias, você percebe uma coisa que os passos não resolvem. A hora em que o hábito morava ficou vazia. O gesto cobre o instante da onda, e o instante passa; a hora inteira fica, e as mãos não sabem o que fazer com ela. Vem um tédio sem dono, uma inquietação sem objeto. Se nada ocupar o lugar, o velho hábito volta a ocupá-lo.", PI)
add("Baruch de Espinosa, filósofo de Amsterdã do século XVII, escreveu a <i>Ética</i> como um livro de geometria. Chamava de afeto o que aumenta ou diminui a nossa força de agir. Na frase acima, diz que um afeto só cede a outro, contrário e mais forte. Uma ordem da razão, sozinha, não desloca um desejo. A linha e as pontes tiram o hábito do caminho; falta querer outra coisa com força.", PI)
add("Algumas proposições adiante (IV, 14), Espinosa diz que saber o bem e o mal não refreia afeto nenhum enquanto é só saber. Saber que o hábito lhe faz mal não pesa nada na balança. Começa a pesar quando vira desejo, quando você quer outra coisa com a força com que queria aquela.", PI)
add("Thomas Chalmers, pregador escocês do começo do século XIX, chamou isso de <i>o poder expulsivo de uma nova afeição</i>. Mostrar a um homem que o que ele ama é vão não dá certo, dizia, porque o coração não suporta ficar vazio. Arrancado o objeto sem outro no lugar, ele volta ao antigo, que é o que conhece. Alguma afeição vai ocupar o lugar; convém que seja você a escolhê-la.", PI)
add("Em maio de 1521, em Pamplona, Íñigo de Loyola, fidalgo basco de trinta anos, vaidoso, dado a armas e a damas, teve uma perna quebrada por uma bala de canhão. Os ossos se soldaram mal. Ele deixou que os quebrassem de novo, sem dizer palavra, e depois mandou serrar um osso saliente, por vaidade. Na convalescença, em Loyola, pediu romances de cavalaria. Não havia nenhum em casa. Deram-lhe uma vida de Cristo e um livro de vidas de santos.", PI)
add("Ele se viu alternando dois devaneios: as façanhas para servir uma dama muito acima dele, e a pergunta <i>e se eu fizesse o que fez São Francisco?</i> Os pensamentos da dama davam gosto enquanto duravam e, largados, o deixavam seco e descontente. Os outros o deixavam contente também depois. Ninguém pregou para ele contra os romances. A paixão maior foi ocupando o lugar da menor, à força de comparação, e a menor saiu.", PI)
add("Íñigo escolheu a paixão nova pelo que ela deixava depois. E a troca começou porque faltaram os romances: a ponte queimada, por acaso, abriu o lugar, e o resto dependeu do que se pôs dentro dele.", PI)
proc("A paixão contrária", [
 "Numa destas noites, abra a página do nome do hábito.",
 "Meça o vazio: quanto tempo o hábito ocupava, em que horas, o que pagava.",
 "Escolha uma ocupação que exija o corpo ou a obra e tenha progresso visível.",
 "Escolha-a tão difícil quanto o hábito era fácil: correr, lutar, um instrumento, uma língua, a obra.",
 "Se o hábito pagava alívio, escolha algo que esgote. Se pagava excitação, algo que desafie.",
 "Escolha o que, uma hora depois, deixa você contente por ter feito.",
 "Ponha a paixão exatamente na hora e no lugar onde o hábito morava.",
 "Escreva-a embaixo da linha: o que é, a hora em que entra, o primeiro número a alcançar.",
 "Anote números crescentes: mais distância, mais carga, mais páginas, mais horas.",
 "Nos primeiros meses, deixe que ela tome mais espaço do que pareceria razoável.",
 "· O excesso é a vara torta de Aristóteles: é ele que expulsa o velho.",
 "Se ela virar fuga, ou ferir o sono, o corpo ou as pessoas, releia o §8.",
])

sec("Da queda")
add("Logo depois de ceder vem uma frase: <i>já que caí, o dia está perdido</i>. Ou <i>amanhã recomeço do zero</i>, ou <i>afinal não sou capaz</i>. É essa frase que faz de uma recaída muitas.", PI)
proc("No dia da recaída", [
 "Diga por dentro, inteira: <i>caí; a linha continua</i>.",
 "Se outra ocasião vier hoje, passe por ela com o gesto.",
 "À noite, deixe <i>Dias limpos</i> sem casa.",
 "Não apague nem reescreva a linha do alto da página.",
 "Escreva a linha da queda: onde foi e o que vai fazer diferente.",
 "Nomeie a ocasião que trouxe a recaída.",
 "Se ela abriu uma ponte que você não tinha visto, ponha-a na lista e afaste-a.",
 "· Pelo §4, nada volta ao começo.",
])
proc("No dia seguinte", [
 "· Nunca dois dias seguidos. O corte não tem piso: nem doente, nem em viagem.",
 "De manhã, releia a linha.",
 "Releia a lista das pontes.",
 "Preveja onde a ocasião de ontem vai voltar.",
 "Ponha o gesto à frente dela antes que ela chegue.",
])
add("Alan Marlatt, psicólogo americano que estudou recaídas, deu nome ao <i>já que caí</i>: efeito de violação da abstinência. Ele observou que quem explicava a recaída pelo caráter (<i>sou fraco, nunca vou conseguir</i>) deixava uma recaída virar muitas. Quem a explicava pela ocasião (<i>estava cansado, estava sozinho, estava ali</i>) voltava à linha mais vezes.", PI)
add("Por isso a frase deste livro não pede que você se sinta bem com a recaída, nem deixa que você se condene por ela. Pede que você anote a ocasião. Uma ocasião nomeada se evita ou se prepara; um juízo sobre o próprio caráter não indica nada que se possa fazer.", PI)
add("A mulher de <i>Do primeiro dia</i> fez o corte dela na segunda estação. O hábito eram os vídeos no telefone, no ônibus da volta e no sofá, entre o jantar e a mesa; às oito e meia ela se sentava com a cabeça em pedaços, e a primeira página levava meia hora. No domingo à noite, nomeou: <i>vejo vídeos no telefone</i>; no ônibus das seis e vinte e no sofá, cansada, sozinha; o pagamento, o alívio do escritório. Na segunda de manhã, depois dos minutos de sempre, escreveu a linha, <i>A partir de hoje, não vejo vídeos no telefone</i>, com a data, e assinou. No mesmo dia apagou o aplicativo e saiu da conta, passou a jantar na mesa da cozinha, longe do sofá, e escreveu o gesto: <i>quando a mão procurar o telefone, ele vai para o fundo da bolsa e eu abro o caderno de questões</i>. Segunda, terça e quarta ganharam casa.", PI)
add("Na quinta, depois de uma reunião ruim, a onda disse <i>só um, para desligar</i>. O aplicativo não estava lá, e o navegador abriu o mesmo site. Ela desceu duas paradas depois da sua, e no caminho de volta veio a frase: <i>gente como eu não larga isso</i>. Disse por dentro <i>caí; a linha continua</i>. Em casa, a ocasião seguinte foi o sofá, e ela passou por ele com o telefone na bolsa. À noite, depois da marca da vez, <i>Dias limpos</i> ficou sem casa, e a linha da queda ficou na ocasião: <i>Onde: o ônibus das seis e vinte, depois da reunião, pelo navegador. Diferente: saio da conta no navegador também.</i> O navegador entrou na lista das pontes, e ela saiu da conta ali mesmo. Na sexta não havia piso a declarar, porque o corte não tem. De manhã, releu a linha e as pontes e previu o ônibus. Às seis e vinte, antes de subir, pôs o telefone no fundo da bolsa e o caderno de questões na mão. A onda veio na segunda parada, com a mesma frase, e ela a nomeou e abriu o caderno na questão marcada. À noite, ela preencheu a quarta casa; a contagem não tinha voltado ao começo.", PI)
add("Tolstói, aos dezoito anos, começou em Kazan diários que abrem com regras de vida. As páginas dos anos seguintes voltam a elas sem parar: o jogo, a ociosidade, a resolução de recomeçar no dia seguinte, a recaída, a resolução de novo. Em 1854, para pagar dívidas de jogo, vendeu a casa principal de Iásnaia Poliana, que foi desmontada e levada embora. O homem que escreveria <i>Guerra e paz</i> naquela terra passou anos fazendo listas novas. Cada promessa feita sem mudar a ocasião abria caminho à recaída seguinte.", PI)
add("Não espere que a linha cale tudo. Mais de dez anos depois do jardim, já bispo, Agostinho escreveu (<i>Confissões</i> X) que as imagens dos velhos hábitos continuavam vivas na memória: fracas de dia, fortes no sono. Ele não concluiu que o jardim tinha sido inútil. Concluiu que a memória guarda o que o corpo já deixou, e que guardar a linha é trabalho que não acaba no dia em que ela é traçada.", PI)

sec("Da contagem")
add("Nas noites seguintes, a contagem se faz quase sem palavras: a marca e, depois, uma casa em <i>Dias limpos</i>. Um corte de cada vez.", PI)
add("A contagem vem de Epicteto (<i>Discursos</i> II, 18). Todo hábito se conserva e cresce pelos atos que lhe correspondem: anda-se melhor andando. O mesmo vale para o que você quer perder. Quando você cede à ira, diz ele, alimenta o hábito e põe lenha na fogueira; a abstenção também se acumula. Conte os dias em que não se irritou: <i>eu me irritava todos os dias; agora, um sim, outro não; depois, a cada três</i>. E, se chegar aos trinta, ofereça um sacrifício aos deuses.", PI)
add("Epicteto avisa também que as doenças do espírito deixam marcas, como a febre deixa no corpo. A mesma ocasião reabre a ferida mais depressa que da primeira vez. A contagem que cresce diz que a cicatriz está fechando, e uma cicatriz recente se rasga com pouco.", PI)
proc("Trinta e noventa", [
 "Na noite da trigésima casa, demore um minuto a mais.",
 "Releia a linha do alto da página.",
 "Releia a lista das pontes e as linhas da queda do corte.",
 "Releia o número da paixão contrária.",
 "Escreva o que mudou nas horas que o hábito ocupava.",
 "Na nonagésima casa, faça o mesmo.",
 "Depois delas, continue a linha e a contagem.",
 "· Trinta e noventa são marcos para olhar para trás. Não são prazo para afrouxar.",
 "Se uma voz disser que você já está seguro perto da coisa, não reabra ponte nenhuma.",
])
add("Há hábitos que já não obedecem à decisão, por mais firme que ela seja. Se a linha cai uma vez e outra, se você caiu dois dias seguidos apesar das pontes, do gesto e da paixão contrária, ou se o hábito já está lhe custando a saúde, o dinheiro ou as pessoas, procure ajuda profissional. Procurá-la faz parte do corte.", NOTE)
add("Daqui em diante, você anda com a da vez numa mão e um corte na outra. Um método levado a sério assim, com leis, marcas e linhas absolutas, pode se voltar contra quem o usa: endurecê-lo, deixá-lo surdo para o corpo, fazer de cada falha uma acusação. Contra isso as leis não bastam. É preciso juízo, e o juízo tem um livro próprio.", PI)
proc("Antes de seguir", [
 "Se a linha não está no presente, datada e assinada no alto de <i>Dias limpos</i>, refaça o segundo passo.",
 "Se nada foi riscado na lista das pontes, risque hoje, antes de dormir.",
 "Se a paixão contrária não está escrita, com a hora e o primeiro número a alcançar, escreva-a esta noite.",
 "Se você caiu dois dias seguidos, ou a linha cai uma vez e outra, procure ajuda profissional.",
])
# O fecho vai junto do parágrafo anterior, para não ficar sozinho no alto de uma página.
st[-2:] = [KeepTogether(st[-2:])]
# ===================== DO PÊNDULO =====================
estribilho_pagina()
st.append(PageBreak()); sp(30)
add("Em qualquer ponto das estações", LIV)
QUANDO["Do pêndulo"] = "quando o cansaço bater"
add("Do pêndulo", LT); sumario(st[-1], 0, "Do pêndulo")
SEC_NO_SUMARIO = True


sec("Do pêndulo")
abertura([("Quando ler", "Na noite do dia em que um peso bater no meio da obra e pedir para parar, fora das horas da obra. Ou antes, para reconhecê-lo."),
          ("Se a pergunta passar para a vida inteira", "Releia <i>Da descida</i>. Se vier a ideia de que seria melhor não estar aqui, fale hoje com alguém.")],
         "Os seis passos de <i>Do instante</i> sabidos de cor e, se o pêndulo bateu hoje, a linha da folha de captura decidida.")
add("Você está no meio do caminho. As primeiras semanas ficaram para trás, há microações entre as que ficaram, e o dia de hoje ia bem. Você não estava num trecho difícil. De repente, sem causa que você encontre, vem um peso no corpo, e com ele uma voz:", PI)
for v in ["Estou cansado.", "Será que tudo isso vale mesmo a pena?", "Estou muito cansado. Tenho de parar."]:
    add(v, VOICE)
add("Ela vem nesta ordem: primeiro o corpo, depois a pergunta, depois a conclusão. Não tem hora: vem depois de vinte minutos ou de duas horas. Passa em um minuto, ou vai, volta, e persiste. Por isso o livro a chama de pêndulo: ela oscila, e oscila sozinha.", PI)
add("Duas vozes se parecem com ela. A da linha II chega com o trecho difícil e pede para largar aquele trecho. O pêndulo bate também em trecho fácil, com a obra andando, e pergunta pelo valor do todo. A resistência que fala traz argumentos e volta igual noite após noite; o pêndulo traz um argumento só, o peso, e vai embora pelo próprio movimento. Se ele parar do mesmo lado por semanas, já não é pêndulo, e o Livro V tem as provas.", PI)
add("O pêndulo pede uma coisa só: você continua. A pergunta sobre se a obra vale a pena teve resposta no dia zero, por escrito, e no meio do passo ela não se reabre. É uma escolha do livro: no meio da obra, continuar vem antes de ouvir. Ouvir tem hora marcada: a noite, a passagem e, se o pêndulo deixar de oscilar, as quatro provas.", PI)

sec("Do instante")
add("Quando o pêndulo bate, a pergunta <i>isto vale a pena?</i> parece pedir resposta imediata. Ela é exame, e da maior espécie, e o exame pertence à noite. Os seis passos são a linha II e a folha de captura postas em ordem para este caso.", PI)
proc("Os seis passos", [
 "Repare que a voz veio e pergunta pelo todo. Não responda agora, nem a favor nem contra.",
 "Diga a linha II: <i>É vontade, não fato. Até o fim deste passo.</i>",
 "Termine o passo, com a mão no lugar.",
 "Se a pergunta insistir, escreva-a na folha de captura, com a hora, e volte à obra.",
 "No fim do passo, olhe outra vez. Se passou, siga. Se não, outro passo, até a hora de parar.",
 "À noite, depois da marca, decida a linha da captura: fazer amanhã, marcar para um dia ou riscar.",
 "· Se o pêndulo voltar sete dias seguidos sem passar, já não é pêndulo: faça as quatro provas.",
])
add("Na folha de captura basta uma linha: <i>dez e quarenta, cansado, vale a pena?</i> Escrita, a pergunta sai da cabeça e espera pela noite. O peso que você sente é real; a conclusão que ele tira, <i>tenho de parar</i>, pertence à vontade.", PI)
sp(4)
add("D O &nbsp; P O R Q U Ê", LBX)
add("<b>A ideia.</b> Os monges do deserto egípcio conheciam esse peso e o chamavam de acédia. Evágrio Pôntico lhe deu como remédio a <i>hypomoné</i>, a perseverança; ao pé da letra, ficar debaixo, aguentar sem sair do lugar. O pêndulo pede que você saia, e a resposta dos monges era ficar o tempo necessário para ele passar.", PI)
add("<b>O mecanismo.</b> A pergunta pelo todo, feita no meio do peso, é julgada por um juiz que naquele instante só vê o peso. Escrita e adiada, ela é julgada à noite, com as folhas à frente e de cabeça mais fria. O passo pequeno deixa o tempo correr sem obedecer, e o pêndulo volta sozinho para o outro lado. Nenhum estudo testou esses passos: é o autor quem acha, com os autores das seções seguintes.", PI)
add("<b>Por isso.</b> <i>Faço isto porque o cansaço do instante não responde pelo todo, e o pêndulo que não obedeço volta sozinho.</i>", PI)

sec("Do demônio do meio-dia")
add("Evágrio nasceu no Ponto, à beira do mar Negro, por volta de 345, e foi pregador conhecido em Constantinopla. Depois de uma crise, foi viver como monge no deserto do Egito, onde morreu em 399. Escreveu para outros monges o <i>Prático</i>, um manual curto em capítulos numerados, sobre os pensamentos que os assaltavam no trabalho de cada dia.", PI)
add("<i>Akédia</i> quer dizer falta de cuidado: o estado de quem deixou de se importar. Evágrio a situa no meio do dia, quando o fervor da manhã passou e o fim ainda não se vê. O alvo dela é fazer o monge sair: da cela, do trabalho, da vida que escolheu. O demônio o faz odiar o lugar, a vida que leva e o trabalho das mãos (<i>Prático</i>, 12). A arma é o tempo: o presente parece longuíssimo e o futuro vazio. É a pergunta do pêndulo, <i>isto vale a pena?</i>, feita ao meio-dia.", PI)
add("O remédio tem três partes. A primeira é não sair da cela na hora da tentação (<i>Prático</i>, 28, paráfrase): a decisão grande, tomada naquela hora, seria tomada pela acédia. A segunda é dividir a alma em duas, uma parte que fala e outra que ouve, e falar consigo com exatidão, sem negar o peso nem lhe dar razão (27, paráfrase). A terceira é a perseverança: ficar debaixo do peso enquanto ele dura.", PI)
add("No fim do capítulo do demônio do meio-dia, Evágrio escreve que, depois dessa luta, ficam na alma um estado de paz e uma alegria indizível (12, paráfrase). Terminar o passo é ficar na cela. A linha da folha de captura é a parte que fala à outra, e lhe diz um fato: a pergunta será ouvida à noite. Se hoje você ficou, repare, uma hora depois, se veio uma calma que você não esperava.", PI)

sec("Do fastio")
add("Sêneca escreveu a um amigo mais novo, Aneu Sereno, o tratado <i>Da tranquilidade da alma</i>. Sereno descrevia o seu estado: não estava doente, e também não estava são. Decidia uma vida e, dias depois, desanimava dela e desejava outra. Nada o prendia por muito tempo.", PI)
add("Sêneca chama o mal de desagrado de si, <i>displicentia sui</i>, e de fastio, <i>taedium</i>: o espírito que não se assenta em lugar nenhum. Quem sofre disso viaja, muda de casa, troca de ocupação, esperando que a próxima o liberte. De que serve fugir, pergunta Sêneca, se cada um segue a si mesmo e pesa sobre si mesmo, o mais pesado dos companheiros? A causa está no espírito. O remédio é a dedicação constante a uma ocupação escolhida, alternada com um descanso que tem a sua medida.", PI)
add("Junto com <i>isto vale a pena?</i> vem uma pergunta mais baixa: <i>outra coisa valeria</i>. Outra obra, outro domínio, outro método. Pelo diagnóstico de Sêneca, o peso vai com você para a seguinte; a outra coisa só parece leve porque você ainda não a carregou. Por isso as emendas esperam a passagem (§9). O que o pêndulo disser fica na folha de captura, e se for verdade, será verdade também na passagem.", PI)
add("No outono de 1849, Flaubert leu aos amigos Louis Bouilhet e Maxime Du Camp, em quatro dias, a primeira <i>Tentação de santo Antão</i>, que tinha por sua obra-prima. Segundo Du Camp, os dois lhe disseram que a jogasse ao fogo e tomasse um assunto comum. Dali saiu <i>Madame Bovary</i>, escrita de 1851 a 1856. Nas cartas a Louise Colet, ele se queixa do livro: dias inteiros para uma página, saudade dos assuntos grandiosos, a vontade de outra obra a cada trecho difícil. E não trocou de obra. A queixa ia para as cartas, à noite, e no dia seguinte ele voltava à mesma página.", PI)
add("Na décima sexta carta a Lucílio, Sêneca pede ao amigo que persevere até que seja boa mente o que agora é boa vontade. A boa vontade, <i>bona voluntas</i>, quer o bem e precisa ser defendida a cada vez. A boa mente, <i>bona mens</i>, é o espírito assentado, em que o bem virou a maneira de agir. Só se passa de uma à outra perseverando, nos dias em que a boa vontade é posta à prova. Os dias do pêndulo são desses.", PI)

sec("Da obra de homem")
add("O Livro I começou com Marco Aurélio debaixo das cobertas, numa manhã em que lhe custava se levantar. O resto do trecho responde à frase <i>tenho de parar</i>.", PI)
add("Ele faz a si mesmo a objeção: mas também é preciso descansar. E responde que sim. A natureza deu medida ao descanso, como ao comer e ao beber, e ele passa da medida; nas ações, fica aquém do que pode. Depois se acusa: você não ama a si mesmo, porque, se amasse, amaria a sua natureza e o que ela quer. E lembra os que amam o seu ofício e se gastam nele, esquecidos de se lavar e de comer (<i>Meditações</i>, V, 1, paráfrase).", PI)
add("Para o estoico, o amor de si é o amor da própria natureza, e quem o tem quer a obra dela, como o artesão quer o seu ofício. O conforto e o prazer eram coisas indiferentes. Perguntar se nasceu para ficar aquecido é perguntar para que serve um homem.", PI)
add("O livro já lhe deu a medida do descanso: a hora de parar, escrita toda manhã, e o dia de ócio, declarado na véspera. Quando o pêndulo diz <i>tenho de parar</i> às dez e quarenta de uma manhã que ia bem, pede descanso fora da medida. A resposta de Marco Aurélio é a que você já escreveu: você descansa na hora que marcou. O que vale está na folha do dia zero, e o peso de uma manhã não tem autoridade para revisá-lo.", PI)
add("Fica a imagem de alguém que ama o que faz e por isso continua nos dias em que não tem vontade.", PI)

sec("Do segundo fôlego")
add("Em dezembro de 1906, William James, o psicólogo mais conhecido dos Estados Unidos, leu a conferência <i>As energias dos homens</i>. Ele começa por uma experiência que todos conhecem: pegar um trabalho sem vontade nenhuma e ir se aquecendo nele.", PI)
add("A forma mais clara desse aquecimento é o segundo fôlego. Paramos uma ocupação, diz James, na primeira camada séria de fadiga. Se uma necessidade nos obriga a continuar, a fadiga piora até um ponto crítico e depois passa, e ficamos mais descansados do que antes. E pode haver um terceiro e um quarto fôlego. James sabia que as árvores não crescem até o céu. Pedia só que a primeira fadiga não fosse tomada pela última.", PI)
add("O pêndulo bate na primeira camada. O passo da linha II é a maneira pequena de ver se há mais por baixo, sem prometer nada a você. O que James reuniu foram cartas e testemunhos, sem medição, e não está demonstrado que a fadiga do espírito tenha camadas assim. O autor acha que basta isto: a primeira fadiga não mede o que resta.", PI)
add("Sobre a força de vontade, há indícios mais recentes. Em 2016, uma réplica de Martin Hagger e colegas em vinte e três laboratórios encontrou perto de zero o efeito que Roy Baumeister chamara de esgotamento do ego. Em 2010, Veronika Job, Carol Dweck e Gregory Walton observaram que quem acreditava que a vontade não se esgota depressa não mostrava a queda depois de uma tarefa exigente. O efeito de dormir pouco está demonstrado. Quando o <i>estou muito cansado</i> chega numa manhã que ia depressa, o autor acha que vem do que você esperava sentir.", PI)

sec("Da descida")
add("A última voz é a de Albert Camus. Nascido em 1913 na Argélia, numa família pobre, ele publicou <i>O mito de Sísifo</i> em 1942, na França ocupada. O livro começa dizendo que julgar se a vida vale a pena ser vivida é a questão fundamental da filosofia. Absurdo, para Camus, é o choque entre a exigência humana de sentido e um mundo que não responde a ela.", PI)
add("Acontece, diz Camus, que os cenários desabam. Acordar, o bonde, quatro horas de escritório ou de fábrica, a refeição, o bonde, quatro horas de trabalho, a refeição, o sono, e segunda, terça, quarta, quinta, sexta e sábado no mesmo ritmo. Um dia, apenas, surge o porquê, e tudo começa nesse cansaço tingido de espanto.", PI)
add("Para Camus, o <i>por quê?</i> no meio da rotina é o começo da lucidez. O erro está nas duas fugas: abandonar, e saltar para uma esperança que dispense a pergunta. Os deuses condenaram Sísifo a empurrar um rochedo até o alto, de onde ele volta a rolar, sem fim. O que interessa a Camus é a descida, quando Sísifo volta ao rochedo: essa é a hora da consciência, e nela Sísifo é superior ao seu destino. O ensaio termina dizendo que a luta para chegar aos cumes basta para encher um coração de homem, e que é preciso imaginar Sísifo feliz (tradução livre).", PI)
add("A pergunta do pêndulo é legítima, e você não precisa se envergonhar dela. Ela não obriga a largar a obra: Sísifo faz a pergunta e volta ao rochedo. Aqui a pergunta tem hora: no meio do passo, vai para a folha de captura e espera a noite. A sua obra foi escolhida por você no dia zero, e não rola de volta: a linha do dia mostra, noite após noite, o que passou a existir.", PI)
add("Se, em vez de <i>isto vale a pena?</i>, vier a ideia de que seria melhor não estar aqui, a pergunta saiu da obra e pertence a outro lugar. É o terceiro sinal de <i>Do escrúpulo</i>, e pede que você fale com alguém hoje.", PI)

sec("Do que volta")
add("O pêndulo volta, amanhã ou daqui a três semanas, com as mesmas palavras. A volta diz só que você ainda está no trecho do caminho em que ele oscila. Evágrio escrevia para monges com anos de cela, e Marco Aurélio escreveu o quinto livro quando já era imperador havia muito. Nenhum deles conta que o pêndulo tenha deixado de vir de vez.", PI)
add("Mas ele muda. O que se sofre repetidamente pesa menos, e o que se faz repetidamente se faz melhor. Uma obra feita na mesma hora e no mesmo lugar começa e continua quase sozinha, e dá ao pêndulo menos ocasião. O autor acha que, com o tempo, ele bate mais fraco e mais raro; as suas folhas, relidas numa passagem, dirão quanto. Chega um dia em que a voz vem, a mão continua, e só à noite, ao fazer a marca, você se lembra de que ela veio.", PI)
add("Há um peso que não oscila. Vem no fim, depois de horas: os olhos já não seguram a linha, o mesmo erro se repete, a mesma frase é lida três vezes sem entrar. Não pergunta pelo valor de nada. Diz que o corpo chegou ao fim do que tinha para hoje, e não passa no fim do passo.", PI)
proc("O peso que não passa", [
 "Se o peso não passa no fim do passo nem do seguinte, termine a sessão no fim do passo.",
 "Escreva a quinta linha.",
 "Se a hora de parar chegou, termine o passo e feche a obra, sem culpa.",
 "Se a dúvida ficar, faça amanhã de manhã a prova do sono.",
 "Se você acordou com febre, o dia é de piso: escreva <i>hoje, piso</i> de manhã.",
 "Se a prova do sono falhou três manhãs seguidas, com a hora de parar cumprida, declare na véspera um dia de ócio.",
 "Se o sono não descansa sete noites seguidas, leia <i>Do escrúpulo</i>.",
])
add("Evágrio deixou aos monges um conselho do seu mestre: viver como quem vai morrer amanhã, e tratar o corpo como quem vai viver muitos anos (<i>Prático</i>, 29, paráfrase). A primeira metade corta a acédia, porque a obra de hoje importa hoje. A segunda mantém o corpo na medida, para que a obra dure.", PI)
proc("Esta noite", [
 "Faça a marca.",
 "Escreva a linha do dia.",
 "Escreva a linha da queda.",
 "Se o pêndulo bateu, decida a linha que ele deixou na folha de captura.",
 "Escreva a primeira tarefa.",
 "Amanhã, ao sentar para a obra de hoje, diga a frase: <i>Isto, até acabar</i>.",
])
add("Se o pêndulo voltar, vai encontrar você diante de uma coisa só.", PI)
proc("Antes de seguir", [
 "Se você não sabe de cor os seis passos de <i>Do instante</i>, releia-os antes da próxima obra.",
 "Se o pêndulo bateu hoje e a pergunta não está na folha de captura, escreva-a agora.",
 "Decida-a como as outras linhas.",
 "Se a pergunta passou da obra para a vida inteira, leia os sinais em <i>Do escrúpulo</i>.",
 "Se vier a ideia de que seria melhor não estar aqui, procure ajuda hoje.",
]); fleur()
# O fecho vai junto do parágrafo anterior, para não ficar sozinho numa página.
st[-3:] = [KeepTogether(st[-3:])]

# ===================== LIVRO V: DISCERNIMENTO =====================
livro("V", "Do discernimento")
add("<i>“A virtude é um meio-termo, determinado pela razão, tal como o determinaria o homem prudente.”</i>", ParagraphStyle('ds1', parent=PC, fontSize=12, spaceAfter=2))
add("Aristóteles, <i>Ética a Nicômaco</i>, II", ParagraphStyle('ds2', parent=EPA, spaceAfter=18))
add("O estado de foco também pede juízo, e o juízo se aprende. Este livro ensina a reconhecer quando uma regra ainda serve à obra e quando deixou de servir, e quando uma resistência é preguiça e quando traz uma informação.", PI)
abertura([("Quando ler", "Inteiro, no meio das estações, numa noite sem pressa. <i>Da prova</i>, agora, uma vez só."),
          ("Quando voltar a <i>Do escrúpulo</i>", "Quando a anti-visão ou o exame da noite afundarem você, ou a marca não se decidir sete noites seguidas."),
          ("Se o caderno pesa mais do que ajuda", "Comece por <i>Do escrúpulo</i>.")],
         "A página das quatro provas com a conclusão embaixo, e os cinco sinais de <i>Do escrúpulo</i> sabidos sem abrir o livro.")
add("Se você chegou aqui pela ordem, muitas noites se passaram. Há microações entre as que ficaram, um corte com a contagem correndo, e a folha de marcas cheia de traços, de algumas cruzes e de umas poucas noites de <i>chegou</i>. Este é o trecho plano e longo do caminho. Nele o método encontra o que nenhuma regra escrita antecipa: uma doença em casa, um filho que nasce, um pai que morre, uma mudança de cidade. Um mês em que o sono do §8 não se cumpre porque alguém precisa de você à noite. Um exercício cumprido à risca que deixou de fazer sentido.", PI)
add("Este livro foi escrito para quem sabe o que deve fazer e não faz. Para essa pessoa, a resistência é para atravessar. Mas ninguém está nesse lugar o tempo todo, e um método que não reconhece os próprios limites acaba quebrando quem o usa.", PI)
add("Aristóteles chamava de <i>phrónesis</i>, prudência, a virtude que decide as outras: saber o que convém, a quem, quando e quanto. A coragem sem prudência vira temeridade; a firmeza sem prudência vira rigidez. Nenhuma lei deste livro dispensa o juízo, e as leis servem para que ele não seja usado como desculpa. A epígrafe diz que o meio é determinado pela razão, tal como o determinaria o homem prudente. Aristóteles também mede o ato por um homem. Diante do caso difícil, você pergunta <i>O que ele faria agora?</i>, e as provas deste livro garantem que <i>ele</i> tem juízo.", PI)
add("A prudência trata de coisas particulares, que podem ser de outra maneira, e por isso não é ciência. Um rapaz pode ser bom geômetra, observa Aristóteles no sexto livro, mas não se vê um rapaz prudente: a prudência pede experiência, e a experiência pede tempo. Por isso este livro se lê no meio do caminho.", PI)
add("Aristóteles compara quem conhece o seu fim a um arqueiro com um alvo (I, 2). O seu alvo está escrito desde o dia zero, na visão e na anti-visão. Mas o vento muda, a distância muda, e o mesmo alvo pede, a cada tiro, outra pontaria. Errar é fácil e acertar é difícil, escreve (II, 6), porque há muitas maneiras de errar e uma só de acertar. Apertar a lei quando a vida mudou e afrouxá-la quando ela só custa são duas maneiras de errar o mesmo alvo.", PI)
add("O primeiro dos <i>Aforismos</i> de Hipócrates diz: a vida é breve, a arte é longa, a ocasião é fugaz, a experiência enganadora, o juízo difícil. Os gregos chamavam o momento oportuno de <i>kairós</i>. O bom médico sabe a regra e sabe quando ela se aplica a este doente, hoje. É isso que este livro pede a você para as leis do método.", PI)
add("Pascal distinguiu dois espíritos nos <i>Pensamentos</i>. O de geometria trabalha com poucos princípios nítidos: custa vê-los, mas, uma vez vistos, ninguém se engana a partir deles. O de finura trabalha com princípios que estão diante de todos, tantos e tão sutis que é preciso vê-los com um só olhar. O método, com as marcas e as contagens, é obra do primeiro, e precisa dele: sem a folha de marcas, a impressão do momento governaria tudo. A sua vida pede o segundo, para ler o que as marcas dizem dela.", PI)

sec("Das quatro quedas")
add("A linha da queda pede onde foi e o que você vai fazer diferente. A segunda resposta depende de um diagnóstico, porque a mesma cruz tem quatro causas, e cada uma pede outro remédio. Examine-as nesta ordem: quem não viu a ocasião não pôs o gesto à prova, e quem não tinha o gesto à mão não chegou a perguntar para quê.", PI)
add("<i>A falha de ocasião.</i> A ocasião veio e você não a reconheceu. O sinal está na lembrança: você só soube da queda depois, e não se lembra de ter escolhido ceder. Foi o que aconteceu à mulher de <i>Do primeiro dia</i> na terça da semana de prazos.", PI)
add("<i>A falha de gesto.</i> Você viu a ocasião, soube que era ela, e não fez. O sinal é a hesitação: um instante parado diante dela, sem saber por onde começar, e depois outra coisa. O gesto, como você o tinha na cabeça, era grande ou vago: <i>organizar tudo</i>, no lugar de tirar da mesa o que distrai.", PI)
add("<i>A falha de sentido.</i> Você viu a ocasião, sabia o que fazer, podia, e não quis: o gesto pareceu não servir para nada. O sinal é a indiferença: a queda vem sem luta, e a linha da manhã foi escrita de cor. O porquê se gastou pelo uso, como qualquer frase repetida.", PI)
add("<i>A falha de terreno.</i> Você tinha a ocasião, o gesto e o porquê, e o que estava em volta não deixou: a casa cheia, a hora em que você já não tem cabeça, a pessoa que entra e pede. O sinal é que a linha da queda nomeia uma coisa fora de você, e a mesma coisa volta nas quedas seguintes. O terreno é a desculpa mais à mão: só conta o obstáculo que um estranho veria se estivesse na sala.", PI)
proc("O remédio de cada queda", [
 "Se foi de ocasião, escreva na linha da queda o que vem logo antes dela.",
 "Na manhã seguinte, preveja a ocasião por esse aviso: o lugar, a hora, o que vem antes.",
 "Se foi de gesto, reduza a frase da manhã ao que as mãos fazem nos primeiros segundos.",
 "Na ocasião, faça a versão de dois minutos da sexta linha.",
 "· O gesto do exercício só muda numa passagem.",
 "Se foi de sentido, escreva na linha da queda para que servia o gesto ontem.",
 "Na manhã seguinte, escreva a obra de hoje devagar, conferindo que ela desce da obra em curso.",
 "Se o terreno é passageiro (febre ou doença, viagem, prova ou compromisso marcado por outro, alguém da casa), declare o piso de manhã.",
 "Se o terreno é constante, arrume-o na véspera: o que distrai fora do alcance, a porta fechada.",
 "Se a falha de gesto se repete com o gesto já reduzido, leve a forma da microação a uma passagem.",
 "Se a falha de sentido volta sete noites seguidas e chega à obra inteira, faça a prova do fim.",
 "Se a vida já não comporta a hora da ocasião, mude-a numa passagem, por escrito.",
])
proc("Ler as quedas juntas", [
 "Numa noite de passagem, ou quando a da vez demorar a chegar, releia juntas as linhas da queda.",
 "Se quatro cruzes são de ocasião, melhore a previsão. Não endureça a lei.",
 "Se quatro são de terreno, arrume a casa.",
 "Se quatro são de gesto ou de sentido, com os remédios já tentados, faça as quatro provas.",
])
add("No fim de agosto de 1854, o cólera matou mais de quinhentas pessoas em dez dias, em poucas ruas do Soho, em Londres. O médico John Snow marcou cada morto no mapa do bairro. As mortes se juntavam em volta de uma bomba pública da Broad Street, e as exceções fecharam o diagnóstico. O asilo de pobres ao lado, com poço próprio, teve poucas mortes; os homens da cervejaria, que bebiam a cerveja da casa, nenhuma. Uma viúva de Hampstead, que mandava buscar a água daquela bomba porque preferia o gosto, morreu.", PI)
add("A paróquia retirou o braço da bomba, e Snow admite que a epidemia já declinava. A causa estava no desenho das mortes lidas juntas, como a das suas quedas está nas linhas de várias semanas.", PI)

sec("Da resistência que fala")
add("Numa manhã, na hora da ocasião, ou numa noite ao fazer a marca, vem uma voz. Você conhece as do Livro I, que pediam cinco minutos ou um depois. Esta traz argumentos, e alguns são bons:", PI)
for v in ["O cansaço é de verdade, e também conta.",
          "Isso deixou de fazer sentido para você; já percebeu que faz isso sem saber para quê?",
          "Há semanas que você tenta, e nada. Talvez o problema seja o gesto, e não você.",
          "O método foi feito para uma vida mais simples do que a sua.",
          "Hoje você tem razões verdadeiras; amanhã faz o dobro."]:
    add(v, VOICE)
sp(6)
add("Algumas dessas frases mentem, outras dizem a verdade, e todas chegam com uma voz parecida com a sua. A última mente sempre: pelo §4, nada se compensa. As outras se julgam pelo que acontece quando você as põe à prova.", PI)
add("Há duas resistências, e por fora elas se parecem. A primeira se atravessa: preguiça, tédio, medo do trecho difícil, vontade de fazer algo mais fácil. Ela diz só que a obra custa. A segunda informa: o esgotamento real, o alvo que perdeu o sentido, a circunstância que mudou, a dor que pede outra coisa. O homem disperso trata toda resistência como informação, e nunca age. O homem rígido trata toda resistência como fraqueza, e um dia se quebra.", PI)
provas = [
 ("A prova do começo.", "Faça a versão de dois minutos, na ocasião. Se a resistência se dissolve, era da primeira espécie. Se cresce, ou se o peso continua igual depois de começar, há indício da segunda."),
 ("A prova do sono.", "Durma e olhe de novo pela manhã. A resistência da primeira espécie volta igual todos os dias e cede ao primeiro movimento. O esgotamento real diminui com o repouso."),
 ("A prova do fim.", "Pergunte: <i>se isto já estivesse terminado, eu ficaria contente?</i> Se a resposta é sim, a resistência é ao caminho, e o caminho se atravessa. Se é não, há indício de que o destino precisa ser revisto."),
 ("A prova da duração.", "Uma resistência que acompanha a mesma obra sete noites seguidas ou mais, sem ceder ao começo nem ao repouso, pede que se reveja o domínio. Apertar a lei não a resolve. Se o <i>chegou</i> não vem, declare a passagem por decisão."),
]
for i,(a_,b_) in enumerate(provas,1):
    add(f"{rom(i)}. &nbsp;<b>{a_}</b> {b_}", LAW)
proc("A noite das provas", [
 "Escolha uma resistência só: a que mais pesa agora.",
 "Depois dos minutos de sempre, abra o caderno numa página nova.",
 "No alto, escreva a resistência numa linha: a que se agarra, a que horas vem, o que diz.",
 "Embaixo, abra quatro linhas, uma para cada prova.",
 "Na linha do fim, responda à pergunta da prova do fim.",
 "Se a resposta for alívio ou indiferença, escreva-a assim.",
 "Na linha da duração, conte na folha de marcas há quantas noites a resistência vem.",
 "Conte quantas cruzes houve desde então, e se ela cedeu alguma vez ao começo ou ao descanso.",
 "Deite-se na hora, com o sono do §8 defendido.",
])
proc("O dia seguinte", [
 "De manhã, antes de abrir qualquer outra coisa, olhe de novo a resistência.",
 "Na linha do sono, escreva se ela pesa o mesmo, mais ou menos.",
 "Na ocasião, faça a versão de dois minutos, a sexta linha, e nada mais.",
 "À noite, escreva na linha do começo o que aconteceu depois dela.",
 "Leia as quatro linhas juntas.",
 "Escreva embaixo uma conclusão, numa frase.",
 "Se o começo dissolveu a resistência, cumpra a lei como sempre.",
 "Se o sono a aliviou, respeite a hora de parar.",
 "Se há um fato de piso (febre ou doença, viagem, prova ou compromisso marcado por outro, alguém da casa), declare o piso de manhã.",
 "Se a prova do sono falhou três manhãs seguidas, com a hora de parar cumprida, declare na véspera um dia de ócio.",
 "Se o fim respondeu não, ou a duração mostra sete noites seguidas sem ceder, leve-a a uma passagem, por escrito.",
])
add("Antes das provas, três sinais ajudam a desconfiar, sem decidir nada sozinhos. A resistência que se atravessa troca de razão a cada dia e conserva a conclusão, que é adiar; a que informa repete a mesma razão e pede uma mudança: outra hora, outra forma, outro fim. A primeira só fala diante da ocasião; a segunda fala também longe dela, num domingo, quando nada lhe é pedido. A primeira oferece alívio e não cobra nada. A segunda traz um custo, porque ouvi-la obriga a admitir uma escolha errada, e por isso é a que você menos quer ouvir.", PI)
add("Um homem treina às seis da manhã. Na segunda, a voz diz que choveu; na terça, que dormiu mal; na quarta, que há reunião cedo. A conclusão é sempre <i>amanhã</i>, e às sete ela se cala. Essa se atravessa. Uma mulher estuda piano depois do jantar, e toda noite a voz diz o mesmo: o filho do vizinho dorme do outro lado da parede. A frase volta no almoço, quando ninguém lhe pede piano, e propõe trocar a hora que ela mais gostava de ter. Essa informa, e vai às provas.", PI)
add("Há um caso que as quatro provas não tocam sozinhas: a resistência que se agarra a quase tudo o que a visão pede, além de uma obra.", PI)
proc("Se a resistência é à visão", [
 "Leia o segundo ponto da folha do dia zero, a visão.",
 "Pergunte: <i>já vivendo esta vida, eu ficaria contente?</i>",
 "Se a resposta honesta for alívio, a resistência informa sobre <i>ele</i>.",
 "Corrija a visão numa passagem, por escrito, com as marcas à frente.",
 "A partir dessa noite, faça a pergunta ao rosto novo. Até lá, ao antigo.",
 "· O eu antigo escolheu o rosto num só dia. Esta é a única emenda da máscara.",
])
add("Um homem fez este caminho antes de você. No quarto mês, sentia todas as manhãs um peso enorme antes de começar um relatório difícil. Fez os dois minutos, uma frase ruim, e dez minutos depois tinha esquecido o peso. Era a primeira espécie, e a lei se cumpriu sem drama.", PI)
add("No mês seguinte, o pai dele adoeceu, e ele passou três semanas dormindo em cadeiras de hospital. A da vez começou a cair, e ele se acusava de preguiça. Numa noite em que um irmão o substituiu, dormiu oito horas seguidas, e no dia seguinte fez a microação sem esforço. A resistência tinha cedido ao repouso. A resposta, para ele, era o piso, porque alguém da casa precisava dele, e o sono do §8 defendido como fosse possível.", PI)
add("Mais tarde, fez a prova do fim sobre um curso que escolhera aos vinte anos para agradar a outra pessoa. <i>Se já estivesse terminado, eu ficaria contente?</i> Ficaria aliviado, o que é outra coisa. Diante de um livro que lhe custava cada página, a mesma pergunta dava uma alegria clara: o livro era caminho a atravessar. O curso era destino a rever, e ele o reviu numa passagem, por escrito, com as marcas à frente.", PI)
add("Depois disso, durante muitas noites, a da vez caía noite sim, noite não. Nenhum <i>chegou</i>, os pisos cumpridos a custo, e nem o começo nem o descanso mudavam nada. A tentação dele foi acrescentar uma lei: levantar-se mais cedo. A quarta prova mandava parar de apertar e rever o domínio numa passagem. Mas a passagem só vinha com um <i>chegou</i>, e o <i>chegou</i> não vinha. Para isto existe a passagem por decisão.", PI)
add("<b>A passagem por decisão.</b> É a única passagem sem <i>chegou</i>, para o gesto que não chega, noite após noite, sem que a resistência ceda.", PI)
proc("Passagem por decisão", [
 "Faça antes, por escrito, as quatro provas.",
 "Declare-a só se a conclusão escrita diz que a resistência informa.",
 "Declare-a numa noite sem cruz.",
 "· Nunca em noite de cruz. Nunca no dia em que a microação entrou.",
 "Depois da marca, escreva <i>passagem por decisão</i>, a data e a razão numa linha.",
 "Tire a razão da conclusão das provas.",
 "Leia a Lição do exercício da vez.",
 "Releia a folha do dia zero, com a frase da anti-visão, e <i>Do homem</i>.",
 "Faça por escrito as emendas que as marcas pedirem.",
 "Reveja o domínio, por escrito, diante das marcas.",
 "Se o domínio é seu e falha a forma, redefina por escrito a ocasião ou o gesto.",
 "Escreva a nova forma no caderno. A microação continua sendo a da vez.",
 "De manhã, leia a nova forma no lugar da linha do breviário.",
 "Se o domínio mudou, volte na manhã seguinte à estação zero e refaça o exercício zero.",
 "· Ela não serve para pular exercício: a da vez só fica com <i>chegou</i>, numa noite de traço.",
])
add("O homem do relatório a declarou numa noite sem cruz. A da vez era a primeira hora do dia longe das distrações, e as manhãs dele pertenciam ao hospital. As provas disseram que o domínio continuava sendo o dele; o que a vida já não comportava era a ocasião. Ele escreveu a linha, leu a Lição, releu a folha do dia zero e mudou a ocasião para a primeira hora depois de voltar para casa, com o mesmo gesto. Semanas depois, numa noite de traço, escreveu <i>chegou</i>.", PI)
add("A mulher de <i>Do primeiro dia</i> declarou a dela no corpo, depois de ler este livro antes do tempo, pela ordem. A ficha marcava treino às seis e meia, nas segundas, quartas e sextas, e em onze semanas o <i>chegou</i> não veio: as cruzes caíam nas segundas e nas quartas, os dias da reunião das oito, e nas sextas ela ainda precisava do breviário para sair com a ficha na mão. A voz repetia a mesma razão, que aquelas duas manhãs não cabiam, e a repetia também no almoço de domingo, longe de qualquer treino. Numa terça, noite de ponto, ela abriu uma página nova e escreveu a resistência no alto. Na prova do fim, perguntou se ficaria contente com o corpo já treinado e escreveu <i>sim</i>. Na da duração, contou na folha: onze semanas, nove cruzes, todas em segunda ou quarta, e a resistência nunca tinha cedido ao começo nem ao descanso.", PI)
add("Deitou-se na hora. De manhã, antes de abrir qualquer outra coisa, escreveu na linha do sono <i>o mesmo peso</i>. Às seis e vinte fez a versão de dois minutos, o tênis e a garrafa, e o peso continuou igual. Foi ao treino assim mesmo, cumpriu a ficha olhando o relógio a cada série e entrou na reunião dez minutos atrasada. À noite, traço. Leu as quatro linhas juntas e escreveu embaixo: <i>informa; o domínio é meu, e a hora não cabe nas manhãs de reunião</i>. Depois da marca, escreveu <i>passagem por decisão</i>, a data e essa razão. Leu a Lição do corpo, releu a folha do dia zero, com a frase da anti-visão, e <i>Do homem</i>, e reviu o domínio diante das marcas: continuava sendo o direito. Redefiniu a ocasião, terças, quintas e sextas às seis e meia, com o mesmo gesto, e a escreveu no caderno, onde passou a lê-la de manhã no lugar da linha do breviário. O corpo continuou sendo a da vez. Cinco semanas depois, numa quinta de traço, ela saiu de casa com a ficha na mão sem ter pensado nela, e escreveu <i>chegou</i>.", PI)
add("Se o peso está há semanas em tudo, além da obra, nenhuma passagem por decisão o resolve; os sinais e o caminho estão em <i>Do escrúpulo</i>.", NOTE)

sec("Da firmeza e da rigidez")
add("Você se pega defendendo uma lei contra a razão para a qual ela existe. Cumpre a hora da microação com um filho doente no colo, porque a lei é a lei. Recusa o piso num dia de febre, porque o piso lhe parece fraqueza. Por fora parece firmeza.", PI)
add("<b>Firme</b> é quem mantém a linha no que importa. <b>Rígido</b> é quem mantém a forma depois que a realidade mudou, e já não pergunta para que a regra existia. Com a máscara é o mesmo: mantê-la no que serve à obra é firmeza; mantê-la quando já não serve ao rosto que você tem é rigidez.", PI)
proc("Quando uma lei pesar", [
 "Pergunte: <i>para que existe esta regra, e o que ela protege hoje?</i>",
 "Se a resposta é a obra, o gesto ou a segunda queda que ela impede, cumpra-a.",
 "Se a resposta é só a própria regra, leve a correção a uma passagem, por escrito.",
 "· A correção deixa uma linha datada, com as marcas à frente. A fuga não deixa nada.",
])
add("Sêneca, em <i>Dos benefícios</i>, discute se quem prometeu fica obrigado em qualquer caso. O sábio, escreve, não muda de decisão enquanto permanecem as condições em que a tomou; se as condições mudaram, mudar de decisão é ser coerente com elas. A constância do sábio pertence ao juízo que decidiu. As leis deste livro valem enquanto servem.", PI)
add("A partir de 1600, Kepler passou anos tentando ajustar a órbita de Marte a círculos, a forma perfeita da astronomia desde os gregos. Chegou a uma hipótese que concordava com as observações de Tycho Brahe em quase tudo, e errava em alguns pontos por oito minutos de arco. Tycho observava com precisão maior que essa. Kepler escreveu na <i>Astronomia nova</i>, de 1609, que esses oito minutos, sozinhos, abriram o caminho para reformar a astronomia inteira. Largou o círculo e chegou à elipse, fiel às observações para as quais o círculo existia.", PI)
add("O Livro II mandou para cá o sinal de que a hora de parar já não basta: a noite deixou de desfazer o peso da véspera.", PI)
proc("Quando a hora de parar não basta", [
 "Se a prova do sono falhou três manhãs seguidas, com a hora de parar cumprida, declare na véspera um dia de ócio.",
 "Escreva a declaração à noite, no caderno.",
 "Se depois dele o peso volta igual, leia <i>Do escrúpulo</i>.",
])
add("Há uma rigidez mais fina: fazer do próprio livro a obra. Se ler, reler, anotar e aperfeiçoar o método toma mais do que os minutos da manhã e da noite, o método ocupou o lugar de um velho hábito, o de se preparar em vez de fazer. O sinal aparece na linha do dia: o dia teve ar de disciplina e nada existe agora que não existia de manhã. Nesse dia, feche o livro e volte à obra que tinha à frente.", PI)

sec("Do chegou e do engano")
add("Ao reler os seus <i>chegou</i>, você desconfia de um deles. A desconfiança é justa. A regra de <i>Da medida</i> continua a mesma: na dúvida, não chegou. Esta seção diz o que, numa noite de marca, conta como dúvida.", PI)
add("A testemunha é fraca. A lembrança de um dia se refaz cada vez que é chamada, e se refaz com os desejos de quem lembra: quem quer avançar lembra a sessão em que avançou. O gesto feito sem decisão deixa pouco rastro, e a falta de rastro se parece com o esquecimento. Na manhã seguinte, a lembrança já foi refeita a seu favor.", PI)
proc("Antes de escrever chegou", [
 "Escreva <i>chegou</i> só na mesma noite. Nunca sobre um dia que já passou.",
 "Se você não se lembra da sessão, deixe a coluna vazia.",
 "Prova da ocasião: confira nas linhas da queda se hoje houve as condições em que você caía.",
 "Se a ocasião que mais pesou hoje foi branda, há dúvida.",
 "Prova da repetição: confira se o gesto já veio sozinho antes, em ocasiões diferentes.",
 "Se ele precisou do caderno em todas as noites anteriores, há dúvida.",
 "Prova do breviário: lembre o que estava à vista e o que você leu antes da ocasião.",
 "Se o breviário estava aberto, ou a linha da manhã ainda soava, há dúvida.",
 "Se uma prova falhar, não escreva <i>chegou</i>.",
 "· No <i>chegou</i>, quem lembra é a ocasião, e só ela.",
])
add("Os estudos mostram, como resumiram Wendy Wood e David Neal em 2007, que o hábito é uma resposta disparada pela pista do contexto, aprendida pela repetição e relativamente independente do objetivo do momento. O <i>chegou</i> registra o primeiro sinal disso: o gesto disparado pela mesa vista ao sentar, sem o objetivo lembrado. A força do hábito cresce aos poucos, ao longo de semanas e meses. O <i>chegou</i> marca um ponto dessa subida, e a consolidação continua entre as que ficaram.", PI)
proc("Se um gesto que chegou se perde", [
 "Ponha a queda na última coluna, com a linha da queda.",
 "Se ele cair duas noites seguidas, ele volta a ser a da vez.",
 "Releia as linhas da queda e procure o que mudou na ocasião.",
 "Se caiu nas primeiras semanas, sem mudança, o <i>chegou</i> foi cedo: aperte as três provas.",
 "Se caiu depois de meses, procure a pista que sumiu: casa, horário, mesa, viagem.",
 "Se a ocasião escrita deixou de existir, emende-a na passagem, por escrito.",
 "Não risque o <i>chegou</i> antigo.",
])
add("Sem a pista, o gesto volta a ser lembrado pelo caderno até se prender à pista nova, e o autor acha que chega mais depressa da segunda vez. O <i>chegou</i> antigo fica na folha daquela noite, como cada cruz fica na dela, e mostra a quem relê onde você se enganou.", PI)

sec("Do escrúpulo")
add("Há uma terceira maneira de o método se virar contra quem o usa, e ela se reconhece à noite. Você faz a marca e não consegue decidi-la. <i>Foi traço mesmo? A ocasião que mais pesou foi esta, ou a outra, em que cedi? E o piso de terça, não terá sido preguiça disfarçada de piso?</i> Você escreve cruz, por via das dúvidas. Na noite seguinte, a mesma pergunta, e outra cruz. O exame passa a durar vinte minutos e acaba numa acusação.", PI)
add("Inácio de Loyola viveu isto em Manresa, em 1522, depois de fazer em Montserrat a confissão geral de toda a vida. Parecia-lhe sempre que não tinha confessado tudo, ou que confessara mal. Voltava ao confessor, anotava os pecados para não esquecer nenhum, e não tinha paz. Conta na <i>Autobiografia</i> que lhe veio a tentação de se atirar por uma abertura do quarto onde rezava. Passou uma semana sem comer nem beber, até que o confessor lhe mandou parar.", PI)
add("Libertou-o uma decisão, tomada com grande clareza: não voltar a confessar nada do passado. Anos depois, nos <i>Exercícios espirituais</i>, ele deixou notas para quem sofre de escrúpulos. O inimigo, escreve, trata uma consciência delicada tentando torná-la mais delicada, até a angústia. A alma deve fazer o contrário da tendência que nota em si e se firmar no meio, para ficar em paz. É a vara torta de Aristóteles aplicada à consciência.", PI)
add("A regra <i>na dúvida, cruz</i> continua de pé para o caso duvidoso de uma noite. O escrúpulo faz da dúvida o estado de todas as noites e enche a folha de cruzes sem queda.", PI)
proc("Contra o escrúpulo", [
 "Decida, de uma vez, por escrito, não reabrir as marcas já postas.",
 "Não corrija folhas antigas.",
 "Se a dúvida vier sobre o passado, diga a nona linha, como diante de uma onda.",
 "Dê ao exame da marca cinco minutos.",
 "No fim dos cinco minutos, feche o caderno, decidido ou não.",
 "Se não decidiu, marque pela regra e não rumine.",
 "Se você pôs traço onde houve cruz, escreva na linha desta noite que mentiu.",
 "Não corrija a marca antiga.",
])
proc("Quando suspender", [
 "Se o exame passa de cinco minutos sete noites seguidas, suspenda.",
 "Se a simples visão do caderno traz angústia, suspenda.",
 "Se você pôs traço onde houve cruz pela segunda vez, suspenda.",
 "Para suspender, escreva no caderno a data e a palavra <i>suspenso</i>.",
 "Feche o caderno.",
 "Fale com alguém com formação para ouvir você antes de reabri-lo.",
])
add("John Stuart Mill quebrou de outra maneira, e contou isso na <i>Autobiografia</i>. O pai o educou com grego aos três anos e lógica aos doze, e fez dele, aos vinte, um prodígio de análise com um fim claro: reformar o mundo. No outono de 1826, abatido, ele se perguntou: <i>se todos os seus objetivos se realizassem neste instante, isso seria uma grande alegria para você?</i> Uma consciência que ele não conseguia calar respondeu: <i>não</i> (paráfrase, cap. V). Tudo aquilo sobre o que tinha construído a vida desabou.", PI)
add("Mill fez a si mesmo a prova do fim e recebeu o não. O destino estava certo: ele trabalhou a vida inteira pelas mesmas reformas. Alguma coisa nele, por baixo de todos os destinos, tinha se apagado. Passou meses cumprindo o trabalho mecanicamente, sem falar com ninguém. As provas deste livro supõem um juízo que funciona. Quando o que adoece é o próprio juízo, elas respondem errado, e com toda a convicção.", PI)
add("Mill atribuiu a crise, em parte, ao hábito da análise sem descanso, que gasta os sentimentos. Saiu devagar. Em 1828, leu Wordsworth e encontrou o que chamou de cultura dos sentimentos: alegrias que não dependem de luta para existir. Tirou daí uma regra: pergunte a si mesmo se é feliz, e você deixa de ser. Só são felizes os que têm o espírito posto em outra coisa, uma obra, uma pessoa, uma arte praticada por si mesma.", PI)
add("O exame da noite tem cinco minutos, e a folha de marcas serve para registrar. Se o método treina você a se vigiar até você não sentir nada do que faz, falta a ele o que Wordsworth foi para Mill: aquilo que você faz sem contar, com a atenção posta na coisa. A hora de parar e o dia de ócio existem também para isso.", PI)
add("William James, aos vinte e oito anos, estava pior: formado em medicina sem vontade de exercê-la, o corpo doente, uma melancolia de anos. Em 30 de abril de 1870, escreveu no diário que o dia anterior tinha sido uma crise na sua vida. Lera Charles Renouvier, que definia o livre-arbítrio como sustentar um pensamento porque o escolho, quando poderia ter outros. <i>O meu primeiro ato de livre-arbítrio será acreditar no livre-arbítrio</i>, escreveu.", PI)
add("O que ele decidiu foi modesto e provisório. Até o ano seguinte, assumiria que o livre-arbítrio não era ilusão, se absteria da ruminação em que a sua natureza mais se comprazia, leria livros que o favorecessem, e agiria. Um prazo, uma linha, uma paixão contrária para as horas da ruminação. A melancolia voltou a ele ao longo da vida, mas ele ganhou um ponto onde apoiar o pé. James saiu agindo; Mill saiu deixando de se examinar. Saber qual das duas saídas cabe a você nem sempre se consegue sozinho.", PI)
add("Há sinais que não se tratam com traços nem com linhas, e que pedem um médico ou alguém com formação para ouvir você. Aqui, <i>há semanas</i> e <i>noite após noite</i> querem dizer sete noites seguidas ou mais. Saiba-os sem abrir o livro:", PI)
sinais = [
 ("Se há semanas nada lhe dá prazer,", "nem o que antes dava, e não só a obra."),
 ("Se o sono não descansa você,", "ou você não dorme, noite após noite."),
 ("Se lhe vêm pensamentos de morte,", "a ideia de que seria melhor não estar aqui, mesmo que passem depressa."),
 ("Se um hábito que você cortou volta sempre,", "apesar das pontes queimadas, da paixão contrária e da contagem, e já está lhe custando a saúde, o dinheiro ou as pessoas."),
 ("Se o método, em vez de pôr você em ordem, atormenta você,", "e o exame da noite se tornou a pior hora do dia."),
]
for i,(a_,b_) in enumerate(sinais,1):
    add(f"{rom(i)}. &nbsp;<b>{a_}</b> {b_}", LAW)
add("Nada disso mede a sua disciplina. Mede um estado que tem tratamento, e esse tratamento não está neste livro. Não é preciso esperar que fique grave. Mill passou meses sozinho porque não via com quem falar; você não precisa repetir esse erro. <b>Se o pensamento de morte aparecer, não espere pela próxima passagem nem pela manhã seguinte: fale hoje com alguém, e procure ajuda hoje.</b> Nada no caderno se perde com isso. A contagem espera, os exercícios esperam, e o que importa acima de qualquer linha é que você esteja aqui para retomá-la.", PI)

sec("Do que este método não resolve")
add("Este método treina gestos, e há males que nenhum gesto alcança. Nos casos abaixo ele não resolve nada, e insistir nele gasta um tempo que o caso não tem. O remédio de cada um está fora deste livro:", PI)
naoresolve = [
 ("Doença mental.", "Depressão, transtorno bipolar, transtorno de ansiedade ou outro estado que um médico nomeie se tratam com ele e com quem ele indicar; durante o tratamento, o método só continua se esse profissional não vir nele um peso. No Brasil, o CVV atende pelo 188 a qualquer hora."),
 ("Dívida e falta de dinheiro.", "Ponha numa folha cada dívida, com o credor, o valor e os juros, e leve essa folha a quem possa renegociá-la ou orientar você; a disciplina ajuda a cumprir o acordo, mas não paga a conta."),
 ("Relação em que alguém fere você.", "Se alguém fere você, com as mãos ou com a palavra, saia do alcance dessa pessoa e conte o que acontece a alguém de fora da relação; havendo perigo, ligue 190."),
 ("Luto recente.", "Nos primeiros meses depois de uma morte, deixe o método em suspenso, com o piso no máximo, porque o luto tem um tempo que não se treina; se, passado esse tempo, ele ainda impedir a vida, procure um médico."),
 ("Trauma.", "O que feriu você a fundo se trabalha com um terapeuta formado para isso, e nem o exame da noite nem a escrita sobre o que perturba devem reabrir essa ferida sozinhos, como o <i>Manual operacional</i> já avisa."),
 ("Dependência química.", "A dependência de álcool, de remédio ou de droga se trata com médico e com serviço especializado, que no SUS é o CAPS AD; o corte do Livro IV foi feito para hábitos, e parar de uma vez certas substâncias, o álcool entre elas, pode ser perigoso sem acompanhamento."),
]
for i,(a_,b_) in enumerate(naoresolve,1):
    add(f"{rom(i)}. &nbsp;<i>{a_}</i> {b_}", LAW)

sec("Dos dois lados")
add("<i>Do escrúpulo</i> guarda um lado do caminho: o método que passa a vigiar quem o usa. O outro lado se perde de dois modos. A obra toma o que o método protege, o sono, as noites, as pessoas; ou o método vira o lugar onde a obra se esconde, com noites de traço e nenhuma obra. Cada sinal tem a sua resposta.", PI)
for a_, b_ in [
 ("A obra sobe e o sono cai.", "A obra tomou o corpo. Uma semana com a obra no piso, e o §8 relido na primeira noite."),
 ("A obra sobe e as pessoas se ferem.", "A obra tomou a casa. Encerre o bloco, se houver um, por escrito, e conserte primeiro o que a pressa estragou."),
 ("A hora de parar passa sete noites seguidas.", "A obra tomou a noite. Marque-a amanhã meia hora mais cedo, e cumpra."),
 ("Meses de marcas e nenhuma obra.", "O método tomou o lugar da obra: as noites de traço se acumulam e a linha do dia repete o mesmo nada. Declare um bloco de obra na próxima passagem."),
 ("A marca virou nota.", "A medida tomou a pessoa: você relê a folha para se julgar, ou anota horas fora do bloco. Volte a <i>Do teto</i>, em <i>Da medida</i>, e a <i>Do escrúpulo</i>."),
 ("Um peso que o descanso não tira.", "Um dos lados está errado, e ainda não se sabe qual. Faça as quatro provas, a do sono primeiro."),
]:
    add(f"<i>{a_}</i> {b_}", LAW)

sec("Da prova")
add("Esta seção é para a noite em que a décima terceira microação chegar, ou uma das seguintes, antes do novo dia zero. Leia-a agora uma vez e volte a ela nessa noite.", PI)
add("Nessa noite você terá à frente as folhas de marcas do ciclo, as linhas da queda e a folha do dia zero. Vista de dentro, a mudança quase não se nota. Ela está em abrir a obra sem vontade, ficar numa coisa só até ela acabar, voltar depois da dispersão, ouvir uma crítica sem inventar defesa. Vem sobretudo das semanas em que as frases já não davam entusiasmo e a rotina tinha voltado a ser banal.", PI)
proc("Antes do novo dia zero", [
 "Abra as folhas de marcas, as linhas da queda e a folha do dia zero.",
 "Na página seguinte, responda por escrito às cinco perguntas, uma de cada vez.",
 "Responda com o que você faz.",
 "Se uma resposta sair como um estado, como <i>estou mais calmo</i>, procure nas folhas o ato.",
 "Risque o estado e escreva o ato.",
 "Se as respostas forem pobres, corrija o método por escrito.",
 "Leve a correção ao novo dia zero.",
])
add("A mulher de <i>Do primeiro dia</i> respondeu à prova numa sexta, com as folhas de onze meses abertas na mesa da sala. Na primeira pergunta, a mão escreveu <i>estou mais calma no escritório</i>. Era um estado, e ela foi às folhas atrás do ato: a manhã em que mandou à colega duas linhas com o número certo, a reunião em que pediu ao chefe o argumento dele. Riscou a frase e escreveu os atos, e depois os outros: as duas mesas em ordem sem pensar, a ficha cumprida nas terças, quintas e sextas, a sessão começada sem esperar vontade. Para as tardes numa coisa só, as linhas do dia deram três sábados, o dos prazos, o dos recursos, o do quadro das nulidades; em todos, o telefone fora da mesa, a primeira linha escrita e a hora de parar marcada de manhã. Na segunda pergunta abriu <i>Dias limpos</i>: os vídeos, com uma casa vazia numa quinta de ônibus, e nenhuma outra. Na terceira escreveu o corpo, a ocasião que ela mesma tinha posto em manhãs de reunião, e as onze semanas até a passagem por decisão.", PI)
add("A quarta levou mais tempo. A resistência ouvida tinha sido a do corpo, e as marcas diziam que ela fizera bem. Mas a folha guardava outra. No fechamento do balanço, em fevereiro, ela declarou piso três manhãs seguidas. Na terça e na quarta tinha saído do escritório depois das dez da noite. Na quinta saíra às seis, como em qualquer dia, e a linha do dia dizia <i>nada</i>. Ela escreveu: <i>Ouvi o cansaço de fevereiro. Na terça e na quarta, o piso serviu à circunstância. Na quinta, serviu à falta de vontade, e eu sabia disso de manhã, quando o declarei.</i> Não escreveu o que aquilo dizia dela. Na última pergunta pôs a correção que levaria ao novo dia zero: a ficha nasce nos dias que a agenda do escritório comporta, conferida contra a agenda antes de ser escrita.", PI)

# página da prova
st.append(PageBreak()); sp(20)
add("A prova do ciclo", ParagraphStyle('pv', parent=LT, fontSize=20, spaceAfter=6)); sumario(st[-1], 1, "A prova do ciclo")
add("Ciclo nº ____ &nbsp;&nbsp; de ___/___/_____ &nbsp; a ___/___/_____", ParagraphStyle('pv2', parent=PC, spaceAfter=18))
LN = ParagraphStyle('ln', **{**base, 'textColor': colors.HexColor('#b0b0b0')}, fontSize=11, leading=22)
perg = ["O que faço hoje sem negociar que, no começo do ciclo, não fazia, e em que tardes fiquei numa coisa só até ela acabar, e o que havia nelas?",
        "O que abandonei de vez?",
        "Onde o método falhou, e por quê?",
        "Que resistência ouvi em vez de atravessá-la, e fiz bem em ouvi-la?",
        "O que muda no próximo ciclo?"]
for q in perg:
    st.append(KeepTogether([Paragraph(f"<i>{q}</i>", ParagraphStyle('pq', parent=P, spaceBefore=6, spaceAfter=2)),
                            Paragraph("_"*78 + "<br/>" + "_"*78 + "<br/>" + "_"*78, LN)]))
proc("Antes de seguir", [
 "Se você ainda não escreveu a resistência que mais lhe pesa, escreva-a hoje numa linha.",
 "Faça hoje a prova do fim e a da duração.",
 "Amanhã de manhã, faça a do sono.",
 "Escreva a conclusão.",
 "Se um dos sinais de <i>Do escrúpulo</i> é seu, procure ajuda. O caderno espera.",
 "Se for o pensamento de morte, procure ajuda hoje.",
 "No fim do ciclo, se uma resposta da prova diz o que você sente, reescreva-a com o que você faz.",
]); fleur()
# O ornamento vai junto do último parágrafo, para não ficar sozinho numa página.
st[-2:] = [KeepTogether(st[-2:])]
# ===================== INTERLÚDIO: DO HÁBITO E DE QUEM SE É =====================
estribilho_pagina()
st.append(PageBreak()); sp(8)
add("I N T E R L Ú D I O", LIV)
add("Do hábito e de quem se é", LT); sumario(st[-1], 0, "Interlúdio · Do hábito e de quem se é")
SEC_NO_SUMARIO = True
add("<i>“As virtudes não nascem em nós nem por natureza nem contra a natureza: somos feitos para recebê-las, e nos completamos nelas pelo costume.”</i>", ParagraphStyle('it1', parent=PC, fontSize=12, spaceAfter=2))
add("Aristóteles, <i>Ética a Nicômaco</i>, II, 1 (paráfrase)", ParagraphStyle('it2', parent=EPA, spaceAfter=18))
add("Leia este capítulo devagar, no fim do ciclo, na noite em que respondeu à prova ou numa das seguintes. Você sai daqui com o capítulo do ciclo escrito e uma só promessa para o ciclo seguinte, dita em atos.", PI)
proc("Antes de ler", [
 "Se ainda não respondeu às cinco perguntas da prova do ciclo, responda-as antes de seguir.",
 "Ponha sobre a mesa as folhas de marcas do ciclo.",
 "Abra o caderno na primeira página, na folha do dia zero.",
 "Leia a folha do dia zero ao lado das folhas de marcas.",
 "· Ver: <i>Da prova</i>.",
])
add("Nas folhas estão meses de linhas, uma por dia. Na coluna do número, o um das primeiras noites, depois o dois, o três, até o treze; se uma das que ficaram caiu duas noites seguidas e voltou a ser a da vez, o mesmo número aparece lá duas vezes. Na coluna estreita, os <i>chegou</i>. Embaixo de cada cruz, a linha da queda, na letra que você tinha naquela noite. Na primeira página, a anti-visão e a visão, escritas num dia sem trabalho, há meses. O livro não sabe o que está escrito ali. Você sabe.", PI)
add("A prova perguntou o que você faz hoje sem negociar. Com as folhas à frente, vem outra pergunta, em voz mais baixa: <i>quem fez tudo isto?</i> Quem respondeu à prova é quem escreveu a anti-visão? Se é o mesmo, mudou só a superfície? Se é outro, para quem você trabalhou?", PI)
add("Este capítulo não traz linha nem lei novas. Traz as respostas que outros deram a essa pergunta, de Aristóteles a MacIntyre, e um único exercício no fim.", PI)
add("<b>Hábito</b> é o que você faz por repetição, até fazê-lo sem decidir de novo; o <i>chegou</i> começa a registrá-lo. <b>Caráter</b> é a maneira de ser pela qual quem conhece você sabe o que você vai fazer diante do medo, do prazer, da pressa, do outro. A pergunta desta noite é se o caráter é só a soma dos hábitos. E, se há nele mais alguma coisa, onde ela estava nas noites de cruz.", PI)

sec("Da objeção que ficou")
add("No dia zero, o Prólogo ouviu o protesto <i>sou mais do que os meus atos</i> e deu a ele só metade da resposta: o dia zero lê provas e não pronuncia sentença sobre o fundo. A outra metade ficou para depois do primeiro ciclo, porque naquele dia a objeção também servia de abrigo.", PI)
add("Esta noite ela volta com outro rosto: <i>se sou apenas o que faço, fui neste ciclo uma fila de traços e cruzes, e amanhã, se parar, volto a ser a semana da anti-visão; se sou mais do que faço, que coisa é essa, e onde estava enquanto eu caía?</i> A inquietação é legítima. A filosofia trata dela há vinte e quatro séculos, com respostas que se corrigem umas às outras.", PI)

sec("Do costume e do caráter")
add("Atenas, por volta de 335 antes de Cristo. Aristóteles ensina no Liceu, um ginásio fora das muralhas, junto de um bosque consagrado a Apolo. A tradição diz que ele dava as lições caminhando, e daí veio o nome dos discípulos: peripatéticos, os que andam em volta. A <i>Ética a Nicômaco</i> guarda essas lições, e a pergunta que a atravessa é a sua: como alguém se torna bom, se não nasceu assim?", PI)
add("A primeira resposta está numa palavra. Em grego, <i>éthos</i>, com a vogal breve, é o hábito. <i>Ēthos</i>, com a vogal longa, é o caráter, e nos poemas antigos era o lugar habitual a que um animal volta, a morada dele. A língua guardou o que a experiência ensinava: o caráter é o costume que se assentou.", PI)
add("A pedra, que por natureza cai, não se habitua a subir, ainda que alguém a atire para cima dez mil vezes. As virtudes não nos são dadas nem vedadas: nascemos aptos a recebê-las e nos completamos nelas pelo costume.", PI)
add("Aristóteles chama de <i>héxis</i> o que esse costume deixa em quem o pratica: uma disposição adquirida e firme, um ter. Ela faz alguém portar-se bem ou mal diante do medo ou do prazer sem deliberar do zero. O corajoso que dorme continua corajoso; quem fugiu uma vez não se tornou covarde por isso. Nisso a objeção tem razão: você é mais do que os seus atos de hoje.", PI)
add("Mas a disposição só se forma por atos, e só por atos se desfaz. Tornamo-nos justos praticando atos justos. Olhe a coluna estreita das suas folhas: cada <i>chegou</i> marca a noite em que um gesto começou a ser disposição.", PI)
add("Aristóteles pedia mais antes de chamar uma disposição de virtude. A virtude é disposição de escolha, <i>héxis proairetiké</i> (II, 6): quem age sabe o que faz e escolhe o ato pelo que ele é. Pelos critérios dele, o que o método treina, sobretudo no corte, está mais perto da <i>enkráteia</i>, a continência de quem ainda deseja e se domina (VII, 9). O livro toma de Aristóteles a formação pelos atos. A escolha do que merece ser escolhido fica com você.", PI)
add("A primeira resposta é dupla: a disposição não se reduz aos atos de um dia, e só se forma por atos repetidos, os que as suas folhas registram.", PI)

sec("Da mulher e do bezerro")
add("A segunda resposta vem de Montaigne, que desconfiava de quase tudo, e do costume mais do que de qualquer outra força. No ensaio <i>Do costume e de não mudar facilmente uma lei recebida</i>, ele conta uma fábula. Uma mulher de aldeia aprendeu a carregar nos braços um bezerro desde a hora em que ele nasceu. Fez isso todos os dias, sem interromper. Quando o bezerro já era um grande boi, ela ainda o carregava.", PI)
add("Não houve um dia em que ela se tornou forte. O bezerro crescia um pouco por noite, e os braços dela também. Se no último dia lhe tivessem posto o boi nos braços sem os anos de antes, ela teria caído com ele.", PI)
add("Montaigne conta a fábula a propósito da servidão. O costume, escreve, é uma mestra-escola violenta e traiçoeira: instala a autoridade dela aos poucos, com um começo brando e humilde, e depois mostra um rosto furioso e tirânico, contra o qual já não temos a liberdade de erguer os olhos. No mesmo ensaio, Platão repreende um menino que jogava com nozes. O menino responde que é por pouca coisa. <i>O costume</i>, diz Platão, <i>não é coisa pouca</i>.", PI)
add("Olhe a primeira página e a última folha de marcas: é a mesma lei pelos dois lados. A semana da anti-visão também era um bezerro carregado todos os dias; por isso pesava tão pouco e era tão difícil de largar. O ciclo trocou, devagar, o animal que você tem nos braços. A resposta de Montaigne é desconfortável: o que você é depende do costume mais do que você gostaria de admitir. Aqui o aviso dele serve para você escolher a que costumes se sujeita.", PI)

sec("Do feixe")
add("Um século e meio depois, David Hume, com pouco mais de vinte anos, escreveu o <i>Tratado da natureza humana</i> em La Flèche, no interior da França. Na seção sobre a identidade pessoal, fez uma experiência. Quando entro mais intimamente naquilo que chamo de <i>eu mesmo</i>, escreve, sempre tropeço numa percepção particular: de calor ou de frio, de luz ou de sombra, de amor ou de ódio, de dor ou de prazer. Nunca me flagro sem uma percepção. O eu, conclui, é um feixe de percepções que se sucedem com rapidez inconcebível, em fluxo perpétuo.", PI)
proc("A experiência de Hume", [
 "Esta noite, à mesa, com as folhas à frente, feche os olhos.",
 "Procure em você o que estava presente no primeiro dia e está presente agora, igual.",
 "Procure aquilo que possui o que você encontrou.",
 "· Você vai encontrar uma lembrança, uma frase, o peso do corpo na cadeira. E outra lembrança.",
])
add("Daí alguém tiraria que tudo foi em vão: se não há um eu por baixo do feixe, ninguém mudou, e ninguém precisa começar amanhã. Hume não tirou essa conclusão. Para comparar a alma, escolheu uma república: os membros mudam, as leis e a constituição mudam, e a república continua a mesma. A unidade da pessoa vem das relações: a causa que liga uma percepção à seguinte, a memória que as percorre.", PI)
add("Anos depois, na <i>Investigação sobre o entendimento humano</i>, Hume perguntou por que esperamos que o futuro se pareça com o passado. Respondeu que quem nos leva a isso é o costume, e escreveu:", PI)
st.append(KeepTogether([Paragraph("<i>“O costume é, pois, o grande guia da vida humana.”</i>", ParagraphStyle('it3', parent=PC, fontSize=12, spaceAfter=2)),
                        Paragraph("Hume, <i>Investigação sobre o entendimento humano</i>, V", ParagraphStyle('it4', parent=EPA, spaceAfter=14))]))
add("Se você é uma república governada pelo costume, mudar é mudar as leis dela. Você as mudou uma microação de cada vez, sem precisar convencer um eu escondido por trás delas. Hume fala de percepções; o livro estende a imagem aos costumes que governam os atos.", PI)
add("Hume confessou num apêndice ao <i>Tratado</i> que a própria explicação não o satisfazia e que se via num labirinto. Para praticar, você não precisa sair dele: em qualquer hipótese sobre o que você é, o costume governa, e obedece ao que se repete.", PI)

sec("Da vontade que desceu")
add("Em 1838, em Paris, Félix Ravaisson, com vinte e cinco anos, defendeu uma tese breve chamada <i>Do hábito</i>. Hume deixara o costume do lado de fora da razão, como força cega. Ravaisson o olhou por dentro.", PI)
add("No começo, diz ele, o movimento é todo vontade: há esforço, consciência de cada parte, a distância sentida entre querer e fazer. Com a repetição, o esforço e a consciência diminuem, e o movimento fica mais rápido e mais certo. O hábito é a passagem, por graus insensíveis, da vontade à natureza: uma segunda natureza, um querer que já não precisa querer a si mesmo. Ravaisson retoma de Maine de Biran uma lei dupla. A sensação repetida enfraquece; a ação repetida se fortalece.", PI)
add("Isso responde à pergunta de onde você estava enquanto caía. Lembre as primeiras manhãs do exercício do corpo, ou as noites em que voltar ao que estava aberto custava mais do que abrir coisa nova. A vontade daquelas manhãs não se gastou: desceu ao gesto. Ela está nos exercícios marcados com H, que acontecem quase sem decisão, e na rapidez maior dos marcados com J.", PI)
add("Pela mesma lei, vista de dentro, a mudança quase não se nota. O esforço do começo sumiu porque o gesto se tornou seu, e por isso, ao fim do ciclo, você sente menos do que esperava sentir.", PI)
add("Resta a pergunta das folhas: você saiu do ciclo com treze hábitos, ou com um caráter? Aristóteles diz que as virtudes de caráter, no sentido pleno, não existem separadas da prudência, a <i>phrónesis</i>, e que com ela, que é uma só, vêm todas (VI, 13, paráfrase). Sem ela, são boas inclinações que causam dano, como um corpo forte que se move sem ver e cai com mais força por não ver.", PI)
add("O livro não dá a você essa prudência. O que une os treze gestos é <i>ele</i>, o homem da visão: os gestos são os meios dele, e a máscara os junta, porque é a pergunta sobre ele que escolhe, a cada entrada, o que você faz. Ravaisson fala de uma segunda natureza, no singular, e a máscara a pede assim, com um só rosto. <i>Do retorno</i> reabre essa escolha no fim de cada ciclo.", PI)

sec("Do que se conta")
add("Nas últimas décadas do século XIX, nos Estados Unidos, Joseph Jefferson subiu ao palco milhares de vezes como Rip Van Winkle, numa adaptação do conto de Washington Irving. O Rip é um bêbado afável que, a cada copo novo, se desculpa com a mesma frase, e a plateia ria com ele: <i>desta vez não conta</i>.", PI)
add("Em 1890, William James levou o Rip para o capítulo sobre o hábito dos <i>Princípios de psicologia</i>. Ele pode não contar a vez, comenta James, e um céu bondoso pode não contá-la; mas ela está sendo contada do mesmo modo. Lá embaixo, entre as células e as fibras nervosas, as moléculas estão contando e guardando, para usar contra ele quando vier a próxima tentação. O sistema nervoso, como a água que corre, cava o próprio leito e volta a correr por ele.", PI)
add("James tira daí, apoiado em Alexander Bain, umas poucas máximas. Lançar-se com uma iniciativa tão forte quanto possível: foi o seu dia zero, e é a linha do corte assinada no dia em que se queimam as pontes. Nunca permitir uma exceção enquanto o hábito novo não se enraizou: cada lapso é deixar cair o novelo, e um só desfaz mais voltas do que muitas tornam a enrolar. Agir na primeira ocasião, antes que a resolução esfrie: é o §2.", PI)
add("O Rip fala neste livro de três maneiras. Pede um ponto no dia em que a ocasião veio e você cedeu. Diz que o dia sem ocasião entre duas cruzes as separou. Escreve <i>chegou</i> numa noite sem certeza, descontando adiantado o que ainda não está feito.", PI)
proc("Contra o Rip", [
 "Se a ocasião veio e você cedeu, marque cruz.",
 "Se houve um ponto entre duas cruzes, conte as duas como seguidas.",
 "Se você não tem certeza de que o gesto veio sem o caderno lembrar, não escreva <i>chegou</i>.",
 "· Ver: <i>Da medida</i>.",
])
add("A folha de marcas é a contabilidade que as moléculas de James fazem de qualquer modo. O livro pediu que você a fizesse à vista, com a sua letra, em vez de deixá-la correr às escondidas contra você.", PI)
add("A exceção de que James fala é uma licença dada antes, ou uma queda descontada depois: a do Rip, que bebe e não conta. A cruz conta a queda, com a linha da queda ao lado dizendo onde estava o buraco. O que a máxima de James tem de verdadeiro vive inteiro no §5: nunca dois dias seguidos de queda.", PI)

sec("Do mesmo e de si")
add("Falta uma parte da objeção, e para ela há uma cena de Roma, em meados do século III antes de Cristo. Marco Atílio Régulo, cônsul feito prisioneiro pelos cartagineses, é mandado a Roma sob juramento: deve negociar a troca de prisioneiros e, se ela fracassar, voltar. No Senado, aconselha que a troca seja recusada, porque não convém a Roma. Depois, contra os pedidos da família e dos amigos, embarca de volta para Cartago, onde o esperam a prisão e a morte. Cícero conta a história em <i>Dos deveres</i>; os historiadores de hoje duvidam de parte dela. Roma guardou o gesto: chegado o dia, ele já não podia querer o que tinha jurado, e cumpriu.", PI)
add("Se, ao dizer <i>sou mais do que os meus atos</i>, você quer dizer que há em você alguém que responde por eles, que os promete antes e os reconhece depois, nenhuma resposta anterior chega a esse alguém. Ele não aparece em nenhuma folha de marcas. É ele que lê as folhas esta noite.", PI)
add("Paul Ricoeur deu nome a esse alguém em 1990, em <i>O si-mesmo como outro</i>. Há dois sentidos em que uma pessoa permanece a mesma, e o latim tinha uma palavra para cada um. <i>Idem</i> é a mesmidade: o que continua igual e permite reconhecer alguém, como se reconhece um rosto ou uma assinatura. Na pessoa, a mesmidade é o caráter, e Ricoeur o liga ao hábito: cada hábito contraído se sedimenta num traço de caráter. Tudo o que vem antes neste capítulo trata do <i>idem</i>.", PI)
add("<i>Ipse</i> é o si que se mantém mesmo quando muda, e o modelo dele é a palavra dada e cumprida. Quem promete fixa o que fará num tempo em que já poderá querer outra coisa; chegado esse tempo, mantém. Ainda que o meu desejo mude, ainda que eu mude de opinião, eu mantenho. Ricoeur chama isso de manutenção de si.", PI)
add("Repare na forma do estribilho que você disse esta manhã. <i>Reivindique-se para si</i> está no imperativo. Ele não descreve o seu caráter, que no primeiro dia ainda era o da anti-visão; manda fazer uma coisa naquele dia. Quem o diz de manhã dá a palavra a si mesmo, sobre as horas do dia e a da vez na ocasião dela. Cada manhã a palavra foi dada, e cada noite a marca conferiu se ela foi mantida. A folha de marcas é o registro dessa promessa.", PI)
add("Agora você pode responder se é quem escreveu a anti-visão. No <i>idem</i>, você é um pouco menos aquele: há hábitos novos onde moravam os velhos, e haverá mais. No <i>ipse</i>, contam os dias em que você manteve a palavra sem gosto nenhum; as suas folhas sabem quantos foram, e o livro não. A objeção do dia zero recebe aqui a parte de razão que lhe faltava: você é mais do que os seus atos por ser quem os promete e responde por eles. Mas esse si só se atesta mantendo, e se mantém em atos, hora a hora.", PI)

sec("Da vida como história")
add("A última resposta é de Alasdair MacIntyre, em <i>Depois da virtude</i>, de 1981. Um homem cava a terra no quintal. O que ele está fazendo? Cava; cuida do jardim; faz exercício; prepara a terra para o inverno; agrada à mulher. Todas as respostas são verdadeiras, e o corpo faz o mesmo movimento em todas. O que as distingue é a história em que o gesto entra.", PI)
add("Contra a vida moderna repartida em papéis, cada um com as próprias normas, MacIntyre propõe que a unidade de uma vida é a unidade de uma narrativa. O homem, escreve, é essencialmente um animal que conta histórias. Só posso responder à pergunta <i>que devo fazer?</i> se responder antes a esta: <i>de que história faço parte?</i> Um traço isolado das suas folhas diz tão pouco quanto o movimento do homem que cava. Dentro do ciclo, ele ganha sentido.", PI)
add("MacIntyre chama essa vida de busca, e o que se procura se aprende procurando. A sua visão do dia zero foi escrita por alguém que ainda não tinha feito um ciclo, e esta noite você verá nela coisas a corrigir. Ser o sujeito de uma história, diz ainda MacIntyre, é ser alguém a quem se podem pedir contas dos atos que a compõem. Na narrativa cabem o <i>idem</i> e o <i>ipse</i>: a continuidade do caráter e a palavra mantida.", PI)
proc("Se a visão pede correção", [
 "Não corrija a folha antiga.",
 "Escreva a correção na nova folha, no próximo dia zero.",
])

sec("Do exercício")
add("A prova do ciclo respondeu ao que você faz, e continua como está. Agora você escreve o ciclo como um capítulo da sua vida, em três parágrafos. O primeiro é do <i>idem</i>: o que se sedimentou e o que não. O segundo, do <i>ipse</i>: a palavra mantida. O terceiro é uma promessa, a forma que Ricoeur dá à permanência de si.", PI)
proc("O capítulo do ciclo", [
 "Escolha uma noite entre a prova e o dia zero seguinte.",
 "Sente-se a sós, longe de toda distração.",
 "Escreva em uma hora, no máximo.",
 "· Passar de uma hora é tratar o capítulo como obra.",
 "No alto da página 37, escreva o número do ciclo e as datas.",
 "Escreva um título curto, que nomeie o ciclo pelo que aconteceu nele.",
 "Primeiro parágrafo, <i>o que fui</i>: quem começou e quem terminou o ciclo, contado pelas provas.",
 "Use a folha do dia zero, as folhas de marcas, as linhas do dia e as linhas da queda.",
 "Escreva só fatos, como alguém que observou você durante o ciclo inteiro.",
 "Inclua o que não mudou.",
 "Segundo parágrafo, <i>o que mantive</i>: a palavra cumprida sem vontade, as voltas depois de cada cruz.",
 "Terceiro parágrafo, <i>o que prometo</i>: uma só promessa para o ciclo seguinte, dita em atos.",
 "Não repita a promessa em outro lugar. Não a conte a ninguém.",
 "Leia os três parágrafos uma vez.",
 "Se o primeiro traz um juízo sobre você, troque-o pelo que aconteceu.",
 "Se a promessa diz um estado, escreva o ato que o mostraria.",
 "· Ver: §7.",
])
proc("O caderno do ciclo", [
 "Escreva o capítulo nas páginas 37 e 38 do caderno deste ciclo.",
 "No novo dia zero, abra um caderno novo.",
 "Guarde este caderno com os dos ciclos anteriores.",
 "Não releia os capítulos durante o ciclo, nem nas noites de passagem.",
 "Na véspera de cada novo dia zero, releia todos de uma vez, cada um no seu caderno, antes de dormir.",
])
add("Há dois erros. O primeiro é escrever bonito, como se alguém fosse ler: ninguém vai ler, e o capítulo enfeitado mente a quem o reler daqui a três anos. O segundo é escrever uma sentença em vez de uma história. <i>Fui fraco</i> ou <i>sou outra pessoa</i> são veredictos, e um veredicto sobre o caráter fecha o processo que a história deixa aberto. A história diz o que aconteceu e onde estava o buraco.", PI)
add("Relidos na véspera de cada dia zero, os capítulos respondem à pergunta deste interlúdio com os seus próprios fatos: o que se sedimentou, o que voltou a cair, o que se manteve através de tudo.", PI)
proc("Depois do capítulo", [
 "Releia as doze Lições, cada uma no fim do seu exercício.",
 "Releia <i>Do homem</i> como quem volta a assinar.",
 "Leia <i>Do retorno</i>, que leva você ao novo dia zero.",
])
fleur(); st[-2:] = [KeepTogether(st[-2:])]
# ===================== DO HOMEM =====================
st.append(PageBreak()); sp(30)
add("Do homem", LT); sumario(st[-1], 0, "Do homem")
add("Leia esta página na primeira noite de passagem, depois da Lição. Você sai daqui com as treze frases copiadas de próprio punho, tal como estão.", PI)
proc("Antes de copiar", [
 "Confira que esta noite você escreveu <i>chegou</i> ao lado do traço da ordem.",
 "Se não escreveu <i>chegou</i> nem declarou passagem por decisão, não copie.",
 "Nesse caso, leia a página, se quiser, e volte a ela na noite da passagem.",
])
add("Amanhã de manhã a ordem passa a ficar e entra a do terminar. As treze frases a seguir estão na primeira pessoa e no presente: <i>tenho</i>, <i>faço</i>, <i>calo</i>. O estribilho manda; estas frases descrevem alguém que já age assim. Esse alguém é <i>ele</i>, o homem da máscara, e estas frases são o credo dele.", PI)
add("São os meios do método, os mesmos para qualquer pessoa que leia este livro. Os fins estão na sua visão, e esses foi você quem escreveu. Escrevê-las com <i>eu</i> antes de serem verdade é pôr a máscara com a sua letra. Lida, uma frase se percorre num segundo; copiada, ela ocupa o tempo de escrevê-la, e é nesse tempo que aparece a palavra que a leitura pulava.", PI)
proc("A cópia", [
 "Abra o caderno na segunda página, a reservada para elas desde o dia zero.",
 "Copie as treze frases à mão, uma por linha, na ordem.",
 "Escreva devagar: são dez minutos.",
 "Se a mão hesitar ao escrever <i>eu</i>, copie assim mesmo.",
 "Não melhore as frases. Não as passe para o futuro. Não acrescente nenhuma.",
])
for c in ["Tenho um domínio escolhido, e é nele que ponho as horas difíceis do dia.",
          "Quando decido uma coisa, eu a faço sem reabrir a decisão.",
          "Aprendo pondo a atenção numa coisa de cada vez, e recordando depois, de memória, o que estudei.",
          "Treino o corpo com regularidade, pela ficha, porque é com ele que faço tudo o resto.",
          "Antes de começar uma coisa, eu me informo sobre o terreno; depois de começada, sigo o plano que fiz.",
          "O que quero, eu escrevo como um caminho, com o primeiro passo marcado.",
          "Deixo terminar quem fala comigo, pergunto antes de opinar e sou cortês também com quem me cria dificuldades.",
          "Sob pressão, espero que passe o pico antes de responder.",
          "Quando me mostram que estou errado, examino e, se for o caso, mudo de ideia e digo isso.",
          "Calo os meus planos até a obra estar feita.",
          "Quando corto um hábito, mantenho a linha que tracei sem voltar a discuti-la.",
          "Eu me lembro de que vou morrer, e faço hoje o que hoje me cabe.",
          "Quando algo dá errado, escrevo a causa e dou o passo seguinte."]:
    add(c, CRE)
proc("Depois da cópia", [
 "Releia as treze frases esta noite, junto da folha do dia zero.",
 "Neste ciclo, não as copie de novo.",
 "Em cada noite de passagem, releia a segunda página do caderno junto da folha do dia zero.",
 "Leia e feche o caderno. A releitura não tem marca.",
 "No fim do ciclo, releia-as depois do capítulo do ciclo.",
 "No caderno do ciclo seguinte, copie-as de novo, na primeira passagem dele.",
])
add("A folha do dia zero diz de onde você partiu e para onde vai; as treze frases dizem o modo de agir com que se chega lá. Haverá passagens em que uma delas já descreve você, e outras em que nenhuma.", PI); fleur()
# ===================== DO RETORNO =====================
st.append(PageBreak()); sp(30)
add("Do retorno", LT); sumario(st[-1], 0, "Do retorno")
add("Leia este capítulo no fim do ciclo, depois da prova e do capítulo do ciclo, numa noite antes do novo dia zero. Releia-o na véspera e na manhã dele. Você sai daqui com um caderno novo e a nova folha do dia zero na primeira página, cada ponto aprovado no seu teste.", PI)
add("Na noite em que você escreveu <i>chegou</i> ao lado do traço do décimo terceiro exercício, a passagem já não tinha uma seguinte para trazer: na manhã depois dela, a da vez passou a ficar e nenhuma entrou. O caminho, que parecia seguir sempre em frente, traz você de volta ao lugar de onde saiu. Ao fechar o caderno, vem a frase: <i>então foi tudo para voltar ao começo?</i>", PI)
add("Daqui a poucos dias você fará outro dia zero, e na tarde dele a da vez será de novo a da ordem. As microações, as linhas e os cortes ficam, todos os dias, nas ocasiões deles, pelo resto da vida, porque as ocasiões continuam a chegar. Franklin dava uma semana a cada uma das treze virtudes. O curso completo levava treze semanas, cabiam quatro num ano, e ao fim da última semana ele recomeçava pela primeira. A virtude que já teve a sua semana continua pedindo vigilância.", PI)
add("Marco Aurélio escreveu as mesmas poucas ideias até morrer. No sétimo livro das <i>Meditações</i>, pergunta como os próprios princípios poderiam morrer, e responde: só se as imagens que lhes correspondem se apagarem, e está nas mãos dele reacendê-las sem cessar. Um princípio que não volta à mente quando a coisa acontece já não governa nada. Ele se conserva como um fogo, alimentado todos os dias, e ninguém o possui de uma vez. O dia zero põe você outra vez diante da sua folha, por escrito, para que ela volte a estar à mão quando a ocasião chegar.", PI)
add("Nietzsche imaginou a maior prova a que se pode submeter um ciclo. Em <i>A gaia ciência</i>, no aforismo <i>O maior dos pesos</i>, um demônio entra na sua solidão mais funda e diz que esta vida terá de ser vivida outra vez e ainda inúmeras vezes, sem nada de novo: cada dor e cada prazer, até esta aranha e este luar entre as árvores, e este instante, e você mesmo. Você se jogaria no chão, rangendo os dentes, amaldiçoando quem falou assim? Ou teria vivido um instante tão grande que lhe responderia que nunca ouviu nada mais divino?", PI)
add("Se esse pensamento dominasse você, escreve Nietzsche, a pergunta <i>você quer isto ainda uma vez, e ainda inúmeras vezes?</i> pesaria sobre cada ato como o maior dos pesos. Quem a faz diante de cada ato deixa de agir por inércia. Você não precisa acreditar no demônio para usar a pergunta. Nietzsche pede o sim à vida inteira, com as cruzes; aqui ela serve de crivo, e só a forma do ciclo se repete.", PI)
proc("A pergunta de Nietzsche", [
 "Numa noite antes do dia zero, ponha sobre a mesa as folhas de marcas.",
 "Pegue uma folha de cada vez.",
 "Pergunte: <i>você quereria estes dias outra vez, tal como foram, com as cruzes e os pontos?</i>",
 "Se a resposta for sim, guarde o que fez.",
 "Se for não, escreva isso ao lado, numa linha.",
 "· Onde a resposta é não está o que muda no próximo ciclo.",
])
add("Um teorema demonstrado não se demonstra outra vez. O que este livro treina se guarda como uma língua aprendida tarde, que se perde quando se deixa de falá-la. No capítulo da <i>Ética a Nicômaco</i> em que diz que nos tornamos justos praticando atos justos, Aristóteles acrescenta que cada virtude nasce e se destrói pelas mesmas causas, como na arte da cítara, em que é tocando que se formam os bons e os maus citaristas. A disposição formada pelos atos só se mantém enquanto os atos continuam. Por isso o caminho se refaz, e a frase dele fecha o retorno.", PI)
add("Hokusai, o gravador japonês da <i>Grande onda</i>, tinha setenta e quatro anos e milhares de desenhos publicados quando lançou, em 1834, as <i>Cem vistas do monte Fuji</i>. No posfácio, escreveu que desenhava desde os seis anos e que nada do que fizera antes dos setenta merecia atenção. Aos setenta e três, dizia, tinha começado a entender a estrutura dos animais, dos pássaros, dos peixes e dos insetos; aos noventa esperava penetrar o segredo das coisas, e aos cem chegar a algo admirável. Assinou como o velho louco por desenho e desenhou até morrer, em 1849. Quem tinha chegado mais longe tratou a obra feita como um começo.", PI)
add("No Japão, o grande santuário de Ise é desmontado e reconstruído a cada vinte anos, há mais de treze séculos, com algumas interrupções, sempre pelo mesmo desenho, num terreno ao lado do antigo. É pela reconstrução que o ofício passa de mãos velhas para mãos novas: cada geração aprende a construí-lo construindo-o. O seu retorno é dessa espécie. Você volta ao dia zero porque quem chega lá agora já não é quem escreveu a primeira folha.", PI)
add("Falta o leão que <i>Da máscara</i> prometeu. A visão antiga foi desenhada pelo eu antigo, num só dia. Dizer <i>não</i> aos atos dela é o sagrado não, dito a um <i>Tu deves</i> que você mesmo escreveu, e é assim que se deixa o educador. O leão só abre o lugar; a visão nova dá o rosto do ciclo seguinte.", PI)
proc("A véspera", [
 "Se faltar a prova do ciclo ou o capítulo do ciclo, escreva-o antes.",
 "Escolha para o dia zero um dia sem trabalho, como da primeira vez.",
 "Na véspera, separe um caderno novo e a caneta.",
 "Antes de dormir, releia o capítulo do ciclo, nas páginas 37 e 38 do caderno que termina.",
 "Releia de uma vez os capítulos dos cadernos anteriores, se houver.",
])
proc("A manhã do dia zero", [
 "Antes das perguntas, abra o caderno que termina na primeira página.",
 "Leia uma vez a folha do dia zero do começo do ciclo. Não a corrija.",
 "Leia a visão dela como a máscara de outra pessoa.",
 "Passe cada ato do <i>ele</i> antigo pelo teste: <i>quero isto, ou quero ser visto com isto?</i>",
 "Embaixo da folha antiga, escreva numa linha cada ato que você já não quer, com <i>não</i> na frente.",
 "Escreva a nova folha na primeira página do caderno novo, pelo roteiro do Prólogo.",
 "Ponha nela a promessa do capítulo do ciclo.",
 "À tarde, faça a arrumação grande do exercício da ordem e escreva a lista da mesa.",
 "À noite, confira os oito pontos da nova folha, cada um no seu teste.",
 "Na noite do dia zero, faça a primeira marca na primeira linha da folha de marcas do caderno novo, com o número um.",
 "Guarde o caderno antigo. Releia a folha dele no dia zero seguinte.",
])
add("A folha antiga é o retrato de quem você era quando começou. A distância entre ela e as respostas de hoje é a medida mais exata que o caderno dá do caminho feito. A anti-visão será outra, porque a semana que você prolonga já não é a mesma. Se a visão se parecer com a antiga, os atos que a dizem terão mudado.", PI)
proc("O dia seguinte", [
 "Acorde e abra o caderno antes de qualquer outra coisa.",
 "Diga o estribilho em voz baixa.",
 "Escreva a linha da manhã com a obra de hoje, que desce da nova obra em curso.",
 "Ao sentar diante da obra, diga por dentro a frase: <i>Isto, até acabar.</i>",
 "· A da vez é de novo a da ordem.",
])
add("A da vez será a mesma do primeiro dia zero, num dia que já não é o da primeira vez.", PI); fleur(); st[-2:] = [KeepTogether(st[-2:])]
add("“Tornamo-nos justos praticando atos justos.”<br/>Aristóteles, <i>Ética a Nicômaco</i>, II, 1", BOX)
estribilho(size=14, before=6, after=6)
add("<i>Torne-se o que você é, depois de aprendê-lo.</i><br/><font size=10 color='#6b6b6b'>Píndaro, <i>Píticas</i>, II</font>", ParagraphStyle('end', parent=PC, fontSize=14, spaceBefore=6, spaceAfter=40))
# Epígrafe, estribilho e Píndaro fecham juntos o capítulo, sem deixar Píndaro sozinho numa página.
st[-3:] = [KeepTogether(st[-3:])]

# ===================== MANUAL OPERACIONAL =====================
st.append(PageBreak()); sp(30)
add("Apêndice", LIV)
add("Manual operacional", LT); sumario(st[-1], 0, "Manual operacional")
add("Este apêndice é opcional, e pode ficar fechado para sempre. Ele responde a uma pergunta que vem depois da quarta passagem, com a primeira estação inteira entre as que ficaram: o que fazer com o resto do dia. A resposta é uma lista de ações, cada uma com a sua medida, os cuidados que algumas pedem e o que os estudos dizem de cada grupo.", PI)
add("Nenhuma delas é microação. O livro deixa o resto do dia sem soma: uma conta noturna ensinaria a encher o dia de coisas pequenas e a ler o número como sentença sobre quem o escreveu. Elas não pedem a atenção nova que só a da vez recebe, e por isso a regra de não juntar não as alcança.", PI)
proc("Como usar as ações", [
 "Escolha uma ou duas ações por dia, se quiser, nas horas que sobrarem.",
 "Não faça nenhuma à custa da da vez nem da obra de hoje.",
 "Não leve nenhuma à folha de marcas. Não as conte.",
 "Troque-as de um dia para outro, se quiser.",
 "Se a ação tem o sinal <i>cuidados</i>, leia antes o parágrafo dela em <i>Dos cuidados</i>.",
 "Se o dia está dentro de um bloco de obra, não faça ações deste apêndice.",
])

sec("Das ações")
add("São cinquenta e uma, em sete grupos, pelo que treinam. A linha no alto de cada grupo diz o que ele treina e por quê; as ações vêm secas, com a medida.", PI)
MO_G = [
 ("Atenção e obra", "Treina a atenção numa coisa só, no ponto em que você ainda falha: é a assentada posta em minutos. Os minutos são o mínimo que conta; se o passo não acabou quando eles acabam, <i>Isto, até acabar</i> vale até o fim dele, dentro da hora de parar. Cada troca de uma coisa para outra custa tempo e erros, e a obra de hoje se faz nas horas sem trocas. A parede e a pausa dão à atenção o descanso para voltar.", [
  ("Noventa minutos na parte difícil da obra, numa coisa só, sem nada que distraia no cômodo.", 3, 0),
  ("Quarenta e cinco minutos na parte difícil da obra, numa coisa só.", 2, 0),
  ("Quinze minutos na parte difícil da obra, mesmo num dia de piso.", 1, 0),
  ("Três sessões de vinte e cinco minutos numa coisa só, escrita antes de cada sessão, com cinco minutos de pausa entre elas.", 2, 0),
  ("Antes de abrir a obra, leve para outro cômodo tudo o que toca ou avisa, e deixe tudo lá até o fim da sessão.", 1, 0),
  ("Cinco minutos sentado diante de uma parede, sem nada nas mãos.", 1, 1),
  ("No meio da obra, dez minutos longe da mesa, sem nada que brilhe e sem conversa.", 1, 0),
  ("Dez minutos sentado, de olhos abertos ou fechados, com a atenção na respiração; quando você sair dela, volte.", 1, 1),
  ("Vinte minutos da mesma prática.", 2, 1)]),
 ("Corpo", "Treina o corpo, que Musônio Rufo queria tão habituado ao esforço quanto a alma. Está demonstrado que mexer-se faz bem à saúde e ao humor, que a luz da manhã acerta o relógio interno com o dia e que o sono regular preserva a atenção do dia seguinte.", [
  ("Vinte minutos andando, sem nada nos ouvidos.", 1, 0),
  ("Cinquenta minutos andando num parque, num bosque ou à beira da água.", 2, 0),
  ("Um treino de força inteiro, pela sua ficha.", 2, 1),
  ("Trinta minutos correndo, nadando ou pedalando, num ritmo em que você ainda consiga falar.", 2, 1),
  ("Vinte minutos de um esforço que lhe tire o fôlego para conversar.", 2, 1),
  ("Dez minutos de exercício onde você estiver: agachamentos, flexões, alongamentos.", 1, 0),
  ("Na primeira meia hora depois de acordar, quinze minutos ao ar livre, à luz do dia, sem olhar para o sol.", 1, 1),
  ("Termine o banho com trinta a noventa segundos de água fria.", 1, 1),
  ("Durma sete horas ou mais e acorde a menos de meia hora do horário de ontem.", 2, 1),
  ("Na última hora antes de dormir, luz baixa e nada que brilhe no quarto.", 1, 0)]),
 ("Privação voluntária", "Treina o desapego em relação ao conforto. É o exercício da pobreza voluntária, com a pergunta de Sêneca, em ações de um dia.", [
  ("Até o meio-dia, só água, café ou chá sem açúcar.", 2, 1),
  ("Um dia sem açúcar e sem nada entre as refeições.", 1, 0),
  ("Uma refeição do mais simples que houver em casa: pão, arroz, água.", 1, 0),
  ("Faça a pé um caminho de mais de dez minutos que você faria de outra maneira.", 1, 0),
  ("Um dia sem comprar nada que você não tenha escrito de manhã.", 1, 0),
  ("Um dia sem abrir distração nenhuma fora de uma meia hora escolhida de manhã.", 2, 0),
  ("O dia de pobreza, declarado na véspera, como ensina o exercício da pobreza voluntária.", 3, 1)]),
 ("Pensamento", "Treina a distância entre você e o que você pensa: decidir antes o que fará quando a coisa vier, olhar o pensamento como pensamento, deixar a vontade subir e descer sem obedecer a ela, como na linha IX, e tratar a falha como dado sobre o terreno.", [
  ("Antes de abrir a obra, escreva numa linha: se X acontecer, faço Y.", 1, 0),
  ("Escreva um desejo para hoje; imagine por dois minutos o melhor resultado, depois o obstáculo que está em você; escreva: se o obstáculo vier, faço ____.", 1, 0),
  ("Quando um pensamento pesar em você, escreva esse pensamento; embaixo dele, o que o confirma e o que o desmente; depois, uma frase mais exata.", 1, 1),
  ("Antes de uma conversa difícil, passe dois minutos pensando nela pelo seu próprio nome: o que o ____ vai fazer?", 1, 0),
  ("Quando um pensamento prender você, diga-o três vezes por dentro, começando por <i>estou tendo o pensamento de que</i>.", 1, 1),
  ("Quando vier uma vontade, note onde ela está no corpo e observe a vontade subir e descer, sem agir, até passar.", 1, 1),
  ("Quinze minutos escrevendo sem parar sobre o que perturba você, só para você mesmo; no máximo quatro dias seguidos.", 2, 1),
  ("Depois de uma falha, três linhas a si mesmo, como você as escreveria a um amigo que falhou na mesma coisa.", 1, 0)]),
 ("Aprender", "Treina a memória pelo esforço de recordar e pelo intervalo entre as revisões. Está demonstrado que os dois funcionam, e são o gesto do exercício do aprender.", [
  ("Feche o livro e diga em voz alta, durante dois minutos, o que você leu.", 1, 0),
  ("Vinte minutos escrevendo de memória o que você estudou ontem; depois abra e corrija.", 2, 0),
  ("Dez perguntas sobre o que você estudou de três a seis dias atrás, respondidas sem olhar.", 1, 0),
  ("Dez minutos quieto, de olhos fechados, logo depois de estudar.", 1, 0),
  ("Explique a alguém, em cinco minutos, uma coisa que você aprendeu nesta semana.", 1, 0),
  ("Uma página, ao menos, de um livro do seu domínio.", 1, 0),
  ("Trinta páginas de um livro do seu domínio, com as três ideias escritas de memória no fim.", 2, 0)]),
 ("Ordem", "Treina o lugar. O que está à vista dispara muito do que você faz, e mudar o lugar custa menos do que resistir dentro dele.", [
  ("Dez minutos arrumando um só lugar: uma gaveta, uma prateleira, um canto.", 1, 0),
  ("Leve para outro cômodo aquilo que a mão procura sem você pedir, e deixe lá até amanhã.", 1, 0),
  ("À noite, deixe pronto o que a primeira tarefa de amanhã pede.", 1, 0),
  ("Termine uma coisa da lista do que está aberto, ou encerre-a por escrito, com a razão.", 2, 0),
  ("Faça hoje uma pendência da folha de captura adiada há mais de uma semana.", 1, 0)]),
 ("Pessoas", "Treina a atenção posta no outro e a correção que vem de fora: o autor não vê os defeitos da própria obra, e quem ouve até o fim fica sabendo o que o outro disse.", [
  ("Vinte minutos de conversa sem nada nas mãos, perguntando mais do que falando.", 1, 0),
  ("Peça a quem sabe mais a crítica de uma obra sua, com a pergunta: o que está mais fraco aqui?", 2, 0),
  ("Volte a quem você tratou mal e conserte o que a pressa estragou.", 1, 0),
  ("Uma refeição com alguém, sem nada que distraia na mesa.", 1, 0),
  ("Vinte minutos andando com alguém, ouvindo.", 1, 0)]),
]
n_ = 0
for g_, why_, acoes_ in MO_G:
    st.append(Paragraph(g_, HEAD)); st.append(Paragraph(why_, WHEN))
    for t_, p_, c_ in acoes_:
        n_ += 1
        cu_ = " <font color='#6b6b6b'><i>cuidados</i></font>" if c_ else ""
        add(f"{n_}. &nbsp;{t_}{cu_}", LAW)

sec("Dos cuidados")
add("Nada neste manual substitui o médico. Quem tem doença crônica, toma medicação contínua, está grávida ou tem histórico psiquiátrico fala com o médico antes de mudar o jejum, o sono, o exercício intenso ou o frio. Os sinais de <i>Do escrúpulo</i>, no Livro V, valem também aqui; se lhe vierem pensamentos de morte, procure ajuda hoje.", PI)
for a_, b_ in [
 ("Jejum (20, 26):", "não o fazem quem tem diabetes, sobretudo com insulina ou com comprimidos que baixam o açúcar; grávidas e mulheres que estão amamentando; quem tem ou teve transtorno alimentar; menores de dezoito anos; quem tem baixo peso; quem toma medicação que deve ser tomada com comida."),
 ("Frio (17):", "não o fazem, sem avaliação médica, quem tem doença cardíaca, arritmia, hipertensão não controlada ou doença de Raynaud, nem grávidas. A ação é água fria no fim do banho; nunca imersão em água fria sozinho, nem em águas abertas. Comece pelos trinta segundos."),
 ("Exercício intenso (12 a 14):", "doença cardíaca, dor no peito durante o esforço, hipertensão não controlada, lesão ou gravidez de risco pedem o médico antes. Quem não se exercita começa pelo mais leve e sobe devagar."),
 ("Sono (18):", "roncar alto, pausas na respiração durante o sono, sonolência de dia que não passa ou insônia de meses pedem o médico. Nenhuma ação deste manual tira horas do sono."),
 ("Luz (16):", "nunca olhe para o sol. Quem tem transtorno bipolar, doença da retina ou toma medicação que aumenta a sensibilidade à luz fala antes com o médico."),
 ("Atenção na respiração e parede (6, 8, 9):", "quem teve psicose, trauma grave ou transtorno dissociativo pratica só com acompanhamento. Se ficar quieto aumentar a ruminação ou a angústia, pare."),
 ("Pensamento (29, 31, 33):", "depressão grave, pensamentos de morte, transtorno de estresse pós-traumático ou transtorno obsessivo pedem tratamento com um profissional; essas ações não substituem o tratamento. Há indícios de que a escrita sobre o que perturba deixa a pessoa mais triste no próprio dia; em trauma recente ou grave, ela é feita com terapeuta, e é interrompida se a angústia persistir."),
 ("Vontade (32):", "quem tem dependência física de álcool, de calmantes ou de opioides precisa de acompanhamento médico; parar de repente pode ser perigoso."),
 ("Registro:", "quem tem ou teve transtorno alimentar ou obsessivo não registra peso, calorias nem minutos de exercício no caderno."),
 ("Dia de pobreza (26):", "se a pobreza que você escolher tocar a comida, valem os cuidados do jejum."),
]:
    add(f"<b>{a_}</b> {b_}", LAW)

sec("Do que se sabe")
add("As ações não dependem desta tabela. De cada grupo, ela diz o que os estudos mostram, quem mostrou e com que força. <b>Forte</b>: várias meta-análises concordam e o efeito se repete. <b>Moderado</b>: há vários estudos, e o efeito é pequeno ou varia. <b>Fraco</b>: poucos estudos, ou estudos pequenos.", PI)
MO_S = [
 ("Trabalhar numa coisa só", "Mudar de tarefa custa tempo e erros, mesmo quando a mudança é prevista (Monsell, 2003).", "Forte, em laboratório"),
 ("Sessões e pausas marcadas", "Pausas marcadas e pausas livres produziram o mesmo esforço e o mesmo número de tarefas feitas (Biwer e colegas, 2023).", "Fraco"),
 ("Pausas curtas", "Dão mais vigor e menos fadiga; no desempenho, pouco (Albulescu e colegas, 2022).", "Moderado"),
 ("Minutos quietos, a parede", "Dez minutos de descanso quieto logo depois de aprender ajudam um pouco a reter (Humiston e colegas, 2019); ficar a sós com os pensamentos é penoso para muitos (Wilson e colegas, 2014). Que isso treine o foco, nenhum estudo mostrou.", "Moderado"),
 ("Atenção na respiração", "Melhora pouco o controle da atenção (Sumantry e Stewart, 2021); cerca de oito em cada cem praticantes relatam algum efeito adverso (Farias e colegas, 2020).", "Moderado"),
 ("Exercício", "Uma sessão melhora pouco a cognição (Chang e colegas, 2012); em adultos saudáveis, o ganho cognitivo de meses de treino quase desaparece depois de corrigido o viés de publicação (Ciria e colegas, 2023).", "Moderado"),
 ("Andar na natureza", "A memória de trabalho e a atenção melhoram um pouco depois de algum tempo num lugar natural (Stevenson e colegas, 2018).", "Moderado"),
 ("Luz da manhã", "A luz de manhã adianta o relógio interno, e a da noite o atrasa (Khalsa e colegas, 2003); o efeito no estado de alerta é incerto (Souman e colegas, 2018).", "Forte no relógio; fraco a moderado no alerta"),
 ("Sono", "Dormir pouco degrada a atenção, e quem dorme pouco subestima o próprio déficit (Lim e Dinges, 2010; Van Dongen e colegas, 2003).", "Forte"),
 ("Água fria no fim do banho", "Num ensaio com três mil adultos, menos faltas ao trabalho e os mesmos dias de doença (Buijze e colegas, 2016).", "Fraco a moderado"),
 ("Jejum até o meio-dia", "Um jejum curto não melhora nem piora a cognição de um adulto saudável (Bamberg e Moreau, 2025). Entra como privação voluntária.", "Forte, quanto à ausência de efeito"),
 ("Outras privações", "Prática de Sêneca (<i>Cartas a Lucílio</i>, 18) e do exercício da pobreza voluntária. O treino de autocontrole em geral tem efeito pequeno e mecanismo ainda não esclarecido (Friese e colegas, 2017).", "Prática do livro"),
 ("Planos se-então", "Decidir antes, em concreto, quando e o que fazer aumenta a probabilidade de fazê-lo (Gollwitzer e Sheeran, 2006; Sheeran, Listrom e Gollwitzer, 2025).", "Forte"),
 ("Desejo e obstáculo", "Imaginar o objetivo e depois o obstáculo interno, com um plano para ele, ajuda um pouco mais do que só imaginar o objetivo (Wang, Wang e Gai, 2021).", "Moderado"),
 ("Distância do pensamento", "Pensar em si pelo próprio nome diminuiu a angústia antes de falar em público (Kross e colegas, 2014); a desfusão teve efeitos positivos em laboratório (Levin e colegas, 2012); o efeito do registro de pensamentos feito sozinho não foi medido (Longmore e Worrell, 2007).", "Moderado"),
 ("Observar a vontade", "Num estudo com estudantes que fumavam, a vontade não diminuiu, mas eles fumaram menos na semana seguinte (Bowen e Marlatt, 2009).", "Fraco"),
 ("Escrever o que perturba", "Efeito médio positivo e pequeno (Frattaroli, 2006).", "Moderado"),
 ("Compreensão depois de falhar", "Em laboratório, levou as pessoas a estudar por mais tempo para a prova seguinte (Breines e Chen, 2012).", "Fraco a moderado"),
 ("Recordar e espaçar", "Testar-se rende mais do que reler (Rowland, 2014); espaçar as revisões rende mais do que concentrá-las (Cepeda e colegas, 2006).", "Forte"),
 ("Lugar e hábito", "Os hábitos são disparados pelas pistas do contexto (Wood e Neal, 2007) e levam de semanas a meses para se formar (Lally e colegas, 2010).", "Forte na teoria; moderado como técnica"),
 ("Registrar o progresso", "Acompanhar o progresso por escrito aumenta a probabilidade de chegar ao objetivo (Harkin e colegas, 2016).", "Forte"),
 ("Pessoas e crítica", "Gestos dos exercícios da crítica e das pessoas; não foram medidos para este manual.", "Prática do livro"),
]
rows = [[Paragraph(f"<font color='#6b6b6b'>{h}</font>", CU_P) for h in ("Prática", "O que se sabe", "Nível")]]
for a_, b_, c_ in MO_S:
    rows.append([Paragraph(f"<i>{a_}</i>", CU_P), Paragraph(b_, CU_P), Paragraph(c_, CU_P)])
tb = Table(rows, colWidths=[3.5*cm, 9.0*cm, 3.1*cm], repeatRows=1)
tb.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-2),0.3,colors.HexColor('#cccccc')),
                        ('LINEBELOW',(0,0),(-1,0),0.6,GRAY),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
st.append(tb); sp(10)
add("<b>O que não entra, e por quê.</b> O jejum como maneira de ficar mais concentrado e a água fria como maneira de pensar melhor: os estudos não mostram esse efeito, e as duas ações entram por outras razões. A parede como treino do foco: nenhum ensaio testou isso, e ela entra como descanso quieto. Os vinte e um dias para formar um hábito: no estudo de Lally, o tempo foi de pouco menos de três semanas a bem mais de meio ano. Acordar às cinco à custa de horas de sono: nenhum estudo mostra ganho, e o custo de dormir pouco está medido. As sessões de tempo marcado como técnica comprovada: não há ensaio controlado, e elas valem como prática do livro.", NOTE)
fleur(); st[-2:] = [KeepTogether(st[-2:])]





# ===================== COMENTÁRIO AO ESTRIBILHO =====================
st.append(PageBreak()); sp(30)
add("Comentário ao estribilho", LT); sumario(st[-1], 0, "Comentário ao estribilho")
st.append(KeepTogether([Paragraph(f"<i>“{ESTR}”</i>", ParagraphStyle('ce1', parent=PC, fontSize=13.5, leading=20, spaceAfter=2)),
                        Paragraph(ESTR_A, ParagraphStyle('ce1a', parent=EPA, spaceAfter=22))]))
add("Esta manhã você disse a frase em voz baixa, como em todas as manhãs, e ela lhe soou alheia, escrita para outra pessoa. <i>Do estribilho</i> previu esta manhã. Este comentário é leitura opcional e não acrescenta nenhuma regra.", PI)
proc("Se a frase soar alheia", [
 "Termine a manhã como sempre.",
 "Vá para a obra.",
 "Leia este comentário depois, fora das horas da obra.",
 "Amanhã de manhã, diga a frase como está escrita, com os colchetes calados.",
 "Se ela ainda soar alheia, não a troque.",
 "Releia a carta 1 de Sêneca inteira, ou uma destas páginas.",
])
add("A frase é de Sêneca. É o começo da primeira carta ao amigo Lucílio, procurador na Sicília, que queria se tornar melhor. Sêneca as escreveu nos últimos anos de vida, depois de se afastar da corte de Nero. Restam cento e vinte e quatro. Cada uma parte de um acontecimento miúdo, uma viagem, o barulho de um banho público embaixo da janela, um ataque de falta de ar, e tira dele uma coisa a praticar. Nas primeiras, Sêneca fecha com uma frase alheia, de Epicuro, para Lucílio levar consigo, e a chama, por brincadeira, de pequeno pagamento do dia.", PI)
add("É um curso de prática por correspondência, uma carta de cada vez, e este livro é da mesma família. Eu poderia ter lhe dado uma frase inventada. Preferi uma que se lê há quase dois mil anos e cujo contexto você confere em qualquer edição. É também a primeira instrução de Sêneca a quem quer mudar de vida: antes da virtude, da morte e da amizade, retomar as horas. Nenhum ensinamento tem onde ser praticado enquanto as horas estão nas mãos de outros.", PI)
add("Saber de cor é, na própria língua, saber pelo coração. Nos <i>Relatos de um peregrino russo</i>, livro anônimo do século XIX, um velho monge dá a um homem uma só frase de oração para dizer milhares de vezes por dia. Com o tempo, conta o homem, ela passou a se dizer sozinha, no ritmo da respiração. O estribilho pede muito menos: uma vez por manhã e quando o dia vacila. Apoia-se no mesmo hábito da memória: uma frase repetida com atenção vem sozinha no momento em que é necessária.", PI)
add("A repetição também esvazia. Uma palavra repetida em voz alta acaba soando estranha, e foi o que aconteceu com a frase esta manhã. Søren Kierkegaard escreveu sobre isso em 1843, em <i>A repetição</i>. O narrador volta a Berlim para refazer uma viagem feliz: o mesmo quarto, o mesmo teatro, o mesmo café. Nada se repete, e tudo lhe parece pior. A recordação repete para trás e quer reviver o que foi; essa repetição é impossível. A outra repete para a frente, e o narrador diz que ela é como uma roupa que não se gasta.", PI)
add("O estribilho fica com a repetição para a frente. Ele diz de novo, num dia diferente, a mesma decisão, e cada dia diferente dá a ela um peso que a primeira noite não tinha. O entusiasmo dessa noite fica onde ficou, e a frase não o pede de volta. A frase tem três partes, na ordem em que Sêneca as escreveu.", PI)

sec("Reivindique-se para si")
add("A carta abre como quem responde a outra: <i>faça assim, meu Lucílio</i>. Logo vêm três palavras, <i>vindica te tibi</i>, traduzidas por <i>reivindique-se para si</i>. A tradução perde o mais importante. <i>Vindicare</i> é verbo dos tribunais romanos: diz-se de quem reclama em juízo uma coisa sua que está na posse de outro. Diz-se também do processo em que, diante do magistrado, alguém declarava livre uma pessoa tida como escrava, tocando-a com uma vara, a <i>vindicta</i>. A ordem supõe duas coisas: o que você reclama é seu por direito, e neste momento está em mãos alheias.", PI)
add("Sêneca diz logo em que mãos. Há horas que nos são arrancadas, outras que nos são levadas às escondidas, outras que escorrem; e a perda mais vergonhosa é a que vem da negligência. Na primeira há alguém que toma à vista: a obrigação, o pedido, a urgência de outro. Na segunda há um ladrão que não se vê, e que só se descobre à noite, quando você procura a hora e ela não está. Na terceira não há ninguém: o tempo cai das mãos de quem não o segurava. Sêneca chama esta de vergonhosa porque só ela dependia de quem a sofreu.", PI)
add("Uma frase adiante dá a medida do estrago: grande parte da vida escapa a quem age mal, a maior parte a quem nada faz, e a vida inteira a quem faz outra coisa. A última é a categoria mais larga, e a sua. Quem faz outra coisa está ocupado, e ocupado com o que não escolheu. Na imagem do verbo, está na posse de outro. Reivindicar-se começa por saber quem tem as suas horas.", PI)
add("E vem a razão de tudo: todas as coisas, Lucílio, são alheias; só o tempo é nosso, e dele nos expulsa quem quiser. Sêneca nota a estranheza das contas humanas. Os homens aceitam dever o que receberam de mais barato e mais fácil de repor. Ninguém se considera devedor por ter recebido tempo, a única coisa que nem o mais agradecido pode devolver.", PI)
add("Quinze séculos depois, Montaigne, leitor de Sêneca, escreveu <i>Da solidão</i>. Ele pede um quarto dos fundos, todo nosso, livre, e traduz o <i>vindica te tibi</i> para o seu século: a maior coisa do mundo é saber pertencer a si mesmo. Poucos anos depois, foi eleito prefeito de Bordeaux e exerceu dois mandatos. Escreveu que é preciso emprestar-se aos outros e só dar-se a si mesmo, e que o prefeito e Montaigne sempre tinham sido dois. A ordem é a da carta: primeiro a posse das horas, porque só se dá aos outros, por escolha, o tempo de que se dispõe.", PI)
add("A frase que fecha <i>Do retorno</i> é aparentada com essa ordem, e mais antiga que Sêneca. Píndaro a escreveu no século V a.C., numa ode para Híeron, senhor de Siracusa: <i>torne-se o que você é, depois de aprendê-lo</i>. O conselho é ser nos atos o que você aprendeu que é, em vez da imagem que os outros oferecem. Nietzsche fez dela uma divisa sem as duas últimas palavras, e são elas que interessam aqui. O que se é se aprende; o que é seu por direito se recupera aprendendo. Cada ciclo é uma volta desse aprendizado, e o dia zero é onde ele recomeça.", PI)


sec("Abrace todas as horas")
add("A segunda parte vem do meio da carta e começa por uma concessão: faça o que você me diz que faz, abrace todas as horas. Lucílio já tinha começado; a carta manda que ele continue. O verbo latino, <i>complecti</i>, é o do abraço: cingir com os dois braços, segurar uma coisa inteira. Pede que nenhuma hora seja vivida pela metade, com uma parte de você nela e outra em outro lugar. Na hora da obra, a frase de <i>Da assentada</i> diz o mesmo: <i>Isto, até acabar.</i>", PI)
add("Quem tenta pela metade segura a hora com um braço e guarda o outro livre para a saída.", PI)
add("Em 1843, Kierkegaard publicou <i>Ou-ou</i>, assinado por um editor fictício. O primeiro volume reúne os papéis de A, um esteta decidido a não se prender a nada. Ele aconselha a nunca casar, a não fazer amizade que obrigue, a não aceitar cargo, e a variar o modo de gozar o que está à mão, como o lavrador que alterna as culturas no mesmo campo. Resume o seu estado num aforismo: case-se, e você se arrependerá; não se case, e também se arrependerá. Tudo continua possível para ele, porque não escolheu nada.", PI)
add("O segundo volume são as cartas de um juiz, o assessor Wilhelm, homem casado e de ofício. Ele diz a A que o seu mal está em não escolher. Quem escolhe com seriedade é corrigido por aquilo que escolheu; quem não escolhe não é corrigido por nada. Ao escolher, um homem escolhe a si mesmo e ganha uma forma que não tinha. Na hora da obra, A é a parte de você que deixa todas as saídas abertas para não arriscar nenhuma. O juiz é a parte que escolhe a obra de hoje e aceita ser corrigida por ela.", PI)
add("Quatro anos depois, em <i>Pureza de coração é querer uma só coisa</i>, Kierkegaard deu a isso um nome antigo: o ânimo dobre, de quem quer o bem e, ao lado, mais alguma coisa. Abraçar a hora é querer nela a obra sem querer, ao lado da obra, a saída honrosa.", PI)
add("Ninguém abraça todas as horas, e Sêneca o sabia. No fim da carta, ele imagina Lucílio perguntando como faz ele, que dá esses conselhos. Responde que não pode dizer que não perde tempo; pode dizer o que perde, por que razão e de que maneira, como quem presta contas da própria pobreza. A carta junta à ordem uma contabilidade: saber, de cada hora perdida, onde e como se perdeu. A marca de cada noite faz essa contabilidade. Quando a hora escapar, a ordem vale para a hora seguinte, e Marco Aurélio a dizia a si mesmo numa palavra: <i>volte</i>.", PI)


sec("Lançar mão do hoje")
add("A frase completa diz: assim você dependerá menos do amanhã, se lançar mão do hoje. No latim, <i>sic fiet ut minus ex crastino pendeas, si hodierno manum inieceris</i>, as duas imagens são do corpo. <i>Pendere</i> é estar pendurado; quem depende do amanhã está preso a um gancho que ainda não existe. <i>Manum inicere</i> é pôr a mão numa coisa e agarrá-la. Nos tribunais, a expressão nomeava o gesto do credor que prendia pelo braço quem lhe devia. Sêneca volta à língua da posse com que abriu a carta: o hoje é a parte do tempo que se pode segurar.", PI)
add("Logo vem a frase mais curta da carta: enquanto se adia, a vida passa. A carta fecha com um provérbio antigo, que Hesíodo já tinha escrito: é tarde para poupar quando se chegou ao fundo do vaso, porque no fundo fica o pior. Quem guarda para o fim da semana, do mês ou da vida o que hoje podia fazer guarda para depois a parte do tempo que menos vale. Entre as duas metades do estribilho, a carta fala da morte, e dessa página vem a linha com que você abre cada manhã.", PI)

add("O adiamento tem um parente no espaço, e a tradição monástica lhe deu nome. Bento de Núrsia, no primeiro capítulo da <i>Regra</i>, chama a pior espécie de monges de giróvagos. Passam a vida de província em província, hóspedes por três ou quatro dias em cada mosteiro, sempre a caminho, sem uma regra e sem um abade que os corrija. Quem adia faz o mesmo no tempo: muda de dia antes que o dia possa dar alguma coisa.", PI)
add("Contra isso, a Regra pôs na entrada do mosteiro uma promessa. Quem chega passa um ano em provação, e a Regra lhe é lida inteira três vezes: eis a lei sob a qual queres militar; se a podes guardar, entra; se não podes, vai-te em liberdade. No fim do ano, se ficar, ele promete diante de todos estabilidade, conversão dos costumes e obediência. Escreve a promessa de próprio punho e a põe sobre o altar.", PI)
add("A estabilidade vem antes da conversão. O monge promete ficar naquela comunidade, com aqueles irmãos, e é por ficar que a conversão se torna possível. Num lugar de onde não se sai, os defeitos são trabalhados ali mesmo, diante de quem os viu ontem. O dia, neste livro, é um lugar desses. Quem lança mão dele não deixa para amanhã o que nele correu mal: olha para isso na noite do mesmo dia, escreve, e decide a primeira tarefa.", PI)
add("Gabriel Marcel, no século XX, separou duas coisas. A constância é a persistência no mesmo, que se mantém por teimosia ou por inércia, com a cabeça em outro lugar. A <i>fidelidade criadora</i> se reinventa por dentro, porque aquilo a que se é fiel muda, e quem é fiel muda também. Lançar mão do hoje pede a segunda. Cada manhã a mão pousa num dia que não é o de ontem, e a escolha se faz de novo, nas condições desse dia.", PI)
add("Sêneca manda depender menos do amanhã. O longe é pensado no dia zero, na visão e no alvo, e relido nas passagens. Nada que se pode fazer hoje fica pendurado nele.", PI)
add("Há uma forma discreta de depender do amanhã: acreditar que falta mais informação, mais método, mais um livro, e adiar o começo para o dia em que a falta for suprida. Heráclito, em Éfeso, por volta de 500 a.C., deixou duas frases sobre isso. Uma é áspera: saber muitas coisas não ensina a ter inteligência, senão teria ensinado Hesíodo e Pitágoras. A outra é sobre a alma: você não encontraria os limites dela, ainda que percorresse todos os caminhos, tão profundo é o seu <i>logos</i>, a medida que a ordena.", PI)
add("A primeira recusa a largura como substituto. A segunda diz que o fundo não se esgota. O que você tem nas mãos esta manhã, a mesma página, o mesmo gesto, a mesma pessoa, tem fundo para o dia inteiro. Você não precisa esperar o método seguinte para começar a descer nele.", PI)
add("Na capa deste livro, Nietzsche parece puxar para o outro lado: o seu verdadeiro ser está imensamente acima de você. Acima quer dizer adiante, e parece pôr tudo num amanhã. Mas Nietzsche recusa a escavação em si mesmo como caminho, e Sêneca pede que você agarre o dia e trabalhe nele. Quem desce assim na obra vai formando, dia a dia, o que Nietzsche punha acima. Agostinho disse de Deus que Ele lhe era mais íntimo que o seu íntimo e mais alto que o seu mais alto. Para ele, o fundo e o alto se encontravam em Deus, e este livro não o tem. No caderno, o que está acima de você é a visão, e o que aproxima você dela é a linha da manhã de hoje.", PI)
# ===================== DA LUZ ANTIGA =====================
st.append(PageBreak()); sp(30)
add("Por último", LIV)
QUANDO["Da luz antiga"] = "numa noite limpa, quando quiser"
add("Da luz antiga", LT); sumario(st[-1], 0, "Da luz antiga")
add("<i>“Young hearts, be free tonight.<br/>Time is on your side.”</i>", ParagraphStyle('lz1', parent=PC, fontSize=12, spaceAfter=2))
add("Rod Stewart, <i>Young Turks</i> (1981)", ParagraphStyle('lz2', parent=EPA, spaceAfter=10))
add("<i>“Why can't we give love one more chance?”</i>", ParagraphStyle('lz3', parent=PC, fontSize=12, spaceAfter=2))
add("Queen e David Bowie, <i>Under Pressure</i> (1981)", ParagraphStyle('lz4', parent=EPA, spaceAfter=20))
add("Uma última coisa, que não vem de filósofo nem de general. Numa noite limpa, longe das luzes da cidade, olhe para cima. Tudo o que você vê ali é passado. A luz da Lua saiu dela há pouco mais de um segundo. A do Sol, que você não pode olhar, levou oito minutos para chegar. Sírius, a estrela mais brilhante do céu da noite, aparece como era há oito anos e meio. Betelgeuse, o ombro vermelho de Órion, aparece como era há uns seiscentos anos, mais ou menos quando Gutenberg imprimia os primeiros livros. E a mancha pálida de Andrômeda, a coisa mais distante que o olho nu alcança, mostra uma luz que partiu há dois milhões e meio de anos, antes que existisse qualquer pessoa para vê-la.", PI)
add("Os astrônomos convivem com isso sem susto. Betelgeuse é uma estrela velha e enorme, e um dia vai explodir. Se já explodiu, a notícia ainda está a caminho, e por séculos o céu vai continuar mostrando o ombro de Órion inteiro, vermelho, como se nada tivesse acontecido. O céu que você vê é um arquivo, e cada ponto dele é uma carta escrita há muito tempo, que só agora chegou.", PI)
add("As pessoas à sua volta veem você assim. Veem a luz que você soltou há meses ou anos: o que você fazia, o que prometia e não cumpria, o homem da anti-visão. E você se vê do mesmo jeito. Quando se olha no espelho, ou quando pensa em quem é, o que aparece é o acúmulo de atos antigos, que continuam chegando muito depois de você ter parado de fazê-los. Já o que você faz hoje, a da vez feita na ocasião que mais pesou, o traço desta noite, a obra que acabou, é luz que acabou de partir. Ninguém a vê ainda. Nem você.", PI)
add("Por isso as primeiras semanas parecem não dar em nada. Você faz o gesto, marca o traço, e o espelho mostra o mesmo rosto, os outros chamam você pelo nome antigo, e a voz antiga aproveita para dizer que nada mudou. O método não falhou. Entre o ato e o momento em que ele é visto há uma distância, e a distância tem o seu tempo, que não se apressa. Quem desiste nessas semanas desiste com a luz no meio do caminho.", PI)
add("E um dia, numa noite comum, ela chega. Alguém diz sobre você uma coisa que você nunca tinha ouvido. Ou você mesmo, diante de uma ocasião que antes o derrubava, percebe que o gesto já foi feito, sem o breviário, sem a pergunta, sem esforço. Neste livro isso tem nome, e você o escreve na coluna das marcas: <i>chegou</i>. A palavra estava ali desde o dia zero, antes de você saber por que tinha sido escolhida.", PI)
add("A luz antiga também continua chegando por um tempo. Numa noite qualquer, depois de meses de traços, a vontade velha aparece inteira, nítida, como o ombro de Órion no céu, e parece dizer que você continua o mesmo. Ela é luz de alguém que já não está lá. Não discuta com ela: faça o gesto, marque a noite como ela foi, e deixe essa luz terminar de passar.", PI)
add("Os astrônomos ensinam mais uma coisa, sem querer. Apontam o instrumento, medem a luz que vem, anotam no caderno e voltam na noite seguinte, durante anos, porque sabem que o céu só mostra o que mudou para quem continua olhando. É o que você faz com as folhas de marcas. A estrela não precisa de você para existir; a sua obra, sim.", PI)
add("Em 1981, Rod Stewart gravou <i>Young Turks</i>, a história de Billy e Patti, dois jovens que vão embora numa noite, sem esperar que alguém os ache prontos. O refrão, no alto deste capítulo, diz: corações jovens, sejam livres esta noite; o tempo está do seu lado. A segunda metade soa como promessa de tempo de sobra. A lição está na ordem das frases: o tempo fica do seu lado depois do <i>esta noite</i>. Para quem espera estar pronto, o tempo é o rio de Horácio, que nunca termina de passar; para quem sai, cai e sai de novo, cada dia que vem traz uma luz que já está a caminho. No mesmo ano, Queen e David Bowie fecharam <i>Under Pressure</i> com a pergunta que está ao lado dela no alto deste capítulo: por que não dar ao amor mais uma chance? Este livro fez essa pergunta em <i>Da outra chance</i>: debaixo de pressão, depois da queda, a chance seguinte é a única que você ainda pode dar.", PI)
add("Oito anos antes, o Pink Floyd tinha posto em <i>Time</i> o mesmo céu visto do outro lado: o sol que nasce igual, o dia que passa igual, e um homem que um dia levanta os olhos e encontra dez anos para trás. Que essa seja a última voz do livro, e que você a ouça hoje, enquanto ainda é de noite e a luz acabou de partir.", PI)
add("<i>“And then one day you find ten years have got behind you.<br/>No one told you when to run, you missed the starting gun.<br/>[...] The sun is the same in a relative way, but you’re older.”</i>", ParagraphStyle('lz5', parent=PC, fontSize=11, spaceBefore=6, spaceAfter=2))
add("Pink Floyd, <i>Time</i> (1973)", ParagraphStyle('lz6', parent=EPA, spaceAfter=12))
add("Feche o livro. Lá fora, agora mesmo, há luz partindo de você em direção a quem você vai ser, e ela já está a caminho.", PI)
fleur()
# O fecho, de Pink Floyd ao ornamento, fica junto, sem linha órfã no alto da página.
st[-5:] = [KeepTogether(st[-5:])]
sp(18)
add("As <i>Doze Lições</i> são de M Castro. O prólogo adapta ideias de Dan Koe, <i>How to fix your entire life in 1 day</i>; confira no original. As citações do restante do livro foram feitas a partir de traduções, e as que vêm sem aspas são paráfrases; confira-as nas suas edições.", NOTE)
add("F O N T E S", LBL); sumario(st[-1], 0, "Fontes")
FONTES = [
 ['Abu Dawud, <i>Sunan</i> (<i>Da técnica</i>, <i>Para conter a raiva</i>)', 'Santo Agostinho, <i>Confissões</i> (Livro IV, <i>Da decisão</i>; <i>Comentário ao estribilho</i>, <i>Lançar mão do hoje</i>)', 'Albulescu e colegas (2022), sobre as pausas curtas', 'Roald Amundsen, <i>O polo sul</i> (Livro I)', 'Aristóteles, <i>Ética a Nicômaco</i> e <i>Do céu</i> (Livro I; Interlúdio, <i>Do costume e do caráter</i>)', 'Arriano, <i>Anábase de Alexandre</i> (<i>Da técnica</i>, <i>Para resistir a um impulso</i>)', 'Carl Philipp Emanuel Bach e Johann Friedrich Agricola, obituário de Johann Sebastian Bach (Livro III, <i>Da crítica</i>)', 'M. A. Balban e colegas (2023), sobre o suspiro duplo e o humor', 'Bamberg e Moreau (2025), sobre o jejum e a cognição', 'Honoré de Balzac, <i>Tratado dos excitantes modernos</i> (Livro II, <i>Do bloco de obra</i>)', 'A. Bandura e D. H. Schunk (1981), sobre metas próximas e metas distantes', 'Charles Baudelaire, <i>Diários íntimos</i> (Livro I, <i>Da ordem das linhas</i>)', 'Roy Baumeister e colegas (1998), sobre o esgotamento do ego', 'Max Beerbohm, <i>O hipócrita feliz</i> (<i>Da máscara</i>)', 'São Bento, <i>Regra</i> (Livro II, <i>Da lei</i>; <i>Comentário ao estribilho</i>, <i>Lançar mão do hoje</i>)', 'Bíblia: Evangelhos de Mateus (6:34), Lucas e João (<i>Da outra chance</i>; Livro II, <i>Do dia</i>; Livro III, <i>Da discrição</i>)', 'Maine de Biran, <i>Influência do hábito sobre a faculdade de pensar</i> (Interlúdio, <i>Da vontade que desceu</i>)', 'Biwer e colegas (2023), sobre pausas marcadas e pausas livres', 'James Boswell, <i>Vida de Samuel Johnson</i> (Livro IV, <i>Da decisão</i>)', 'Sarah Bowen e G. Alan Marlatt (2009), sobre observar a vontade de fumar', 'Juliana Breines e Serena Chen (2012), sobre a autocompaixão depois do fracasso', 'A. W. Brooks (2014), sobre chamar o nervosismo de animação', 'Buijze e colegas (2016), sobre a água fria no fim do banho', 'Albert Camus, <i>O mito de Sísifo</i> (<i>Do pêndulo</i>, <i>Da descida</i>)', 'João Cassiano, <i>Instituições</i> (Livro I)', 'N. J. Cepeda e colegas (2006), sobre espaçar as revisões', 'Thomas Chalmers, <i>O poder expulsivo de uma nova afeição</i> (Livro IV, <i>Da paixão contrária</i>)', 'Yu-Kai Chang e colegas (2012), sobre o exercício e a cognição', 'Winston Churchill, <i>A pintura como passatempo</i> (<i>Da técnica</i>, <i>Para limpar a mente</i>)', 'Cícero, <i>Academica</i>, <i>Do orador</i>, <i>Dos deveres</i> e <i>Tusculanas</i> (<i>Da máscara</i>, <i>Das quatro máscaras</i>, <i>Do papel</i>; <i>Da técnica</i>, <i>Para tirar o nervosismo</i>; Livro II, <i>Da lei</i>; Interlúdio, <i>Do mesmo e de si</i>)', 'Ciria e colegas (2023), sobre o treino físico e a cognição', 'Carl von Clausewitz, <i>Da guerra</i> (<i>Da técnica</i>, <i>Para não sair da obra</i>)', 'Samuel Taylor Coleridge, <i>Biographia Literaria</i> (Livro II, <i>Da lei</i>)', 'Mihaly Csikszentmihalyi, <i>Flow</i> (1990; <i>Da assentada</i>, <i>Da atenção</i>)', 'Ève Curie, <i>Madame Curie</i> (<i>Da técnica</i>, <i>Para aguentar um golpe</i>)'],
 ['Charles Darwin, <i>Autobiografia</i> e cartas (Livro III, <i>Da mente móvel</i>; Livro I)', 'René Descartes, <i>Discurso do método</i> (<i>Da assentada</i>, <i>Da frase</i>, <i>Da floresta</i>; Livro II, <i>Da lei</i>)', '<i>Ditos dos Padres do Deserto</i> (Livro III, <i>Da ordem</i>)', 'Denis Diderot, <i>Paradoxo do comediante</i> (<i>Da máscara</i>, <i>Do se mágico</i>)', 'Diógenes Laércio, <i>Vidas</i> (Livro III; <i>Da técnica</i>)', 'Dōgen, <i>Instruções ao cozinheiro</i> e <i>Genjōkōan</i> (<i>Da assentada</i>, <i>Do cozinheiro</i>)', 'Élio Donato, <i>Vida de Virgílio</i> (Livro I)', 'Fiódor Dostoiévski, <i>Notas de inverno sobre impressões de verão</i> (Livro IV, <i>Do modo</i>)', 'Frederick Douglass, <i>Narrativa da vida</i> (<i>Da técnica</i>, <i>Para entrar e falar</i>)', 'Maxime Du Camp, <i>Recordações literárias</i> (<i>Do pêndulo</i>, <i>Do fastio</i>)', 'John Dunlosky e colegas (2013), sobre as técnicas de estudo', 'Kevin Dutton, <i>A sabedoria dos psicopatas</i> (<i>Da máscara</i>, <i>Do mostrador</i>)', 'Hermann Ebbinghaus, <i>Sobre a memória</i> (Livro III, <i>Das pessoas</i>)', 'Epicteto, <i>Manual</i> (8 e 46) e <i>Discursos</i> (<i>Da máscara</i>, <i>Do papel</i>; Livro II, <i>Da lei</i>)', 'Erasmo, <i>De copia</i> (Livro III, <i>Do aprender</i>)', 'K. Anders Ericsson, Ralf Krampe e Clemens Tesch-Römer (1993), sobre a prática deliberada', 'Espinosa, <i>Ética</i> (Livro IV, <i>Da paixão contrária</i>)', 'Evágrio Pôntico, <i>Praktikos</i> (12, 27, 28 e 29; <i>Do pêndulo</i>, <i>Do demônio do meio-dia</i>; Livro I)', 'Farias e colegas (2020), sobre os efeitos adversos da meditação', 'Gustave Flaubert, cartas a Louise Colet (<i>Do pêndulo</i>, <i>Do fastio</i>)', 'John Forster, <i>Vida de Charles Dickens</i> (<i>Da assentada</i>, <i>Da sessão</i>)', 'Benjamin Franklin, <i>Autobiografia</i> (<i>Da técnica</i>, <i>Para decidir</i>; Livro II, <i>Da lei</i>)', 'Frattaroli (2006), sobre a escrita do que perturba', 'Sigmund Freud e Josef Breuer, <i>Estudos sobre a histeria</i> (Livro III, <i>Das pessoas</i>)', 'Friese e colegas (2017), sobre o treino do autocontrole', 'Carl Friedrich Gauss, diário matemático (Livro III, <i>Da discrição</i>)', 'Aulo Gélio, <i>Noites áticas</i> (Livro I)', 'Edward Gibbon, <i>Memórias</i> (Livro III, <i>Do terminar</i>)', 'James Gleick, <i>Genius</i> (<i>Da técnica</i>)', 'Goethe, <i>Xênias mansas</i> (Livro III, <i>Da prática deliberada</i>; Lição I)', 'Peter Gollwitzer e Paschal Sheeran (2006), sobre os planos <i>se... então</i>', 'Peter Gollwitzer e colegas (2009), sobre as intenções tornadas públicas', 'Robert Greene, <i>Maestria</i> (Livro III)'],
 ['Pierre Hadot, <i>Exercícios espirituais e filosofia antiga</i> e <i>A cidadela interior</i> (<i>Proêmio</i>)', 'Martin Hagger e colegas (2016), replicação do esgotamento do ego', 'G. H. Hardy, <i>Ramanujan</i> (Livro II, <i>Da companhia</i>)', 'Robert Hare, escala de avaliação da psicopatia', 'B. Harkin e colegas (2016), sobre o registro do progresso', 'E. Harmon-Jones e C. K. Peterson (2009), sobre a postura reclinada diante do insulto', 'Steven Hayes, Kirk Strosahl e Kelly Wilson (1999), sobre a terapia de aceitação e compromisso', 'Piet Hein, <i>Grooks</i> (<i>Da técnica</i>, <i>Para decidir</i>)', 'Ernest Hemingway, <i>Paris é uma festa</i> (<i>Da técnica</i>, <i>Para começar</i>; Livro I)', 'Heráclito, fragmentos (<i>Comentário ao estribilho</i>, <i>Lançar mão do hoje</i>)', 'Abraham Joshua Heschel, <i>The Sabbath</i> (Livro II, <i>Do descanso</i>)', 'Hipócrates, <i>Aforismos</i> (Livro V)', 'Katsushika Hokusai, posfácio das <i>Cem vistas do monte Fuji</i> (<i>Do retorno</i>)', 'Homero, <i>Odisseia</i> (Livro IV, <i>Do modo</i>; Livro II, <i>Da lei</i>)', 'Horácio, <i>Epístolas</i> e <i>Arte poética</i> (Livro I; Livro III, <i>Da crítica</i>)', 'Adèle Hugo, <i>Victor Hugo raconté par un témoin de sa vie</i> (Livro IV, <i>Do modo</i>)', 'David Hume, <i>Tratado da natureza humana</i> e <i>Investigação sobre o entendimento humano</i> (Interlúdio, <i>Do feixe</i>)', 'Humiston e colegas (2019), sobre o descanso quieto depois de aprender', 'William James, <i>The Energies of Men</i> (1907) e <i>O evangelho do relaxamento</i> (1899; <i>Da máscara</i>, <i>Do corpo primeiro</i>)', 'William James, <i>Princípios de psicologia</i> e <i>As variedades da experiência religiosa</i> (Interlúdio, <i>Do que se conta</i>; <i>Da técnica</i>, <i>No instante em que você percebe</i>)', 'Veronika Job, Carol Dweck e Gregory Walton (2010), sobre as crenças acerca da força de vontade', 'Henry Bence Jones, <i>Vida e cartas de Faraday</i> (Livro III, <i>Do aprender</i>)', 'Franz Kafka, <i>Diários</i> (<i>Da assentada</i>)', 'Johannes Kepler, <i>Astronomia nova</i> (Livro V, <i>Da firmeza e da rigidez</i>)', 'Khalsa e colegas (2003), sobre a luz e o relógio interno', 'Søren Kierkegaard, <i>Ou-ou</i>, <i>A repetição</i> e <i>Pureza de coração é querer uma só coisa</i> (<i>Da assentada</i>, <i>Do ânimo dobre</i>; <i>Comentário ao estribilho</i>, <i>Abrace todas as horas</i>)', 'Avraham Kluger e Angelo DeNisi (1996), sobre o efeito do retorno no desempenho', 'Dan Koe, <i>How to fix your entire life in 1 day</i> (Prólogo)', 'Ethan Kross e colegas (2014), sobre pensar em si pelo próprio nome'],
 ['Phillippa Lally e colegas (2010), sobre a formação de hábitos', 'Sophie Leroy e Theresa Glomb (2018), sobre o plano de retomada depois da interrupção', 'Levin e colegas (2012), sobre a desfusão', 'M. Levitt (2021), sobre deixar uma moeda decidir', 'Kurt Lewin, sobre a tensão das intenções por cumprir', 'Georg Christoph Lichtenberg, <i>Sudelbücher</i> (<i>Da técnica</i>, <i>Para pensar com clareza</i>)', 'Lim e Dinges (2010), sobre a privação de sono e a atenção', 'Abraham Lincoln, carta a George Meade (1863; Livro III, <i>Da serenidade</i>)', 'Longmore e Worrell (2007), sobre o registro de pensamentos', 'Inácio de Loyola, <i>Exercícios espirituais</i> e <i>Autobiografia</i> (Prólogo, <i>Como se escreve a visão</i>; Livro III, <i>Do amor ao destino</i>; Livro V, <i>Do escrúpulo</i>)', 'Alasdair MacIntyre, <i>Depois da virtude</i> (Interlúdio, <i>Da vida como história</i>)', 'Brooke Macnamara, David Hambrick e Frederick Oswald (2014), sobre o peso da prática deliberada', 'Nicolau Maquiavel, carta a Francesco Vettori (1513; Livro II, <i>Da companhia</i>)', 'Gabriel Marcel, <i>Fidelidade criadora</i> (<i>Comentário ao estribilho</i>, <i>Lançar mão do hoje</i>)', 'Marco Aurélio, <i>Meditações</i> (V, 20; Livro III; Livro II, <i>Do dia</i>)', 'G. Alan Marlatt e colegas, sobre a prevenção da recaída', 'E. J. Masicampo e Roy Baumeister (2011), sobre os objetivos por cumprir', 'Henri Matisse, <i>Jazz</i> (Livro II, <i>Do piso</i>)', 'Michelangelo, sonetos (Livro I)', 'John Stuart Mill, <i>Autobiografia</i> e <i>Sobre a liberdade</i> (Livro V, <i>Do escrúpulo</i>)', 'John Milton, sonetos (Livro III, <i>Do amor ao destino</i>)', 'Walter Mischel, estudos dos anos 1970 sobre a espera das crianças', 'D. Mischkowski, E. Kross e B. J. Bushman (2012), sobre olhar a provocação de longe', 'Mishná, tratado <i>Yoma</i> (Livro II, <i>Da lei</i>)', 'Stephen Monsell (2003), sobre a alternância de tarefas', 'Michel de Montaigne, <i>Ensaios</i> (Interlúdio, <i>Da mulher e do bezerro</i>; <i>Da técnica</i>, <i>Diante do perigo</i>; Livro II, <i>Da companhia</i>; <i>Comentário ao estribilho</i>, <i>Reivindique-se para si</i>)', 'Hannah More, sobre Samuel Johnson', 'Leopold Mozart, cartas (<i>Da técnica</i>, <i>Para memorizar</i>)', 'Miyamoto Musashi, <i>O livro dos cinco anéis</i> (<i>Da técnica</i>)', 'Musônio Rufo, <i>Diatribes</i> (<i>Do primeiro dia</i>, <i>Da medida</i>; <i>Manual operacional</i>, <i>Das ações</i>)', 'Fridtjof Nansen, <i>A primeira travessia da Groenlândia</i> (<i>Da técnica</i>, <i>No instante em que você percebe</i>)', 'David Neal, Wendy Wood e colegas (2011), sobre as pipocas do cinema', 'Humphrey Newton, cartas a John Conduitt (<i>Da assentada</i>, <i>Da sessão</i>)', 'Raymond Nickerson (1998), sobre o viés de confirmação', 'Friedrich Nietzsche, <i>Assim falou Zaratustra</i>, <i>Além do bem e do mal</i>, <i>Ecce Homo</i>, <i>Schopenhauer como educador</i> e <i>A gaia ciência</i> (<i>Da máscara</i>, <i>Do estilo</i>; Livro III)'],
 ['Blaise Pascal, <i>Pensamentos</i> (Livro I)', 'J. W. Pennebaker e S. K. Beall (1986), sobre a escrita expressiva', 'Josef Pieper, <i>Muße und Kult</i> (Livro II, <i>Do descanso</i>)', 'Píndaro, <i>Píticas</i> (<i>Do retorno</i>; <i>Comentário ao estribilho</i>, <i>Reivindique-se para si</i>)', 'Platão, <i>Apologia de Sócrates</i>, <i>Górgias</i>, <i>Banquete</i> e <i>República</i> (Livro III; Prólogo, <i>O roteiro</i>)', 'Plínio, o Velho, <i>História natural</i> (Livro II, <i>Do dia</i>)', 'Plutarco, <i>Moralia</i> (Livro III, <i>Das pessoas</i> e <i>Da crítica</i>)', 'Plutarco, <i>Vidas de Demóstenes e de Catão, o Jovem</i> (<i>Da técnica</i>, <i>Para começar</i>, <i>Para atravessar o ridículo</i>)', 'Henri Poincaré, <i>Ciência e método</i> (Livro I)', 'George Pólya, <i>A arte de resolver problemas</i> (Livro I)', 'Quintiliano, <i>Instituição oratória</i> (<i>Da técnica</i>, <i>Para memorizar</i>)', 'B. Rasch e J. Born (2013), sobre o sono e a memória', 'Félix Ravaisson, <i>Do hábito</i> (Interlúdio, <i>Da vontade que desceu</i>)', '<i>Relatos de um peregrino russo</i>, de autor anônimo (<i>Comentário ao estribilho</i>)', 'Charles Renouvier, <i>Ensaios</i> (Livro V, <i>Do escrúpulo</i>)', 'Paul Ricoeur, <i>O si-mesmo como outro</i> (Interlúdio, <i>Do mesmo e de si</i>)', 'Rainer Maria Rilke, <i>Cartas a um jovem poeta</i> e <i>Torso arcaico de Apolo</i> (Livro III, <i>Da vocação</i>)', 'Henry Roediger e Jeffrey Karpicke (2006), sobre a recordação como estudo', 'Christopher Rowland (2014), sobre testar-se em vez de reler', 'L. Rozenblit e F. Keil (2002), sobre a ilusão de entender um mecanismo', 'Jean-Paul Sartre, <i>O ser e o nada</i> (<i>Da máscara</i>)', 'Arthur Schopenhauer, <i>Parerga e Paralipomena</i> (Lição VI; <i>Da máscara</i>, <i>Do estilo</i>)', 'Sêneca, <i>Cartas a Lucílio</i> (1, 18 e 24), <i>Da ira</i>, <i>Dos benefícios</i>, <i>Da tranquilidade da alma</i> e <i>Da brevidade da vida</i> (estribilho; Livro III)', 'P. Sheeran, O. Listrom e P. M. Gollwitzer (2025), sobre os planos <i>se... então</i>', 'Joe Simpson, <i>Tocando o vazio</i> (<i>Da técnica</i>, <i>Para continuar quando o cansaço bate</i>)', 'John Snow, <i>Sobre o modo de transmissão do cólera</i> (Livro V, <i>Das quatro quedas</i>)', 'Souman e colegas (2018), sobre a luz e o estado de alerta', 'Konstantin Stanislávski, <i>A preparação do ator</i> (<i>Da máscara</i>, <i>Do se mágico</i>)', 'Stevenson e colegas (2018), sobre a atenção depois de um lugar natural', 'Suetônio, <i>Vidas dos doze Césares</i> (<i>Da técnica</i>, <i>Para entrar e falar</i>)', 'M. J. Sullivan e colegas (1995), sobre o hábito de ampliar e ruminar a dor', 'Sumantry e Stewart (2021), sobre a meditação e o controle da atenção', 'Sun Tzu, <i>A arte da guerra</i> (Livro I)'],
 ['Piotr Tchaikóvski, cartas a Nadejda von Meck (Livro I)', 'Henry David Thoreau, <i>Walden</i> (Livro III, <i>Da pobreza voluntária</i>)', 'Guilherme de Tocco, <i>Vida de santo Tomás de Aquino</i> (Livro III, <i>Da absorção</i>)', 'Liev Tolstói, <i>Diários</i> (Livro IV, <i>Da queda</i>)', 'Anthony Trollope, <i>Autobiografia</i> (Livro I)', 'Hans Van Dongen e colegas (2003), sobre o sono curto e a atenção', 'Giorgio Vasari, <i>Vidas dos artistas</i> (Livro I)', '<i>Versos de ouro</i>, da tradição pitagórica (Livro II, <i>Do dia</i>)', 'Wang, Wang e Gai (2021), sobre o desejo e o obstáculo', 'T. W. Watts, G. J. Duncan e H. Quan (2018), sobre a réplica dos estudos da espera das crianças', 'Marianne Weber, <i>Max Weber: uma biografia</i> (Livro II, <i>Do descanso</i>)', 'Daniel Wegner e colegas (1987), sobre a supressão do pensamento', 'Simone Weil, <i>Reflexões sobre o bom uso dos estudos escolares em vista do amor de Deus</i> (<i>Da assentada</i>, <i>Da atenção</i>; Lição III)', 'Rachel White e colegas (2017), sobre o efeito Batman', 'T. D. Wilson e colegas (2014), sobre ficar a sós com os pensamentos', 'T. D. Wilson e colegas (1993), sobre listar razões antes de uma escolha de gosto', 'Wendy Wood e David Neal (2007), sobre o hábito e as pistas do contexto', 'William Wordsworth, poemas (Livro V, <i>Do escrúpulo</i>)', 'Xenofonte, <i>Memoráveis</i> (<i>Da técnica</i>, <i>Para aguentar um golpe</i>; Livro III, <i>Do corpo</i>)', 'Bluma Zeigarnik (1927), sobre as tarefas interrompidas'],
]
FONTES_ST = ParagraphStyle('fontes', parent=NOTE, fontSize=8.6, leading=10.8, spaceAfter=3)
for grupo in FONTES: add("; ".join(grupo) + ".", FONTES_ST)
# A lista cabe numa página; partida, deixava duas ou três linhas sozinhas na seguinte.
fontes_blk = st[-len(FONTES) - 1:]
del st[-len(FONTES) - 1:]
st.append(KeepTogether(fontes_blk))
# ===================== DO CADERNO, PÁGINA A PÁGINA =====================
st.append(PageBreak()); sp(30)
add("Do caderno, página a página", LT); sumario(st[-1], 0, "Do caderno, página a página")
add("Estas páginas são de consulta. Elas dizem onde fica cada coisa no caderno e como fica escrita a página de um dia comum.", PI)
CD_P = ParagraphStyle('cd1', parent=BODY, fontSize=10.5, leading=13.5, alignment=TA_LEFT, spaceBefore=0, spaceAfter=0)
cad = [("1", "A folha do dia zero.", "Na noite do dia zero. É relida em cada passagem."),
       ("2", "A página <i>Do homem</i>.", "Fica em branco até a primeira noite de passagem, em que você a copia à mão."),
       ("3 e 4", "O breviário, frente e verso.", "Na primeira noite de passagem, em cerca de meia hora, ou impresso e colado antes. Até lá, lê-se no livro. É consultado todas as manhãs."),
       ("5 a 34", "As folhas de marcas, uma por mês.", "A primeira na noite do dia zero, com a data dele e o número um; depois, uma linha por noite. Trinta páginas dão para dois anos e meio; se não bastarem, a folha continua num segundo caderno do mesmo ciclo."),
       ("35", "<i>Dias limpos</i>.", "Só se houver corte; até lá, em branco."),
       ("36", "A lista do que está aberto.", "No primeiro dia do exercício do terminar."),
       ("37 e 38", "O capítulo do ciclo.", "No fim do ciclo, com o Interlúdio, no caderno do ciclo que termina."),
       ("39 em diante", "A escrita da manhã do dia zero e a lista da mesa; depois, uma página por dia; a lista das provas quando <i>Da outra chance</i> a pedir.", "Na ordem em que acontecem. O que um capítulo lhe pedir numa página nova se escreve na primeira página livre."),
       ("A última", "A carta da outra chance.", "Na noite seguinte à primeira cruz. É ela que fica no fundo do caderno."), ("No ciclo seguinte", "Um caderno novo, com a mesma organização: cada ciclo tem o seu caderno.", "No novo dia zero, com a nova folha do dia zero na página 1. Na primeira passagem do novo ciclo, você copia de novo o breviário para as páginas 3 e 4 e a página <i>Do homem</i> para a página 2. O caderno do ciclo que terminou é guardado e relido nesse dia zero.")]
rows = [[Paragraph("<font color='#6b6b6b'>Página</font>", CD_P), Paragraph("<font color='#6b6b6b'>O que tem</font>", CD_P), Paragraph("<font color='#6b6b6b'>Quando se escreve</font>", CD_P)]]
for a_, b_, c_ in cad:
    rows.append([Paragraph(f"<i>{a_}</i>", CD_P), Paragraph(b_, CD_P), Paragraph(c_, CD_P)])
tb = Table(rows, colWidths=[2.6*cm, 5.6*cm, 7.4*cm])
tb.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-2),0.3,colors.HexColor('#cccccc')),
                        ('LINEBELOW',(0,0),(-1,0),0.6,GRAY),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
st.append(KeepTogether([Paragraph("O caderno se organiza assim:", PI), Spacer(1, 4), tb])); sp(12)
pd = [("De manhã: a linha da manhã", "<i>Posso morrer hoje. A obra de hoje é o primeiro capítulo do programa, lido e resumido.</i>"),
      ("A primeira tarefa", "<i>O relatório que venho adiando no escritório.</i> Escrita ontem à noite e confirmada agora. A obra só vem à noite: por isso é a coisa evitada do emprego."),
      ("A ocasião que vai pesar", "<i>Oito e meia da noite, ao sentar à mesa da sala.</i>"),
      ("A hora de parar", "<i>Dez da noite.</i>"),
      ("À noite: a linha do dia", "<i>O resumo do primeiro capítulo existe. Alavancas: sim.</i>"),
      ("A linha da queda", "<i>Deixada cair. Onde: o levantar das dez, com sono. Diferente: arrumo às quinze para as dez.</i> Sem queda: <i>nenhuma</i>."),
      ("A primeira tarefa de amanhã", "<i>Responder ao fornecedor a quem devo resposta desde segunda.</i> Escrita depois de percorrida a folha de captura: cada linha passou para amanhã, para um dia marcado, ou foi riscada.")]
rows = [[Paragraph(f"<i>{a_}</i>", CD_P), Paragraph(b_, CD_P)] for a_, b_ in pd]
tb = Table(rows, colWidths=[5.0*cm, 10.6*cm])
tb.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BOX',(0,0),(-1,-1),0.5,INK),('LINEBELOW',(0,0),(-1,-2),0.3,colors.HexColor('#cccccc')),
                        ('LINEBELOW',(0,3),(-1,3),0.6,GRAY),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
                        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
st.append(KeepTogether([Paragraph("Cada dia comum ocupa uma página, ou parte dela: no alto a data, depois o que se escreve de manhã e, embaixo, o que se escreve à noite. A marca vai na linha desse dia, na folha de marcas. Um exemplo, de alguém que trabalha num escritório de dia e estuda à noite:", PI), Spacer(1, 4), tb])); sp(10)
add("Esta página diz onde escrever cada linha; o que cada uma quer dizer está em <i>Do primeiro dia</i>. Um caderno de 200 folhas tem 400 páginas. Tiradas as 38 do começo, a do fundo e as primeiras da página 39, sobram cerca de 350 para os dias, pouco menos de um ano.", PI)
proc("Na página do dia", [
 "Se hoje é dia de piso, escreva <i>hoje, piso</i> no alto, antes da linha da manhã.",
 "Se as páginas do dia acabarem, abra um segundo caderno do mesmo ciclo.",
 "Nele, recopie nas páginas 1 a 4 a folha do dia zero, a página <i>Do homem</i> e o breviário.",
 "Siga no segundo caderno com as páginas do dia.",
 "Deixe o primeiro ao lado, com as folhas de marcas, até que elas também acabem.",
])
proc("Folhas do fim do livro", [
 "Copie à mão no caderno o breviário, a folha de marcas, <i>Dias limpos</i> e a folha do dia zero.",
 "Se preferir, imprima cada folha e cole no caderno.",
 "Não escreva nas folhas do livro.",
 "· Vale sempre que o livro mandar copiar uma delas.",
])
fleur()

# ===================== GLOSSÁRIO =====================
st.append(PageBreak()); sp(30)
add("Glossário", LT); sumario(st[-1], 0, "Glossário")
add("Os nomes do método, em ordem alfabética, cada um com o lugar onde é ensinado por inteiro; um nome que depende de outro aparece no verbete dele. Na dúvida, vale o que esse lugar diz.", PI)
GL_P = ParagraphStyle('gl', parent=CU_P, fontSize=9, leading=10.8)
GLOSS = [
 ("A da vez", "A microação que você está treinando. Há só uma de cada vez.", "Do primeiro dia"),
 ("Alavancas diárias", "Duas ou três ações de todos os dias que fazem avançar a obra em curso; à noite, a linha do dia diz se a de hoje foi feita.", "Prólogo, <i>Da escada</i>"),
 ("As que ficaram", "As microações que já chegaram: continuam todos os dias, nas suas ocasiões, sem marca própria.", "Do primeiro dia"), ("Assentada", "O modo de fazer uma coisa de uma vez, sentado, até estar feita; é o que a frase <i>Isto, até acabar</i> guarda. Não é unidade de tempo.", "Da assentada"), 
 ("Bloco de obra", "Período declarado numa noite de passagem, de quatro a oito semanas, em que a obra passa à frente, com a linha do bloco, as três paredes e uma semana de descarga no fim.", "Do bloco de obra"), ("Breviário", "As duas páginas do fim do livro com as linhas, os exercícios e o corte, numa linha cada; são copiadas nas páginas 3 e 4 do caderno na primeira noite de passagem, ou impressas e coladas.", "Breviário"),
 ("Chegou", "O que você escreve ao lado do traço na noite em que, na ocasião que mais pesou, o gesto veio sem que o caderno precisasse lembrar. Na dúvida, não chegou.", "Do primeiro dia"),
 ("Ciclo", "O caminho pelas treze microações, agrupadas em estações no Livro III, de um dia zero à prova do ciclo: cinco perguntas respondidas por escrito, com as folhas de marcas à frente. Fecha com o capítulo do ciclo, três parágrafos nas páginas 37 e 38 do caderno: o que você foi, o que manteve, o que promete. Dura o que durar.", "Como usar este livro; Livro V, <i>Da prova</i>; Interlúdio"),
 ("Corte", "Deixar um hábito de uma vez, a partir de um dia certo, com uma linha escrita, datada e assinada. No dia do corte você queima as pontes, tudo o que deixava o hábito ao alcance da mão; as horas que ele deixou vazias recebem uma paixão contrária, ocupação maior que ele; e cada dia limpo é contado, casa por casa, na página 35 do caderno.", "Livro IV"),
 ("Cruz", "A marca de quem cedeu, ou fez metade, na ocasião que mais pesou. Na dúvida entre traço e cruz, é cruz.", "Do primeiro dia"),
 ("Dia sagrado", "O dia seguinte a uma cruz: a da vez se cumpre, com o piso se preciso. Não pode ser dia de ócio.", "Livro II, §5"),
 ("Dia zero", "O dia sem trabalho que abre cada ciclo. Nele você escreve a folha do dia zero, na primeira página do caderno, com oito pontos: a anti-visão, a vida que você terá se nada mudar, numa frase sem drama, lida só nas noites de passagem e na onda; a visão, a vida que você quer daqui a três anos, descrita em atos; o domínio; o alvo de um ano, uma só conquista que daqui a doze meses estará feita ou não; a obra em curso; as alavancas diárias; as regras, três a cinco frases começadas por <i>não</i>; e a frase <i>Sou alguém que</i>, completada com três atos. À tarde entra o gesto da ordem; à noite se faz a primeira marca.", "Prólogo; <i>Da primeira marca</i>"),
 ("Domínio", "O campo de trabalho ou de estudo em que você vai até o fundo, escrito numa frase; embaixo dele, o porquê com rosto, a razão concreta que tira você da cama.", "Prólogo, exercício zero"),
 ("Estribilho", "A frase de Sêneca que você diz a cada manhã, uma vez, em voz baixa, e quando o dia vacila.", "Do estribilho"),
 ("Folha de captura", "Folha solta ao lado da obra onde vai, numa linha, o que surge sem pertencer a ela; fora de casa, qualquer papel dobrado que você leva consigo, passado para o caderno à noite. Decide-se à noite, antes da última das três linhas.", "Do primeiro dia"),
 ("Folha de marcas", "A tabela com uma linha por dia e cinco colunas: a data, o número da da vez, a marca, o <i>chegou</i> e as quedas das que ficaram.", "Do primeiro dia"),
 ("Hora de parar e dia de ócio", "A hora, escrita de manhã, depois da qual, nesse dia, não há obra nem culpa; e o dia inteiro sem obra, declarado por escrito na véspera, em que as microações e a marca continuam.", "Livro II, <i>Do descanso</i>"),
 ("Linha da manhã", "<i>Posso morrer hoje. A obra de hoje é ____.</i> Quem está frágil pode escrever <i>O meu tempo é limitado</i>.", "Livro II, <i>Do dia</i>"),
 ("Linhas da noite", "As três que se escrevem toda noite na página do dia, depois da marca, nesta ordem: a linha do dia, o que existe agora que não existia de manhã, com as alavancas feitas ou não; a linha da queda, numa palavra se a hora foi tirada, levada ou deixada cair, onde foi e o que você fará diferente, ou <i>nenhuma</i>; e a primeira tarefa de amanhã, depois de decidida a folha de captura.", "Do primeiro dia; Livro II, <i>Do dia</i>"),
 ("Linhas de pensamento", "Nove frases curtas que você diz por dentro nos instantes em que o dia se decide.", "Livro I"),
 ("Marca", "O sinal de cada noite na folha de marcas, só sobre a da vez: traço, cruz ou ponto.", "Do primeiro dia"),
 ("Máscara", "O rosto de <i>ele</i>, tirado da sua visão: você copia os meios dele, os fins são seus e quem decide é você; a frieza com que você veste a máscara é andaime, e sai de cada entrada onde você já faz o que ele faria sem a pergunta. A pergunta, <i>O que ele faria agora?</i>, é dita na entrada da obra e entre passos; depois de dito <i>Isto</i>, ela se cala até o fim do passo.", "Da máscara"),
 ("Microação", "Um gesto central, curto, na sua ocasião. Alguns exercícios trazem práticas que o servem, mas só o gesto central se marca. No alto de cada exercício, H indica o que se torna hábito, e J, o que pede sempre juízo; no fim, o sinal de consolidação descreve o gesto já maduro e não decide a passagem.", "Do primeiro dia; <i>Da medida</i>"),

 ("Obra", "O trabalho no seu domínio. A obra em curso é o primeiro passo grande na direção do alvo, e deixa um objeto no mundo; a obra de hoje é o pedaço dela que cabe num dia, escrito na linha da manhã.", "Prólogo; Livro II, <i>Do dia</i>"),
 ("Ocasião", "O momento do dia que chama a microação. A que mais pesou decide a marca.", "Do primeiro dia"),
 ("Onda", "A vontade daquilo que você cortou. Sobe e passa; é atravessada com a nona linha.", "Livro I e Livro IV"),
 ("Passagem", "A noite de um <i>chegou</i> e a manhã seguinte, em que a da vez passa a ficar e entra a seguinte. Se o gesto não chega e a voz que traz argumentos contra ele (a resistência que fala) não cede, as quatro provas dizem se ela deve ser atravessada ou se informa; depois delas, a passagem por decisão, declarada por escrito, sem <i>chegou</i>. Só numa passagem se emenda o método, a folha ou o domínio, por escrito e com base nas marcas.", "Do primeiro dia; Livro V; Livro II, §9"),
 ("Pêndulo", "O peso que vem no meio da obra, sem causa, com <i>estou cansado</i>, <i>vale a pena?</i>, <i>tenho de parar</i>; vai e volta. Se fica parado do mesmo lado por semanas, já não é pêndulo.", "Do pêndulo"),
 ("Piso", "O mínimo de cada coisa num dia de piso: febre ou doença que impede sentar à mesa da obra; viagem que tira você de casa antes da hora da obra, ou ocupa o dia em deslocamento; prova, plantão ou compromisso marcado por outro nas horas da obra; alguém da casa doente ou em crise, que precisa de você hoje. Declarado de manhã, por escrito; cumprido o piso do exercício, a marca é traço.", "Livro II, <i>Do piso</i>"),
 ("Ponto", "A marca da noite em que a ocasião da da vez não veio hoje. Não é falha nem mérito, e não separa duas cruzes.", "Do primeiro dia"),
 ("Primeira tarefa", "O primeiro passo da obra de hoje, escolhido na noite anterior, na última das três linhas da noite, e confirmado de manhã.", "Livro II, <i>Do dia</i>"),
 ("Queda", "Uma cruz na da vez, ou ceder numa das que ficaram. Nunca dois dias seguidos; cruz, ponto, cruz contam como seguidas.", "Livro II, §5"),
 ("Sessão", "O tempo sentado na obra, com começo e fim marcados antes de começar: a entrada, a duração, a volta.", "<i>Da assentada</i>, <i>Da sessão</i>"),
 ("Traço", "A marca de quem fez o gesto na ocasião que mais pesou.", "Do primeiro dia"),
]
rows = [[Paragraph("<font color='#6b6b6b'>Termo</font>", GL_P), Paragraph("<font color='#6b6b6b'>O que é, e onde se aprende</font>", GL_P)]]
for a_, b_, c_ in GLOSS:
    rows.append([Paragraph(f"<i>{a_}</i>", GL_P), Paragraph(f"{b_} <font color='#6b6b6b'><i>{c_}</i></font>", GL_P)])
tb = Table(rows, colWidths=[3.3*cm, 12.3*cm], repeatRows=1)
tb.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-2),0.3,colors.HexColor('#cccccc')),
                        ('LINEBELOW',(0,0),(-1,0),0.6,GRAY),('TOPPADDING',(0,0),(-1,-1),1),('BOTTOMPADDING',(0,0),(-1,-1),1)]))
st.append(tb); sp(12)

# ===================== BREVIÁRIO =====================
BR_T = ParagraphStyle('brt', parent=LT, fontSize=20, spaceAfter=4)
BR_N = ParagraphStyle('brn', parent=NOTE, alignment=TA_CENTER, spaceAfter=14)
BR_H = ParagraphStyle('brh', **base, fontSize=11.5, leading=14, spaceBefore=6, spaceAfter=1, keepWithNext=1)
BR_L = ParagraphStyle('brl', fontName='G-I', textColor=INK, fontSize=10.5, leading=13.5, leftIndent=14, spaceAfter=0)
BR_P = ParagraphStyle('brp', **base, fontSize=10.5, leading=13.5, spaceAfter=3)

st.append(PageBreak()); sp(10)
add("Breviário", BR_T); sumario(st[-1], 0, "Breviário")
st.append(KeepTogether([Paragraph(f"<i>“{ESTR.replace('<br/>', ' ', 1)}”</i>", ParagraphStyle('bres', parent=PC, fontSize=11.5, spaceAfter=0)),
                        Paragraph(ESTR_A, ParagraphStyle('bresa', parent=EPA, fontSize=9, leading=11, spaceBefore=1, spaceAfter=4))]))
add("Tudo o que se pratica, em duas páginas. É copiado nas páginas 3 e 4 do caderno na primeira noite de passagem, em cerca de meia hora, ou impresso e colado. Até lá, lê-se aqui.<br/>O tempo: cerca de dez minutos de manhã e dez à noite. Enquanto é a da vez, cada exercício acrescenta à noite uma escrita curta; depois do <i>chegou</i>, fica o gesto, e só a escrita e as práticas que o exercício indica.<br/>À noite, depois da marca, as três linhas: a linha do dia, com as alavancas; a linha da queda, se a hora foi tirada, levada ou deixada cair; a primeira tarefa, com a folha de captura decidida.", BR_N)
ln = [("I","Do começar",["O que deve existir quando eu me levantar?","Qual é o primeiro movimento? Comece."]),
      ("II","Da vontade de parar",["É vontade, não fato. Até o fim deste passo."]),
      ("III","Da dispersão",["Saí. Onde eu estava?"]),
      ("IV","Do impasse",["O que exatamente eu não sei? Qual a menor parte que faço agora?"]),
      ("V","Do fim",["Está feito, ou está quase? O que faço primeiro amanhã?"]),
      ("VI","Da falta de vontade",["Preciso do primeiro movimento. Qual a versão de dois minutos?"]),
      ("VII","Da escolha",["Qual eu evitaria, se pudesse? Essa."]),
      ("VIII","Da estratégia",["O que quero? Qual é o terreno? Qual é o sistema?","Qual o primeiro movimento, e até quando pesquiso?"]),
      ("IX","Da onda",["É a onda. Ela sobe, e passa. O que faço com as mãos agora?"])]
rows = []
for n,t,vs in ln:
    rows.append([Paragraph(f"<font color='#6b6b6b'>{n}</font>", BR_P), Paragraph(f"<b>{t}</b><br/><i>{'<br/>'.join(vs)}</i>", BR_P)])
tb = Table(rows, colWidths=[1.3*cm, 14.3*cm])
tb.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-2),0.3,colors.HexColor('#cccccc')),
                        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
add("AS &nbsp;LINHAS", SEC); st.append(tb)
add("<b>A frase de todas</b>, desde o dia um, logo que a obra começa: <i>Isto, até acabar.</i> <font color='#6b6b6b'>(é entendida por inteiro em <i>Da assentada</i>)</font>", BR_P)
add("<b>A pergunta</b>, desde o dia um, ao escrever a obra de hoje, na entrada e quando a voz antiga falar: <i>O que ele faria agora?</i> Depois de dito <i>Isto</i>, ela se cala até o fim do passo. Você copia os meios dele; os fins são seus, e quem decide é você. <font color='#6b6b6b'>(é entendida por inteiro em <i>Da máscara</i>)</font>", BR_P)

st.append(PageBreak()); sp(10)
add("AS &nbsp;EXERCÍCIOS".replace("AS &nbsp;EXERC","OS &nbsp;EXERC"), SEC)
ex = [("0","Da vocação","","Início do ciclo.","O domínio em uma frase."),
      ("1","Da ordem","H","Sento ou levanto da mesa.","A distração sai. Mesa em ordem."),
      ("2","Do terminar","H","Desejo de abrir algo novo.","Volto ao aberto. Próximo passo. À noite, encerro por escrito o que já não pede nada."),
      ("3","Da absorção","H","Percebi que me dispersei.","Terceira linha. A primeira hora do dia longe das distrações."),
      ("4","Do corpo","H","Cheguei ao treino.","Nada que distraia; a ficha na mão, inteira. No fim, comparo e mudo no máximo uma coisa."),
      ("5","Da prática","H","Começo a obra no domínio.","A parte mais difícil primeiro. À noite, as horas reais."),
      ("6","Do aprender","H","Fechei o livro.","O essencial, de memória. Um minuto por dia, em voz alta."),
      ("7","Da crítica","J","Entreguei a obra.","Peço crítica. Ouço. Corrijo."),
      ("8","Das pessoas","J","Alguém me fala.","Deixo terminar. Pergunto antes."),
      ("9","Da serenidade","J","Irritação, pressão.","Pauso. Respondo depois do pico."),
      ("10","Da mente móvel","J","Fui contrariado.","Talvez você tenha razão. Examino. À noite, uma crença de hoje e o melhor argumento contra."),
      ("11","Da pobreza","J","Impulso de conforto.","Espero vinte e quatro horas. De manhã, escolho uma recusa de conforto. Uma vez por ciclo, o dia de pobreza."),
      ("12","Da discrição","H","Vontade de contar um plano.","Calo. Volto à obra. Um ato bom por dia, que ninguém saberá."),
      ("13","Do amor ao destino","J","Algo deu errado.","A causa, e o próximo passo.")]
rows = [[Paragraph("<font color='#6b6b6b'>Nº</font>", BR_P), Paragraph("<font color='#6b6b6b'>Exercício</font>", BR_P),
         Paragraph("<font color='#6b6b6b'>Quando</font>", BR_P), Paragraph("<font color='#6b6b6b'>Gesto</font>", BR_P)]]
for n,t,k,q,e in ex:
    rows.append([Paragraph(n, BR_P), Paragraph(f"{t} <font size=8.5 color='#6b6b6b'>{k}</font>", BR_P), Paragraph(q, BR_P), Paragraph(f"<i>{e}</i>", BR_P)])
tb = Table(rows, colWidths=[1*cm, 3.7*cm, 4.5*cm, 6.4*cm])
tb.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-2),0.3,colors.HexColor('#cccccc')),
                        ('LINEBELOW',(0,0),(-1,0),0.6,GRAY),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2)]))
st.append(tb)
add("Uma de cada vez (§1). Chegou: muda na manhã seguinte. Nunca dois dias seguidos de queda; o ponto não os separa (§5).<br/>Se não chega e a resistência que fala volta: as quatro provas, e a passagem por decisão (Livro V).", ParagraphStyle('bn2', parent=NOTE, alignment=TA_CENTER, spaceBefore=6))

add("O &nbsp;CORTE", SEC)
for a in ["<b>Nomeie</b> o hábito e a sua ocasião.", "<b>Trace a linha</b>: <i>A partir de hoje, não ____.</i> Data e assinatura.",
          "<b>Queime as pontes</b> no mesmo dia.", "<b>Mude o terreno</b>.", "<b>Ponha um gesto no lugar</b>, e uma paixão contrária nas mesmas horas.",
          "<b>Atravesse a onda</b> com a nona linha.", "<b>Conte os dias</b>. Se você cair: <i>caí; a linha continua.</i>"]:
    add(a, ParagraphStyle('bc', parent=BR_P, alignment=TA_CENTER))

# ===================== FOLHA DE MARCAS =====================
st.append(PageBreak()); sp(10)
add("Folha de marcas", BR_T); sumario(st[-1], 0, "Folha de marcas")
add("É copiada à mão nas páginas 5 a 34 do caderno, tantas vezes quantas forem necessárias, ou impressa e colada. Uma linha por dia; a marca é sobre hoje e só sobre a da vez.", BR_N)
BR_C = ParagraphStyle('brc', parent=BR_P, alignment=TA_CENTER)
rows = [[Paragraph(f"<font color='#6b6b6b'>{h}</font>", BR_C) for h in
         ["Data", "Nº", "Marca", "Chegou", "Queda das que ficaram"]]]
rows += [[Paragraph("<font size=8 color='#b0b0b0'>___/___</font>", BR_C), "", "", "", ""] for _ in range(31)]
t = Table(rows, colWidths=[2.6*cm, 1.6*cm, 2.2*cm, 2.4*cm, 6.8*cm], rowHeights=[0.8*cm] + [0.56*cm]*31)
t.setStyle(TableStyle([('GRID',(0,1),(-1,-1),0.4,GRAY),('LINEBELOW',(0,0),(-1,0),0.6,GRAY),
                       ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),1),('BOTTOMPADDING',(0,0),(-1,-1),1)]))
st.append(t)
add("<b>Nº</b>: o número do exercício da microação da vez. <b>Traço</b>: na ocasião que mais pesou, você fez. <b>Cruz</b>: você cedeu, ou fez metade. <b>Ponto</b>: a ocasião da da vez não veio hoje. Na dúvida, cruz. <b>Chegou</b>: na ocasião que mais pesou, o gesto veio sem que o caderno precisasse lembrar; nunca no dia em que entrou, nunca numa noite de cruz; na dúvida, não chegou. <b>Queda das que ficaram</b>: o número daquela em que você cedeu hoje. Nunca dois dias seguidos de queda; o ponto não os separa.", ParagraphStyle('bn4', parent=NOTE, spaceBefore=8))

st.append(PageBreak()); sp(10)
add("DIAS &nbsp;LIMPOS", SEC); sumario(st[-1], 0, "Dias limpos")
add("Corte: <i>A partir de ___/___, não ________________________________.</i> &nbsp; Assinatura: ______________", ParagraphStyle('ct2', parent=BR_P, spaceAfter=8))
cells = [[Paragraph(f"<font size=7.5 color='#999999'>{r*15+c+1}</font>", BR_P) for c in range(15)] for r in range(6)]
t = Table(cells, colWidths=[1.04*cm]*15, rowHeights=[0.75*cm]*6)
t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.4,GRAY),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),2),('TOPPADDING',(0,0),(-1,-1),1)]))
st.append(t)
add("É copiada à mão na página 35 do caderno no dia do corte, ou impressa e colada. Marcos: trinta e noventa dias. Depois deles, a linha continua.", ParagraphStyle('bn3', parent=NOTE, alignment=TA_CENTER, spaceBefore=8))

# ===================== FOLHA DO DIA ZERO =====================
st.append(PageBreak()); sp(10)
add("Folha do dia zero", BR_T); sumario(st[-1], 0, "Folha do dia zero")
add("É copiada à mão na primeira página do caderno, ou impressa e colada; cada ciclo abre um caderno novo, e a folha nova vai na primeira página dele. É relida nas noites de passagem.", BR_N)
LNZ = ParagraphStyle('lnz', **{**base, 'textColor': colors.HexColor('#b0b0b0')}, fontSize=11, leading=19)
for t_, n_ in [("Anti-visão", 2), ("Visão", 2), ("Domínio, e o porquê com rosto", 2), ("Alvo de um ano", 1),
               ("Obra em curso", 1), ("Alavancas diárias", 2), ("Regras", 2), ("Sou alguém que", 3)]:
    st.append(KeepTogether([Paragraph(f"<i>{t_}</i>", ParagraphStyle('fz', parent=BR_P, spaceBefore=5, spaceAfter=0)),
                            Paragraph("<br/>".join(["_"*68]*n_), LNZ)]))

doc.multiBuild(st)
