from schedule_generator import ScheduleManager
import random
import pandas as pd

if __name__ == "__main__":
    default_seed = None
    seed = default_seed or random.randint(0, 1000000)
    print("Seed:", seed)
    random.seed(seed)

    schedule_manager = ScheduleManager()
    schedule_manager.from_yaml("schedule.yaml")

    best_schedule = schedule_manager.genetic(100)

    print(best_schedule)
    print(best_schedule.is_valid())
            
    schedule_df = best_schedule.to_dataframe()
    schedule_df.to_csv("schedule_output.csv")
    best_schedule.save_to_database("schedule.db")

    lecturer_name = "Lecturer 1"
    lecturer_schedule_df = best_schedule.to_lecturer_schedule(lecturer_name)
    lecturer_schedule_df.to_csv(f"lecturer_{lecturer_name}_schedule.csv")
