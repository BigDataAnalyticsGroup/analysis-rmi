#include <iostream>
#include <random>
#include <vector>

#include "rmi/models.hpp"
#include "rmi/rmi.hpp"


int main()
{
    /* Create 1M random keys. */
    using key_type = uint64_t;
    std::vector<key_type> keys_vec(1e7);
    std::generate(keys_vec.begin(), keys_vec.end(), std::rand);
    std::sort(keys_vec.begin(), keys_vec.end());
    auto keys = keys_vec.data();
    auto n_keys = keys_vec.size();

    /* Build a two-layer RMI. */
    using layer1_type = rmi::LinearSpline<key_type>;
    using layer2_type = rmi::LinearRegression<key_type>;
    std::size_t layer2_size = 2UL << 16;
    rmi::Rmi<key_type, layer1_type, layer2_type> rmi(keys, n_keys, layer2_size);

    /* Pick a key. */
    std::mt19937 gen(42);
    std::uniform_int_distribution<std::size_t> distrib(0, n_keys);
    key_type key = keys[distrib(gen)];

    /* Perform a lookup. */
    auto range = rmi.search(key);
    auto pos = std::distance(keys, std::lower_bound(keys + range.lo, keys + range.hi, key));
    std::cout << "Key " << key << " is located at position " << pos << '.' << std::endl;

   return 0;
}
