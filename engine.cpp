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
    m.def("calculate_signal", [](nb::ndarray<double, nb::c_contig> prices) {
        // Convert the nanobind ndarray directly into a C++20 span
        auto prices_view = std::span<double>(prices.data(), prices.shape(0));

        // Offload GIL to allow multi-threaded math execution on the 9800X3D
        nb::gil_scoped_release release;
        calculate_signal(prices_view);
    }, "Processes price arrays using 512-bit wide SIMD paths.");

    m.def("apply_mean_reversion", [](nb::ndarray<double, nb::c_contig> data, double mean) {
        apply_mean_reversion(data.data(), data.shape(0), mean);
    }, "Applies mean reversion math on ZMM registers");
}