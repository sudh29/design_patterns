"""Facade Design Pattern.

Classification: Structural
Intent:
    Provide a unified interface to a set of interfaces in a subsystem.
    Facade defines a higher-level interface that makes the subsystem easier to use.

Motivation & Real-World Analogy:
    A multimedia processing pipeline contains complex, granular subsystems:
    audio stream extraction, video decoding, color space conversion, bitrate compression,
    and container multiplexing (MKV/MP4).
    Clients (such as a simple web upload controller) only care about:
    "Convert this file to MP4 with 1080p quality."
    The Facade provides a clean entrypoint, managing subsystem initialization and
    orchestration behind the scenes.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class VideoConverterFacade {
            -decoder: VideoDecoder
            -audio_mixer: AudioMixer
            -compressor: BitrateCompressor
            -muxer: ContainerMuxer
            +convert_video(file_path: str, target_format: str) str
        }
        class VideoDecoder {
            +decode(file: str) str
        }
        class AudioMixer {
            +extract_and_normalize(file: str) str
        }
        class BitrateCompressor {
            +compress(video_stream: str, quality: str) str
        }
        class ContainerMuxer {
            +mux(video: str, audio: str, fmt: str) str
        }
        VideoConverterFacade o--> VideoDecoder
        VideoConverterFacade o--> AudioMixer
        VideoConverterFacade o--> BitrateCompressor
        VideoConverterFacade o--> ContainerMuxer
    ```
"""

from __future__ import annotations

from dataclasses import dataclass


# ==============================================================================
# 1. Complex Subsystem Classes
# ==============================================================================
@dataclass
class VideoStream:
    raw_data: str
    fps: int = 30


@dataclass
class AudioStream:
    channels: int
    bitrate_kbps: int


class VideoDecoder:
    """Subsystem 1: Low-level video decoder."""

    def decode(self, file_path: str) -> VideoStream:
        return VideoStream(raw_data=f"raw_frames_from_{file_path}")


class AudioMixer:
    """Subsystem 2: Audio extraction and normalization."""

    def extract_audio(self, file_path: str) -> AudioStream:
        return AudioStream(channels=2, bitrate_kbps=320)


class BitrateCompressor:
    """Subsystem 3: Heavy video frame compression."""

    def compress(self, stream: VideoStream, target_quality: str) -> VideoStream:
        return VideoStream(raw_data=f"{stream.raw_data}_compressed_{target_quality}")


class ContainerMuxer:
    """Subsystem 4: Packaging streams into containers (.mp4, .webm)."""

    def mux(self, video: VideoStream, audio: AudioStream, target_format: str) -> str:
        return (
            f"output_bundle.{target_format} "
            f"[Video: {video.raw_data}, Audio: {audio.bitrate_kbps}kbps]"
        )


# ==============================================================================
# 2. Facade
# ==============================================================================
class VideoConverterFacade:
    """Unified Facade simplifying the complex video pipeline into a single call."""

    def __init__(
        self,
        decoder: VideoDecoder | None = None,
        audio_mixer: AudioMixer | None = None,
        compressor: BitrateCompressor | None = None,
        muxer: ContainerMuxer | None = None,
    ) -> None:
        self._decoder = decoder or VideoDecoder()
        self._audio_mixer = audio_mixer or AudioMixer()
        self._compressor = compressor or BitrateCompressor()
        self._muxer = muxer or ContainerMuxer()

    def convert_video(self, file_path: str, target_format: str, quality: str = "1080p") -> str:
        """High-level simple interface coordinating all underlying subsystems."""
        if not file_path.endswith((".avi", ".mov", ".mkv", ".mp4")):
            raise ValueError(f"Unsupported source video format: {file_path}")

        raw_video = self._decoder.decode(file_path)
        audio = self._audio_mixer.extract_audio(file_path)
        compressed_video = self._compressor.compress(raw_video, quality)
        result = self._muxer.mux(compressed_video, audio, target_format)
        return result


# ==============================================================================
# 3. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    facade = VideoConverterFacade()
    output = facade.convert_video("holiday_vacation.mov", target_format="mp4", quality="4k")
    print(f"Transcoding Result: {output}")
