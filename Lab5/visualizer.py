
import math
import time
import heapq
import random
import os
import sys

import pygame

# ── Try to reuse display.py if it lives next to this file ────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
try:
    from display import Window, TextBox, SlideBox, DropdownBox, TextButtonBox
except ImportError:
    # Minimal inline fallbacks so the file is self-contained
    class Box:
        def __init__(self, rect):
            self.rect = pygame.Rect(rect)
            self.mousePos = (0, 0)
            self.clicked = False
            self.hovered = False
        def update(self, event):
            self.mousePos = pygame.mouse.get_pos()
            self.clicked = event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(self.mousePos)
            self.hovered = self.rect.collidepoint(self.mousePos)

    class TextBox(Box):
        def __init__(self, rect, label, color, font, text):
            super().__init__(rect)
            self.label, self.color, self.font, self.text = label, color, font, text
        def render(self, screen):
            lbl = self.font.render(self.label, True, self.color)
            screen.blit(lbl, (self.rect.x + (self.rect.w - lbl.get_width()) / 2, self.rect.y - 26))
            pygame.draw.rect(screen, self.color, self.rect, 2)
            s = self.font.render(self.text, True, self.color)
            screen.blit(s, s.get_rect(center=self.rect.center))
        def update(self, event):
            super().update(event)
            if self.hovered and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.unicode.isdigit():
                    self.text += event.unicode
        def get_value(self): return self.text
        def set_value(self, v): self.text = v

    class SlideBox(Box):
        def __init__(self, rect, label, color, font):
            super().__init__(rect)
            self.label, self.color, self.font = label, color, font
            self.start = self.rect.x + 6
            self.end = self.rect.x + self.rect.w - 6
            self.value = self.start
            self.dragging = False
        def render(self, screen):
            lbl = self.font.render(self.label, True, self.color)
            screen.blit(lbl, (self.rect.x + (self.rect.w - lbl.get_width()) / 2, self.rect.y - 26))
            pygame.draw.rect(screen, self.color, self.rect, 2)
            pygame.draw.line(screen, self.color, (self.start, self.rect.y + 25), (self.end, self.rect.y + 25), 2)
            pygame.draw.line(screen, self.color, (self.value, self.rect.y + 5), (self.value, self.rect.y + 45), 12)
        def update(self, event):
            super().update(event)
            self.start = self.rect.x + 6
            self.end = self.rect.x + self.rect.w - 6
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(self.mousePos):
                self.dragging = True
            if event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
            if self.dragging:
                self.value = min(max(self.mousePos[0], self.start), self.end)
        def get_value(self):
            return (self.value - self.start) / max(1, self.end - self.start)
        def set_value(self, v):
            self.value = self.start + v * (self.end - self.start)

    class DropdownBox(Box):
        def __init__(self, rect, label, color, font, options, bg):
            super().__init__(rect)
            self.label, self.color, self.font = label, color, font
            self.options, self.bg = options, bg
            self.selected_option = 0
            self.openDropdown = False
        def render(self, screen):
            lbl = self.font.render(self.label, True, self.color)
            screen.blit(lbl, (self.rect.x + (self.rect.w - lbl.get_width()) / 2, self.rect.y - 26))
            pygame.draw.rect(screen, self.color, self.rect, 2)
            s = self.font.render(self.options[self.selected_option], True, self.color)
            screen.blit(s, s.get_rect(center=self.rect.center))
            if self.openDropdown:
                for idx, opt in enumerate(self.options):
                    r = pygame.Rect(self.rect.x, self.rect.y - (idx + 1) * self.rect.h, self.rect.w, self.rect.h)
                    pygame.draw.rect(screen, self.bg, r)
                    pygame.draw.rect(screen, self.color, r, 1)
                    os = self.font.render(opt, True, self.color)
                    screen.blit(os, os.get_rect(center=r.center))
        def update(self, event):
            super().update(event)
            if self.clicked:
                self.openDropdown = not self.openDropdown
            if self.openDropdown:
                for idx in range(len(self.options)):
                    r = pygame.Rect(self.rect.x, self.rect.y - (idx + 1) * self.rect.height,
                                    self.rect.width, self.rect.height)
                    if r.collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                        self.selected_option = idx
                        self.openDropdown = False
        def get_value(self): return self.options[self.selected_option]
        def set_value(self, v):
            if isinstance(v, int): self.selected_option = v
            elif v in self.options: self.selected_option = self.options.index(v)

    class TextButtonBox(Box):
        def __init__(self, rect, label, color, font, bg_color=(40,40,40), active_bg=(80,140,90)):
            super().__init__(rect)
            self.label, self.color, self.font = label, color, font
            self.bg_color, self.active_bg = bg_color, active_bg
            self.active = False
        def render(self, screen):
            bg = self.active_bg if self.active else self.bg_color
            pygame.draw.rect(screen, bg, self.rect)
            pygame.draw.rect(screen, self.color, self.rect, 2)
            s = self.font.render(self.label, True, self.color)
            screen.blit(s, s.get_rect(center=self.rect.center))
        def update(self, event):
            super().update(event)
            if self.clicked:
                self.active = not self.active
        def get_value(self): return self.active
        def set_value(self, v): self.active = v

    class Window:
        def __init__(self, screen):
            self.screen = screen
            self.widgets = {}
        def add_widget(self, wid, w): self.widgets[wid] = w
        def get_widget_value(self, wid):
            return self.widgets[wid].get_value() if wid in self.widgets else None
        def set_widget_value(self, wid, v):
            if wid in self.widgets: self.widgets[wid].set_value(v)
        def render(self):
            for w in self.widgets.values(): w.render(self.screen)
        def update(self, event):
            for w in self.widgets.values(): w.update(event)


