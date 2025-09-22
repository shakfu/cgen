#!/usr/bin/env python3
"""
Conway's Game of Life - C-Compatible Implementation

A cellular automaton simulation implementing Conway's Game of Life rules.
This version is designed to be compatible with CGen for C translation.

Rules:
1. Any live cell with 2 or 3 live neighbors survives
2. Any dead cell with exactly 3 live neighbors becomes alive
3. All other live cells die in the next generation
4. All other dead cells stay dead

Features:
- Grid-based cellular automaton
- Multiple preset patterns (glider, blinker, toad, beacon)
- Step-by-step evolution simulation
- Statistics tracking (generation count, live cells)
- ASCII visualization
- Pattern initialization and manipulation

This implementation uses only static Python features suitable for C translation:
- No classes or complex object-oriented features
- Simple data structures (lists as 2D arrays)
- Basic control flow with while loops
- No dynamic memory allocation patterns
- Static typing throughout
"""

from typing import List, Tuple

# Grid dimensions
GRID_WIDTH: int = 40
GRID_HEIGHT: int = 20

# Cell states
DEAD: int = 0
ALIVE: int = 1

# Pattern definitions - coordinates for initial live cells
GLIDER_PATTERN: List[Tuple[int, int]] = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]
BLINKER_PATTERN: List[Tuple[int, int]] = [(1, 0), (1, 1), (1, 2)]
TOAD_PATTERN: List[Tuple[int, int]] = [(1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2)]
BEACON_PATTERN: List[Tuple[int, int]] = [(0, 0), (1, 0), (0, 1), (2, 3), (3, 2), (3, 3)]


def create_empty_grid(width: int, height: int) -> List[List[int]]:
    """Create an empty grid filled with dead cells."""
    grid: List[List[int]] = []
    i: int = 0
    while i < height:
        row: List[int] = []
        j: int = 0
        while j < width:
            row.append(DEAD)
            j = j + 1
        grid.append(row)
        i = i + 1
    return grid


def copy_grid(source: List[List[int]], width: int, height: int) -> List[List[int]]:
    """Create a deep copy of the grid."""
    new_grid: List[List[int]] = []
    i: int = 0
    while i < height:
        row: List[int] = []
        j: int = 0
        while j < width:
            row.append(source[i][j])
            j = j + 1
        new_grid.append(row)
        i = i + 1
    return new_grid


def set_cell(grid: List[List[int]], x: int, y: int, state: int, width: int, height: int) -> None:
    """Set the state of a cell at coordinates (x, y)."""
    if x >= 0 and x < width and y >= 0 and y < height:
        grid[y][x] = state


def get_cell(grid: List[List[int]], x: int, y: int, width: int, height: int) -> int:
    """Get the state of a cell at coordinates (x, y)."""
    if x >= 0 and x < width and y >= 0 and y < height:
        return grid[y][x]
    return DEAD


def count_live_neighbors(grid: List[List[int]], x: int, y: int, width: int, height: int) -> int:
    """Count the number of live neighbors around a cell."""
    count: int = 0

    # Check all 8 neighboring positions
    dx: int = -1
    while dx <= 1:
        dy: int = -1
        while dy <= 1:
            # Skip the center cell
            if dx != 0 or dy != 0:
                neighbor_x: int = x + dx
                neighbor_y: int = y + dy
                if get_cell(grid, neighbor_x, neighbor_y, width, height) == ALIVE:
                    count = count + 1
            dy = dy + 1
        dx = dx + 1

    return count


def apply_game_rules(current_state: int, live_neighbors: int) -> int:
    """Apply Conway's Game of Life rules to determine next state."""
    if current_state == ALIVE:
        # Live cell with 2 or 3 neighbors survives
        if live_neighbors == 2 or live_neighbors == 3:
            return ALIVE
        else:
            return DEAD
    else:
        # Dead cell with exactly 3 neighbors becomes alive
        if live_neighbors == 3:
            return ALIVE
        else:
            return DEAD


def evolve_generation(grid: List[List[int]], width: int, height: int) -> List[List[int]]:
    """Evolve the grid to the next generation."""
    new_grid: List[List[int]] = create_empty_grid(width, height)

    y: int = 0
    while y < height:
        x: int = 0
        while x < width:
            current_state: int = get_cell(grid, x, y, width, height)
            neighbors: int = count_live_neighbors(grid, x, y, width, height)
            new_state: int = apply_game_rules(current_state, neighbors)
            set_cell(new_grid, x, y, new_state, width, height)
            x = x + 1
        y = y + 1

    return new_grid


def count_live_cells(grid: List[List[int]], width: int, height: int) -> int:
    """Count the total number of live cells in the grid."""
    count: int = 0
    y: int = 0
    while y < height:
        x: int = 0
        while x < width:
            if get_cell(grid, x, y, width, height) == ALIVE:
                count = count + 1
            x = x + 1
        y = y + 1
    return count


