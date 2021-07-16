# A Critical Analysis of Recursive Model Indexes
Code used for the arXiv report.

## Build
```
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make
bin/example
```

## Example
```c++
// Initialize random number generator.
using key_type = uint64_t;
std::mt19937 gen(42);
std::uniform_int_distribution<key_type> key_distrib(0, 1UL << 48);
auto rand = [&gen, &key_distrib] { return key_distrib(gen); };

// Create 1M random keys.
std::size_t n_keys = 1e7;
std::vector<key_type> keys(n_keys);
std::generate(keys.begin(), keys.end(), rand);
std::sort(keys.begin(), keys.end());

// Build a two-layer RMI.
using layer1_type = rmi::LinearSpline;
using layer2_type = rmi::LinearRegression;
std::size_t layer2_size = 2UL << 16;
rmi::RmiLAbs<key_type, layer1_type, layer2_type> rmi(keys, layer2_size);

// Pick a key.
std::uniform_int_distribution<std::size_t> uniform_distrib(0, n_keys - 1);
key_type key = keys[uniform_distrib(gen)];

// Perform a lookup.
auto range = rmi.search(key);
auto pos = std::lower_bound(keys.begin() + range.lo, keys.begin() + range.hi, key);
std::cout << "Key " << key << " is located at position "
          << std::distance(keys.begin(), pos) << '.' << std::endl;
```

## Experimental Results
The code to reproduce our experimental results will be added in a future commit.

## Cite
```
@misc{maltry2021critical,
    title={A Critical Analysis of Recursive Model Indexes},
    author={Marcel Maltry and Jens Dittrich},
    year={2021},
    eprint={2106.16166},
    archivePrefix={arXiv},
    primaryClass={cs.DB}
}
```
