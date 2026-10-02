"""Tests for the Facade pattern implementation."""

import pytest

from design_patterns.structural.facade import (
    VideoConverterFacade,
    VideoDecoder,
)


class TestVideoConverterFacade:
    def test_facade_conversion_success(self) -> None:
        facade = VideoConverterFacade()
        result = facade.convert_video("clip.mov", target_format="mp4", quality="720p")

        assert "output_bundle.mp4" in result
        assert "compressed_720p" in result
        assert "320kbps" in result

    def test_facade_unsupported_format(self) -> None:
        facade = VideoConverterFacade()
        with pytest.raises(ValueError, match="Unsupported source video format"):
            facade.convert_video("audio.mp3", target_format="mp4")

    def test_custom_subsystem_injection(self) -> None:
        class CustomDecoder(VideoDecoder):
            pass

        decoder = CustomDecoder()
        facade = VideoConverterFacade(decoder=decoder)
        res = facade.convert_video("movie.mkv", target_format="webm")
        assert "output_bundle.webm" in res