# ── Theme ─────────────────────────────────────────────────────────────────────
BG           = (15, 15, 15)
PANEL_BG     = (26, 26, 26)
CTRL_BG      = (20, 20, 20)
TEXT         = (220, 220, 220)
DIM_TEXT     = (140, 140, 140)
HEADER_TEXT  = (170, 170, 170)
GRID_LINE    = (55, 55, 55)
WIDGET_COLOR = (170, 170, 170)
DROPDOWN_BG  = (32, 32, 32)

UNVISITED    = (44, 44, 44)
VISITED      = (15, 110, 86)
CURRENT      = (186, 117, 23)
IN_MST       = (29, 158, 117)
CANDIDATE    = (80, 80, 160)
REJECTED     = (120, 40, 40)
START_COLOR  = (24, 95, 165)

EDGE_DEFAULT = (68, 68, 68)
EDGE_MST     = (29, 158, 117)
EDGE_CURRENT = (186, 117, 23)
EDGE_REJECT  = (120, 40, 40)
EDGE_CAND    = (80, 80, 180)

INF = float('inf')


# ── Graph builder ─────────────────────────────────────────────────────────────

def random_graph(n, density='Sparse', seed=None):
    rng = random.Random(seed)
    edges_set = set()
    nodes = list(range(n))
    rng.shuffle(nodes)
    for i in range(1, n):
        u = nodes[i]
        v = nodes[rng.randint(0, i - 1)]
        edges_set.add((min(u, v), max(u, v)))
    extra = int(n * 1.5) if density == 'Sparse' else n * (n - 1) // 2
    while len(edges_set) < extra:
        u = rng.randint(0, n - 1)
        v = rng.randint(0, n - 1)
        if u != v:
            edges_set.add((min(u, v), max(u, v)))
    weighted = [(u, v, rng.randint(1, 20)) for (u, v) in edges_set]
    # Build adjacency dict
    graph = {i: [] for i in range(n)}
    for u, v, w in weighted:
        graph[u].append((v, w))
        graph[v].append((u, w))
    return graph, weighted


def circular_positions(n, cx, cy, r):
    pos = {}
    for i in range(n):
        angle = 2 * math.pi * i / max(n, 1) - math.pi / 2
        pos[i] = (int(cx + r * math.cos(angle)), int(cy + r * math.sin(angle)))
    return pos


# ── Step generators ───────────────────────────────────────────────────────────

