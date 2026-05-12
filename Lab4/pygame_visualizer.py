import os
import math
import time
import copy
import heapq
import random

import pygame

from display import Window, TextBox, SlideBox, DropdownBox, ButtonBox, TextButtonBox


# ─── Theme ────────────────────────────────────────────────────────────────────

BG          = (15, 15, 15)
PANEL_BG    = (26, 26, 26)
CTRL_BG     = (20, 20, 20)
TEXT        = (220, 220, 220)
DIM_TEXT    = (140, 140, 140)
HEADER_TEXT = (170, 170, 170)
GRID_LINE   = (55, 55, 55)
WIDGET_COLOR = (170, 170, 170)
DROPDOWN_BG  = (32, 32, 32)

UNVISITED    = (44, 44, 44)
VISITED      = (15, 110, 86)
CURRENT      = (186, 117, 23)
START_COLOR  = (24, 95, 165)
END_COLOR    = (121, 31, 31)
PATH_COLOR   = (29, 158, 117)

EDGE_DEFAULT = (68, 68, 68)
EDGE_CURRENT = (186, 117, 23)
EDGE_PATH    = (29, 158, 117)
EDGE_RELAX   = (220, 180, 60)

HIGHLIGHT_K  = (29, 158, 117)
HIGHLIGHT_IJ = (186, 117, 23)
UPDATE_FLASH = (0, 230, 180)

INF = float('inf')


# ─── Step generators ──────────────────────────────────────────────────────────

def dijkstra_steps(graph, start):
    """Yield ('init'|'visit'|'relax'|'done', current, distances, previous, visited, relax_target, updated)."""
    distances = {n: INF for n in graph}
    distances[start] = 0
    previous = {n: None for n in graph}
    heap = [(0, start)]
    visited = set()

    yield ('init', None, dict(distances), dict(previous), set(visited), None, None)

    while heap:
        current_dist, current_node = heapq.heappop(heap)
        if current_node in visited:
            continue
        visited.add(current_node)
        yield ('visit', current_node, dict(distances), dict(previous), set(visited), None, None)

        for neighbor, weight in graph[current_node]:
            if neighbor in visited:
                continue
            new_dist = current_dist + weight
            old_dist = distances[neighbor]
            updated = new_dist < old_dist
            if updated:
                distances[neighbor] = new_dist
                previous[neighbor] = current_node
                heapq.heappush(heap, (new_dist, neighbor))
            yield ('relax', current_node, dict(distances), dict(previous), set(visited), neighbor, updated)

    yield ('done', None, dict(distances), dict(previous), set(visited), None, None)


def floyd_warshall_steps(matrix):
    """Yield (k, i, j, updated, dist_snapshot)."""
    n = len(matrix)
    dist = [row[:] for row in matrix]
    yield (-1, -1, -1, False, [row[:] for row in dist])
    for k in range(n):
        for i in range(n):
            for j in range(n):
                updated = False
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    updated = True
                yield (k, i, j, updated, [row[:] for row in dist])


# ─── Graph utilities ──────────────────────────────────────────────────────────

def random_graph(n, density='Sparse', seed=None):
    """Build an undirected connected graph with random positive weights."""
    rng = random.Random(seed)
    graph = {i: [] for i in range(n)}

    if density == 'Sparse':
        edge_target = max(n - 1, int(n * 1.4))
    else:
        edge_target = n * (n - 1) // 2

    edges = set()
    nodes = list(range(n))
    rng.shuffle(nodes)
    for i in range(1, n):
        u = nodes[i]
        v = nodes[rng.randint(0, i - 1)]
        edges.add((min(u, v), max(u, v)))

    while len(edges) < edge_target:
        u = rng.randint(0, n - 1)
        v = rng.randint(0, n - 1)
        if u != v:
            edges.add((min(u, v), max(u, v)))

    for (u, v) in edges:
        w = rng.randint(1, 20)
        graph[u].append((v, w))
        graph[v].append((u, w))

    return graph


def graph_to_matrix(graph, n):
    matrix = [[INF] * n for _ in range(n)]
    for i in range(n):
        matrix[i][i] = 0
    for u in graph:
        for v, w in graph[u]:
            matrix[u][v] = w
    return matrix


