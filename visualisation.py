import pygame
import math
import json
import random

WIDTH, HEIGHT = 1200, 900
BG_COLOR = (10, 10, 15)
NODE_COLOR = (50, 100, 180)
NODE_HOVER_COLOR = (255, 255, 255)
EDGE_HIGHLIGHT_COLOR = (0, 255, 200) 
NODE_RADIUS = 2

REPULSION_STRENGTH = 6500.0
SPRING_STRENGTH = 0.06
REST_LENGTH = 45.0
GRAVITY_STRENGTH = 0.08 
DAMPING = 0.8
MAX_SPEED = 5.0
OPTIMIZATION_THRESHOLD = 300**2 

try:
    with open("storing_project/megagraph.json", "r", encoding="utf-8") as f:
        graph_data = json.load(f)
    
    nodes_dict = {node["id"]: {"label": node["label"]} for node in graph_data["nodes"]}
    graph_data["nodes"] = nodes_dict
    if "edges_by_node" in graph_data:
        graph_data["edges"] = graph_data.pop("edges_by_node")
except Exception:
    graph_data = {"nodes": {str(i): {"label": f"Knowledge Node {i}"} for i in range(500)}, "edges": {}}
    for i in range(500):
        graph_data["edges"][str(i)] = [str(random.randint(0, 499)) for _ in range(random.randint(1, 3))]

nodes = list(graph_data["nodes"].keys())
node_positions = {}
node_velocities = {}
temperature = 1.0
paused = False 

def reset_layout():
    global temperature, paused
    temperature = 1.0
    paused = False
    for node in nodes:
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, 250)
        node_positions[node] = [r * math.cos(angle), r * math.sin(angle)]
        node_velocities[node] = [0.0, 0.0]

reset_layout()

def apply_force_directed_layout(force=False):
    global temperature
    if not force and (paused or temperature < 0.005): 
        return 

    forces = {node: [0.0, 0.0] for node in nodes}

    pos_list = [node_positions[n] for n in nodes]
    for i in range(len(nodes)):
        ax, ay = pos_list[i]
        for j in range(i + 1, len(nodes)):
            bx, by = pos_list[j]
            dx, dy = ax - bx, ay - by
            dist_sq = dx * dx + dy * dy + 1.0
            
            if dist_sq < OPTIMIZATION_THRESHOLD:
                force = REPULSION_STRENGTH / dist_sq
                dist = math.sqrt(dist_sq)
                fx, fy = (dx / dist) * force, (dy / dist) * force
                forces[nodes[i]][0] += fx
                forces[nodes[i]][1] += fy
                forces[nodes[j]][0] -= fx
                forces[nodes[j]][1] -= fy

    for from_node, neighbors in graph_data["edges"].items():
        if from_node not in node_positions: continue
        ax, ay = node_positions[from_node]
        for to_node in neighbors:
            if to_node not in node_positions: continue
            bx, by = node_positions[to_node]
            dx, dy = bx - ax, by - ay
            dist = math.sqrt(dx * dx + dy * dy) + 0.1
            force = SPRING_STRENGTH * (dist - REST_LENGTH)
            fx, fy = (dx / dist) * force, (dy / dist) * force
            forces[from_node][0] += fx
            forces[from_node][1] += fy
            forces[to_node][0] -= fx
            forces[to_node][1] -= fy

    for node in nodes:
        fx, fy = forces[node]
        ax, ay = node_positions[node]
        fx -= ax * GRAVITY_STRENGTH
        fy -= ay * GRAVITY_STRENGTH

        vx, vy = node_velocities[node]
        vx = (vx + fx) * DAMPING * temperature
        vy = (vy + fy) * DAMPING * temperature

        speed = math.hypot(vx, vy)
        if speed > MAX_SPEED:
            vx, vy = (vx / speed) * MAX_SPEED, (vy / speed) * MAX_SPEED

        node_positions[node][0] += vx
        node_positions[node][1] += vy
        node_velocities[node] = [vx, vy]

    temperature *= 0.994 

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clean Knowledge Map - Hover to Reveal Connections")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 13)

cam_x, cam_y, zoom = 0, 0, 1.0
dragging = False

running = True
while running:
    screen.fill(BG_COLOR)
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: paused = not paused
            if event.key == pygame.K_r: reset_layout()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: dragging = True
            if event.button == 4: zoom *= 1.1
            if event.button == 5: zoom /= 1.1
            last_mouse = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONUP: dragging = False
        
        if event.type == pygame.MOUSEMOTION and dragging:
            cam_x += (last_mouse[0] - mx) / zoom
            cam_y += (last_mouse[1] - my) / zoom
            last_mouse = (mx, my)

    apply_force_directed_layout()

    def to_screen(pos):
        return int((pos[0] - cam_x) * zoom + WIDTH//2), int((pos[1] - cam_y) * zoom + HEIGHT//2)

    hovered_node = None
    for n in nodes:
        sx, sy = to_screen(node_positions[n])
        if math.hypot(mx - sx, my - sy) < 5 * zoom:
            hovered_node = n
            break

    if hovered_node:
        p1 = to_screen(node_positions[hovered_node])
        
        if hovered_node in graph_data["edges"]:
            for neighbor in graph_data["edges"][hovered_node]:
                if neighbor in node_positions:
                    p2 = to_screen(node_positions[neighbor])
                    pygame.draw.aaline(screen, EDGE_HIGHLIGHT_COLOR, p1, p2)
        
        for start_node, neighbors in graph_data["edges"].items():
            if hovered_node in neighbors:
                p_start = to_screen(node_positions[start_node])
                pygame.draw.aaline(screen, EDGE_HIGHLIGHT_COLOR, p_start, p1)

    for n in nodes:
        sx, sy = to_screen(node_positions[n])
        if -20 < sx < WIDTH+20 and -20 < sy < HEIGHT+20:
            if n == hovered_node:
                color = NODE_HOVER_COLOR
                rad = max(4, int(4 * zoom))
            else:
                color = NODE_COLOR
                rad = max(1, int(NODE_RADIUS * zoom))
            
            pygame.draw.circle(screen, color, (sx, sy), rad)

    if hovered_node:
        sx, sy = to_screen(node_positions[hovered_node])
        label_str = graph_data["nodes"][hovered_node]["label"]
        txt_surf = font.render(label_str, True, (255, 255, 255))
        
        bg_rect = txt_surf.get_rect(topleft=(sx + 15, sy - 10))
        pygame.draw.rect(screen, (30, 40, 60), bg_rect.inflate(10, 4), border_radius=3)
        pygame.draw.rect(screen, EDGE_HIGHLIGHT_COLOR, bg_rect.inflate(10, 4), width=1, border_radius=3)
        
        screen.blit(txt_surf, (sx + 15, sy - 10))

    ui_text = f"Nodes: {len(nodes)} | SPACE: {'Resume' if paused else 'Pause'} | R: Reset"
    info = font.render(ui_text, True, (100, 110, 130))
    screen.blit(info, (20, HEIGHT - 30))
    if paused:
        p_txt = font.render("SIMULATION PAUSED", True, (255, 100, 100))
        screen.blit(p_txt, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()