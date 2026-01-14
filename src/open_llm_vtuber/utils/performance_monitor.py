"""
Performance monitoring module for tracking latency in different stages of the conversation pipeline.

This module provides functionality to measure and log the time taken for:
1. Request reception (user request to server acceptance)
2. ASR service processing
3. LLM service processing
4. TTS service processing
5. Total end-to-end latency
"""

import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from loguru import logger


class PerformanceMonitor:
    """Monitor and log performance metrics for conversation processing."""

    def __init__(
        self, log_dir: str = "logs", csv_file: str = "performance_metrics.csv"
    ):
        """
        Initialize the performance monitor.

        Args:
            log_dir: Directory to store log files and CSV files
            csv_file: Name of the CSV file to store metrics
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.csv_file = self.log_dir / csv_file
        self._init_csv_file()

    def _init_csv_file(self) -> None:
        """Initialize CSV file with headers if it doesn't exist."""
        if not self.csv_file.exists():
            with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "timestamp",
                        "session_id",
                        "network_latency_ms",
                        "asr_latency_ms",
                        "llm_first_token_ms",
                        "llm_total_latency_ms",
                        "tts_latency_ms",
                        "time_to_first_response_ms",
                        "user_input_length",
                        "response_length",
                    ]
                )

    def create_session(self, session_id: str) -> "PerformanceSession":
        """
        Create a new performance monitoring session.

        Args:
            session_id: Unique identifier for this conversation session

        Returns:
            PerformanceSession instance for tracking this session
        """
        return PerformanceSession(session_id, self)


