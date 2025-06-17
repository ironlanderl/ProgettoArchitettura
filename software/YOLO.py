import ultralytics


class YOLO:
    def __init__(self, model: str):
        """
        Initialize the YOLO model with the specified path.
        
        :param model: Path to the YOLO model file.
        """
        self.model = ultralytics.YOLO(model)

    def predict_on_cv2_image(self, image):
        """
        Perform inference on a given OpenCV image.
        
        :param image: An OpenCV image (numpy array).
        :return: List of detected objects with their bounding boxes and labels.
        """
        results = self.model(image)
        detections = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = result.names[int(box.cls[0].item())]
                detections.append({
                    'bbox': (x1, y1, x2, y2),
                    'label': label,
                    'confidence': box.conf[0].item()
                })

        return detections