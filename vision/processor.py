"""Computer vision processing using OpenCV and YOLO."""

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from core.config import VisionSettings


@dataclass
class Detection:
    """A detected object in an image."""

    label: str
    confidence: float
    bbox: tuple[int, int, int, int]  # x1, y1, x2, y2
    center: tuple[int, int]


@dataclass
class FrameAnalysis:
    """Analysis results for a video frame."""

    detections: list[Detection]
    frame: np.ndarray
    timestamp: float


class VisionProcessor:
    """Handles computer vision tasks using YOLO for object detection.

    Supports real-time camera processing and single image analysis.
    """

    def __init__(self, settings: VisionSettings) -> None:
        self.settings = settings
        self._model: Any = None
        self._camera: cv2.VideoCapture | None = None

    def _load_model(self) -> Any:
        """Lazy load the YOLO model."""
        if self._model is None:
            from ultralytics import YOLO

            self._model = YOLO(self.settings.model)
        return self._model

    def _get_camera(self) -> cv2.VideoCapture:
        """Get or create camera capture."""
        if self._camera is None or not self._camera.isOpened():
            self._camera = cv2.VideoCapture(self.settings.camera_index)
            self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return self._camera

    async def capture_frame(self) -> np.ndarray | None:
        """Capture a single frame from the camera."""
        loop = asyncio.get_running_loop()

        def capture() -> np.ndarray | None:
            camera = self._get_camera()
            ret, frame = camera.read()
            return frame if ret else None

        return await loop.run_in_executor(None, capture)

    async def detect_objects(
        self, frame: np.ndarray, confidence_threshold: float | None = None
    ) -> list[Detection]:
        """Detect objects in a frame.

        Args:
            frame: Image as numpy array (BGR format from OpenCV)
            confidence_threshold: Minimum confidence for detections

        Returns:
            List of detected objects
        """
        threshold = confidence_threshold or self.settings.confidence_threshold
        model = self._load_model()

        loop = asyncio.get_running_loop()

        def run_detection() -> list[Detection]:
            results = model(frame, verbose=False)[0]
            detections = []

            for box in results.boxes:
                conf = float(box.conf[0])
                if conf < threshold:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = results.names[int(box.cls[0])]

                detections.append(
                    Detection(
                        label=label,
                        confidence=conf,
                        bbox=(x1, y1, x2, y2),
                        center=((x1 + x2) // 2, (y1 + y2) // 2),
                    )
                )

            return detections

        return await loop.run_in_executor(None, run_detection)

    async def analyze_frame(self, frame: np.ndarray | None = None) -> FrameAnalysis:
        """Analyze a frame or capture and analyze.

        Args:
            frame: Optional frame to analyze. If None, captures from camera.

        Returns:
            FrameAnalysis with detections and frame
        """
        import time

        if frame is None:
            frame = await self.capture_frame()
            if frame is None:
                raise RuntimeError("Failed to capture frame")

        detections = await self.detect_objects(frame)

        return FrameAnalysis(
            detections=detections,
            frame=frame,
            timestamp=time.time(),
        )

    async def stream_analysis(self, interval: float = 0.5) -> AsyncIterator[FrameAnalysis]:
        """Continuously analyze camera frames.

        Args:
            interval: Seconds between analyses

        Yields:
            FrameAnalysis for each processed frame
        """
        while True:
            try:
                analysis = await self.analyze_frame()
                yield analysis
                await asyncio.sleep(interval)
            except RuntimeError:
                # Camera error, wait and retry
                await asyncio.sleep(1.0)

    def describe_scene(self, detections: list[Detection]) -> str:
        """Generate a natural language description of detections."""
        if not detections:
            return "I don't see anything notable."

        # Count objects by type
        counts: dict[str, int] = {}
        for det in detections:
            counts[det.label] = counts.get(det.label, 0) + 1

        # Build description
        parts = []
        for label, count in sorted(counts.items(), key=lambda x: -x[1]):
            if count == 1:
                parts.append(f"a {label}")
            else:
                parts.append(f"{count} {label}s")

        if len(parts) == 1:
            return f"I see {parts[0]}."
        elif len(parts) == 2:
            return f"I see {parts[0]} and {parts[1]}."
        else:
            return f"I see {', '.join(parts[:-1])}, and {parts[-1]}."

    async def close(self) -> None:
        """Release camera and cleanup."""
        if self._camera is not None:
            self._camera.release()
            self._camera = None
