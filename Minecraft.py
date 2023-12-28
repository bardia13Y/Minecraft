import pygame
import random

last_log_time = 0
log_interval = 3000  # 3000 milliseconds (3 seconds)

# Load Steve image and scale it to 32x32  
steve_image = pygame.image.load('steve.png')
steve_image = pygame.transform.scale(steve_image, (32, 32))  # Scale the image to 32x32

# Initialize Pygame
pygame.init()

# Constants
WHITE = (255, 255, 255)
CHUNK_SIZE = 40  # Number of blocks in a chunk
BLOCK_SIZE = 32  # Size of each block

# Define the screen wrapping threshold
wrap_threshold = BLOCK_SIZE * 0.3  # 0.3 blocks from the edge

# Screen dimensions
SCREEN_WIDTH = CHUNK_SIZE * BLOCK_SIZE  # Width of one chunk
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('2D Minecraft-Like Game with Improved Physics')

# Load grass block image
grass_image = pygame.image.load('grass.png')

# Player settings
player_size = (32, 32)  # Player size
player_pos = [50, 300]
player_speed = 0.5  # Updated player speed
player_velocity = 0
gravity = 0.01  # Increased gravity for more realistic jumping
jump_height = -2  # Increased jump height
is_jumping = False

# Terrain generation
def generate_terrain(chunk_index):
    terrain = []
    for i in range(CHUNK_SIZE):
        height = random.randint(1, 4)  # Random height for terrain variation
        for j in range(height):
            terrain.append((i * BLOCK_SIZE + chunk_index * CHUNK_SIZE * BLOCK_SIZE, SCREEN_HEIGHT - (j + 1) * BLOCK_SIZE))
    
    print(f"Generated terrain for chunk {chunk_index}")  # Log when new terrain is generated
    return terrain

# Modify the initial chunk creation
chunks = {i: generate_terrain(i) for i in range(-1, 2)}  # Generate initial chunks -1, 0, and 1

# After generating initial chunk
max_height = max([block[1] for block in chunks[0]])
player_pos[1] = max_height - player_size[1] - 10  # Spawn above the highest block

# Check if player is standing on ground
def is_on_ground(player_rect, blocks):
    for block in blocks:
        if player_rect.colliderect(pygame.Rect(*block, BLOCK_SIZE, BLOCK_SIZE)):
            return True
    return False

# Game loop
running = True
current_chunk_index = 0
running = True
current_chunk_index = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement and chunk loading
    keys = pygame.key.get_pressed()

    new_x_pos = player_pos[0] + (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed
    player_rect = pygame.Rect(new_x_pos, player_pos[1], *player_size)

    # Preload adjacent chunks
    for offset in [-1, 0, 1]:
        adjacent_chunk_index = current_chunk_index + offset
        if adjacent_chunk_index not in chunks:
            chunks[adjacent_chunk_index] = generate_terrain(adjacent_chunk_index)



    # Generate new chunk if needed when wrapping
    if current_chunk_index not in chunks:
        chunks[current_chunk_index] = generate_terrain(current_chunk_index)
        # Adjust player's vertical position to avoid falling
        player_pos[1] = max([block[1] for block in chunks[current_chunk_index]]) - player_size[1] - 10

    # Calculate current chunk index
    chunk_index = int(player_pos[0] // (CHUNK_SIZE * BLOCK_SIZE))

    # Check if player has moved to a new chunk and generate terrain if needed
    if chunk_index != current_chunk_index:
        current_chunk_index = chunk_index
        if current_chunk_index not in chunks:
            chunks[current_chunk_index] = generate_terrain(current_chunk_index)

    # Check horizontal collision
    collision = False
    for block in chunks[current_chunk_index]:
        if player_rect.colliderect(pygame.Rect(*block, BLOCK_SIZE, BLOCK_SIZE)):
            collision = True
            break

    if not collision:
        player_pos[0] = new_x_pos
            
    # Define ground blocks for collision detection
    ground_blocks = [pygame.Rect(*block, BLOCK_SIZE, BLOCK_SIZE) for block in chunks[current_chunk_index]]

    # Gravity and jumping
    player_rect = pygame.Rect(*player_pos, *player_size)

    # Apply gravity if player is not on ground or is jumping
    if not is_on_ground(player_rect, chunks[current_chunk_index]) or is_jumping:
        player_velocity += gravity
        player_pos[1] += player_velocity

        # Check vertical collision with ground
        player_rect = pygame.Rect(*player_pos, *player_size)
        ground_blocks = [pygame.Rect(*block, BLOCK_SIZE, BLOCK_SIZE) for block in chunks[current_chunk_index]]
        
        for block in ground_blocks:
            if player_rect.colliderect(block):
                if player_velocity > 0:  # Falling down
                    player_pos[1] = block.top - player_size[1]
                    player_velocity = 0
                    is_jumping = False
                elif player_velocity < 0:  # Going up
                    player_pos[1] = block.bottom
                    player_velocity = 0

    # Jumping logic
    if not is_jumping and keys[pygame.K_SPACE] and is_on_ground(player_rect, chunks[current_chunk_index]):
        is_jumping = True
        player_velocity = jump_height


    # Apply gravity
    player_velocity += gravity
    new_y_pos = player_pos[1] + player_velocity

    collision = False
    for block in ground_blocks:
        if player_rect.colliderect(block):
            collision = True
            if player_velocity > 0:  # Falling down
                player_pos[1] = block.top - player_size[1]
                player_velocity = 0
                is_jumping = False
            break

    if not collision:
        player_pos[1] = new_y_pos

    # Drawing
    screen.fill(WHITE)

    # Draw terrain for all chunks
    for chunk_idx, terrain in chunks.items():
        for block_pos in terrain:
            # Calculate the actual position to draw based on the current chunk index
            actual_x = block_pos[0] - (current_chunk_index - chunk_idx) * CHUNK_SIZE * BLOCK_SIZE
            actual_pos = (actual_x, block_pos[1])
            screen.blit(grass_image, actual_pos)

    # Draw the player using the Steve image
    screen.blit(steve_image, player_pos)

    pygame.display.flip()


pygame.quit()
