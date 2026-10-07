from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm
CONTENT_W = PAGE_W - 2 * MARGIN
TOP_Y = PAGE_H - MARGIN
BOTTOM_Y = MARGIN + 10 * mm  # laisse la place au pied de page


class Cursor:
    """Curseur vertical : avance une position y, saute de page quand on atteint le bas."""

    def __init__(self, canv, on_new_page=None):
        self.canv = canv
        self.y = TOP_Y
        self.on_new_page = on_new_page
        self.page_num = 1

    def ensure_space(self, height):
        if self.y - height < BOTTOM_Y:
            self.new_page()

    def new_page(self):
        if self.on_new_page:
            self.on_new_page(self.canv, self.page_num)
        self.canv.showPage()
        self.page_num += 1
        self.y = TOP_Y

    def advance(self, height, gap=4):
        self.y -= height + gap