def print_grid(grid: List[List[int]], width: int, height: int) -> None:
    """Print the grid to stdout using ASCII characters."""
    # Print top border
    print("+", end="")
    i: int = 0
    while i < width:
        print("-", end="")
        i = i + 1
    print("+")

    # Print grid content
    y: int = 0
    while y < height:
        print("|", end="")
        x: int = 0
        while x < width:
            if get_cell(grid, x, y, width, height) == ALIVE:
                print("*", end="")
            else:
                print(" ", end="")
            x = x + 1
        print("|")
        y = y + 1

    # Print bottom border
    print("+", end="")
    i = 0
    while i < width:
        print("-", end="")
        i = i + 1
    print("+")


def initialize_pattern(grid: List[List[int]], pattern: List[Tuple[int, int]],
                      offset_x: int, offset_y: int, width: int, height: int) -> None:
    """Initialize a pattern on the grid at the specified offset."""
    i: int = 0
    pattern_length: int = len(pattern)
    while i < pattern_length:
        coord: Tuple[int, int] = pattern[i]
        x: int = coord[0] + offset_x
        y: int = coord[1] + offset_y
        set_cell(grid, x, y, ALIVE, width, height)
        i = i + 1


def clear_grid(grid: List[List[int]], width: int, height: int) -> None:
    """Clear all cells in the grid."""
    y: int = 0
    while y < height:
        x: int = 0
        while x < width:
            set_cell(grid, x, y, DEAD, width, height)
            x = x + 1
        y = y + 1


def grids_equal(grid1: List[List[int]], grid2: List[List[int]], width: int, height: int) -> int:
    """Check if two grids are identical. Returns 1 if equal, 0 if not."""
    y: int = 0
    while y < height:
        x: int = 0
        while x < width:
            if get_cell(grid1, x, y, width, height) != get_cell(grid2, x, y, width, height):
                return 0
            x = x + 1
        y = y + 1
    return 1


def detect_stilllife(grid: List[List[int]], width: int, height: int) -> int:
    """Detect if the grid is in a still life state. Returns 1 if still, 0 if not."""
    next_gen: List[List[int]] = evolve_generation(grid, width, height)
    is_equal: int = grids_equal(grid, next_gen, width, height)
    return is_equal


def detect_oscillator_period(grid: List[List[int]], width: int, height: int, max_period: int) -> int:
    """Detect oscillator period. Returns period if found, 0 if none detected."""
    states: List[List[List[int]]] = []
    current: List[List[int]] = copy_grid(grid, width, height)

    generation: int = 0
    while generation < max_period:
        # Check if current state matches any previous state
        i: int = 0
        while i < len(states):
            if grids_equal(current, states[i], width, height):
                return generation - i
            i = i + 1

        # Store current state
        states.append(copy_grid(current, width, height))

        # Evolve to next generation
        current = evolve_generation(current, width, height)
        generation = generation + 1

    return 0


def simulate_pattern(pattern: List[Tuple[int, int]], pattern_name: str,
                    generations: int, width: int, height: int) -> None:
    """Simulate a specific pattern for the given number of generations."""
    print(f"Simulating {pattern_name} pattern:")
    print("=" * 50)

    # Initialize grid with pattern
    grid: List[List[int]] = create_empty_grid(width, height)
    offset_x: int = width // 2 - 5
    offset_y: int = height // 2 - 5
    initialize_pattern(grid, pattern, offset_x, offset_y, width, height)

    # Initial state
    print(f"Generation 0:")
    live_count: int = count_live_cells(grid, width, height)
    print(f"Live cells: {live_count}")
    print_grid(grid, width, height)
    print()

    # Evolve through generations
    gen: int = 1
    while gen <= generations:
        grid = evolve_generation(grid, width, height)
        live_count = count_live_cells(grid, width, height)

        print(f"Generation {gen}:")
        print(f"Live cells: {live_count}")
        print_grid(grid, width, height)
        print()

        # Check for extinction
        if live_count == 0:
            print(f"Pattern extinct at generation {gen}")
            break

        # Check for still life
        if detect_stilllife(grid, width, height):
            print(f"Still life detected at generation {gen}")
            break

        gen = gen + 1


def run_pattern_analysis() -> None:
    """Run analysis on different patterns."""
    print("Conway's Game of Life - Pattern Analysis")
    print("=" * 60)
    print()

    # Analyze glider
    print("GLIDER ANALYSIS:")
    print("-" * 30)
    grid: List[List[int]] = create_empty_grid(GRID_WIDTH, GRID_HEIGHT)
    initialize_pattern(grid, GLIDER_PATTERN, 5, 5, GRID_WIDTH, GRID_HEIGHT)

    period: int = detect_oscillator_period(grid, GRID_WIDTH, GRID_HEIGHT, 10)
    if period > 0:
        print(f"Glider period: {period} generations")
    else:
        print("Glider is a spaceship (travels)")

    live_cells: int = count_live_cells(grid, GRID_WIDTH, GRID_HEIGHT)
    print(f"Initial live cells: {live_cells}")
    print()

    # Analyze blinker
    print("BLINKER ANALYSIS:")
    print("-" * 30)
    clear_grid(grid, GRID_WIDTH, GRID_HEIGHT)
    initialize_pattern(grid, BLINKER_PATTERN, 10, 10, GRID_WIDTH, GRID_HEIGHT)

    period = detect_oscillator_period(grid, GRID_WIDTH, GRID_HEIGHT, 10)
    if period > 0:
        print(f"Blinker period: {period} generations")
    else:
        print("Blinker behavior unclear")

    live_cells = count_live_cells(grid, GRID_WIDTH, GRID_HEIGHT)
    print(f"Initial live cells: {live_cells}")
    print()

    # Analyze beacon
    print("BEACON ANALYSIS:")
    print("-" * 30)
    clear_grid(grid, GRID_WIDTH, GRID_HEIGHT)
    initialize_pattern(grid, BEACON_PATTERN, 15, 8, GRID_WIDTH, GRID_HEIGHT)

    period = detect_oscillator_period(grid, GRID_WIDTH, GRID_HEIGHT, 10)
    if period > 0:
        print(f"Beacon period: {period} generations")
    else:
        print("Beacon behavior unclear")

    live_cells = count_live_cells(grid, GRID_WIDTH, GRID_HEIGHT)
    print(f"Initial live cells: {live_cells}")
    print()


