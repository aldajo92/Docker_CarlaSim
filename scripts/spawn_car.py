"""
Hello-world script for CARLA 0.9.15.
Spawns a Tesla Model 3, attaches the spectator camera to it, and keeps
the connection alive until you press Ctrl+C.

Run from inside the container:
    python3.7 /home/carla/scripts/spawn_car.py

The CARLA server must already be running (started via docker_scripts/run.sh).
"""

import time
import carla


def remove_actor_by_role(world: carla.World, role_name: str) -> None:
    for actor in world.get_actors():
        if actor.attributes.get('role_name') == role_name:
            actor.destroy()
            print(f"Removed previous actor with role '{role_name}'")


def attach_spectator(world: carla.World, vehicle: carla.Vehicle) -> None:
    spectator = world.get_spectator()
    transform = vehicle.get_transform()
    fwd = transform.get_forward_vector()
    offset = carla.Location(x=-20 * fwd.x, y=-20 * fwd.y, z=15)
    spectator.set_transform(
        carla.Transform(
            transform.location + offset,
            carla.Rotation(pitch=-30, yaw=transform.rotation.yaw, roll=0),
        )
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
    print(f"Location: {vehicle.get_location()}")

    attach_spectator(world, vehicle)
    print("Spectator camera attached. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Destroying vehicle...")
        vehicle.destroy()


if __name__ == '__main__':
    main()
