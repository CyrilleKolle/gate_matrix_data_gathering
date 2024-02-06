import numpy as np
import pandas as pd
from loguru import logger
from scipy.integrate import cumtrapz


class MotionFeatureCalculator:
    def __init__(self, df, timestamp_col, accel_cols, time_unit="ms"):
        self.df = df
        self.timestamp_col = timestamp_col
        self.accel_cols = accel_cols
        self.time_unit = time_unit

    def check_all_columns(self):
        logger.info("Checking if all columns are present")
        for col in self.accel_cols:
            if col not in self.df.columns:
                logger.error(f"Column {col} not found in dataframe")
                raise ValueError(f"Column {col} not found in dataframe")
        logger.info("All columns found")

    def calculate_time_interval(self):
        logger.info("Calculating time interval")
        self.df[self.timestamp_col] = pd.to_datetime(self.df[self.timestamp_col])
        self.df["time_interval"] = (
            self.df[self.timestamp_col].diff().fillna(pd.Timedelta(seconds=0))
        )
        self.df["time_interval"] = self.df["time_interval"].dt.total_seconds()
        time_divisor = 1000 if self.time_unit == "ms" else 1
        self.df["time_interval"] /= time_divisor
        logger.info("Time interval calculated")

    def calculate_velocity_displacement(self):
        logger.info("Calculating velocity and displacement")
        for axis in self.accel_cols:
            logger.info(f"Calculating velocity and displacement for {axis}")
            velocity_col = f"v{axis[-1]}"
            self.df[velocity_col] = cumtrapz(
                self.df[axis], self.df["time_interval"], initial=0
            )

            displacement_col = f"d{axis[-1]}"
            self.df[displacement_col] = cumtrapz(
                self.df[velocity_col], self.df["time_interval"], initial=0
            )

    def calculate_angles(self):
        logger.info("Calculating angles")
        for axis1, axis2 in [("ax", "ay"), ("ay", "az"), ("az", "ax")]:
            logger.info(f"Calculating angle between {axis1} and {axis2}")
            angle_col = f"angle_{axis1[-1]}{axis2[-1]}"
            self.df[angle_col] = np.degrees(np.arctan2(self.df[axis1], self.df[axis2]))

    def calculate_g_force(self):
        logger.info("Calculating g force")
        self.df["g_force"] = np.sqrt(
            self.df["ax"] ** 2 + self.df["ay"] ** 2 + self.df["az"] ** 2
        )

    def calculate_jerk_orientation(self):
        logger.info("Calculating jerk and orientation")
        self.df["jerk"] = (
            self.df["g_force"].diff().fillna(9.8) / self.df["time_interval"]
        )
        logger.info("Calculating orientation in xy")
        self.df["orientation_xy"] = np.degrees(np.arctan2(self.df["ay"], self.df["ax"]))

        logger.info("Calculating orientation in yz")
        self.df["orientation_yz"] = np.degrees(np.arctan2(self.df["az"], self.df["ay"]))

        logger.info("Calculating orientation in zx")
        self.df["orientation_zx"] = np.degrees(np.arctan2(self.df["ax"], self.df["az"]))

    def calculate_magnitudes(self):
        logger.info("Calculating magnitude of acceleration")
        self.df["magnitude_acceleration"] = np.sqrt(
            self.df["ax"] ** 2 + self.df["ay"] ** 2 + self.df["az"] ** 2
        )

        logger.info("Calculating magnitude of velocity")
        self.df["magnitude_velocity"] = np.sqrt(
            self.df["vx"] ** 2 + self.df["vy"] ** 2 + self.df["vz"] ** 2
        )

        logger.info("Calculating magnitude of displacement")
        self.df["magnitude_displacement"] = np.sqrt(
            self.df["dx"] ** 2 + self.df["dy"] ** 2 + self.df["dz"] ** 2
        )

    def calculate_impact_detection(self):
        logger.info("Calculating impact detection")
        self.df["impact_detection"] = self.df["jerk"].apply(
            lambda x: 1 if x > 75000 else 0
        )

    def calculate_all_features(self):
        self.check_all_columns()
        self.calculate_time_interval()
        self.calculate_velocity_displacement()
        self.calculate_angles()
        self.calculate_g_force()
        self.calculate_jerk_orientation()
        self.calculate_magnitudes()
        self.calculate_impact_detection()
        return self.df