def run_comprehensive_demo() -> None:
    """Run comprehensive demonstration of Game of Life patterns."""
    print("Conway's Game of Life - Comprehensive Demo")
    print("=" * 60)
    print()

    # Demo each pattern
    simulate_pattern(BLINKER_PATTERN, "Blinker", 3, 15, 10)
    simulate_pattern(TOAD_PATTERN, "Toad", 3, 20, 12)
    simulate_pattern(BEACON_PATTERN, "Beacon", 3, 20, 12)
    simulate_pattern(GLIDER_PATTERN, "Glider", 8, 25, 15)

    # Run pattern analysis
    run_pattern_analysis()


def calculate_statistics(grid: List[List[int]], width: int, height: int) -> None:
    """Calculate and display grid statistics."""
    live_count: int = count_live_cells(grid, width, height)
    total_cells: int = width * height
    dead_count: int = total_cells - live_count

    print(f"Grid Statistics:")
    print(f"  Dimensions: {width} x {height}")
    print(f"  Total cells: {total_cells}")
    print(f"  Live cells: {live_count}")
    print(f"  Dead cells: {dead_count}")

    if total_cells > 0:
        live_percentage: float = (live_count * 100.0) / total_cells
        print(f"  Live percentage: {live_percentage:.1f}%")


def create_random_pattern(grid: List[List[int]], width: int, height: int, density: int) -> None:
    """Create a pseudo-random pattern with specified density (0-100)."""
    # Simple pseudo-random number generator
    seed: int = 12345

    y: int = 0
    while y < height:
        x: int = 0
        while x < width:
            # Generate pseudo-random number
            seed = (seed * 1103515245 + 12345) % (2 ** 31)
            random_val: int = (seed % 100)

            if random_val < density:
                set_cell(grid, x, y, ALIVE, width, height)
            else:
                set_cell(grid, x, y, DEAD, width, height)
            x = x + 1
        y = y + 1


def run_evolution_study() -> None:
    """Run a study of evolution from random initial conditions."""
    print("Evolution Study - Random Initial Conditions")
    print("=" * 60)
    print()

    # Create random initial state
    grid: List[List[int]] = create_empty_grid(GRID_WIDTH, GRID_HEIGHT)
    create_random_pattern(grid, GRID_WIDTH, GRID_HEIGHT, 25)  # 25% density

    print("Initial random state (25% density):")
    calculate_statistics(grid, GRID_WIDTH, GRID_HEIGHT)
    print_grid(grid, GRID_WIDTH, GRID_HEIGHT)
    print()

    # Track evolution
    generation: int = 0
    max_generations: int = 20
    previous_live_count: int = count_live_cells(grid, GRID_WIDTH, GRID_HEIGHT)

    while generation < max_generations:
        grid = evolve_generation(grid, GRID_WIDTH, GRID_HEIGHT)
        generation = generation + 1

        current_live_count: int = count_live_cells(grid, GRID_WIDTH, GRID_HEIGHT)

        print(f"Generation {generation}:")
        print(f"  Live cells: {current_live_count} (change: {current_live_count - previous_live_count})")

        # Show grid every 5 generations or if significant change
        change: int = current_live_count - previous_live_count
        if change < 0:
            change = -change

        if generation % 5 == 0 or change > 5 or current_live_count == 0:
            print_grid(grid, GRID_WIDTH, GRID_HEIGHT)
            print()

        # Check for extinction
        if current_live_count == 0:
            print("Population extinct!")
            break

        # Check for stability
        if current_live_count == previous_live_count:
            if detect_stilllife(grid, GRID_WIDTH, GRID_HEIGHT):
                print("Population stabilized (still life)")
                break

        previous_live_count = current_live_count


def main() -> None:
    """Main function to run Game of Life demonstration."""
    print("Starting Conway's Game of Life simulation...")
    print()

    # Run comprehensive demo
    run_comprehensive_demo()

    # Run evolution study
    run_evolution_study()

    print("Game of Life simulation completed!")


if __name__ == "__main__":
    main()