#pragma once

#include <cmath>

#include "rmi/util/fn.hpp"


namespace rmi {

template<typename X>
struct LinearSpline
{
    using x_type = X;

    static_assert(std::is_arithmetic<X>::value, "X must be numeric.");

    private:
    double slope_;
    double intercept_;

    public:
    LinearSpline() = default;
    LinearSpline(double slope, double intercept) : slope_(slope), intercept_(intercept) { }

    LinearSpline(const X *Xs, std::size_t offset, std::size_t n, double compression_factor = 1.f) {
        if (n == 0) {
            slope_ = 0.f;
            intercept_ = 0.f;
            return;
        }
        if (n == 1) {
            slope_ = 0.f;
            intercept_ = static_cast<double>(offset) * compression_factor;
            return;
        }

        double numerator = static_cast<double>(n); // (offset + n) - offset
        double denominator = static_cast<double>(Xs[offset + n - 1] - Xs[offset]);

        slope_ = denominator != 0.0 ? numerator/denominator * compression_factor : 0.0;
        intercept_ = offset * compression_factor - slope_ * Xs[offset];
    }

    LinearSpline(const X *Xs, std::size_t n) : LinearSpline(Xs, 0, n, 1.f) { }

    public:
    double predict(const x_type x) const { return std::fma(slope_, static_cast<double>(x), intercept_); }

    double slope() const { return slope_; }
    double intercept() const { return intercept_; }

    std::size_t size_in_bytes() { return 2 * sizeof(double); }

    friend std::ostream & operator<<(std::ostream &out, const LinearSpline &m) {
        return out << m.slope() << " * x + " << m.intercept();
    }
};


template<typename X>
struct LinearRegression
{
    using x_type = X;

    static_assert(std::is_arithmetic<X>::value, "X must be numeric.");

    private:
    double slope_;
    double intercept_;

    public:
    LinearRegression() = default;
    LinearRegression(double slope, double intercept) : slope_(slope), intercept_(intercept) { }

    LinearRegression(const X *Xs, std::size_t offset, std::size_t n, double compression_factor = 1.f) {
        if (n == 0) {
            slope_ = 0.f;
            intercept_ = 0.f;
            return;
        }
        if (n == 1) {
            slope_ = 0.f;
            intercept_ = static_cast<double>(offset) * compression_factor;
            return;
        }

        double mean_x = 0.0;
        double mean_y = 0.0;
        double c = 0.0;
        double m2 = 0.0;

        for (std::size_t i = 0; i != n; ++i) {
            x_type x = Xs[offset + i];
            std::size_t y = offset + i;

            double dx = x - mean_x;
            mean_x += dx /  (i + 1);
            mean_y += (y - mean_y) / (i + 1);
            c += dx * (y - mean_y);

            double dx2 = x - mean_x;
            m2 += dx * dx2;
        }

        double cov = c / (n - 1);
        double var = m2 / (n - 1);

        if (var == 0.f) {
            slope_  = 0.f;
            intercept_ = mean_y;
            return;
        }

        slope_ = cov / var * compression_factor;
        intercept_ = mean_y * compression_factor - slope_ * mean_x;
    }

    LinearRegression(const X *Xs, std::size_t n) : LinearRegression(Xs, 0, n, 1.f) { }

    public:
    double predict(const x_type x) const { return std::fma(slope_, static_cast<double>(x), intercept_); }

    std::size_t size_in_bytes() { return 2 * sizeof(double); }

    double slope() const { return slope_; }
    double intercept() const { return intercept_; }

    friend std::ostream & operator<<(std::ostream &out, const LinearRegression &m) {
        return out << m.slope() << " * x + " << m.intercept();
    }
};


template<typename X>
struct CubicSpline
{
    using x_type = X;

    static_assert(std::is_arithmetic<X>::value, "X must be numeric.");

    private:
    double a_;
    double b_;
    double c_;
    double d_;

    public:
    CubicSpline() = default;
    CubicSpline(double a, double b, double c, double d) : a_(a), b_(b), c_(c), d_(d) { }