def circular_positions(n, cx, cy, r):
    pos = {}
    for i in range(n):
        angle = 2 * math.pi * i / max(n, 1) - math.pi / 2
        pos[i] = (int(cx + r * math.cos(angle)), int(cy + r * math.sin(angle)))
    return pos


def get_path(previous, start, end):
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous.get(current)
    path.reverse()
    if not path or path[0] != start:
        return []
    return path


# ─── Dijkstra drawing ─────────────────────────────────────────────────────────

def draw_dijkstra(screen, fonts, state, graph, positions, start, end):
    step_type, current, distances, previous, visited, relax_target, updated = state
    n = len(graph)

    path_so_far = get_path(previous, start, end) if end in visited else []
    path_edges = set(zip(path_so_far, path_so_far[1:]))
    path_edges |= {(b, a) for (a, b) in path_edges}

    # Draw edges first
    drawn = set()
    for u in graph:
        for v, w in graph[u]:
            key = (min(u, v), max(u, v))
            if key in drawn:
                continue
            drawn.add(key)

            color = EDGE_DEFAULT
            width = 2
            if (u, v) in path_edges:
                color = EDGE_PATH
                width = 4
            elif step_type == 'relax' and (
                (u == current and v == relax_target) or (v == current and u == relax_target)
            ):
                color = EDGE_RELAX if updated else (110, 110, 110)
                width = 3
            elif current is not None and (u == current or v == current):
                color = EDGE_CURRENT
                width = 3

            pygame.draw.line(screen, color, positions[u], positions[v], width)

            mx = (positions[u][0] + positions[v][0]) // 2
            my = (positions[u][1] + positions[v][1]) // 2
            txt = fonts['small'].render(str(w), True, DIM_TEXT)
            bg_rect = txt.get_rect(center=(mx, my)).inflate(6, 2)
            pygame.draw.rect(screen, BG, bg_rect)
            screen.blit(txt, txt.get_rect(center=(mx, my)))

    # Draw nodes
    radius = max(14, min(24, 220 // max(n, 1)))
    for i in range(n):
        x, y = positions[i]
        if i in visited and i in path_so_far:
            color = PATH_COLOR
        elif i == current:
            color = CURRENT
        elif step_type == 'relax' and i == relax_target:
            color = EDGE_RELAX if updated else UNVISITED
        elif i in visited:
            color = VISITED
        elif i == start:
            color = START_COLOR
        elif i == end:
            color = END_COLOR
        else:
            color = UNVISITED

        pygame.draw.circle(screen, color, (x, y), radius)
        pygame.draw.circle(screen, (85, 85, 85), (x, y), radius, 2)

        label = fonts['node'].render(str(i), True, (240, 240, 240))
        screen.blit(label, label.get_rect(center=(x, y)))

        # Distance label outside the node
        d = distances[i]
        d_str = '∞' if d == INF else str(d)
        dist_color = (220, 200, 110) if d != INF else (110, 110, 110)
        d_label = fonts['small'].render(d_str, True, dist_color)
        # Position label radially outward
        cx, cy = positions[i]
        # approximate centre direction from screen centre
        ang = math.atan2(cy - 320, cx - 360)
        ox = int(math.cos(ang) * (radius + 14))
        oy = int(math.sin(ang) * (radius + 10))
        screen.blit(d_label, d_label.get_rect(center=(cx + ox, cy + oy)))


def draw_dijkstra_panel(screen, fonts, state, graph, start, end, panel_x, panel_y, panel_w, panel_h):
    step_type, current, distances, previous, visited, relax_target, updated = state

    pygame.draw.rect(screen, PANEL_BG, (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(screen, GRID_LINE, (panel_x, panel_y, panel_w, panel_h), 1)

    title = fonts['header'].render('Distance Table', True, HEADER_TEXT)
    screen.blit(title, (panel_x + 16, panel_y + 12))

    col_x = [panel_x + 18, panel_x + 90, panel_x + 180, panel_x + 280]
    y = panel_y + 44
    for i, h in enumerate(['Node', 'Distance', 'Previous', 'Visited']):
        screen.blit(fonts['small'].render(h, True, DIM_TEXT), (col_x[i], y))
    y += 20
    pygame.draw.line(screen, GRID_LINE, (panel_x + 12, y), (panel_x + panel_w - 12, y), 1)
    y += 6

    nodes = sorted(graph.keys())
    row_h = 22
    table_bottom = panel_y + panel_h - 90
    for node in nodes:
        if y + row_h > table_bottom:
            screen.blit(fonts['small'].render('…', True, DIM_TEXT), (col_x[0], y))
            break
        d = distances.get(node, INF)
        d_str = '∞' if d == INF else str(d)
        prev = previous.get(node)
        prev_str = str(prev) if prev is not None else '—'
        vis_str = '✓' if node in visited else ''

        bg_color = None
        if node == current:
            bg_color = (61, 44, 10)
        elif node in visited:
            bg_color = (10, 30, 23)
        if bg_color:
            pygame.draw.rect(screen, bg_color, (panel_x + 8, y - 2, panel_w - 16, row_h - 2))

        screen.blit(fonts['small'].render(str(node), True, TEXT), (col_x[0], y))
        screen.blit(fonts['small'].render(d_str, True, TEXT), (col_x[1], y))
        screen.blit(fonts['small'].render(prev_str, True, TEXT), (col_x[2], y))
        screen.blit(fonts['small'].render(vis_str, True, (100, 200, 150)), (col_x[3], y))
        y += row_h

    # Footer
    status_y = panel_y + panel_h - 70
    pygame.draw.line(screen, GRID_LINE, (panel_x + 12, status_y), (panel_x + panel_w - 12, status_y), 1)

    if step_type == 'init':
        status = 'Initializing — start = ' + str(start)
        status_color = DIM_TEXT
    elif step_type == 'visit':
        status = f'Visit node {current}'
        status_color = CURRENT
    elif step_type == 'relax':
        if updated:
            status = f'Relax {current}→{relax_target}: improved'
            status_color = EDGE_RELAX
        else:
            status = f'Relax {current}→{relax_target}: no change'
            status_color = DIM_TEXT
    elif step_type == 'done':
        d = distances.get(end, INF)
        if d == INF:
            status = f'Done. No path {start} → {end}'
            status_color = (200, 100, 100)
        else:
            status = f'Done. {start}→{end} cost = {d}'
            status_color = PATH_COLOR
    else:
        status = ''
        status_color = TEXT

    screen.blit(fonts['small'].render(status, True, status_color), (panel_x + 16, status_y + 10))

    if step_type == 'done':
        path = get_path(previous, start, end)
        path_str = ' → '.join(str(p) for p in path) if path else '(no path)'
        screen.blit(fonts['small'].render(f'Path: {path_str}', True, PATH_COLOR),
                    (panel_x + 16, status_y + 32))


# ─── Floyd-Warshall drawing ───────────────────────────────────────────────────

def draw_floyd_warshall(screen, fonts, state, n, area_x, area_y, area_w, area_h):
    k, i, j, updated, dist = state

    pad = 36
    cell_size = min((area_w - 2 * pad) // (n + 1), (area_h - 2 * pad) // (n + 1))
    cell_size = max(20, min(60, cell_size))

    grid_w = cell_size * (n + 1)
    grid_h = cell_size * (n + 1)
    grid_x = area_x + (area_w - grid_w) // 2
    grid_y = area_y + (area_h - grid_h) // 2

    max_val = 0
    for r in range(n):
        for c in range(n):
            if dist[r][c] != INF:
                max_val = max(max_val, dist[r][c])
    if max_val == 0:
        max_val = 1

    title = fonts['header'].render('Distance Matrix  (From ↓ / To →)', True, DIM_TEXT)
    screen.blit(title, (grid_x, grid_y - 28))

    # Top-left corner
    pygame.draw.rect(screen, PANEL_BG, (grid_x, grid_y, cell_size, cell_size))
    pygame.draw.rect(screen, GRID_LINE, (grid_x, grid_y, cell_size, cell_size), 1)

    # Column headers
    for c in range(n):
        cx = grid_x + (c + 1) * cell_size
        cy = grid_y
        header_bg = (10, 40, 30) if c == k else PANEL_BG
        pygame.draw.rect(screen, header_bg, (cx, cy, cell_size, cell_size))
        pygame.draw.rect(screen, GRID_LINE, (cx, cy, cell_size, cell_size), 1)
        col = HIGHLIGHT_K if c == k else TEXT
        label = fonts['small'].render(str(c), True, col)
        screen.blit(label, label.get_rect(center=(cx + cell_size // 2, cy + cell_size // 2)))

    # Row headers
    for r in range(n):
        cx = grid_x
        cy = grid_y + (r + 1) * cell_size
        header_bg = (10, 40, 30) if r == k else PANEL_BG
        pygame.draw.rect(screen, header_bg, (cx, cy, cell_size, cell_size))
        pygame.draw.rect(screen, GRID_LINE, (cx, cy, cell_size, cell_size), 1)
        col = HIGHLIGHT_K if r == k else TEXT
        label = fonts['small'].render(str(r), True, col)
        screen.blit(label, label.get_rect(center=(cx + cell_size // 2, cy + cell_size // 2)))

    # Cells
    cell_font = fonts['small'] if cell_size > 30 else fonts['tiny']
    for r in range(n):
        for c in range(n):
            cx = grid_x + (c + 1) * cell_size
            cy = grid_y + (r + 1) * cell_size
            val = dist[r][c]

            if val == INF:
                cell_color = (35, 35, 35)
            else:
                ratio = min(1.0, val / max_val) if max_val > 0 else 0
                rcol = int(50 + 195 * ratio)
                gcol = int(70 + 60 * (1 - ratio))
                bcol = int(40 * (1 - ratio))
                cell_color = (rcol, gcol, bcol)

            if (r == k or c == k) and not (r == k and c == k):
                # blend with relay tint
                cell_color = tuple(
                    int(cell_color[idx] * 0.65 + (29, 158, 117)[idx] * 0.35)
                    for idx in range(3)
                )

            pygame.draw.rect(screen, cell_color, (cx, cy, cell_size, cell_size))

            if i >= 0 and r == i and c == j:
                border_color = UPDATE_FLASH if updated else HIGHLIGHT_IJ
                pygame.draw.rect(screen, border_color, (cx, cy, cell_size, cell_size), 3)
            else:
                pygame.draw.rect(screen, GRID_LINE, (cx, cy, cell_size, cell_size), 1)

            if val == INF:
                txt = '∞'
                tc = (120, 120, 120)
            else:
                txt = str(val)
                tc = (240, 240, 240) if val > max_val * 0.45 else (30, 30, 30)
            if i >= 0 and r == i and c == j and updated:
                tc = (0, 30, 25)
            label = cell_font.render(txt, True, tc)
            screen.blit(label, label.get_rect(center=(cx + cell_size // 2, cy + cell_size // 2)))


def draw_fw_panel(screen, fonts, state, n, panel_x, panel_y, panel_w, panel_h):
    k, i, j, updated, dist = state

    pygame.draw.rect(screen, PANEL_BG, (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(screen, GRID_LINE, (panel_x, panel_y, panel_w, panel_h), 1)

    title = fonts['header'].render('Floyd-Warshall', True, HEADER_TEXT)
    screen.blit(title, (panel_x + 16, panel_y + 12))

    y = panel_y + 50
    if k == -1:
        screen.blit(fonts['base'].render('Initial matrix', True, TEXT), (panel_x + 16, y))
        y += 26
        screen.blit(fonts['small'].render(
            'Iterating relays k = 0 … n-1 and trying to', True, DIM_TEXT), (panel_x + 16, y))
        y += 18
        screen.blit(fonts['small'].render(
            'shorten dist[i][j] via dist[i][k] + dist[k][j].', True, DIM_TEXT), (panel_x + 16, y))
    else:
        screen.blit(fonts['base'].render(f'Relay  k = {k}', True, HIGHLIGHT_K), (panel_x + 16, y))
        y += 28
        screen.blit(fonts['base'].render(f'Cell  ({i}, {j})', True, HIGHLIGHT_IJ), (panel_x + 16, y))
        y += 28

        d_ij = dist[i][j]
        d_ik = dist[i][k]
        d_kj = dist[k][j]

        def fmt(v):
            return '∞' if v == INF else str(v)

        screen.blit(fonts['small'].render(
            f'dist[{i}][{k}] + dist[{k}][{j}]  =  {fmt(d_ik)} + {fmt(d_kj)}',
            True, DIM_TEXT), (panel_x + 16, y))
        y += 20
        if updated:
            screen.blit(fonts['small'].render(
                f'<  dist[{i}][{j}]  →  updated to {fmt(d_ij)}',
                True, UPDATE_FLASH), (panel_x + 16, y))
        else:
            screen.blit(fonts['small'].render(
                f'≥  dist[{i}][{j}] = {fmt(d_ij)}  (no change)',
                True, DIM_TEXT), (panel_x + 16, y))

    # Progress bar
    total = max(n * n * n, 1)
    if k >= 0:
        steps_done = k * n * n + i * n + j + 1
    else:
        steps_done = 0
    progress_y = panel_y + panel_h - 60
    screen.blit(fonts['small'].render(
        f'Step {steps_done} / {total}', True, DIM_TEXT), (panel_x + 16, progress_y))
    bar_x = panel_x + 16
    bar_y = progress_y + 22
    bar_w = panel_w - 32
    pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_w, 10))
    fill = int(bar_w * steps_done / total)
    pygame.draw.rect(screen, PATH_COLOR, (bar_x, bar_y, fill, 10))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    pygame.display.set_caption('Graph Algorithms Visualizer  ·  Dijkstra & Floyd-Warshall')

    SCREEN_W, SCREEN_H = 1200, 740
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()

    fonts = {
        'title':  pygame.font.SysFont('Arial', 22, bold=True),
        'header': pygame.font.SysFont('Arial', 16, bold=True),
        'base':   pygame.font.SysFont('Arial', 18),
        'small':  pygame.font.SysFont('Arial', 13),
        'tiny':   pygame.font.SysFont('Arial', 10),
        'node':   pygame.font.SysFont('Arial', 14, bold=True),
    }

    widget_font = pygame.font.SysFont('Arial', 18)

    window = Window(screen)

    # Layout (controls live in the strip y ≥ 660)
    CTRL_Y = 670
    window.add_widget('size_input',
                      TextBox((30, CTRL_Y, 80, 50), 'Nodes', WIDGET_COLOR, widget_font, '8'))
    window.add_widget('density_input',
                      DropdownBox((130, CTRL_Y, 130, 50), 'Density',
                                  WIDGET_COLOR, widget_font, ['Sparse', 'Dense'], DROPDOWN_BG))
    window.add_widget('algorithm_input',
                      DropdownBox((280, CTRL_Y, 200, 50), 'Algorithm',
                                  WIDGET_COLOR, widget_font,
                                  ['Dijkstra', 'Floyd-Warshall'], DROPDOWN_BG))
    window.add_widget('delay_slider',
                      SlideBox((500, CTRL_Y, 200, 50), 'Delay', WIDGET_COLOR, widget_font))
    window.add_widget('start_input',
                      TextBox((720, CTRL_Y, 70, 50), 'Start', WIDGET_COLOR, widget_font, '0'))
    window.add_widget('end_input',
                      TextBox((800, CTRL_Y, 70, 50), 'End', WIDGET_COLOR, widget_font, '7'))

    # Try to load play/stop images from Lab2; fall back to text button if missing
    script_dir = os.path.dirname(os.path.abspath(__file__))
    play_img = os.path.join(script_dir, '..', 'Lab2', 'res', 'playButton.png')
    stop_img = os.path.join(script_dir, '..', 'Lab2', 'res', 'stopButton.png')
    try:
        window.add_widget('play_button', ButtonBox((900, CTRL_Y + 5, 40, 40), play_img, stop_img))
    except (pygame.error, FileNotFoundError):
        window.add_widget('play_button',
                          TextButtonBox((900, CTRL_Y + 5, 80, 40),
                                        'Play', WIDGET_COLOR, widget_font))

    # Algorithm runtime state
    is_running = False
    steps_iter = None
    current_state = None
    last_step_time = 0.0
    graph = None
    positions = None
    n = 0
    start_node = 0
    end_node = 0
    cur_algorithm = None

    # Seed for reproducibility per "run"
    rng_seed = None

    running = True
    while running:
        screen.fill(BG)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            window.update(event)

        # Read inputs
        try:
            size_text = window.get_widget_value('size_input') or '8'
            n_input = max(2, min(15, int(size_text)))
        except ValueError:
            n_input = 8

        density = window.get_widget_value('density_input') or 'Sparse'
        algorithm = window.get_widget_value('algorithm_input') or 'Dijkstra'

        delay_norm = window.get_widget_value('delay_slider')  # 0..1
        if delay_norm is None:
            delay_norm = 0.3
        # Map to seconds: 0.02s (very fast) up to 1.5s
        delay_seconds = 0.02 + delay_norm * 1.48

        play_state = window.get_widget_value('play_button')

        # Start a new run on the rising edge of play
        if play_state and not is_running:
            n = n_input
            rng_seed = random.randint(0, 10**9)
            graph = random_graph(n, density, seed=rng_seed)

            try:
                start_node = max(0, min(n - 1, int(window.get_widget_value('start_input') or '0')))
            except ValueError:
                start_node = 0
            try:
                end_node = max(0, min(n - 1, int(window.get_widget_value('end_input') or str(n - 1))))
            except ValueError:
                end_node = n - 1

            # Layout: graph centred in the left half
            positions = circular_positions(n, 360, 340, min(220, 30 * n))

            cur_algorithm = algorithm
            if algorithm == 'Dijkstra':
                steps_iter = iter(dijkstra_steps(graph, start_node))
            else:
                matrix = graph_to_matrix(graph, n)
                steps_iter = iter(floyd_warshall_steps(matrix))

            try:
                current_state = next(steps_iter)
            except StopIteration:
                current_state = None
            is_running = True
            last_step_time = time.time()

        # User toggled play off — pause / reset
        if not play_state and is_running:
            is_running = False

        # Advance steps on a timer
        if is_running and steps_iter is not None:
            if time.time() - last_step_time >= delay_seconds:
                try:
                    current_state = next(steps_iter)
                    last_step_time = time.time()
                except StopIteration:
                    is_running = False
                    window.set_widget_value('play_button', False)

        # Title strip
        title = fonts['title'].render(
            f'{cur_algorithm or algorithm}  ·  Step-by-step visualization', True, TEXT)
        screen.blit(title, (30, 14))
        info = fonts['small'].render(
            f'Nodes: {n_input}   ·   Density: {density}   ·   Delay: {delay_seconds:.2f}s',
            True, DIM_TEXT)
        screen.blit(info, (30, 42))

        # Visualization
        VIZ_Y = 70
        VIZ_H = 580
        if current_state is not None and graph is not None:
            if cur_algorithm == 'Dijkstra':
                draw_dijkstra(screen, fonts, current_state, graph, positions,
                              start_node, end_node)
                draw_dijkstra_panel(screen, fonts, current_state, graph,
                                    start_node, end_node, 740, VIZ_Y, 440, VIZ_H)
            else:
                draw_floyd_warshall(screen, fonts, current_state, n, 0, VIZ_Y, 740, VIZ_H)
                draw_fw_panel(screen, fonts, current_state, n, 740, VIZ_Y, 440, VIZ_H)
        else:
            placeholder = fonts['base'].render(
                'Configure the controls below and press Play to start.',
                True, DIM_TEXT)
            screen.blit(placeholder, placeholder.get_rect(
                center=(SCREEN_W // 2, VIZ_Y + VIZ_H // 2)))

        # Controls strip background
        pygame.draw.rect(screen, CTRL_BG, (0, 654, SCREEN_W, SCREEN_H - 654))
        pygame.draw.line(screen, GRID_LINE, (0, 654), (SCREEN_W, 654), 1)

        window.render()
        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
