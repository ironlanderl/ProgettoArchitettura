import ultralytics
import cv2

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
    
    def overlay_detections(self, image, detections):
        """
        Overlay detected bounding boxes and labels on the image.
        
        :param image: An OpenCV image (numpy array).
        :param detections: List of detected objects with their bounding boxes and labels.
        :return: Image with detections overlaid.
        """
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            label = detection['label']
            confidence = detection['confidence']

            # Draw bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
            # Put label text
            cv2.putText(image, f"{label} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        return image