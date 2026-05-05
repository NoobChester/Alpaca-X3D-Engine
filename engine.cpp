#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <vector>
#include <numeric>
#include <algorithm>
#include <span>
#include <memory>

namespace nb = nanobind;

/**
 * @brief Applies a simple transformation to price data for signal generation
 * @details Multiplies each price by 1.0001 and adds 0.5. This is a placeholder
 *          function that will be replaced with actual trading signal calculations.
 *          Optimized for AVX-512 and Zen 5 architecture with vectorization.
 * @param prices Pointer to array of prices (modified in-place)
 * @param n Number of elements in the prices array
 * @note Uses __restrict to indicate no pointer aliasing, enabling better optimization
 * @warning Input array must be at least n elements long and properly aligned
 */
auto calculate_signal(std::span<double> prices) -> void {
    // Access the raw pointer for the SIMD loop
    double* __restrict prices_ptr = std::assume_aligned<64>(prices.data());
    size_t n = prices.size();

    #pragma clang loop vectorize(enable) vectorize_width(8)
    for (size_t i = 0; i < n; ++i) {
        prices_ptr[i] = (prices_ptr[i] * 1.0001) + 0.5;
    }
}


/**
 * @brief Checks the health of the input buffer for signal processing
 * @details Performs manual checks on the input buffer to ensure it meets the requirements
 *          for optimal performance on AVX-512 and Zen 5 architecture. This includes dtype verification,
 *          alignment checks, and contiguity checks. This function is called before any processing to avoid costly errors down the line.
 * @param prices The input buffer containing price data to be processed
 * @throws nb::type_error if any of the checks fail, providing detailed error messages for debugging
 * @note This is a critical function for ensuring that the engine operates on valid data and can achieve optimal performance
 *       without unexpected crashes or slowdowns due to invalid input.
 * @see calculate_signal() for the main signal processing function that relies on this buffer health check
 */
auto check_buffer_health(nb::ndarray<double, nb::shape<-1>, nb::c_contig, nb::device::cpu> prices) -> void {
    // 1. Manual dtype verification for extra safety
    if (prices.dtype() != nb::dtype<double>()) {
        throw nb::type_error("Dtype Mismatch: Engine requires float64 (double).");
    }
    // 2. Alignment Check (64-byte for Zen 5)
    if (reinterpret_cast<uintptr_t>(prices.data()) % 64 != 0) {
        throw nb::type_error("Alignment Error: Buffer is not 64-byte aligned.");
    }
    // 3. Contiguity Check
    if (prices.stride(0) != 1) {
        throw nb::type_error("Contiguity Error: Buffer must be C_CONTIGUOUS.");
    }
}

/**
 * @brief Applies mean reversion by subtracting the mean from each data point
 * @details Centers the data around zero by subtracting the provided mean value
 *          from each element. Useful for mean reversion trading strategies
 *          where deviations from the mean indicate trading opportunities.
 *          Optimized for AVX-512 and Zen 5 architecture.
 * @param data Pointer to array of data points (modified in-place)
 * @param n Number of elements in the data array
 * @param mean The mean value to subtract from each data point
 * @note This is a placeholder for more sophisticated mean reversion calculations
 * @see calculate_signal() for related signal processing
 */
auto apply_mean_reversion(double* __restrict data, size_t n, double mean) -> void {
    #pragma clang loop vectorize(enable) vectorize_width(8)
    for (size_t i = 0; i < n; ++i) {
        data[i] -= mean;
    }
}

// Creating the Python bridge
NB_MODULE(engine, m) {
    m.def("calculate_signal", [](nb::ndarray<double, nb::shape<-1>, nb::c_contig, nb::device::cpu> prices) {
        // Perform buffer health checks before processing
        check_buffer_health(prices);

        // Convert the nanobind ndarray directly into a C++20 span
        auto prices_view = std::span<double>(prices.data(), prices.shape(0));

        // Offload GIL to allow multi-threaded math execution on the 9800X3D
        nb::gil_scoped_release release;
        calculate_signal(prices_view);
    }, "Processes price arrays using 512-bit wide SIMD paths.");

    m.def("apply_mean_reversion", [](nb::ndarray<double, nb::shape<-1>, nb::c_contig, nb::device::cpu> data, double mean) {
        apply_mean_reversion(data.data(), data.shape(0), mean);
    }, "Applies mean reversion math on ZMM registers");
}