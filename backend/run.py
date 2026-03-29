import os, sys
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

# Python 3.14 兼容性补丁：修复 websockets 库
try:
    from websockets.asyncio.connection import Connection
    _orig_connection_lost = Connection.connection_lost
    def _patched_connection_lost(self, exc):
        if not hasattr(self, 'recv_messages'):
            return
        _orig_connection_lost(self, exc)
    Connection.connection_lost = _patched_connection_lost
except Exception:
    pass

# Python 3.14 兼容: pydantic v1 类型推断broken，patch 让它 fallback 到 Any
if sys.version_info >= (3, 14):
    from typing import Any
    import pydantic.v1.fields as _pv1f
    from pydantic.v1 import errors as _pv1e
    _orig = _pv1f.ModelField._set_default_and_type
    def _patched(self):
        try:
            _orig(self)
        except _pv1e.ConfigError:
            self.type_ = Any
            self.outer_type_ = Any
            self.annotation = Any
    _pv1f.ModelField._set_default_and_type = _patched

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
