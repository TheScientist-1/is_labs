import yaml
import random
import copy
import pandas as pd
import sqlite3



class TimeSlot:
    def __init__(self, day: str, time: str):
        self.day: str = day
        self.time: str = time

    def __eq__(self, value: object) -> bool:
        return value is not None and self.day == value.day and self.time == value.time

    def __str__(self) -> str:
        return f"{self.day}, {self.time}"

    def __repr__(self) -> str:
        return f"{self.day}, {self.time}"

    def __hash__(self) -> int:
        return hash((self.day, self.time))


class Subject:
    def __init__(self, name, hours):
        self.name: str = name
        self.hours: int = hours

    def __eq__(self, value: object) -> bool:
        return (
            value is not None and self.name == value.name and self.hours == value.hours
        )

    def __str__(self) -> str:
        return f"{self.name}"

    def __hash__(self) -> int:
        return hash((self.name, self.hours))


class Group:
    def __init__(self, name, capacity, subject_names):
        self.name: str = name
        self.capacity: int = capacity
        self.subject_names: list[str] = [subject_name for subject_name in subject_names]
        self.subjects: list[Subject] = None

    def __eq__(self, value: object) -> bool:
        return (
            value is not None
            and self.name == value.name
            and self.capacity == value.capacity
        )

    def __str__(self) -> str:
        return f"{self.name}"

    def __hash__(self) -> int:
        return hash((self.name, self.capacity))


class Lecturer:
    def __init__(self, name: str, can_teach_subjects_names: list[Subject],  max_hours_per_week: int = 10) -> None:
        self.name: str = name
        self.can_teach_subjects_names: list[str] = can_teach_subjects_names
        self.max_hours_per_week: int = max_hours_per_week
        self.can_teach_subjects: list[Subject] = None

    def __eq__(self, value: object) -> bool:
        return value is not None and self.name == value.name

    def __str__(self) -> str:
        return f"{self.name}"

    def __hash__(self) -> int:
        return hash(self.name)


class Hall:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity

    def __eq__(self, value: object) -> bool:
        return (
            value is not None
            and self.name == value.name
            and self.capacity == value.capacity
        )

    def __str__(self) -> str:
        return f"{self.name}"

    def __hash__(self) -> int:
        return hash((self.name, self.capacity))


class Slot:
    def __init__(
        self,
        group: Group,
        subject: Subject,
        lecturer: Lecturer = None,
        hall: Hall = None,
        time_slot: TimeSlot = None,
    ):
        self.group = group
        self.subject = subject
        self.lecturer = lecturer
        self.hall = hall
        self.time_slot = time_slot

    def __eq__(self, value: object) -> bool:
        return (
            self.group == value.group
            and self.subject == value.subject
            and self.lecturer == value.lecturer
            and self.hall == value.hall
            and self.time_slot == value.time_slot
        )

    def __str__(self) -> str:
        return f"Group: {self.group.name}, Subject: {self.subject.name}, Lecturer: {self.lecturer}, Hall: {self.hall}, Time Slot: {self.time_slot}"

    def __repr__(self) -> str:
        return f"Group: {self.group.name}, Subject: {self.subject.name}, Lecturer: {self.lecturer}, Hall: {self.hall}, Time Slot: {self.time_slot}"

    def __hash__(self) -> int:
        return hash(
            (self.group, self.subject, self.lecturer, self.hall, self.time_slot)
        )

    def to_table_format(self):
        return f"{self.time_slot.day}\n{self.time_slot.time}\n{self.group.name}\n{self.subject.name}\n{self.lecturer.name}\n{self.hall.name}"


