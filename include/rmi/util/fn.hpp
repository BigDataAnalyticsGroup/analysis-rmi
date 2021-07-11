#pragma once

#include <fstream>
#include <iostream>
#include <limits>
#include <sstream>
#include <type_traits>
#include <vector>


/*======================================================================================================================
 * Bit Functions
 *====================================================================================================================*/

/**
 * Computes the amount of bits needed to represent unsigned value @p n.
 * @tparam Numeric the type of the value
 * @param n the value
 * @return the bit-width of the value
 */
template<typename Numeric>
uint8_t bit_width(Numeric n)
{
    static_assert(std::is_unsigned<Numeric>::value, "not defined for signed integral types");

    // Count leading zeros.
    int lz;
    if constexpr (std::is_same_v<Numeric, unsigned>) {
        lz = __builtin_clz(n);
    } else if constexpr (std::is_same_v<Numeric, unsigned long>) {
        lz = __builtin_clzl(n);
    } else if constexpr (std::is_same_v<Numeric, unsigned long long>) {
        lz = __builtin_clzll(n);
    } else {
        static_assert(sizeof(Numeric) > sizeof(unsigned long long), "unsupported width of integral type");
    }

    return sizeof(Numeric) * 8 - lz;
}

/**
 * Computes the length of the common prefix of two numeric values @p v1 and @p v2.
 * @tparam Numeric the type of the values
 * @param v1 the first value
 * @param v2 the second value
 * @return the length of the common prefix
 */
template<typename Numeric>
uint8_t common_prefix_width(Numeric v1, Numeric v2)
{
    uint8_t length = std::numeric_limits<Numeric>::digits;

    while (v1 != v2) {
        v1 >>= 1;
        v2 >>= 1;
        length -= 1;
    }
    return length;
}


/*======================================================================================================================
 * String Functions
 *====================================================================================================================*/

/**
 * Splits @p str at each occurence of @p delimiter.
 * @param str the string to be split
 * @param delimiter the delimiter to split the string at
 * @return vector of substrings
 */
std::vector<std::string> split(const std::string &str, char delimiter)
{
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream token_stream(str);
    while (std::getline(token_stream, token, delimiter)) {
        tokens.push_back(token);
    }
    return tokens;
}


/*======================================================================================================================
 * Dataset Functions
 *====================================================================================================================*/

/**
 * Reads a dataset file @p filename in binary format and writes keys to vector.
 * @tparam Key the type of the key
 * @param filename name of the dataset file
 * @return vector of keys
 */
template<typename Key>
std::vector<Key> load_data(const std::string &filename) {
    using key_type = Key;

    // Open file.
    std::ifstream in(filename, std::ios::binary);
    if (!in.is_open()) {
        std::cerr << "Could not load " << filename << '.' << std::endl;
        exit(EXIT_FAILURE);
    }

    // Read number of keys.
    uint64_t n_keys;
    in.read(reinterpret_cast<char*>(&n_keys), sizeof(uint64_t));

    // Initialize vector.
    std::vector<key_type> data;
    data.resize(n_keys);

    // Read keys.
    in.read(reinterpret_cast<char*>(data.data()), n_keys * sizeof(key_type));
    in.close();

    return data;
}