def kruskal_steps(n, weighted_edges):
    """
    Yields dicts with keys:
      phase, candidate_edge, mst_edges, rejected_edges, parent, rank, mst_weight
    """
    edges = sorted(weighted_edges, key=lambda e: e[2])
    parent = list(range(n))
    rank = [0] * n
    mst_edges = []
    rejected_edges = []
    mst_weight = 0

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1
        return True

    yield {
        'phase': 'init',
        'candidate_edge': None,
        'mst_edges': list(mst_edges),
        'rejected_edges': list(rejected_edges),
        'parent': list(parent),
        'rank': list(rank),
        'mst_weight': mst_weight,
        'sorted_edges': edges,
        'edge_index': -1,
    }

    for idx, (u, v, w) in enumerate(edges):
        # Considering edge
        yield {
            'phase': 'consider',
            'candidate_edge': (u, v, w),
            'mst_edges': list(mst_edges),
            'rejected_edges': list(rejected_edges),
            'parent': list(parent),
            'rank': list(rank),
            'mst_weight': mst_weight,
            'sorted_edges': edges,
            'edge_index': idx,
        }
        if union(u, v):
            mst_edges.append((u, v, w))
            mst_weight += w
            yield {
                'phase': 'accept',
                'candidate_edge': (u, v, w),
                'mst_edges': list(mst_edges),
                'rejected_edges': list(rejected_edges),
                'parent': list(parent),
                'rank': list(rank),
                'mst_weight': mst_weight,
                'sorted_edges': edges,
                'edge_index': idx,
            }
        else:
            rejected_edges.append((u, v, w))
            yield {
                'phase': 'reject',
                'candidate_edge': (u, v, w),
                'mst_edges': list(mst_edges),
                'rejected_edges': list(rejected_edges),
                'parent': list(parent),
                'rank': list(rank),
                'mst_weight': mst_weight,
                'sorted_edges': edges,
                'edge_index': idx,
            }

    yield {
        'phase': 'done',
        'candidate_edge': None,
        'mst_edges': list(mst_edges),
        'rejected_edges': list(rejected_edges),
        'parent': list(parent),
        'rank': list(rank),
        'mst_weight': mst_weight,
        'sorted_edges': edges,
        'edge_index': len(edges),
    }


def prim_steps(graph, n, start=0):
    """
    Yields dicts with keys:
      phase, current_node, candidate_edge, mst_edges, visited, in_heap, mst_weight
    """
    visited = [False] * n
    mst_edges = []
    mst_weight = 0
    heap = [(0, start, -1)]
    in_heap = {start: 0}   # node -> best weight in heap

    yield {
        'phase': 'init',
        'current_node': start,
        'candidate_edge': None,
        'mst_edges': [],
        'visited': list(visited),
        'in_heap': dict(in_heap),
        'mst_weight': 0,
    }

    while heap:
        weight, node, parent = heapq.heappop(heap)
        if visited[node]:
            continue
        visited[node] = True

        if parent != -1:
            mst_edges.append((parent, node, weight))
            mst_weight += weight

        yield {
            'phase': 'visit',
            'current_node': node,
            'candidate_edge': (parent, node, weight) if parent != -1 else None,
            'mst_edges': list(mst_edges),
            'visited': list(visited),
            'in_heap': dict(in_heap),
            'mst_weight': mst_weight,
        }

        for neighbor, w in graph[node]:
            if not visited[neighbor]:
                if neighbor not in in_heap or w < in_heap[neighbor]:
                    in_heap[neighbor] = w
                    heapq.heappush(heap, (w, neighbor, node))

                yield {
                    'phase': 'relax',
                    'current_node': node,
                    'candidate_edge': (node, neighbor, w),
                    'mst_edges': list(mst_edges),
                    'visited': list(visited),
                    'in_heap': dict(in_heap),
                    'mst_weight': mst_weight,
                }

    yield {
        'phase': 'done',
        'current_node': None,
        'candidate_edge': None,
        'mst_edges': list(mst_edges),
        'visited': list(visited),
        'in_heap': {},
        'mst_weight': mst_weight,
    }


# ── Drawing helpers ───────────────────────────────────────────────────────────