class Schedule:
    def __init__(self):
        self.grid: list[Slot] = []

    def mutate_slot(self, slot):
        pass

    def _find_timeslot_conficts_for_all_groups(self):
        time_slots = {}
        for slot in self.grid:
            if slot.group is None:
                continue
            if slot.group.name not in time_slots:
                time_slots[slot.group.name] = []
            time_slots[slot.group.name].append(slot.time_slot)
        conflicts = {}
        for group, slots in time_slots.items():
            conflicts[group] = []
            for slot in slots:
                if slot is not None and slots.count(slot) > 1:
                    conflicts[group].append(slot)
        return conflicts

    def _find_timeslot_conflicts_for_all_halls(self):
        time_slots = {}
        for slot in self.grid:
            if slot.hall is None:
                continue
            if slot.hall.name not in time_slots:
                time_slots[slot.hall.name] = []
            time_slots[slot.hall.name].append(slot.time_slot)
        conflicts = {}
        for hall, slots in time_slots.items():
            conflicts[hall] = []
            for slot in slots:
                if slot is not None and slots.count(slot) > 1:
                    conflicts[hall].append(slot)
        return conflicts

    def _find_timeslot_conflicts_for_all_lecturers(self):
        time_slots = {}
        for slot in self.grid:
            if slot.lecturer is None:
                continue
            if slot.lecturer.name not in time_slots:
                time_slots[slot.lecturer.name] = []
            time_slots[slot.lecturer.name].append(slot.time_slot)
        conflicts = {}
        for lecturer, slots in time_slots.items():
            conflicts[lecturer] = []
            for slot in slots:
                if slot is not None and slots.count(slot) > 1:
                    conflicts[lecturer].append(slot)
        return conflicts

    def _get_subject_hours_cost(self, subjects):
        subject_hours = {}
        cost = 0

        for slot in self.grid:
            if slot.subject is not None:
                subject_name = slot.subject.name
                subject_hours[subject_name] = subject_hours.get(subject_name, 0) + 1

        for subject in subjects:
            actual_hours = subject_hours.get(subject.name, 0)
            required_hours = subject.hours 
            if actual_hours < required_hours:
                cost += (required_hours - actual_hours)  
            elif actual_hours > required_hours:
                cost += (actual_hours - required_hours)  

        return cost

    def _get_lecturer_hours_cost(self):
        lecturer_hours = {}
        cost = 0

        for slot in self.grid:
            if slot.lecturer is not None:
                lecturer_name = slot.lecturer.name
                lecturer_hours[lecturer_name] = lecturer_hours.get(lecturer_name, 0) + 1

        for lecturer_name, hours in lecturer_hours.items():
            lecturer = next((l for l in self.grid if l.lecturer and l.lecturer.name == lecturer_name), None)
            if lecturer is not None and lecturer.lecturer.max_hours_per_week < hours:
                cost += (hours - lecturer.lecturer.max_hours_per_week) 

        return cost
        
    def is_valid(self):
        group_conflicts = self._find_timeslot_conficts_for_all_groups()
        hall_conflicts = self._find_timeslot_conflicts_for_all_halls()
        lecturer_conflicts = self._find_timeslot_conflicts_for_all_lecturers()

        return (
            (
                not any(group_conflicts.values())
                and not any(hall_conflicts.values())
                and not any(lecturer_conflicts.values())
            ),
            group_conflicts,
            hall_conflicts,
            lecturer_conflicts,
        )

    def crossover(self, other):
            child = Schedule()
            child.grid = self.grid.copy()

            
            other_slots = other.grid
            for i in range(min(len(self.grid), len(other_slots))):
                if random.random() > 0.5:
                    child.grid[i] = copy.copy(other_slots[i])


            return child


    def __str__(self) -> str:
        return "\n".join([str(slot) for slot in self.grid])

    def to_time_slot_oriented_view(self):
        time_slots = {}
        for slot in self.grid:
            if slot.time_slot is None:
                continue
            if slot.time_slot not in time_slots:
                time_slots[f"{slot.time_slot.day} + {slot.time_slot.time}"] = []
            time_slots[f"{slot.time_slot.day} + {slot.time_slot.time}"].append(slot)

        sorted_keys = sorted(time_slots.keys(), key=lambda x: x)
        time_slots = {
            k: time_slots[k] for k in sorted_keys if time_slots[k] is not None
        }
        return time_slots

    def to_groups_schedules(self):
        groups = {}
        for slot in self.grid:
            if slot.group is None:
                continue
            if slot.group.name not in groups:
                groups[slot.group.name] = []
            groups[slot.group.name].append(slot)

        group_tables = {}
        for k, v in groups.items():
            sorted_by_time = sorted(
                v, key=lambda x: (x.time_slot.day, x.time_slot.time)
            )
            group_tables[k] = [slot.to_table_format() for slot in sorted_by_time]

        return group_tables

    def _get_group_windows_cost(self, time_slot_scores):
        time_slots_for_groups = {}
        for slot in self.grid:
            if slot.group is None:
                continue
            if slot.group.name not in time_slots_for_groups:
                time_slots_for_groups[slot.group.name] = []
            time_slots_for_groups[slot.group.name].append(slot.time_slot)

        for _, v in time_slots_for_groups.items():
            sorted_time_slots = sorted(v, key=lambda x: (x.day, x.time))
            cost = 0
            for i in range(len(sorted_time_slots) - 1):
                cost += (
                    time_slot_scores[sorted_time_slots[i + 1]]
                    - time_slot_scores[sorted_time_slots[i]]
                )

        return cost

    def _get_lecturer_windows_cost(self, time_slot_scores):
        time_slots_for_lecturers = {}
        for slot in self.grid:
            if slot.lecturer is None:
                continue
            if slot.lecturer.name not in time_slots_for_lecturers:
                time_slots_for_lecturers[slot.lecturer.name] = []
            time_slots_for_lecturers[slot.lecturer.name].append(slot.time_slot)

        for _, v in time_slots_for_lecturers.items():
            sorted_time_slots = sorted(v, key=lambda x: (x.day, x.time))
            cost = 0
            for i in range(len(sorted_time_slots) - 1):
                cost += (
                    time_slot_scores[sorted_time_slots[i + 1]]
                    - time_slot_scores[sorted_time_slots[i]]
                )

        return cost

    def _get_time_slot_earliness_cost(self, time_slot_scores):
        time_slots = {}
        for slot in self.grid:
            if slot.time_slot is None:
                continue
            if slot.time_slot not in time_slots:
                time_slots[slot.time_slot] = 0
            time_slots[slot.time_slot] += 1

        cost = 0
        for k, v in time_slots.items():
            cost += time_slot_scores[k] * v

        return cost

    def _get_group_capacity_hall_capacity_fill_cost(self):
        cost = 0

        for slot in self.grid:
            if slot.hall is None or slot.group is None:
                continue
            cost += (slot.hall.capacity - slot.group.capacity) / slot.hall.capacity

        return cost
    
    def to_dataframe(self):
        days = sorted(set(slot.time_slot.day for slot in self.grid if slot.time_slot))
        times = sorted(set(slot.time_slot.time for slot in self.grid if slot.time_slot))
        
        index = pd.MultiIndex.from_product([days, times], names=["Day", "Time"])
        columns = sorted(set(slot.group.name for slot in self.grid if slot.group))
        df = pd.DataFrame(index=index, columns=columns)
        
        for slot in self.grid:
            if slot.group and slot.time_slot:
                cell_value = f"{slot.lecturer.name if slot.lecturer else 'N/A'}, {slot.subject.name}, {slot.hall.name if slot.hall else 'N/A'}"
                df.loc[(slot.time_slot.day, slot.time_slot.time), slot.group.name] = cell_value

        return df
    
    def to_lecturer_schedule(self, lecturer_name):

        lecturer_slots = [slot for slot in self.grid if slot.lecturer and slot.lecturer.name == lecturer_name]
        
        if not lecturer_slots:
            print(f"Schedule for {lecturer_name} not found.")
            return pd.DataFrame()  

        days = sorted(set(slot.time_slot.day for slot in lecturer_slots if slot.time_slot))
        times = sorted(set(slot.time_slot.time for slot in lecturer_slots if slot.time_slot))

        index = pd.MultiIndex.from_product([days, times], names=["Day", "Time"])
        df = pd.DataFrame(index=index, columns=["Group", "Subject", "Hall"])

        for slot in lecturer_slots:
            if slot.time_slot:
                group_name = slot.group.name if slot.group else "N/A"
                subject_name = slot.subject.name if slot.subject else "N/A"
                hall_name = slot.hall.name if slot.hall else "N/A"
                df.loc[(slot.time_slot.day, slot.time_slot.time)] = [group_name, subject_name, hall_name]

        return df
    
    def save_to_database(self, db_name="schedule.db"):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                day TEXT,
                time TEXT,
                group_name TEXT,
                subject_name TEXT,
                lecturer_name TEXT,
                hall_name TEXT
            );
        """)

        for slot in self.grid:
            if slot.time_slot and slot.group and slot.subject and slot.lecturer and slot.hall:
                day = slot.time_slot.day
                time = slot.time_slot.time
                group_name = slot.group.name
                subject_name = slot.subject.name
                lecturer_name = slot.lecturer.name
                hall_name = slot.hall.name

                cursor.execute("""
                    INSERT INTO schedule (day, time, group_name, subject_name, lecturer_name, hall_name)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (day, time, group_name, subject_name, lecturer_name, hall_name))

        conn.commit()
        conn.close()

        print(f"Schedule saved to database {db_name}")



