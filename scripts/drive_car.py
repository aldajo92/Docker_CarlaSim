"""
Drives a Tesla Model 3 in CARLA 0.9.15.
The car accelerates at full throttle while the spectator camera follows it.
Press Ctrl+C to stop and destroy the vehicle.

Run from inside the container:
    python3.7 /home/carla/scripts/drive_car.py
"""

import time
import carla


def remove_actor_by_role(world: carla.World, role_name: str) -> None:
    for actor in world.get_actors():
        if actor.attributes.get('role_name') == role_name:
            actor.destroy()
            print(f"Removed previous actor with role '{role_name}'")


def get_spectator_transform(vehicle: carla.Vehicle) -> carla.Transform:
    transform = vehicle.get_transform()
    fwd = transform.get_forward_vector()
    offset = carla.Location(x=-20 * fwd.x, y=-20 * fwd.y, z=15)
    return carla.Transform(
        transform.location + offset,
        carla.Rotation(pitch=-30, yaw=transform.rotation.yaw, roll=0),
    )


def main() -> None:
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    remove_actor_by_role(world, 'my_car')

    spawn_point = world.get_map().get_spawn_points()[0]
    bp_lib = world.get_blueprint_library()
    vehicle_bp = bp_lib.filter('vehicle.tesla.model3')[0]
    vehicle_bp.set_attribute('role_name', 'my_car')

    vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
    if vehicle is None:
        print("ERROR: Could not spawn vehicle (spawn point may be occupied).")
        return

    print(f"Spawned: {vehicle.type_id}  id={vehicle.id}")
    print("Driving... Press Ctrl+C to stop.\n")

    spectator = world.get_spectator()
    control = carla.VehicleControl()
    control.steer = 0.0
    control.throttle = 1.0
    control.brake = 0.0

    try:
        while True:
            vehicle.apply_control(control)
            spectator.set_transform(get_spectator_transform(vehicle))

            loc = vehicle.get_location()
            vel = vehicle.get_velocity()
            speed_kmh = 3.6 * (vel.x**2 + vel.y**2 + vel.z**2) ** 0.5
            print(f"  x={loc.x:.1f}  y={loc.y:.1f}  speed={speed_kmh:.1f} km/h", end="\r")

            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nDestroying vehicle...")
        vehicle.destroy()


if __name__ == '__main__':
    main()