    CubicSpline(const X *Xs, std::size_t offset, std::size_t n, double compression_factor = 1.f) {
        if (n == 0) {
            a_ = 0.f;
            b_ = 0.f;
            c_ = 1.f;
            d_ = 0.f;
            return;
        }
        if (n == 1 or Xs[offset] == Xs[offset + n - 1]) {
            a_ = 0.f;
            b_ = 0.f;
            c_ = 0.f;
            d_ = static_cast<double>(offset) * compression_factor;
            return;
        }

        double xmin = static_cast<double>(Xs[offset]);
        double ymin = static_cast<double>(offset) * compression_factor;
        double xmax = static_cast<double>(Xs[offset + n - 1]);
        double ymax = static_cast<double>(offset + n - 1) * compression_factor;

        double x1 = 0.0;
        double y1 = 0.0;
        double x2 = 1.0;
        double y2 = 1.0;

        double sxn, syn = 0.0;
        for (std::size_t i = 0; i != n; ++i) {
            double x = static_cast<double>(Xs[offset + i]);
            double y = static_cast<double>(offset + i) * compression_factor;
            sxn = (x - xmin) / (xmax - xmin);
            if (sxn > 0.0) {
                syn = (y - ymin) / (ymax - ymin);
                break;
            }
        }
        double m1 = (syn - y1) / (sxn - x1);

        double sxp, syp = 0.0;
        for (std::size_t i = 0; i != n; ++i) {
            double x = static_cast<double>(Xs[offset + i]);
            double y = static_cast<double>(offset + i) * compression_factor;
            sxp = (x - xmin) / (xmax - xmin);
            if (sxp < 1.0) {
                syp = (y - ymin) / (ymax - ymin);
                break;
            }
        }
        double m2 = (y2 - syp) / (x2 - sxp);

        if (std::pow(m1, 2.0) + std::pow(m2, 2.0) > 9.0) {
            double tau = 3.0 / std::sqrt(std::pow(m1, 2.0) + std::pow(m2, 2.0));
            m1 *= tau;
            m2 *= tau;
        }

        a_ = (m1 + m2 - 2.0)
            / std::pow(xmax - xmin, 3.0);

        b_ = -(xmax * (2.0 * m1 + m2 - 3.0) + xmin * (m1 + 2.0 * m2 - 3.0))
            / std::pow(xmax - xmin, 3.0);

        c_ = (m1 * std::pow(xmax, 2.0) + m2 * std::pow(xmin, 2.0) + xmax * xmin * (2.0 * m1 + 2.0 * m2 - 6.0))
            / std::pow(xmax - xmin, 3.0);

        d_ = -xmin * (m1 * std::pow(xmax, 2.0) + xmax * xmin * (m2 - 3.0) + std::pow(xmin, 2.0))
            / std::pow(xmax - xmin, 3.0);

        a_ *= ymax - ymin;
        b_ *= ymax - ymin;
        c_ *= ymax - ymin;
        d_ *= ymax - ymin;
        d_ += ymin;

        /* Check if linear spline performs better. */
        LinearSpline<x_type> ls(Xs, offset, n, compression_factor);

        double ls_error = 0.f;
        double cs_error = 0.f;

        for (std::size_t i = 0; i != n; ++i) {
            auto pos = offset + i;
            double y = (offset +i) * compression_factor;
            auto key = Xs[pos];
            double ls_pred = ls.predict(key);
            double cs_pred = predict(key);
            ls_error += std::abs(ls_pred - y);
            cs_error += std::abs(cs_pred - y);
        }

        if (ls_error < cs_error) {
            a_ = 0;
            b_ = 0;
            c_ = ls.slope();
            d_ = ls.intercept();
        }
    }

    CubicSpline(const X *Xs, std::size_t n) : CubicSpline(Xs, 0, n, 1.f) { }

    public:
    double predict(const x_type x) const {
        double x_ = static_cast<double>(x);
        double v1 = std::fma(a_, x_, b_);
        double v2 = std::fma(v1, x_, c_);
        double v3 = std::fma(v2, x_, d_);
        return v3;
    }

    double a() const { return a_; }
    double b() const { return b_; }
    double c() const { return c_; }
    double d() const { return d_; }

    std::size_t size_in_bytes() { return 4 * sizeof(double); }

    friend std::ostream & operator<<(std::ostream &out, const CubicSpline &m) {
        return out << m.a() << " * x^3 + "
                   << m.b() << " * x^2 + "
                   << m.c() << " * x + d";
    }
};


template<typename X>
struct Radix
{
    using x_type = X;

    static_assert(std::is_arithmetic<X>::value, "X must be numeric.");

    private:
    uint8_t prefix_;
    uint8_t radix_;

    public:
    Radix() = default;
    Radix(uint8_t prefix, uint8_t radix) : prefix_(prefix), radix_(radix)  { }

    Radix(const X *Xs, std::size_t offset, std::size_t n, double compression_factor = 1.f) {
        if (n == 0) {
            prefix_ = 0;
            radix_ = 0;
            return;
        }

        prefix_ = common_prefix_width<x_type>(Xs[offset], Xs[offset + n - 1]); // compute common prefix length

        /* Determine radix width. */
        std::size_t max = static_cast<std::size_t>(offset + n - 1) * compression_factor;
        bool is_power_of_two = (max & (max + 1)) == 0; // check if max is 2^n-1
        radix_ = is_power_of_two ? bit_width<std::size_t>(max) : bit_width<std::size_t>(max) - 1;
    }

    Radix(const X *Xs, std::size_t n) : Radix(Xs, 0, n, 1.f) { }

    public:
    double predict(const x_type x) const {
        return (x << prefix_) >> ((sizeof(x_type) * 8) - radix_);
    }

    uint8_t prefix() const { return prefix_; }
    uint8_t radix() const { return radix_; }

    std::size_t size_in_bytes() { return 2 * sizeof(uint8_t); }

    friend std::ostream & operator<<(std::ostream &out, const Radix &m) {
        return out << "(x << " << unsigned(m.prefix()) << ") >> " << ((sizeof(x_type) * 8) - unsigned(m.radix()));
    }
};

} // namespace rmi
