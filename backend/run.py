import os, sys
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_OFFLINE"] = "1"

# Python 3.14 兼容: pydantic v1 类型推断broken，patch 让它 fallback 到 Any
if sys.version_info >= (3, 14):
    from typing import Any
    import pydantic.v1.fields as _pv1f
    _orig = _pv1f.ModelField._set_default_and_type
    def _patched(self):
        try:
            _orig(self)
        except _pv1f.errors_.ConfigError:
            self.type_ = Any
            self.outer_type_ = Any
            self.annotation = Any
    _pv1f.ModelField._set_default_and_type = _patched

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
