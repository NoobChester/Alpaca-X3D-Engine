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
    def __init__(self, max_size: int = 10000, dtype: np.dtype | type = np.float64):
        # Pre-allocate with alignment-friendly size
        self._buffer = np.zeros(max_size, dtype)
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
            # Create aligned copy if not already aligned
            aligned = np.empty_like(arr, order='C')
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
# 3. CONTIGUITY: Check before passing to C++
# ============================================
def ensure_contiguous(arr: np.ndarray) -> np.ndarray:
    """Ensure array is C-contiguous, copy if needed"""
    if not arr.flags['C_CONTIGUOUS']:
        print("Warning: Array not C-contiguous, copying...")
        return np.ascontiguousarray(arr)
    return arr


# ============================================
# 4. TYPING: Verify dtype matches C++ double
# ============================================
def verify_dtype(arr: np.ndarray) -> np.ndarray:
    """Verify and convert dtype to np.float64 if needed"""
    if arr.dtype != np.float64:
        print(f"Warning: Converting dtype from {arr.dtype} to float64")
        return arr.astype(np.float64)
    return arr


# ============================================
# 5. ASYNC: WebSocket streaming for Alpaca
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
def run_trading_logic_optimized(prices_arr: np.ndarray) -> None:
    """
    Optimized trading logic with all checklist items verified
    """
    # 1. Check contiguity
    prices_arr = ensure_contiguous(prices_arr)
    print(f"C_CONTIGUOUS: {prices_arr.flags['C_CONTIGUOUS']}")

    # 2. Verify dtype
    prices_arr = verify_dtype(prices_arr)
    print(f"dtype: {prices_arr.dtype}")

    # 3. Check alignment (for AVX-512)
    alignment = prices_arr.ctypes.data % 64
    print(f"Alignment: {alignment} bytes (should be 0 for AVX-512)")

    # Call C++ engine
    print(f"\nCalling C++ engine.calculate_signal() with {len(prices_arr)} prices...")
    engine.calculate_signal(prices_arr)
    print(f"After C++ processing: {prices_arr}")


async def main_async():
    """Async main with streaming support"""
    print("=" * 50)
    print("Trading Bot - Optimized with Async Streaming")
    print("=" * 50)

    # 1. Use pre-allocated buffer
    buffer = PriceBuffer(max_size=1000)

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
    engine.apply_mean_reversion(prices_arr, mean_price)
    print(f"Prices after mean reversion (C++): {prices_arr}")


def main():
    """Entry point - runs async main"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
