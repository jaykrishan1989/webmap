#!/usr/bin/env python3
import psycopg2
import random
import math
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        database="drone_db",
        user="postgres",
        password="enter6.",  # Replace with your actual password
        host="localhost",
        port="5432"
    )
    logger.info("Successfully connected to database")
except psycopg2.Error as e:
    logger.error(f"Failed to connect to database: {e}")
    exit(1)

# Assign each drone a direction (angle in radians)
directions = {}

def update_drone_positions():
    try:
        with conn.cursor() as cur:
            # Fetch drones
            cur.execute("SELECT id, latitude, longitude FROM drones")
            drones = cur.fetchall()
            logger.info(f"Fetched {len(drones)} drones")

            for drone in drones:
                drone_id, lat, lon = drone
                # Assign random direction if not set
                if drone_id not in directions:
                    directions[drone_id] = random.uniform(0, 2 * math.pi)
                    logger.debug(f"Assigned initial direction {directions[drone_id]:.2f} for drone {drone_id}")

                # Move forward in the current direction
                angle = directions[drone_id]
                speed = 0.0005  # Approx 55.5 meters per update (at 2s intervals)
                new_lat = float(lat) + speed * math.cos(angle)
                new_lon = float(lon) + speed * math.sin(angle)

                # Keep drones within Nanaimo bounds
                new_lat = max(min(new_lat, 49.25), 49.05)
                new_lon = max(min(new_lon, -123.85), -124.05)

                # Occasionally change direction
                directions[drone_id] += random.uniform(-0.1, 0.1)
                logger.debug(f"Drone {drone_id}: Moving to ({new_lat:.6f}, {new_lon:.6f}) with angle {angle:.2f}")

                # Update database
                cur.execute(
                    "UPDATE drones SET latitude = %s, longitude = %s WHERE id = %s",
                    (new_lat, new_lon, drone_id)
                )

            conn.commit()
            logger.info(f"Updated {len(drones)} drones")
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
    except Exception as e:
        logger.error(f"Error in update_drone_positions: {e}")

if __name__ == "__main__":
    try:
        while True:
            update_drone_positions()
            time.sleep(2)
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    finally:
        conn.close()
        logger.info("Database connection closed")