class ScheduleManager:
    def __init__(self):
        self.time_slots: list[TimeSlot] = None
        self.subjects: list[Subject] = None
        self.groups: list[Group] = None
        self.lecturers: list[Lecturer] = None
        self.halls: list[Hall] = None
        self.time_slots_scores: dict[str, int] = {}

        self.group_windows_weight = 1
        self.lecturer_windows_weight = 1
        self.time_slot_earliness_weight = 0.5
        self.group_capacity_hall_capacity_fill_weight = 0.5
        self.subject_hours_weight = 1
        self.lecturer_hours_weight = 1

    def from_yaml(self, file_path: str) -> None:
        with open(file_path, "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            self.time_slots = [
                TimeSlot(**time_slot) for time_slot in data["time_slots"]
            ]
            self.subjects = [Subject(**subject) for subject in data["subjects"]]
            self.groups = [Group(**group) for group in data["groups"]]
            self.lecturers = [Lecturer(**lecturer) for lecturer in data["lecturers"]]
            self.halls = [Hall(**hall) for hall in data["halls"]]

        for i, time_slot in enumerate(self.time_slots):
            self.time_slots_scores[time_slot] = i

    def create_empty_schedule(self):
        schedule = Schedule()
        for group in self.groups:
            for subject in group.subject_names:
                s = next((s for s in self.subjects if s.name == subject), None)
                for i in range(s.hours):
                    schedule.grid.append(
                        Slot(
                            group=group,
                            subject=s,
                        )
                    )

        return schedule

    def _get_available_time_slots_for_hall_and_lecturer_and_group(
        self, schedule: Schedule, hall: Hall, lecturer: Lecturer, group: Group
    ):
        grid = schedule.grid
        allowed_time_slots = [ts for ts in self.time_slots]
        busy_time_slots = []
        for s in grid:
            if s.hall == hall:
                busy_time_slots.append(s.time_slot)
            if s.lecturer == lecturer:
                busy_time_slots.append(s.time_slot)
            if s.group == group:
                busy_time_slots.append(s.time_slot)

        return sorted(
            list(set(allowed_time_slots) - set(busy_time_slots)),
            key=lambda x: (x.day, x.time),
        )

    def _get_available_lecturers_for_time_slot_and_subject(
        self, schedule: Schedule, time_slot: TimeSlot, subject: Subject
    ):
        if time_slot is None:
            return []

        grid = schedule.grid
        allowed_lecturers = [
            l for l in self.lecturers if subject.name in l.can_teach_subjects_names
        ]
        busy_lecturers = []
        for s in grid:
            if s.time_slot == time_slot:
                busy_lecturers.append(s.lecturer)

        return sorted(
            list(set(allowed_lecturers) - set(busy_lecturers)), key=lambda x: x.name
        )

    def _get_available_halls_for_time_slot_and_group(
        self, schedule: Schedule, time_slot: TimeSlot, group: Group
    ):
        grid = schedule.grid
        busy_halls = []
        allowed_halls = [h for h in self.halls if group.capacity <= h.capacity]
        for s in grid:
            if s.time_slot == time_slot:
                busy_halls.append(s.hall)

        return sorted(list(set(allowed_halls) - set(busy_halls)), key=lambda x: x.name)
    

    
    def mutate_schedule(self, schedule: Schedule):
        grid = schedule.grid
        slot_index = random.randint(0, len(grid) - 1)
        slot = grid[slot_index]
        new_slot = copy.copy(slot)

        what_to_mutate = random.choice(["hall", "lecturer", "time_slot", "del", "add"])

        did_mutate = False
        if what_to_mutate == "hall":
            available_halls = self._get_available_halls_for_time_slot_and_group(
                schedule, slot.time_slot, slot.group
            )
            if len(available_halls) == 0:
                return schedule, False
            new_slot.hall = random.choice(available_halls)
            did_mutate = True
        elif what_to_mutate == "lecturer":
            available_lecturers = (
                self._get_available_lecturers_for_time_slot_and_subject(
                    schedule, slot.time_slot, slot.subject
                )
            )
            if len(available_lecturers) == 0:
                return schedule, False
            new_slot.lecturer = random.choice(available_lecturers)
            did_mutate = True
        elif what_to_mutate == "del":
            if len(schedule.grid) > 10:
                new_schedule = copy.copy(schedule)
                print("Before:",  new_schedule)

                new_schedule.grid.pop(random.randint(0, len(new_schedule.grid) - 1))
                print("After:",  new_schedule)
                return new_schedule, True
            else:
                return schedule, False

        elif what_to_mutate == "add":
            new_schedule = copy.copy(schedule)
            
            random_slot = copy.copy(new_slot)
            random_slot.group = random.choice(self.groups)
            random_slot.hall = random.choice(self.halls)
            random_slot.lecturer = random.choice(self.lecturers)
            random_slot.subject = random.choice(self.subjects)
            random_slot.time_slot = random.choice(self.time_slots)
        
            new_schedule.grid.append(random_slot)

            return new_schedule, False
        else:
            avaliable_time_slots = (
                self._get_available_time_slots_for_hall_and_lecturer_and_group(
                    schedule, slot.hall, slot.lecturer, slot.group
                )
            )
            if len(avaliable_time_slots) == 0:
                return schedule, False
            new_slot.time_slot = random.choice(avaliable_time_slots)
            did_mutate = True

        new_schedule = copy.copy(schedule)
        new_schedule.grid[slot_index] = new_slot

        return new_schedule, did_mutate




    def init_random_schedule(self):
        schedule = self.create_empty_schedule()

        i = 0
        while i < 1000:
            schedule, _ = self.mutate_schedule(schedule)
            i += 1

        for slot in schedule.grid:
            if slot.hall is None:
                available_halls = self._get_available_halls_for_time_slot_and_group(
                    schedule, slot.time_slot, slot.group
                )
                if len(available_halls) == 0:
                    return self.init_random_schedule()
                slot.hall = random.choice(available_halls)

            if slot.lecturer is None:
                available_lecturers = (
                    self._get_available_lecturers_for_time_slot_and_subject(
                        schedule, slot.time_slot, slot.subject
                    )
                )
                if len(available_lecturers) == 0:
                    return self.init_random_schedule()
                slot.lecturer = random.choice(available_lecturers)

            if slot.time_slot is None:
                avaliable_time_slots = (
                    self._get_available_time_slots_for_hall_and_lecturer_and_group(
                        schedule, slot.hall, slot.lecturer, slot.group
                    )
                )
                if len(avaliable_time_slots) == 0:
                    return self.init_random_schedule()
                slot.time_slot = random.choice(avaliable_time_slots)

        return schedule




    def get_schedule_fitness(self, schedule: Schedule):
        cost = 0

        group_windows_cost = (
            self.group_windows_weight
            * schedule._get_group_windows_cost(self.time_slots_scores)
        )

        lecturer_windows_cost = (
            self.lecturer_windows_weight
            * schedule._get_lecturer_windows_cost(self.time_slots_scores)
        )

        time_slot_earliness_cost = (
            self.time_slot_earliness_weight
            * schedule._get_time_slot_earliness_cost(self.time_slots_scores)
        )

        group_capacity_hall_capacity_fill_cost = (
            self.group_capacity_hall_capacity_fill_weight
            * schedule._get_group_capacity_hall_capacity_fill_cost()
        )

        #додавання нежорсткої умови на дотримання кількості годин для кожного предмета  
        subject_hours_cost = (
            self.subject_hours_weight
            * schedule._get_subject_hours_cost(self.subjects) 
        )
        
        lecturer_hours_cost = (
            self.lecturer_hours_weight
            * schedule._get_lecturer_hours_cost()
        )

        cost += (
            group_windows_cost
            + lecturer_windows_cost
            + time_slot_earliness_cost
            + group_capacity_hall_capacity_fill_cost
            + subject_hours_cost
            + lecturer_hours_cost


        )
        return 1 / (1 + cost)

    def tournament_selection(self, population, tournament_size) -> Schedule:
        selected = []
        for _ in range(tournament_size):
            selected.append(random.choice(population))

        return max(selected, key=lambda x: self.get_schedule_fitness(x))

    def genetic(self, population_size: int) -> Schedule:
        current_population = []
        for _ in range(population_size):
            current_population.append(self.init_random_schedule())

        number_of_same_best_fitness = 0
        curr_best_fitness = 0
        number_of_generations = 100
        while number_of_generations > 0 and number_of_same_best_fitness < 10:
            new_population = []
            while len(new_population) < population_size:
                parent1 = self.tournament_selection(current_population, 10)
                parent2 = self.tournament_selection(current_population, 10)
                child = parent1.crossover(parent2)
                if random.random() < 0.5:
                    child, _ = self.mutate_schedule(child)
                if child.is_valid()[0]:
                    new_population.append(child)

            current_population = new_population
            best_fitness = self.get_schedule_fitness(
                max(current_population, key=lambda x: self.get_schedule_fitness(x))
            )
            if best_fitness > curr_best_fitness:
                curr_best_fitness = best_fitness
                print(curr_best_fitness)
                number_of_same_best_fitness = 0
            elif best_fitness == curr_best_fitness:
                number_of_same_best_fitness += 1

        best_schedule = max(
            current_population, key=lambda x: self.get_schedule_fitness(x)
        )

        return best_schedule
