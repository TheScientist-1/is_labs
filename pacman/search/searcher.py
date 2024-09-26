class Searcher:
    def __init__(self, maze, search_algorithm, initial_position):
        self.maze = maze
        self.search_algorithm = search_algorithm
        self.path = None
        self.current_position = initial_position

    def get_next_state(self):
        if self.path is None:
            raise ValueError("Path has not been initialized yet")
        return next(self.path)

    @staticmethod
    def gen_path(path):
        for cell in path:
            yield {
                'pacman': cell
            }
        yield None

    def set_target(self, destination):
        self.path = None
        path = self.search_algorithm.apply(self.maze, self.current_position, destination)
        if path is None:
            raise ValueError(f"Destination {destination} is unreachable from source {self.current_position}")
        self.path = self.gen_path(path)
        self.current_position = destination
