from __future__ import annotations

from pathlib import Path


class MeCabService:
    def __init__(self) -> None:
        self._tagger = None
        self._init_error: str | None = None
        self._ensure_tagger()

    def _ensure_tagger(self) -> None:
        if self._tagger is not None or self._init_error is not None:
            return

        try:
            import MeCab  # type: ignore[import-not-found]
        except ModuleNotFoundError:
            self._init_error = (
                "MeCab tokenizer is unavailable because required dependencies "
                "(`mecab-python3` and a UniDic dictionary package) are not installed."
            )
            return

        dictionary_dir = None
        try:
            import unidic  # type: ignore[import-not-found]

            candidate_dir = Path(unidic.DICDIR)
            if (candidate_dir / "mecabrc").exists():
                dictionary_dir = str(candidate_dir)
        except ModuleNotFoundError:
            pass

        if dictionary_dir is None:
            try:
                import unidic_lite  # type: ignore[import-not-found]

                dictionary_dir = unidic_lite.DICDIR
            except ModuleNotFoundError:
                self._init_error = (
                    "MeCab tokenizer is unavailable because no usable UniDic dictionary "
                    "package (`unidic` with downloaded data or `unidic-lite`) is installed."
                )
                return

        try:
            self._tagger = MeCab.Tagger(f"-r /dev/null -d {dictionary_dir}")
        except Exception as exc:  # pragma: no cover - depends on local dictionary install
            self._init_error = (
                "MeCab tokenizer is unavailable because the UniDic dictionary "
                f"could not be initialized: {exc}"
            )

    @staticmethod
    def _extract_reading(features: list[str], word: str) -> str:
        for index in (7, 8, 6):
            if index < len(features) and features[index] and features[index] != "*":
                return features[index]
        return word

    def tokenize_japanese_sentence(self, text: str) -> list[dict[str, str]]:
        if not text.strip():
            return []

        self._ensure_tagger()
        if self._tagger is None:
            raise RuntimeError(self._init_error or "MeCab tokenizer is unavailable.")

        try:
            parsed = self._tagger.parse(text) or ""
        except Exception as exc:  # pragma: no cover - depends on local MeCab runtime
            raise RuntimeError(f"MeCab tokenizer failed to parse the provided text: {exc}") from exc
        tokens: list[dict[str, str]] = []

        for raw_line in parsed.splitlines():
            line = raw_line.strip()
            if not line or line == "EOS":
                continue

            parts = line.split("\t")
            word = parts[0]
            features_blob = parts[-1] if len(parts) > 1 else ""
            features = [item.strip() for item in features_blob.split(",")] if features_blob else []
            pos = features[0] if features else ""
            reading = self._extract_reading(features, word)
            tokens.append({"word": word, "reading": reading, "pos": pos})

        return tokens
