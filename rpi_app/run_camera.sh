sudo modprobe v4l2loopback devices=1 max_buffers=2 exclusive_caps=1 card_label="VirtualCam #0"
sudo ffmpeg -i http://$1:4747/video/ -f v4l2 -pix_fmt yuv420p /dev/video0