def draw_graph_base(screen, fonts, graph, positions, n,
                    mst_edges, candidate_edge, rejected_edges=None, visited=None,
                    current_node=None, in_heap=None):
    """Draw nodes and edges for both algorithms."""
    mst_set = {(min(u, v), max(u, v)) for u, v, _ in mst_edges}
    rej_set  = {(min(u, v), max(u, v)) for u, v, _ in (rejected_edges or [])}
    cand_key = (min(candidate_edge[0], candidate_edge[1]),
                max(candidate_edge[0], candidate_edge[1])) if candidate_edge else None

    # Collect all edges from graph (undirected, draw once)
    drawn = set()
    for u in graph:
        for v, w in graph[u]:
            key = (min(u, v), max(u, v))
            if key in drawn:
                continue
            drawn.add(key)
            if key == cand_key:
                color, width = EDGE_CURRENT, 4
            elif key in mst_set:
                color, width = EDGE_MST, 4
            elif key in rej_set:
                color, width = EDGE_REJECT, 2
            elif in_heap and (v in in_heap or u in in_heap):
                color, width = EDGE_CAND, 2
            else:
                color, width = EDGE_DEFAULT, 2

            pygame.draw.line(screen, color, positions[u], positions[v], width)
            mx = (positions[u][0] + positions[v][0]) // 2
            my = (positions[u][1] + positions[v][1]) // 2
            txt = fonts['small'].render(str(w), True, DIM_TEXT)
            bg_rect = txt.get_rect(center=(mx, my)).inflate(6, 2)
            pygame.draw.rect(screen, BG, bg_rect)
            screen.blit(txt, txt.get_rect(center=(mx, my)))

    # Nodes
    radius = max(14, min(24, 220 // max(n, 1)))
    for i in range(n):
        x, y = positions[i]
        in_mst = any(i == u or i == v for u, v, _ in mst_edges)
        if i == current_node:
            color = CURRENT
        elif visited and visited[i]:
            color = IN_MST
        elif in_mst:
            color = IN_MST
        elif in_heap and i in in_heap:
            color = CANDIDATE
        else:
            color = UNVISITED

        pygame.draw.circle(screen, color, (x, y), radius)
        pygame.draw.circle(screen, (85, 85, 85), (x, y), radius, 2)
        label = fonts['node'].render(str(i), True, (240, 240, 240))
        screen.blit(label, label.get_rect(center=(x, y)))


# ── Kruskal panel ─────────────────────────────────────────────────────────────

def draw_kruskal_panel(screen, fonts, state, panel_x, panel_y, panel_w, panel_h):
    pygame.draw.rect(screen, PANEL_BG, (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(screen, GRID_LINE, (panel_x, panel_y, panel_w, panel_h), 1)

    screen.blit(fonts['header'].render("Kruskal's MST", True, HEADER_TEXT),
                (panel_x + 16, panel_y + 12))

    phase        = state['phase']
    cand         = state['candidate_edge']
    mst_edges    = state['mst_edges']
    mst_weight   = state['mst_weight']
    sorted_edges = state['sorted_edges']
    edge_index   = state['edge_index']

    y = panel_y + 44
    # Status line
    if phase == 'init':
        msg, mcol = 'Sorted edges — ready to iterate', DIM_TEXT
    elif phase == 'consider':
        msg, mcol = f'Consider edge  {cand[0]}─{cand[1]}  (w={cand[2]})', CURRENT
    elif phase == 'accept':
        msg, mcol = f'Accept  {cand[0]}─{cand[1]}  (w={cand[2]})', IN_MST
    elif phase == 'reject':
        msg, mcol = f'Reject  {cand[0]}─{cand[1]}  — cycle!', (200, 80, 80)
    else:
        msg, mcol = f'Done!  MST weight = {mst_weight}', IN_MST

    screen.blit(fonts['base'].render(msg, True, mcol), (panel_x + 16, y)); y += 30

    # MST weight so far
    screen.blit(fonts['small'].render(f'MST weight so far: {mst_weight}', True, TEXT),
                (panel_x + 16, y)); y += 24
    screen.blit(fonts['small'].render(f'MST edges ({len(mst_edges)}):', True, DIM_TEXT),
                (panel_x + 16, y)); y += 20
    for u, v, w in mst_edges:
        screen.blit(fonts['small'].render(f'  {u} ─ {v}  (w={w})', True, IN_MST),
                    (panel_x + 16, y)); y += 18

    # Sorted edge list (scroll to show current)
    sep_y = panel_y + panel_h - 220
    pygame.draw.line(screen, GRID_LINE, (panel_x + 12, sep_y), (panel_x + panel_w - 12, sep_y), 1)
    screen.blit(fonts['small'].render('Sorted edge queue:', True, DIM_TEXT),
                (panel_x + 16, sep_y + 8))
    ey = sep_y + 28
    row_h = 19
    # Show a window around edge_index
    start_i = max(0, edge_index - 3)
    end_i   = min(len(sorted_edges), start_i + 8)
    for idx in range(start_i, end_i):
        u, v, w = sorted_edges[idx]
        if idx < edge_index:
            col = DIM_TEXT
        elif idx == edge_index:
            col = CURRENT
            pygame.draw.rect(screen, (50, 40, 10), (panel_x + 12, ey - 2, panel_w - 24, row_h))
        else:
            col = TEXT
        screen.blit(fonts['small'].render(f'  {u}─{v}  w={w}', True, col), (panel_x + 16, ey))
        ey += row_h

    # Progress bar
    total = len(sorted_edges)
    done  = max(0, edge_index)
    pb_y = panel_y + panel_h - 30
    screen.blit(fonts['small'].render(f'Edge {done}/{total}', True, DIM_TEXT),
                (panel_x + 16, pb_y - 20))
    pygame.draw.rect(screen, (40, 40, 40), (panel_x + 16, pb_y, panel_w - 32, 10))
    fill = int((panel_w - 32) * done / max(total, 1))
    pygame.draw.rect(screen, IN_MST, (panel_x + 16, pb_y, fill, 10))


# ── Prim panel ────────────────────────────────────────────────────────────────

def draw_prim_panel(screen, fonts, state, panel_x, panel_y, panel_w, panel_h):
    pygame.draw.rect(screen, PANEL_BG, (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(screen, GRID_LINE, (panel_x, panel_y, panel_w, panel_h), 1)

    screen.blit(fonts['header'].render("Prim's MST", True, HEADER_TEXT),
                (panel_x + 16, panel_y + 12))

    phase       = state['phase']
    cand        = state['candidate_edge']
    mst_edges   = state['mst_edges']
    mst_weight  = state['mst_weight']
    visited     = state['visited']
    in_heap     = state['in_heap']
    current     = state['current_node']

    y = panel_y + 44
    if phase == 'init':
        msg, mcol = f'Start at node {current}', START_COLOR
    elif phase == 'visit':
        if cand:
            msg, mcol = f'Visit node {current}  via edge {cand[0]}─{cand[1]} (w={cand[2]})', CURRENT
        else:
            msg, mcol = f'Visit start node {current}', START_COLOR
    elif phase == 'relax':
        u, v, w = cand
        msg, mcol = f'Enqueue  {u}─{v}  (w={w})', CANDIDATE
    else:
        msg, mcol = f'Done!  MST weight = {mst_weight}', IN_MST

    screen.blit(fonts['base'].render(msg, True, mcol), (panel_x + 16, y)); y += 30

    screen.blit(fonts['small'].render(f'MST weight so far: {mst_weight}', True, TEXT),
                (panel_x + 16, y)); y += 24
    screen.blit(fonts['small'].render(f'MST edges ({len(mst_edges)}):', True, DIM_TEXT),
                (panel_x + 16, y)); y += 20
    for u, v, w in mst_edges:
        screen.blit(fonts['small'].render(f'  {u} ─ {v}  (w={w})', True, IN_MST),
                    (panel_x + 16, y)); y += 18

    # Min-heap candidates
    sep_y = panel_y + panel_h - 220
    pygame.draw.line(screen, GRID_LINE, (panel_x + 12, sep_y), (panel_x + panel_w - 12, sep_y), 1)
    screen.blit(fonts['small'].render('Min-heap candidates:', True, DIM_TEXT),
                (panel_x + 16, sep_y + 8))
    hy = sep_y + 28
    for node, best_w in sorted(in_heap.items(), key=lambda kv: kv[1]):
        col = IN_MST if visited[node] else (CURRENT if node == current else CANDIDATE)
        tick = '✓ ' if visited[node] else '  '
        screen.blit(fonts['small'].render(f'{tick}Node {node}  (best w={best_w})', True, col),
                    (panel_x + 16, hy))
        hy += 19
        if hy > panel_y + panel_h - 50:
            break

    # Visited count
    vis_count = sum(visited)
    n = len(visited)
    pb_y = panel_y + panel_h - 30
    screen.blit(fonts['small'].render(f'Visited {vis_count}/{n} nodes', True, DIM_TEXT),
                (panel_x + 16, pb_y - 20))
    pygame.draw.rect(screen, (40, 40, 40), (panel_x + 16, pb_y, panel_w - 32, 10))
    fill = int((panel_w - 32) * vis_count / max(n, 1))
    pygame.draw.rect(screen, IN_MST, (panel_x + 16, pb_y, fill, 10))


# ── Legend ────────────────────────────────────────────────────────────────────

def draw_legend(screen, fonts, algorithm, x, y):
    items_k = [
        (EDGE_DEFAULT, 'Unprocessed edge'),
        (EDGE_CURRENT, 'Candidate edge'),
        (EDGE_MST,     'MST edge (accepted)'),
        (EDGE_REJECT,  'Rejected (cycle)'),
        (UNVISITED,    'Node not in MST'),
        (IN_MST,       'Node in MST'),
    ]
    items_p = [
        (EDGE_DEFAULT, 'Unprocessed edge'),
        (EDGE_CURRENT, 'Current visit'),
        (EDGE_MST,     'MST edge'),
        (CANDIDATE,    'Node in heap'),
        (UNVISITED,    'Unvisited node'),
        (IN_MST,       'Visited node'),
    ]
    items = items_k if algorithm == 'Kruskal' else items_p
    for color, label in items:
        pygame.draw.rect(screen, color, (x, y, 16, 12))
        screen.blit(fonts['small'].render(label, True, DIM_TEXT), (x + 22, y - 1))
        y += 18


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    pygame.display.set_caption('MST Visualizer  ·  Kruskal & Prim')

    SCREEN_W, SCREEN_H = 1200, 740
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    fonts = {
        'title':  pygame.font.SysFont('Arial', 22, bold=True),
        'header': pygame.font.SysFont('Arial', 16, bold=True),
        'base':   pygame.font.SysFont('Arial', 18),
        'small':  pygame.font.SysFont('Arial', 13),
        'tiny':   pygame.font.SysFont('Arial', 10),
        'node':   pygame.font.SysFont('Arial', 14, bold=True),
    }
    wfont = pygame.font.SysFont('Arial', 18)

    window = Window(screen)
    CTRL_Y = 670

    window.add_widget('size_input',
        TextBox((30, CTRL_Y, 80, 50), 'Nodes', WIDGET_COLOR, wfont, '7'))
    window.add_widget('density_input',
        DropdownBox((130, CTRL_Y, 130, 50), 'Density',
                    WIDGET_COLOR, wfont, ['Sparse', 'Dense'], DROPDOWN_BG))
    window.add_widget('algorithm_input',
        DropdownBox((280, CTRL_Y, 180, 50), 'Algorithm',
                    WIDGET_COLOR, wfont, ['Kruskal', 'Prim'], DROPDOWN_BG))
    window.add_widget('delay_slider',
        SlideBox((480, CTRL_Y, 200, 50), 'Delay', WIDGET_COLOR, wfont))
    window.add_widget('start_input',
        TextBox((700, CTRL_Y, 70, 50), 'Start', WIDGET_COLOR, wfont, '0'))
    window.add_widget('play_button',
        TextButtonBox((820, CTRL_Y + 5, 100, 40), '▶  Play', WIDGET_COLOR, wfont))

    is_running    = False
    steps_iter    = None
    current_state = None
    last_step_t   = 0.0
    graph         = None
    weighted_edges= None
    positions     = None
    n             = 0
    start_node    = 0
    cur_algorithm = None

    running = True
    while running:
        screen.fill(BG)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            window.update(event)

        # Read controls
        try:
            n_input = max(3, min(12, int(window.get_widget_value('size_input') or '7')))
        except ValueError:
            n_input = 7

        density   = window.get_widget_value('density_input') or 'Sparse'
        algorithm = window.get_widget_value('algorithm_input') or 'Kruskal'
        delay_n   = window.get_widget_value('delay_slider') or 0.3
        delay_s   = 0.05 + delay_n * 1.45

        try:
            start_raw = int(window.get_widget_value('start_input') or '0')
            start_node = max(0, min(n_input - 1, start_raw))
        except ValueError:
            start_node = 0

        play_state = window.get_widget_value('play_button')

        # Rising edge → start new run
        if play_state and not is_running:
            n = n_input
            seed = random.randint(0, 10**9)
            graph, weighted_edges = random_graph(n, density, seed=seed)
            positions = circular_positions(n, 350, 340, min(230, 28 * n))
            cur_algorithm = algorithm

            if algorithm == 'Kruskal':
                steps_iter = iter(kruskal_steps(n, weighted_edges))
            else:
                steps_iter = iter(prim_steps(graph, n, start=start_node))

            try:
                current_state = next(steps_iter)
            except StopIteration:
                current_state = None
            is_running   = True
            last_step_t  = time.time()

        # Falling edge → pause
        if not play_state and is_running:
            is_running = False

        # Advance on timer
        if is_running and steps_iter is not None:
            if time.time() - last_step_t >= delay_s:
                try:
                    current_state = next(steps_iter)
                    last_step_t = time.time()
                except StopIteration:
                    is_running = False
                    window.set_widget_value('play_button', False)

        # ── Title strip ──────────────────────────────────────────────────────
        alg_label = cur_algorithm or algorithm
        screen.blit(fonts['title'].render(
            f'{alg_label}  ·  Minimum Spanning Tree  ·  Step-by-step', True, TEXT),
            (30, 14))
        screen.blit(fonts['small'].render(
            f'Nodes: {n_input}   ·   Density: {density}   ·   Delay: {delay_s:.2f}s',
            True, DIM_TEXT), (30, 42))

        # ── Visualization area ───────────────────────────────────────────────
        VIZ_Y, VIZ_H = 65, 585
        PANEL_X = 730

        if current_state is not None and graph is not None:
            # Draw graph
            mst_edges   = current_state.get('mst_edges', [])
            cand_edge   = current_state.get('candidate_edge')
            rej_edges   = current_state.get('rejected_edges')
            visited     = current_state.get('visited')
            in_heap     = current_state.get('in_heap')
            current_nd  = current_state.get('current_node')

            draw_graph_base(screen, fonts, graph, positions, n,
                            mst_edges, cand_edge, rej_edges, visited,
                            current_nd, in_heap)

            # Legend
            draw_legend(screen, fonts, cur_algorithm, 30, VIZ_Y + VIZ_H - 115)

            # Right panel
            if cur_algorithm == 'Kruskal':
                draw_kruskal_panel(screen, fonts, current_state,
                                   PANEL_X, VIZ_Y, SCREEN_W - PANEL_X - 10, VIZ_H)
            else:
                draw_prim_panel(screen, fonts, current_state,
                                PANEL_X, VIZ_Y, SCREEN_W - PANEL_X - 10, VIZ_H)
        else:
            ph = fonts['base'].render(
                'Configure controls below and press ▶ Play', True, DIM_TEXT)
            screen.blit(ph, ph.get_rect(center=(SCREEN_W // 2, VIZ_Y + VIZ_H // 2)))

        # ── Controls strip ───────────────────────────────────────────────────
        pygame.draw.rect(screen, CTRL_BG, (0, 654, SCREEN_W, SCREEN_H - 654))
        pygame.draw.line(screen, GRID_LINE, (0, 654), (SCREEN_W, 654), 1)
        window.render()

        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()