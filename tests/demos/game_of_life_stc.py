"""
Conway's Game of Life - STC Enhanced Version

This version is designed to work with STC (Smart Template Containers)
for high-performance, type-safe container operations.
"""

def create_grid_stc(width: int, height: int):
    """Create an empty Game of Life grid using STC containers."""
    grid = []
    for i in range(height):
        row = []
        for j in range(width):
            row.append(0)
        grid.append(row)
    return grid

def set_cell_stc(grid, x: int, y: int, state: int):
    """Set a cell state in the grid."""
    if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
        grid[y][x] = state

def get_cell_stc(grid, x: int, y: int) -> int:
    """Get a cell state from the grid."""
    if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
        return grid[y][x]
    return 0

def count_neighbors_stc(grid, x: int, y: int) -> int:
    """Count live neighbors around a cell."""
    count = 0
    neighbors = [
        [-1, -1], [-1, 0], [-1, 1],
        [0, -1],           [0, 1],
        [1, -1],  [1, 0],  [1, 1]
    ]

    for neighbor in neighbors:
        nx = x + neighbor[0]
        ny = y + neighbor[1]
        if get_cell_stc(grid, nx, ny) == 1:
            count += 1

    return count

def evolve_stc(grid) -> bool:
    """Evolve the grid one generation and return if any changes occurred."""
    height = len(grid)
    if height == 0:
        return False

    width = len(grid[0])
    new_grid = create_grid_stc(width, height)
    changes = False

    for y in range(height):
        for x in range(width):
            current = get_cell_stc(grid, x, y)
            neighbors = count_neighbors_stc(grid, x, y)

            # Apply Game of Life rules
            if current == 1:  # Alive
                if neighbors == 2 or neighbors == 3:
                    set_cell_stc(new_grid, x, y, 1)
                else:
                    set_cell_stc(new_grid, x, y, 0)
                    changes = True
            else:  # Dead
                if neighbors == 3:
                    set_cell_stc(new_grid, x, y, 1)
                    changes = True
                else:
                    set_cell_stc(new_grid, x, y, 0)

    # Copy new grid back to original
    for y in range(height):
        for x in range(width):
            grid[y][x] = new_grid[y][x]

    return changes

def count_live_cells_stc(grid) -> int:
    """Count total live cells in the grid."""
    count = 0
    for row in grid:
        for cell in row:
            if cell == 1:
                count += 1
    return count

def initialize_pattern_stc(grid, pattern, offset_x: int, offset_y: int):
    """Initialize a pattern in the grid."""
    for coord in pattern:
        x = coord[0] + offset_x
        y = coord[1] + offset_y
        set_cell_stc(grid, x, y, 1)

def run_simulation_stc():
    """Run a simple Game of Life simulation with STC containers."""
    # Grid dimensions
    width = 20
    height = 15

    # Create grid
    grid = create_grid_stc(width, height)

    # Blinker pattern (oscillates with period 2)
    blinker = [[0, 1], [1, 1], [2, 1]]
    initialize_pattern_stc(grid, blinker, 5, 5)

    # Glider pattern (moves diagonally)
    glider = [[1, 0], [2, 1], [0, 2], [1, 2], [2, 2]]
    initialize_pattern_stc(grid, glider, 10, 8)

    # Run simulation
    for generation in range(10):
        live_cells = count_live_cells_stc(grid)
        print(f"Generation {generation}: {live_cells} live cells")

        # Evolve to next generation
        changes = evolve_stc(grid)
        if not changes:
            print("Simulation stabilized - no more changes")
            break

    print("Simulation complete")

def main():
    """Main function to run the Game of Life simulation."""
    print("Starting Conway's Game of Life with STC containers...")
    run_simulation_stc()
    print("Game of Life simulation completed!")

if __name__ == "__main__":
    main()