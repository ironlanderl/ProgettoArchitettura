# Progetto di Architettura dei Calcolatori e Cloud Computing

## Getting Started

This project implements a face detection system. A Raspberry Pi captures video frames and sends them via MQTT to a PC, which performs YOLO-based object detection using its GPU and sends the results back.

For detailed setup and usage instructions, please refer to the [Wiki](https://github.com/ironlanderl/ProgettoArchitettura/wiki).

### Quick Start

1.  **Prerequisites:** Ensure you have Docker, Docker Compose, and (for PC) NVIDIA Container Toolkit installed.
2.  **Clone the repository:** `git clone https://github.com/ironlanderl/ProgettoArchitettura`
3.  **Configure Environment Variables:** Copy `.env.example` to `.env` in `pc_app/` and `rpi_app/` and update `MQTT_ENDPOINT` and `MQTT_PORT`.
4.  **Download YOLOv8 Model:**
    *   Download any of the YOLOv8 model from [YOLOv8-Face](https://github.com/Yusepp/YOLOv8-Face) to the `pc_app/` directory. Then modify the `docker-compose.yml` file to mount the model file.
4.  **Start Services:**
    *   Navigate to `mosquitto/` and run `docker compose up -d`.
    *   Navigate to `rpi_app/` and run `docker compose up -d` (ensure camera is connected).
    *   Navigate to `pc_app/` and run `docker compose up -d`.

### Verification

Check Docker logs for each service to confirm they are running and communicating correctly.

## Notes

- [How to set up and use private docker registry with authentication & web-ui](https://medium.com/@shubnimkar/how-to-set-up-and-use-private-docker-registry-with-authentication-web-ui-361ee39b2079)
- [YOLOv8-Face](https://github.com/Yusepp/YOLOv8-Face)
- [Distribute build across multiple runners](https://docs.docker.com/build/ci/github-actions/multi-platform/#distribute-build-across-multiple-runners)
- [Docker Build Cache Backend: Registry](https://docs.docker.com/build/cache/backends/registry/)
