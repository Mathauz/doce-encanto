from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)

BG = "#FFF9F5"
WHITE = "#FFFFFF"
COCOA = "#341713"
MUTED = "#725E59"
BERRY = "#B74751"
LINE = "#D8BDB7"
GREEN = "#DDEFE5"


def font(size, bold=False):
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


F_TITLE = font(38, True)
F_HEAD = font(25, True)
F_BODY = font(21)
F_SMALL = font(18)


def canvas(title):
    image = Image.new("RGB", (1600, 900), BG)
    draw = ImageDraw.Draw(image)
    draw.text((70, 42), title, font=F_TITLE, fill=COCOA)
    draw.line((70, 102, 1530, 102), fill=LINE, width=2)
    return image, draw


def box(draw, xy, title, lines=(), fill=WHITE, outline=LINE, radius=18, title_fill=COCOA):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=3)
    draw.text((x1 + 20, y1 + 16), title, font=F_HEAD, fill=title_fill)
    y = y1 + 55
    for line in lines:
        for part in wrap(line, width=max(18, int((x2 - x1) / 12))):
            draw.text((x1 + 20, y), part, font=F_SMALL, fill=MUTED)
            y += 27
        y += 4


def arrow(draw, start, end, label=None):
    draw.line((*start, *end), fill=BERRY, width=4)
    ex, ey = end
    sx, sy = start
    if abs(ex - sx) >= abs(ey - sy):
        sign = 1 if ex > sx else -1
        points = [(ex, ey), (ex - 14 * sign, ey - 8), (ex - 14 * sign, ey + 8)]
    else:
        sign = 1 if ey > sy else -1
        points = [(ex, ey), (ex - 8, ey - 14 * sign), (ex + 8, ey - 14 * sign)]
    draw.polygon(points, fill=BERRY)
    if label:
        mx, my = (sx + ex) // 2, (sy + ey) // 2
        draw.rectangle((mx - 70, my - 18, mx + 70, my + 18), fill=BG)
        draw.text((mx - 62, my - 13), label, font=F_SMALL, fill=MUTED)


def save(image, name):
    image.save(OUT / name, quality=95)


def use_cases():
    image, draw = canvas("Diagrama de casos de uso")
    draw.ellipse((90, 260, 150, 320), outline=COCOA, width=4)
    draw.line((120, 320, 120, 450), fill=COCOA, width=4)
    draw.line((55, 365, 185, 365), fill=COCOA, width=4)
    draw.line((120, 450, 65, 530), fill=COCOA, width=4)
    draw.line((120, 450, 175, 530), fill=COCOA, width=4)
    draw.text((72, 555), "Cliente", font=F_HEAD, fill=COCOA)
    draw.ellipse((1450, 260, 1510, 320), outline=COCOA, width=4)
    draw.line((1480, 320, 1480, 450), fill=COCOA, width=4)
    draw.line((1415, 365, 1545, 365), fill=COCOA, width=4)
    draw.line((1480, 450, 1425, 530), fill=COCOA, width=4)
    draw.line((1480, 450, 1535, 530), fill=COCOA, width=4)
    draw.text((1402, 555), "Administrador", font=F_HEAD, fill=COCOA)
    cases = [
        ("Criar conta e entrar", 260, 165), ("Consultar catálogo", 570, 165),
        ("Gerenciar carrinho", 880, 165), ("Finalizar pedido", 415, 355),
        ("Consultar pedidos", 725, 355), ("Administrar produtos", 1035, 355),
        ("Atualizar status", 880, 560),
    ]
    for text, x, y in cases:
        draw.ellipse((x, y, x + 245, y + 84), fill=WHITE, outline=LINE, width=3)
        bbox = draw.textbbox((0, 0), text, font=F_SMALL)
        draw.text((x + (245 - (bbox[2] - bbox[0])) / 2, y + 30), text, font=F_SMALL, fill=COCOA)
    for y in [205, 395]:
        draw.line((185, 365, 260 if y == 205 else 415, y), fill=MUTED, width=2)
    draw.line((185, 365, 570, 205), fill=MUTED, width=2)
    draw.line((185, 365, 880, 205), fill=MUTED, width=2)
    draw.line((185, 365, 725, 395), fill=MUTED, width=2)
    draw.line((1415, 365, 1280, 395), fill=MUTED, width=2)
    draw.line((1415, 365, 1125, 600), fill=MUTED, width=2)
    save(image, "casos-de-uso.png")


