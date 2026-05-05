import numpy as np
import engine

# 1. Test Alignment Failure
raw_data = np.random.rand(1024).astype(np.float64)
# Intentionally misalign by slicing (offsets the pointer by 8 bytes)
misaligned = raw_data[1:]

def create_aligned_array(size: int, dtype: np.dtype | str | type = np.float64) -> np.ndarray:
    """Create a 64-byte aligned numpy array for AVX-512"""
    nbytes = size * np.dtype(dtype).itemsize
    buf = np.empty(nbytes + 63, dtype=np.uint8)

    # Calculate aligned offset
    offset = (64 - (buf.ctypes.data % 64)) % 64
    aligned_buf = buf[offset:offset + nbytes].view(dtype)

    return aligned_buf

try:
    engine.calculate_signal(misaligned)
except TypeError as e:
    print(f"Caught expected alignment error: {e}")

# 2. Test Success Path
# Assuming your create_aligned_array utility is used:
aligned_data = create_aligned_array(1024, dtype=np.float64)
engine.calculate_signal(aligned_data)
print("Signal calculation successful on aligned Zen 5 buffer.")
