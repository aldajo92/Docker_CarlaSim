# CarlaSim

A Docker-based setup for running [CARLA Simulator 0.9.15](https://carla.org/) on Linux, with Python 3.7 scripting support.

## Requirements

- Docker
- NVIDIA GPU + [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) (for `nvidia_run.sh`)
- X11 display (for the simulator window)

## Project Structure

```
CarlaSim/
├── Dockerfile                  # Extends carlasim/carla:0.9.15 with Python 3.7 + carla client
├── config_docker.sh            # Image name, container name, network settings
├── docker_scripts/
│   ├── build.sh                # Build the Docker image
│   ├── run.sh                  # Start the CARLA server (CPU/software rendering)
│   ├── nvidia_run.sh           # Start the CARLA server (NVIDIA GPU)
│   └── exec.sh                 # Open a shell in the running container
└── scripts/                    # Python scripts — mounted at /home/carla/scripts
    ├── spawn_car.py            # Spawn a vehicle and attach the spectator camera
    └── drive_car.py            # Spawn a vehicle and drive it forward at full throttle
```

## Getting Started

### 1. Build the image

```bash
./docker_scripts/build.sh
```

This builds a custom image on top of `carlasim/carla:0.9.15` that adds:
- Python 3.7
- `carla` Python client (installed from the wheel bundled inside the base image)
- `numpy`, `matplotlib`, `pygame`

> **Why not `pip install carla==0.9.15`?** The `carla` package on PyPI only goes up to 0.9.5.
> The correct wheel for 0.9.15 ships inside the base image at
> `/home/carla/PythonAPI/carla/dist/`.

### 2. Start the CARLA server

**With NVIDIA GPU (recommended):**
```bash
./docker_scripts/nvidia_run.sh
```

**Without GPU (software rendering):**
```bash
./docker_scripts/run.sh
```

The simulator window will open. The container is named `carla_sim` and the
`scripts/` folder is automatically mounted at `/home/carla/scripts` inside it.

### 3. Open a Python shell in the running container

In a second terminal:
```bash
./docker_scripts/exec.sh
```

### 4. Run a script

```bash
# Spawn a vehicle and attach the spectator camera
python3.7 /home/carla/scripts/spawn_car.py

# Spawn a vehicle and drive it forward
python3.7 /home/carla/scripts/drive_car.py
```

Press `Ctrl+C` to stop any script. The vehicle is destroyed automatically on exit.

## Writing Your Own Scripts

All Python scripts placed in `scripts/` are available inside the container at
`/home/carla/scripts/` without rebuilding the image.

Every script follows the same pattern:

```python
import carla

client = carla.Client('localhost', 2000)   # connect to the running CARLA server
client.set_timeout(10.0)
world = client.get_world()
```

### Spawning a vehicle

```python
spawn_point = world.get_map().get_spawn_points()[0]
vehicle_bp = world.get_blueprint_library().filter('vehicle.tesla.model3')[0]
vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
```

### Controlling a vehicle

```python
control = carla.VehicleControl()
control.throttle = 1.0   # 0.0 – 1.0
control.steer    = 0.0   # -1.0 (left) – 1.0 (right)
control.brake    = 0.0   # 0.0 – 1.0
vehicle.apply_control(control)
```

### Available vehicles

| Category | Blueprint IDs |
|---|---|
| Cars | `vehicle.tesla.model3`, `vehicle.ford.mustang`, `vehicle.audi.tt`, `vehicle.bmw.grandtourer`, `vehicle.chevrolet.impala`, `vehicle.dodge.charger_2020`, `vehicle.jeep.wrangler_rubicon`, `vehicle.lincoln.mkz_2020`, `vehicle.mercedes.coupe_2020`, `vehicle.mini.cooper_s_2021`, `vehicle.nissan.patrol_2021`, `vehicle.seat.leon`, `vehicle.tesla.cybertruck`, `vehicle.toyota.prius`, … |
| Trucks / Special | `vehicle.carlamotors.firetruck`, `vehicle.ford.ambulance`, `vehicle.mercedes.sprinter`, `vehicle.carlamotors.european_hgv`, `vehicle.mitsubishi.fusorosa` |
| Bikes / Motorcycles | `vehicle.harley-davidson.low_rider`, `vehicle.kawasaki.ninja`, `vehicle.yamaha.yzf`, `vehicle.vespa.zx125`, `vehicle.bh.crossbike` |

## Going Further

The tutorial this project is based on walks through building a full self-driving
pipeline step by step:

- [Build a Self-Driving Car in CARLA with Python](https://pub.towardsai.net/build-a-self-driving-car-in-carla-simulator-with-python-step-by-step-022f8997a6a3)
- Example code repository: [github.com/andrey7mel/carla-python-examples](https://github.com/andrey7mel/carla-python-examples)

Clone the examples into `scripts/` to run them directly:

```bash
cd scripts/
git clone https://github.com/andrey7mel/carla-python-examples .
```

Then inside the container:

| Command | What it does |
|---|---|
| `python3.7 -m sd_1` | Spawn car + attach spectator |
| `python3.7 -m sd_2` | Drive straight at full throttle |
| `python3.7 -m sd_4` | Follow waypoints, stop at intersection |
| `python3.7 -m sd_5` | PID speed controller |
| `python3.7 -m sd_6` | Stanley steering — follow a curved route |
| `python3.7 -m sd_7` | Obstacle sensor + emergency braking |

## Ports

| Port | Purpose |
|---|---|
| `2000` | CARLA server (client connections) |
| `2001` | Traffic Manager |
