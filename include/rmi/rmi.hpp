#pragma once

#include <algorithm>

// Define bound types.
#define LIND 0
#define LABS 1
#define GIND 2
#define GABS 3
#define NB 4

// Default: Local absolute.
#ifndef BOUND
#define BOUND LABS
#endif


namespace rmi {

struct RmiApprox {
    std::size_t pos;
    std::size_t lo;
    std::size_t hi;
};

template<typename Key, typename Layer1, typename Layer2>
struct Rmi
{
    using key_type = Key;
    using layer1_type = Layer1;
    using layer2_type = Layer2;

    private:
    layer1_type l1_;
    layer2_type *l2_;
    std::size_t n_keys_;
    std::size_t layer2_size_;

#if BOUND == LIND
    struct bounds {
        std::size_t lo;
        std::size_t hi;
        bounds() : lo(0), hi(0) { }
    };
    bounds *errors_;
#elif BOUND == LABS
    std::size_t *errors_;
#elif BOUND == GIND
    std::size_t error_lo_;
    std::size_t error_hi_;
#elif BOUND == GABS
    std::size_t error_;
#elif BOUND == NB
    // nothing to do
#else
#error "Invalid BOUND."
#endif

    public:
    Rmi(const key_type *keys, std::size_t n_keys, std::size_t layer2_size)
        : n_keys_(n_keys)
        , layer2_size_(layer2_size)
    {

        /* Train layer1. */
        l1_ = layer1_type(keys, 0, n_keys_, static_cast<double>(layer2_size) / n_keys_); // train with compression

        /* Train layer2. We assume only monotonic models. */
        l2_ = new layer2_type[layer2_size_];
        std::size_t bucket_start = 0;
        std::size_t curr_bucket = 0;
        for (std::size_t i = 0; i != n_keys_; ++i) {
            std::size_t pred_bucket = get_bucket(keys[i]);
            if (pred_bucket > curr_bucket) {
                l2_[curr_bucket] = layer2_type(keys, bucket_start, i - bucket_start); // train curr_bucket
                for (std::size_t j = curr_bucket + 1; j != pred_bucket; ++j)
                    l2_[j] = layer2_type(keys, i - 1, 1); // train buckets in-between TODO: check for out-of-bounds
                curr_bucket = pred_bucket;
                bucket_start = i;
            }
        }
        l2_[curr_bucket] = layer2_type(keys, bucket_start, n_keys_ - bucket_start); // train curr_bucket
        for (std::size_t j = curr_bucket + 1; j != layer2_size_; ++j)
            l2_[j] = layer2_type(keys, n_keys_ - 1, 1); // train remaining buckets

        /* Compute error bounds. */
        // TODO: Interleave with layer 2 training to avoid full RMI evaluation.
#if BOUND == LIND
        errors_ = new bounds[layer2_size_];
        for (std::size_t i = 0; i != n_keys_; ++i) {
            key_type key = keys[i];
            std::size_t bucket = get_bucket(key);
            std::size_t pred = std::clamp<double>(l2_[bucket].predict(key), 0, n_keys_ - 1);
            if (pred > i) { // overestimation
                std::size_t &lo = errors_[bucket].lo;
                lo = std::max(lo, pred - i);
            } else { // underestimation
                std::size_t &hi = errors_[bucket].hi;
                hi = std::max(hi, i - pred);
            }
        }
#elif BOUND == LABS
        errors_ = new std::size_t[layer2_size_]();
        for (std::size_t i = 0; i != n_keys_; ++i) {
            key_type key = keys[i];
            std::size_t bucket = get_bucket(key);
            std::size_t pred = std::clamp<double>(l2_[bucket].predict(key), 0, n_keys_ - 1);
            if (pred > i) { // overestimation
                errors_[bucket] = std::max(errors_[bucket], pred - i);
            } else { // underestimation
                errors_[bucket] = std::max(errors_[bucket], i - pred);
            }
        }
#elif BOUND == GIND
        error_lo_ = 0;
        error_hi_ = 0;
        for (std::size_t i = 0; i != n_keys_; ++i) {
            key_type key = keys[i];
            std::size_t bucket = get_bucket(key);
            std::size_t pred = std::clamp<double>(l2_[bucket].predict(key), 0, n_keys_ - 1);
            if (pred > i) { // overestimation
                error_lo_ = std::max(error_lo_, pred - i);
            } else { // underestimation
                error_hi_ = std::max(error_hi_, i - pred);
            }
        }
#elif BOUND == GABS
        error_ = 0;
        for (std::size_t i = 0; i != n_keys_; ++i) {
            key_type key = keys[i];
            std::size_t bucket = get_bucket(key);
            std::size_t pred = std::clamp<double>(l2_[bucket].predict(key), 0, n_keys_ - 1);
            if (pred > i) { // overestimation
                error_ = std::max(error_, pred - i);
            } else { // underestimation
                error_ = std::max(error_, i - pred);
            }
        }
#endif
    }

    ~Rmi() {
        delete[] l2_;
#if BOUND == LIND
        delete[] errors_;
#elif BOUND == LABS
        delete[] errors_;
#endif
    }

    std::size_t get_bucket(const key_type key) const {
        return std::clamp<double>(l1_.predict(key), 0, layer2_size_ - 1);
    }

    RmiApprox search(const key_type key) const {
        std::size_t bucket = get_bucket(key);
        std::size_t pred = std::clamp<double>(l2_[bucket].predict(key), 0, n_keys_ - 1);
#if BOUND == LIND
        bounds err = errors_[bucket];
        std::size_t lo = pred > err.lo ? pred - err.lo : 0;
        std::size_t hi = std::min(pred + err.hi + 1, n_keys_);
#elif BOUND == LABS
        std::size_t err = errors_[bucket];
        std::size_t lo = pred > err ? pred - err : 0;
        std::size_t hi = std::min(pred + err + 1, n_keys_);
#elif BOUND == GIND
        std::size_t lo = pred > error_lo_ ? pred - error_lo_ : 0;
        std::size_t hi = std::min(pred + error_hi_ + 1, n_keys_);
#elif BOUND == GABS
        std::size_t lo = pred > error_ ? pred - error_ : 0;
        std::size_t hi = std::min(pred + error_ + 1, n_keys_);
#elif BOUND == NB
        std::size_t lo = 0;
        std::size_t hi = n_keys_;
#endif
        return {pred, lo, hi};
    }

    layer1_type l1() const { return l1_; }
    layer2_type *l2() const { return l2_; }
    std::size_t n_keys() const { return n_keys_; }
    std::size_t layer2_size() const { return layer2_size_; }
#if BOUND == LIND
    auto errors() const { return errors; }
#elif BOUND == LABS
    auto errors() const { return errors; }
#elif BOUND == GIND
    auto error_lo() { return error_lo_; }
    auto error_hi() { return error_hi_; }
#elif BOUND == GABS
    auto error() { return error_; }
#endif

    std::size_t size_in_bytes() {
#if BOUND == LIND
        auto err_size = layer2_size_ * sizeof(errors_[0]);
#elif BOUND == LABS
        auto err_size = layer2_size_ * sizeof(errors_[0]);
#elif BOUND == GIND
        auto err_size =  sizeof(error_lo_) + sizeof(error_hi_);
#elif BOUND == G1S_BOUND
        auto err_size = sizeof(error_);
#elif BOUND == NON_BOUND
        auto err_size = 0;
#endif
        return l1_.size_in_bytes() + layer2_size_ * l2_[0].size_in_bytes()
            + sizeof(n_keys_) + sizeof(layer2_size_) + err_size;
    }
};

} // namespace rmi
