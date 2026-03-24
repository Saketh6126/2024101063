import os
import sys
import unittest

# Allow importing the StreetRace Manager modules from integration/code
THIS_DIR = os.path.dirname(__file__)
CODE_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "code"))
sys.path.insert(0, CODE_DIR)

import data_store
import registration
import crew_management
import inventory
import race_management
import results
import mission_planning
import garage
import analytics


class StreetRaceManagerIntegrationTests(unittest.TestCase):
    def setUp(self):
        data_store.reset_store()

    def test_registration_then_crew_management_updates_member(self):
        crew_id = registration.register_member("Alex", "driver")
        crew_management.assign_role(crew_id, "strategist")
        crew_management.update_skill(crew_id, 7)
        crew_management.set_availability(crew_id, False)

        member = registration.get_member(crew_id)
        self.assertEqual(member["role"], "strategist")
        self.assertEqual(member["skill_level"], 7)
        self.assertFalse(member["available"])

    def test_cannot_assign_role_to_unregistered_member(self):
        with self.assertRaises(KeyError):
            crew_management.assign_role("crew_999", "driver")

    def test_register_driver_enter_race_and_start(self):
        driver_id = registration.register_member("Mia", "driver")
        car_id = inventory.add_car("Civic", speed=8, condition="good")

        race_id = race_management.create_race("Night Sprint", "Downtown")
        race_management.assign_driver(race_id, driver_id)
        race_management.assign_car(race_id, car_id)
        race_management.start_race(race_id)

        race = data_store.store["races"][race_id]
        self.assertEqual(race["status"], "in_progress")
        self.assertFalse(data_store.store["crew"][driver_id]["available"])

    def test_cannot_enter_race_with_non_driver(self):
        mechanic_id = registration.register_member("Sam", "mechanic")
        car_id = inventory.add_car("Supra", speed=9, condition="good")
        race_id = race_management.create_race("Harbor Run", "Docks")

        with self.assertRaises(ValueError):
            race_management.assign_driver(race_id, mechanic_id)

        # assigning car should still work
        race_management.assign_car(race_id, car_id)

    def test_cannot_assign_wrecked_car_to_race(self):
        driver_id = registration.register_member("Jules", "driver")
        wrecked_car_id = inventory.add_car("Old Beater", speed=3, condition="wrecked")
        race_id = race_management.create_race("Back Alley", "Industrial")
        race_management.assign_driver(race_id, driver_id)

        with self.assertRaises(ValueError):
            race_management.assign_car(race_id, wrecked_car_id)

    def test_cannot_start_race_without_assignments(self):
        race_id = race_management.create_race("Empty Grid", "Nowhere")
        with self.assertRaises(ValueError):
            race_management.start_race(race_id)

        driver_id = registration.register_member("Pat", "driver")
        race_management.assign_driver(race_id, driver_id)
        with self.assertRaises(ValueError):
            race_management.start_race(race_id)

        car_id = inventory.add_car("Focus", speed=5, condition="good")
        race_management.assign_car(race_id, car_id)
        race_management.start_race(race_id)

    def test_complete_race_updates_cash_ranking_and_frees_driver(self):
        driver_id = registration.register_member("Noah", "driver")
        car_id = inventory.add_car("RX-7", speed=9, condition="good")
        race_id = race_management.create_race("Tunnel Dash", "Midtown")
        race_management.assign_driver(race_id, driver_id)
        race_management.assign_car(race_id, car_id)
        race_management.start_race(race_id)

        self.assertEqual(inventory.get_cash(), 0)
        results.record_result(race_id, position=1, prize=1000.0)

        self.assertEqual(inventory.get_cash(), 1000.0)
        self.assertEqual(data_store.store["races"][race_id]["status"], "completed")
        self.assertTrue(data_store.store["crew"][driver_id]["available"])
        self.assertEqual(data_store.store["rankings"][driver_id], 10)
        self.assertEqual(len(data_store.store["results"]), 1)

    def test_cannot_record_result_before_race_started(self):
        driver_id = registration.register_member("Rin", "driver")
        car_id = inventory.add_car("Integra", speed=7, condition="good")
        race_id = race_management.create_race("Warmup", "Lot")
        race_management.assign_driver(race_id, driver_id)
        race_management.assign_car(race_id, car_id)

        with self.assertRaises(ValueError):
            results.record_result(race_id, position=1, prize=50.0)

    def test_inventory_cash_cannot_go_negative(self):
        self.assertEqual(inventory.get_cash(), 0)
        with self.assertRaises(ValueError):
            inventory.update_cash(-1)

    def test_car_damage_flow_marks_inventory_and_result(self):
        driver_id = registration.register_member("Lena", "driver")
        car_id = inventory.add_car("GT-R", speed=10, condition="good")
        race_id = race_management.create_race("Coastline", "Seaside")
        race_management.assign_driver(race_id, driver_id)
        race_management.assign_car(race_id, car_id)
        race_management.start_race(race_id)

        results.record_result(race_id, position=3, prize=200.0)
        results.handle_car_damage(race_id, damaged=True)

        self.assertEqual(inventory.get_car(car_id)["condition"], "damaged")
        self.assertTrue(data_store.store["results"][0]["car_damaged"])

    def test_mission_requires_roles_and_validates_availability(self):
        driver_id = registration.register_member("Kai", "driver")
        strategist_id = registration.register_member("Ivy", "strategist")

        mission_id = mission_planning.create_mission("delivery", ["driver", "strategist"])

        # Missing strategist should fail
        with self.assertRaises(ValueError):
            mission_planning.assign_crew_to_mission(mission_id, [driver_id])

        # Assign both roles should succeed
        mission_planning.assign_crew_to_mission(mission_id, [driver_id, strategist_id])

        # Make one crew unavailable and ensure start fails
        crew_management.set_availability(strategist_id, False)
        with self.assertRaises(ValueError):
            mission_planning.start_mission(mission_id)

        # Now start should work
        crew_management.set_availability(strategist_id, True)
        mission_planning.start_mission(mission_id)
        self.assertFalse(data_store.store["crew"][driver_id]["available"])
        self.assertFalse(data_store.store["crew"][strategist_id]["available"])

        # Completing mission adds cash and frees crew
        mission_planning.complete_mission(mission_id, reward=300.0)
        self.assertEqual(inventory.get_cash(), 300.0)
        self.assertTrue(data_store.store["crew"][driver_id]["available"])
        self.assertTrue(data_store.store["crew"][strategist_id]["available"])

    def test_mission_start_requires_assigned_crew(self):
        mission_id = mission_planning.create_mission("delivery", ["driver"])
        with self.assertRaises(ValueError):
            mission_planning.start_mission(mission_id)

    def test_mission_invalid_type_or_role_rejected(self):
        with self.assertRaises(ValueError):
            mission_planning.create_mission("invalid_type", ["driver"])
        with self.assertRaises(ValueError):
            mission_planning.create_mission("delivery", ["not_a_role"])

    def test_mission_mechanic_requirement_with_damaged_car_proceeds(self):
        # create a damaged car in inventory
        inventory.add_car("Evo", speed=8, condition="damaged")

        mechanic_id = registration.register_member("Bea", "mechanic")
        driver_id = registration.register_member("Zoe", "driver")

        mission_id = mission_planning.create_mission("rescue", ["driver", "mechanic"])
        mission_planning.assign_crew_to_mission(mission_id, [driver_id, mechanic_id])

        # Should proceed (prints warning) rather than raising
        mission_planning.start_mission(mission_id)
        self.assertEqual(data_store.store["missions"][mission_id]["status"], "active")

    def test_garage_repair_deducts_cash_and_restores_car(self):
        # Setup: cash needed for repair and a damaged car
        inventory.update_cash(1000.0)
        car_id = inventory.add_car("Miata", speed=6, condition="damaged")
        mechanic_id = registration.register_member("Omar", "mechanic")

        garage.schedule_repair(car_id, mechanic_id)
        self.assertEqual(inventory.get_cash(), 500.0)
        self.assertFalse(data_store.store["crew"][mechanic_id]["available"])

        garage.complete_repair(car_id)
        self.assertEqual(inventory.get_car(car_id)["condition"], "good")
        self.assertTrue(data_store.store["crew"][mechanic_id]["available"])
        self.assertEqual(data_store.store["garage_log"][-1]["status"], "completed")

    def test_garage_repair_requires_mechanic_and_funds(self):
        inventory.update_cash(400.0)
        car_id = inventory.add_car("Accord", speed=5, condition="damaged")
        driver_id = registration.register_member("Dev", "driver")

        # Wrong role
        with self.assertRaises(ValueError):
            garage.schedule_repair(car_id, driver_id)

        mechanic_id = registration.register_member("Mae", "mechanic")

        # Insufficient funds
        with self.assertRaises(ValueError):
            garage.schedule_repair(car_id, mechanic_id)

    def test_analytics_race_win_rate_unknown_driver_errors(self):
        with self.assertRaises(KeyError):
            analytics.race_win_rate("crew_999")

    def test_analytics_functions_do_not_crash(self):
        # Seed minimal data: run a race and a mission so analytics has something
        driver_id = registration.register_member("Troy", "driver")
        car_id = inventory.add_car("Charger", speed=7, condition="good")
        race_id = race_management.create_race("Sunset", "Hills")
        race_management.assign_driver(race_id, driver_id)
        race_management.assign_car(race_id, car_id)
        race_management.start_race(race_id)
        results.record_result(race_id, position=2, prize=150.0)

        strategist_id = registration.register_member("Nia", "strategist")
        mission_id = mission_planning.create_mission("heist", ["driver", "strategist"])
        mission_planning.assign_crew_to_mission(mission_id, [driver_id, strategist_id])
        mission_planning.start_mission(mission_id)
        mission_planning.complete_mission(mission_id, reward=50.0)

        # These print to stdout; we just ensure no exceptions
        analytics.top_driver()
        analytics.total_earnings()
        analytics.race_win_rate(driver_id)
        analytics.mission_success_rate()
        analytics.cash_flow_summary()


if __name__ == "__main__":
    unittest.main()
