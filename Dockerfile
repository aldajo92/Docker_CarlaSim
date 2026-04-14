FROM carlasim/carla:0.9.15

# Run as root to allow setup
USER root

# Install Python 3.7 (required for the bundled carla cp37 wheel)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.7 \
    python3.7-distutils \
    && rm -rf /var/lib/apt/lists/*

# Bootstrap pip for Python 3.7
ADD https://bootstrap.pypa.io/pip/3.7/get-pip.py /tmp/get-pip.py
RUN python3.7 /tmp/get-pip.py && rm /tmp/get-pip.py

# Install the CARLA Python client from the wheel bundled inside the image
# (carla==0.9.15 is not on PyPI; the cp37 wheel ships at this path)
RUN python3.7 -m pip install \
    /home/carla/PythonAPI/carla/dist/carla-0.9.15-cp37-cp37m-manylinux_2_27_x86_64.whl \
    numpy \
    matplotlib \
    pygame

# Switch back to carla user
USER carla

# Expose CARLA ports
# 2000: CARLA server port
# 2001: Traffic manager port
EXPOSE 2000 2001

ENTRYPOINT ["/bin/bash", "./CarlaUE4.sh"]