class PerformanceSession:
    """Track performance metrics for a single conversation session."""

    def __init__(self, session_id: str, monitor: PerformanceMonitor):
        """
        Initialize a performance session.

        Args:
            session_id: Unique identifier for this session
            monitor: Parent PerformanceMonitor instance
        """
        self.session_id = session_id
        self.monitor = monitor
        self.start_time: Optional[float] = None  # Client sends request (approximate)
        self.request_reception_time: Optional[float] = None  # Server receives request
        self.asr_start_time: Optional[float] = None
        self.asr_end_time: Optional[float] = None
        self.llm_start_time: Optional[float] = None
        self.llm_first_token_time: Optional[float] = None  # First token from LLM
        self.llm_end_time: Optional[float] = None
        self.tts_start_time: Optional[float] = None
        self.tts_end_time: Optional[float] = None
        self.first_response_time: Optional[float] = (
            None  # First audio/text sent to client
        )
        self.end_time: Optional[float] = None
        self.user_input_length: int = 0
        self.response_length: int = 0
        self.tts_calls: int = 0
        self.total_tts_time: float = 0.0
        self._first_response_marked: bool = (
            False  # Track if first response already marked
        )

    def mark_request_received(self) -> None:
        """
        Mark when the server receives the user request.
        This should be called when WebSocket message arrives at server.
        """
        if self.start_time is None:
            # Use current time as approximate client send time
            # In practice, we can't know exact client send time without client-side timestamp
            self.start_time = time.perf_counter()
        self.request_reception_time = time.perf_counter()

    def mark_asr_start(self) -> None:
        """Mark the start of ASR processing."""
        self.asr_start_time = time.perf_counter()

    def mark_asr_end(self) -> None:
        """Mark the end of ASR processing."""
        self.asr_end_time = time.perf_counter()

    def mark_llm_start(self) -> None:
        """Mark the start of LLM processing."""
        self.llm_start_time = time.perf_counter()

    def mark_llm_first_token(self) -> None:
        """Mark when the first token is received from LLM (TTFB)."""
        if self.llm_first_token_time is None:
            self.llm_first_token_time = time.perf_counter()

    def mark_llm_end(self) -> None:
        """Mark the end of LLM processing."""
        self.llm_end_time = time.perf_counter()

    def mark_first_response(self) -> None:
        """Mark when the first response (audio/text) is sent to client."""
        if not self._first_response_marked:
            self.first_response_time = time.perf_counter()
            self._first_response_marked = True

    def mark_tts_start(self) -> None:
        """Mark the start of a TTS call."""
        self.tts_start_time = time.perf_counter()
        self.tts_calls += 1

    def mark_tts_end(self) -> None:
        """Mark the end of a TTS call."""
        if self.tts_start_time is not None:
            tts_end = time.perf_counter()
            tts_duration = (tts_end - self.tts_start_time) * 1000  # Convert to ms
            self.total_tts_time += tts_duration
            self.tts_end_time = tts_end
            self.tts_start_time = None  # Reset for next call

    def set_user_input_length(self, length: int) -> None:
        """
        Set the length of user input.

        Args:
            length: Length of user input (characters or audio samples)
        """
        self.user_input_length = length

    def set_response_length(self, length: int) -> None:
        """
        Set the length of AI response.

        Args:
            length: Length of AI response in characters
        """
        self.response_length = length

    def finalize(self) -> Dict[str, float]:
        """
        Finalize the session and calculate all metrics.

        Returns:
            Dictionary containing all calculated metrics in milliseconds
        """
        if self.end_time is None:
            self.end_time = time.perf_counter()

        metrics = {}

        # Calculate network latency (client send to server receive)
        # Note: This is approximate since we can't know exact client send time
        if self.start_time is not None and self.request_reception_time is not None:
            metrics["network_latency_ms"] = (
                self.request_reception_time - self.start_time
            ) * 1000
        else:
            metrics["network_latency_ms"] = 0.0

        # Calculate ASR latency
        if self.asr_start_time is not None and self.asr_end_time is not None:
            metrics["asr_latency_ms"] = (self.asr_end_time - self.asr_start_time) * 1000
        else:
            metrics["asr_latency_ms"] = 0.0

        # Calculate LLM first token latency (TTFB)
        if self.llm_start_time is not None and self.llm_first_token_time is not None:
            metrics["llm_first_token_ms"] = (
                self.llm_first_token_time - self.llm_start_time
            ) * 1000
        else:
            metrics["llm_first_token_ms"] = 0.0

        # Calculate LLM total latency
        if self.llm_start_time is not None and self.llm_end_time is not None:
            metrics["llm_total_latency_ms"] = (
                self.llm_end_time - self.llm_start_time
            ) * 1000
        else:
            metrics["llm_total_latency_ms"] = 0.0

        # Calculate TTS latency (total time across all TTS calls)
        metrics["tts_latency_ms"] = self.total_tts_time

        # Calculate time to first response (from request to first feedback)
        if self.start_time is not None and self.first_response_time is not None:
            metrics["time_to_first_response_ms"] = (
                self.first_response_time - self.start_time
            ) * 1000
        else:
            metrics["time_to_first_response_ms"] = 0.0

        return metrics

    def log_and_save(self) -> None:
        """Log metrics and save to CSV file."""
        metrics = self.finalize()

        # Log to console
        logger.info(
            f"📊 Performance Metrics for session {self.session_id}:\n"
            f"  Network Latency: {metrics['network_latency_ms']:.2f} ms\n"
            f"  ASR Latency: {metrics['asr_latency_ms']:.2f} ms\n"
            f"  LLM First Token (TTFB): {metrics['llm_first_token_ms']:.2f} ms\n"
            f"  LLM Total Latency: {metrics['llm_total_latency_ms']:.2f} ms\n"
            f"  TTS Latency: {metrics['tts_latency_ms']:.2f} ms ({self.tts_calls} calls)\n"
            f"  Time to First Response: {metrics['time_to_first_response_ms']:.2f} ms"
        )

        # Save to CSV
        with open(self.monitor.csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    datetime.now().isoformat(),
                    self.session_id,
                    f"{metrics['network_latency_ms']:.2f}",
                    f"{metrics['asr_latency_ms']:.2f}",
                    f"{metrics['llm_first_token_ms']:.2f}",
                    f"{metrics['llm_total_latency_ms']:.2f}",
                    f"{metrics['tts_latency_ms']:.2f}",
                    f"{metrics['time_to_first_response_ms']:.2f}",
                    self.user_input_length,
                    self.response_length,
                ]
            )