def classes():
    image, draw = canvas("Diagrama de classes")
    box(draw, (90, 190, 430, 610), "User", ["username: string", "email: string", "password: hash", "orders: Order[*]"])
    box(draw, (635, 145, 985, 660), "Order", ["recipient_name: string", "address fields: string", "payment_method: choice", "status: choice", "total: decimal", "created_at: datetime"])
    box(draw, (1175, 190, 1515, 610), "OrderItem", ["product_name: string", "unit_price: decimal", "quantity: integer", "subtotal(): decimal"])
    box(draw, (635, 710, 985, 850), "Product", ["name, description, price", "image, active, featured"])
    arrow(draw, (430, 380), (635, 380), "1 possui N")
    arrow(draw, (985, 380), (1175, 380), "1 contém N")
    arrow(draw, (1175, 560), (985, 765), "0..1 refere")
    save(image, "classes.png")


def sequence():
    image, draw = canvas("Diagrama de sequência do checkout")
    actors = [(120, "Cliente"), (460, "View checkout"), (800, "Carrinho"), (1120, "Banco"), (1410, "Pedido")]
    for x, name in actors:
        draw.rounded_rectangle((x - 85, 135, x + 85, 195), radius=12, fill=WHITE, outline=LINE, width=3)
        bbox = draw.textbbox((0, 0), name, font=F_SMALL)
        draw.text((x - (bbox[2] - bbox[0]) / 2, 155), name, font=F_SMALL, fill=COCOA)
        draw.line((x, 195, x, 825), fill=LINE, width=2)
    steps = [
        (120, 460, 255, "POST dados de entrega"),
        (460, 800, 350, "Ler itens ativos"),
        (800, 1120, 445, "Reconsultar preços"),
        (1120, 460, 540, "Produtos válidos"),
        (460, 1410, 635, "Criar pedido + itens"),
        (1410, 460, 730, "Pedido confirmado"),
        (460, 120, 805, "Redirecionar detalhe"),
    ]
    for x1, x2, y, label in steps:
        arrow(draw, (x1, y), (x2, y), label)
    save(image, "sequencia-checkout.png")


def activity():
    image, draw = canvas("Diagrama de atividades do pedido")
    draw.ellipse((120, 385, 170, 435), fill=COCOA)
    stages = [
        ((240, 350, 470, 470), "Selecionar produtos"),
        ((555, 350, 785, 470), "Revisar carrinho"),
        ((870, 350, 1100, 470), "Informar entrega"),
        ((1185, 350, 1415, 470), "Confirmar pedido"),
    ]
    prev = (170, 410)
    for xy, label in stages:
        box(draw, xy, label, (), fill=WHITE)
        arrow(draw, prev, (xy[0], 410))
        prev = (xy[2], 410)
    draw.polygon([(760, 600), (870, 685), (760, 770), (650, 685)], fill=WHITE, outline=LINE)
    draw.text((701, 675), "Dados válidos?", font=F_SMALL, fill=COCOA)
    arrow(draw, (1290, 470), (1290, 685), "validar")
    arrow(draw, (1290, 685), (870, 685), "sim")
    arrow(draw, (650, 685), (355, 470), "não: corrigir")
    draw.ellipse((900, 660, 950, 710), fill=COCOA)
    save(image, "atividades.png")


def navigation():
    image, draw = canvas("Mapa navegacional")
    nodes = [
        ((650, 140, 950, 245), "Início"),
        ((90, 350, 390, 470), "Cadastro e login"),
        ((470, 350, 770, 470), "Catálogo"),
        ((850, 350, 1150, 470), "Carrinho"),
        ((1230, 350, 1530, 470), "Meus pedidos"),
        ((850, 625, 1150, 745), "Checkout"),
        ((1230, 625, 1530, 745), "Detalhe do pedido"),
    ]
    for xy, title in nodes:
        box(draw, xy, title, (), fill=WHITE)
    for x in [240, 620, 1000, 1380]:
        arrow(draw, (800, 245), (x, 350))
    arrow(draw, (1000, 470), (1000, 625))
    arrow(draw, (1150, 685), (1230, 685))
    arrow(draw, (1380, 470), (1380, 625))
    save(image, "mapa-navegacional.png")


