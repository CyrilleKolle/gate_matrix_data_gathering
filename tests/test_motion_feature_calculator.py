'''Run python -m unittest tests/test_motion_feature_calculator.py in the terminal to run the tests'''
import unittest
import pandas as pd
from src.motion_feature_calculator import MotionFeatureCalculator



class TestMotionFeatureCalculator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Sample data for testing
        data = {
            "timestamp_local": [
                "2024-02-06 10:00:42.430037",
                "2024-02-06 10:00:42.504867",
                "2024-02-06 10:00:42.579836",
                "2024-02-06 10:00:42.654867",
                "2024-02-06 10:00:42.729828",
            ],
            "ax": [-0.562333, -0.737016, -0.356543, -1.072023, 0.485760],
            "ay": [8.858545, 8.805902, 9.480701, 9.566847, 10.150716],
            "az": [0.452260, 0.686765, 0.746587, 0.181861, 1.799467],
            "fall_state": [0, 0, 0, 0, 0],
        }

        # Convert your sample data to a DataFrame
        cls.df = pd.DataFrame(data)

        # Convert the 'timestamp_local' column to datetime
        cls.df["timestamp_local"] = pd.to_datetime(cls.df["timestamp_local"])

        # Initialize the MotionFeatureCalculator with the DataFrame
        cls.calculator = MotionFeatureCalculator(
            cls.df, "timestamp_local", ["ax", "ay", "az"], time_unit="ms"
        )

    def test_calculate_time_interval_returns_float(self):
        # Run the method to calculate time intervals
        self.calculator.calculate_time_interval()

        # Check if all elements in the 'time_interval' column are floating-point numbers
        all_floats = all(
            isinstance(x, float) for x in self.calculator.df["time_interval"]
        )

        # Assert that all calculated intervals are indeed floats
        self.assertTrue(
            all_floats, "Not all calculated time intervals are floating-point numbers."
        )

    def test_calculate_velocity_displacement_columns(self):
        # Before running the method, these columns should not exist
        for axis in self.calculator.accel_cols:
            velocity_col = f"v{axis[-1]}"
            displacement_col = f"d{axis[-1]}"
            self.assertNotIn(
                velocity_col,
                self.calculator.df.columns,
                f"{velocity_col} column unexpectedly exists before calculation.",
            )
            self.assertNotIn(
                displacement_col,
                self.calculator.df.columns,
                f"{displacement_col} column unexpectedly exists before calculation.",
            )

        # Run the method to calculate velocity and displacement
        self.calculator.calculate_velocity_displacement()

        # After running the method, check for the existence of the new columns
        for axis in self.calculator.accel_cols:
            velocity_col = f"v{axis[-1]}"
            displacement_col = f"d{axis[-1]}"

            # Check if the velocity and displacement columns are created
            self.assertIn(
                velocity_col,
                self.calculator.df.columns,
                f"{velocity_col} column not created.",
            )
            self.assertIn(
                displacement_col,
                self.calculator.df.columns,
                f"{displacement_col} column not created.",
            )

            # Additionally, check that the columns contain floating-point numbers
            # This verifies that cumtrapz has been applied to calculate the values
            for value in self.calculator.df[velocity_col]:
                self.assertIsInstance(
                    value, float, f"{velocity_col} contains non-float value."
                )
            for value in self.calculator.df[displacement_col]:
                self.assertIsInstance(
                    value, float, f"{displacement_col} contains non-float value."
                )

    def test_calculate_angles_columns_and_values(self):
        # Expected angle columns to be created
        expected_angle_columns = ["angle_xy", "angle_yz", "angle_zx"]

        # Before running the method, these columns should not exist
        for angle_col in expected_angle_columns:
            self.assertNotIn(
                angle_col,
                self.calculator.df.columns,
                f"{angle_col} column unexpectedly exists before calculation.",
            )

        # Run the method to calculate angles
        self.calculator.calculate_angles()

        # After running the method, check for the existence of the new angle columns
        for angle_col in expected_angle_columns:
            self.assertIn(
                angle_col,
                self.calculator.df.columns,
                f"{angle_col} column not created.",
            )

            # Additionally, check that each angle column contains valid floating-point numbers
            for value in self.calculator.df[angle_col]:
                self.assertIsInstance(
                    value, float, f"{angle_col} contains non-float value."
                )

                # Check if angle values are within the expected range -180 to 180 degrees
                self.assertTrue(
                    -180 <= value <= 180,
                    f"{angle_col} contains a value out of range: {value}",
                )

    def test_calculate_g_force_column_and_values(self):
        # Before running the method, the 'g_force' column should not exist
        self.assertNotIn("g_force", self.calculator.df.columns, "'g_force' column unexpectedly exists before calculation.")

        # Run the method to calculate g-force
        self.calculator.calculate_g_force()

        # After running the method, check for the existence of the 'g_force' column
        self.assertIn("g_force", self.calculator.df.columns, "'g_force' column not created.")

        # Check that the 'g_force' column contains valid floating-point numbers
        for value in self.calculator.df["g_force"]:
            self.assertIsInstance(value, float, "'g_force' column contains non-float value.")
            
            # Check if g-force values are non-negative
            self.assertTrue(value >= 0, f"'g_force' column contains a negative value: {value}")



if __name__ == "__main__":
    unittest.main()
