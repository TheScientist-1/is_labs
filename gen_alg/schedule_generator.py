import random
import csv
import yaml
import pandas as pd

with open("input_data.yaml", "r") as file:
    data = yaml.safe_load(file)

groups = data["groups"]
lecturers = data["lecturers"]
subjects = data["subjects"]
auditoriums = data["auditoriums"]

num_slots = 20
population_size = 10
generations = 100
mutation_rate = 0.1

def initialize_availability():
    availability = {
        "lecturer_slots": {lect["id"]: set() for lect in lecturers},
        "group_slots": {},
        "room_slots": {room["id"]: set() for room in auditoriums}
    }
    for group in groups:
        availability["group_slots"][group["id"]] = set()
        for subgroup in group.get("subgroups", []):
            availability["group_slots"][subgroup["id"]] = set()
    return availability

def generate_conflict_free_individual():
    schedule = []
    availability = initialize_availability()
    for slot in range(num_slots):
        slot_classes = []
        subjects_shuffled = random.sample(subjects, len(subjects))
        for subject in subjects_shuffled:
            group = subject["group"]
            for component in subject["components"]:
                if component["requires_split"]:
                    subgroups = [sg["id"] for g in groups if g["id"] == group for sg in g["subgroups"]]
                    for subgroup in subgroups:
                        success = add_class_to_slot(slot_classes, slot, subgroup, subject["name"], component, availability)
                        if not success:
                            continue
                else:
                    success = add_class_to_slot(slot_classes, slot, group, subject["name"], component, availability)
                    if not success:
                        continue
        schedule.extend(slot_classes)
    return schedule

def add_class_to_slot(slot_classes, slot, group, subject_name, component, availability):
    lecturer = component.get("lecturer")
    if not lecturer:
        lecturer = next((lect["id"] for lect in lecturers if any(subj["name"] == subject_name for subj in lect["subjects"])), None)
    room = find_suitable_room(component, group)
    if not room:
        return False
    if slot in availability["lecturer_slots"][lecturer] or slot in availability["group_slots"][group] or slot in availability["room_slots"][room["id"]]:
        return False
    availability["lecturer_slots"][lecturer].add(slot)
    availability["group_slots"][group].add(slot)
    availability["room_slots"][room["id"]].add(slot)
    slot_classes.append({
        "slot": slot,
        "group": group,
        "subject": subject_name,
        "component_type": component["type"],
        "lecturer": lecturer,
        "room": room["id"]
    })
    return True

def find_suitable_room(component, group_id):
    group_size = None
    for g in groups:
        if g["id"] == group_id:
            group_size = g["students"]
            break
        for sg in g.get("subgroups", []):
            if sg["id"] == group_id:
                group_size = sg["students"]
                break
        if group_size:
            break
    if group_size is None:
        raise ValueError(f"Group ID '{group_id}' not found in groups or subgroups.")
    suitable_rooms = [room for room in auditoriums if room["capacity"] >= group_size]
    if component["type"] == "laboratory":
        suitable_rooms = [room for room in suitable_rooms if room.get("has_lab_equipment", False)]
    return random.choice(suitable_rooms) if suitable_rooms else None

def fitness(schedule):
    score = 100
    lecturer_hours = {lecturer["id"]: 0 for lecturer in lecturers}
    for session in schedule:
        slot = session["slot"]
        lecturer = session["lecturer"]
        lecturer_hours[lecturer] += 1.5
    for lecturer in lecturers:
        max_hours = lecturer.get("max_hours_per_week", 0)
        if lecturer_hours[lecturer["id"]] > max_hours:
            score -= 10 * (lecturer_hours[lecturer["id"]] - max_hours)
    return max(score, 0)

def ensure_conflict_free(individual):
    availability = initialize_availability()
    conflict_free_schedule = []
    for slot in range(num_slots):
        slot_classes = [session for session in individual if session["slot"] == slot]
        valid_slot_classes = []
        for session in slot_classes:
            lecturer, group, room = session["lecturer"], session["group"], session["room"]
            if slot not in availability["lecturer_slots"][lecturer] and slot not in availability["group_slots"][group] and slot not in availability["room_slots"][room]:
                availability["lecturer_slots"][lecturer].add(slot)
                availability["group_slots"][group].add(slot)
                availability["room_slots"][room].add(slot)
                valid_slot_classes.append(session)
        conflict_free_schedule.extend(valid_slot_classes)
    return conflict_free_schedule

def crossover(parent1, parent2):
    crossover_point = random.randint(0, num_slots - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return ensure_conflict_free(child1), ensure_conflict_free(child2)

def mutate(individual):
    if random.random() < 0.5:
        slot1, slot2 = random.sample(range(num_slots), 2)
        individual[slot1], individual[slot2] = individual[slot2], individual[slot1]
    else:
        slot = random.randint(0, num_slots - 1)
        individual[slot] = generate_conflict_free_individual()[slot]
    return ensure_conflict_free(individual)

population = [generate_conflict_free_individual() for _ in range(population_size)]

for generation in range(generations):
    population = sorted(population, key=lambda x: fitness(x), reverse=True)
    avg_fitness = sum(fitness(individual) for individual in population) / len(population)
    next_generation = population[:population_size // 2]
    while len(next_generation) < population_size:
        parent1, parent2 = random.sample(next_generation, 2)
        child1, child2 = crossover(parent1, parent2)
        next_generation.extend([child1, child2])
    population = [mutate(individual) if random.random() < mutation_rate else individual for individual in next_generation]

best_schedule = population[0]
for slot in best_schedule:
    print(f"Slot {slot['slot']}: Group {slot['group']} - {slot['subject']} ({slot['component_type']}) by {slot['lecturer']} in Room {slot['room']}")

with open("schedule.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Slot", "Group", "Subject", "Component Type", "Lecturer", "Room"])
    for slot in best_schedule:
        writer.writerow([slot["slot"], slot["group"], slot["subject"], slot["component_type"], slot["lecturer"], slot["room"]])

def print_lecturer_schedule(schedule, lecturer_id):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slots_per_day = 4
    timetable = {day: [""] * slots_per_day for day in days}
    for session in schedule:
        if session["lecturer"] == lecturer_id:
            day_index = session["slot"] // slots_per_day
            slot_in_day = session["slot"] % slots_per_day
            day_name = days[day_index]
            timetable[day_name][slot_in_day] = f"{session['subject']} ({session['component_type']}) in Room {session['room']}"
    df = pd.DataFrame(timetable)
    df.index = [f"Slot {i + 1}" for i in range(slots_per_day)]
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)
    print(f"Schedule for Lecturer {lecturer_id}:\n")
    print(df)
    pd.reset_option('display.max_columns')
    pd.reset_option('display.expand_frame_repr')

print_lecturer_schedule(best_schedule, "Lecturer1")
