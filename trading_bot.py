"""
Optimized trading_bot.py with proper buffering, alignment, and async support
Addresses the implementation checklist for optimal C++ engine performance
"""

import engine  # Your compiled C++ module
import numpy as np
from typing import List
import asyncio


# ============================================
# 1. BUFFERING: Pre-allocated reusable buffers
# ============================================
class PriceBuffer:
    """Pre-allocated, reusable price buffer for zero-allocation trading"""
    def __init__(self, max_size: int = 10000, dtype: np.dtype = np.dtype(np.float64)):
        # Create 64-byte aligned buffer from the start
        self._buffer = create_aligned_array(max_size, dtype)
        self._size = 0
        self._max_size = max_size

    @property
    def size(self) -> int:
        """Public getter for current number of valid elements in the buffer"""
        return self._size

    @property
    def max_size(self) -> int:
        """Public getter for maximum buffer capacity"""
        return self._max_size

    @max_size.setter
    def max_size(self, value: int):
        """Setter for max_size (updates internal _max_size)"""
        self._max_size = value

    @property
    def buffer(self) -> np.ndarray:
        """Public getter for the underlying buffer array"""
        return self._buffer

    @property
    def data(self) -> np.ndarray:
        """Get view of valid data (no copy) - replaces get_array()"""
        return self._buffer[:self._size]

    def reset(self):
        """Reset without deallocating"""
        self._size = 0

    def append(self, price: float):
        """Add price to buffer"""
        if self._size < self._max_size:
            self._buffer[self._size] = price
            self._size += 1

    def get_aligned_array(self) -> np.ndarray:
        """Get 64-byte aligned array for AVX-512"""
        arr = self.data
        if (arr.ctypes.data % 64) != 0:
            # Create properly aligned copy using the alignment function
            aligned = create_aligned_array(len(arr), arr.dtype)
            np.copyto(aligned, arr)
            return aligned
        return arr

# ============================================
# 2. ALIGNMENT: 64-byte aligned arrays
# ============================================
def create_aligned_array(size: int, dtype: np.dtype | str | type = np.float64) -> np.ndarray:
    """Create a 64-byte aligned numpy array for AVX-512"""
    nbytes = size * np.dtype(dtype).itemsize
    buf = np.empty(nbytes + 63, dtype=np.uint8)

    # Calculate aligned offset
    offset = (64 - (buf.ctypes.data % 64)) % 64
    aligned_buf = buf[offset:offset + nbytes].view(dtype)

    return aligned_buf

# ============================================
# 3. ASYNC: WebSocket streaming for Alpaca
# ============================================
class AlpacaStreamClient:
    """Async WebSocket client for Alpaca market data"""
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.ws_url = "wss://stream.data.alpaca.markets/v2"

    async def stream_quotes(self, symbols: List[str], buffer: PriceBuffer):
        """Stream real-time quotes and fill buffer"""
        # Note: This is a stub - actual Alpaca auth required
        print(f"Streaming quotes for {symbols}...")

        # Simulate streaming with mock data
        mock_prices = [150.2, 151.5, 150.8, 152.1, 153.0]
        for price in mock_prices:
            buffer.append(price)
            await asyncio.sleep(0.1)  # Simulate network delay

        print(f"Buffered {buffer.size} prices")

# ============================================
# Main Trading Logic (Optimized)
# ============================================
def check_buffer_health(prices_arr: np.ndarray) -> None:
    """The Triple-Check: Dtype, Alignment, and Contiguity."""

    # 1. Dtype Check
    expected_dtype = np.dtype(np.float64)
    is_correct_type = (prices_arr.dtype == expected_dtype)
    if is_correct_type:
        print(f"✅ Dtype Check Passed: {prices_arr.dtype}")
    else:
        print(f"❌ Dtype Check Failed: Got {prices_arr.dtype}, expected {expected_dtype}")
        raise TypeError(f"Dtype Error: Got {prices_arr.dtype}, expected {expected_dtype}")

    # 2. Alignment Check
    alignment = prices_arr.ctypes.data % 64
    if alignment == 0:
        print("✅ Python Side: 64-byte Alignment Verified")
    else:
        print(f"❌ Alignment Check Failed: Address {hex(prices_arr.ctypes.data)} is not 64-byte aligned (alignment={alignment} bytes)")
        raise MemoryError(
            f"Performance Contract Broken: Unaligned memory at address {hex(prices_arr.ctypes.data)} (alignment={alignment} bytes, expected 0)"
        )

    # 3. Contiguity Check
    is_contiguous = prices_arr.flags['C_CONTIGUOUS']
    if is_contiguous:
        print("✅ Contiguity Check Passed: Array is C-contiguous")
    else:
        print("❌ Contiguity Check Failed: Array is not C-contiguous")
        raise ValueError("Contiguity Error: Array must be C-contiguous for optimal performance")

def run_trading_logic_optimized(prices_arr: np.ndarray) -> None:
    """
    Optimized trading logic with all checklist items verified
    """
    check_buffer_health(prices_arr)
    # Pass to C++: If this doesn't throw the runtime_error we added above,
    # the bridge is perfectly synchronized.
    try:
        # Call C++ engine
        print(f"\nCalling C++ engine.calculate_signal() with {len(prices_arr)} prices...")
        engine.calculate_signal(prices_arr)
        print("✅ C++ Side: Bridge received aligned data with zero-copy.")
        print(f"After C++ processing: {prices_arr}")
    except RuntimeError as e:
        print(f"❌ Bridge Failure: {e}")

async def main_async():
    """Async main with streaming support"""
    print("=" * 50)
    print("Trading Bot - Optimized with Async Streaming")
    print("=" * 50)

    # 1. Use pre-allocated buffer
    buffer = PriceBuffer(max_size=100000)

    # Simulate getting data
    mock_prices = [150.2, 151.5, 150.8, 152.1, 153.0, 151.2, 154.5, 153.8]
    for p in mock_prices:
        buffer.append(p)

    # Get aligned, contiguous array
    prices_arr = buffer.get_aligned_array()

    # Run optimized trading logic
    run_trading_logic_optimized(prices_arr)

    # Mean reversion demo
    print("\n" + "=" * 50)
    print("Mean Reversion Demo (Optimized)")
    print("=" * 50)

    mean_price = np.mean(prices_arr)
    print(f"Mean price: {mean_price:.4f}")

    # Apply mean reversion (C++)
    engine.apply_mean_reversion(prices_arr, float(mean_price))
    print(f"Prices after mean reversion (C++): {prices_arr}")


def main():
    """Entry point - runs async main"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
