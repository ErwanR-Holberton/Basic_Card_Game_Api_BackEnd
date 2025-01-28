class Phase:
    def __init__(self):
        self.phases = ["Draw", "Preparation", "Reveal", "Action", "Resolve", "Discard"]
        self.timers = [10, 30, 10, 20, 10, 15]
        self.current_index = 0  # Start at the first phase

    def next_phase(self):
        self.current_index = (self.current_index + 1) % len(self.phases)  # Increment and wrap around

    @property
    def current_phase(self):
        return self.phases[self.current_index]  # Return the current phase

    def is_phase(self, phase_name):
        return self.current_phase.lower() == phase_name.lower()  # Case-insensitive comparison

    def timer(self):
        return self.timers[self.current_index] #return timer for current phase