def erd():
    image, draw = canvas("Modelo lógico de dados")
    box(draw, (80, 185, 470, 650), "AUTH_USER", ["PK id", "username", "email", "password_hash"], fill=WHITE)
    box(draw, (605, 140, 995, 710), "SHOP_ORDER", ["PK id", "FK user_id", "recipient_name", "street, number, complement", "district, city, state, postal_code", "payment_method", "status", "total", "created_at, updated_at"], fill=WHITE)
    box(draw, (1130, 185, 1520, 650), "SHOP_ORDERITEM", ["PK id", "FK order_id", "FK product_id (nullable)", "product_name", "unit_price", "quantity"], fill=WHITE)
    box(draw, (605, 755, 995, 865), "SHOP_PRODUCT", ["PK id | name | price | active"], fill=WHITE)
    arrow(draw, (470, 400), (605, 400), "1 : N")
    arrow(draw, (995, 400), (1130, 400), "1 : N")
    arrow(draw, (1130, 600), (995, 805), "0..1 : N")
    save(image, "modelo-logico.png")


def affinity():
    image, draw = canvas("Mapa de afinidade das histórias")
    groups = [
        ((70, 160, 360, 800), "Conta", ["US01 Criar conta", "US02 Entrar", "US03 Sair"]),
        ((385, 160, 735, 800), "Descoberta", ["US04 Ver catálogo", "US05 Ver preço", "US06 Identificar disponibilidade"]),
        ((760, 160, 1110, 800), "Compra", ["US07 Adicionar item", "US08 Alterar quantidade", "US09 Remover item", "US10 Finalizar pedido", "US11 Escolher pagamento"]),
        ((1135, 160, 1530, 800), "Acompanhamento e operação", ["US12 Ver histórico", "US13 Ver detalhe", "US14 Administrar produtos", "US15 Atualizar status"]),
    ]
    for xy, title, cards in groups:
        box(draw, xy, title, (), fill="#F4E6E4")
        x1, y1, x2, _ = xy
        y = y1 + 80
        for card in cards:
            draw.rounded_rectangle((x1 + 22, y, x2 - 22, y + 82), radius=12, fill=WHITE, outline=LINE, width=2)
            draw.text((x1 + 38, y + 28), card, font=F_SMALL, fill=COCOA)
            y += 100
    save(image, "mapa-afinidade.png")


def wireframes():
    image, draw = canvas("Wireframes principais")
    screens = [(70, "Início"), (450, "Catálogo"), (830, "Carrinho"), (1210, "Checkout")]
    for x, title in screens:
        draw.rounded_rectangle((x, 145, x + 310, 805), radius=26, fill=WHITE, outline=COCOA, width=3)
        draw.rectangle((x + 18, 170, x + 292, 218), fill="#F4E6E4")
        draw.text((x + 35, 181), "Doce Encanto", font=F_SMALL, fill=COCOA)
        draw.text((x + 20, 825), title, font=F_HEAD, fill=COCOA)
    draw.rectangle((92, 245, 358, 440), fill="#F2D7D4")
    draw.rectangle((92, 462, 250, 498), fill=BERRY)
    for y in [252, 425, 598]:
        draw.rectangle((472, y, 600, y + 128), fill="#F2D7D4")
        draw.line((620, y + 20, 735, y + 20), fill=COCOA, width=6)
        draw.line((620, y + 52, 712, y + 52), fill=LINE, width=4)
    for y in [260, 385, 510]:
        draw.line((852, y, 1112, y), fill=LINE, width=3)
        draw.text((852, y + 22), "Produto   quantidade   preço", font=F_SMALL, fill=MUTED)
    draw.rectangle((852, 675, 1115, 725), fill=BERRY)
    for y in [260, 350, 440, 530]:
        draw.rectangle((1235, y, 1487, y + 52), outline=LINE, width=2)
    draw.rectangle((1235, 675, 1487, 725), fill=BERRY)
    save(image, "wireframes.png")


if __name__ == "__main__":
    use_cases()
    classes()
    sequence()
    activity()
    navigation()
    erd()
    affinity()
    wireframes()
    print(f"Generated diagrams in {OUT}")
