#pragma once
#include <algorithm>
#include <functional>
#include <iostream>
#include <type_traits>
#include <string>
#include <vector>
#include "../../library/c++/BiPaGe/Collection.h"

#define check_equal(l,r) check_equal_func(l,r,__FUNCTION__, __LINE__)
#define check_exception(e,f) check_exception_func<e>(f,__FUNCTION__, __LINE__, #e)
#define check_type(e,v) check_type_func<e>(v,__FUNCTION__, __LINE__, #e)


template<typename T1, typename T2>
typename std::enable_if<!std::is_enum<T1>::value, void>::type
check_equal_func(const T1& l, const T2& r, const char* caller, int line)
{
    if(l != r)
    {
        std::cerr << "check_equal called from " << caller << ", line " << line << ": " << +l << " is not equal to " << +r << std::endl;
        exit(-1);
    }
}

template<typename T1, typename T2>
typename std::enable_if<std::is_enum<T1>::value, void>::type
check_equal_func(const T1& l, const T2& r, const char* caller, int line)
{
    if(l != r)
    {
        std::cerr << "check_equal called from " << caller << ", line " << line << ": " << +static_cast<int>(l) << " is not equal to " << +static_cast<int>(r) << std::endl;
        exit(-1);
    }
}

template<typename T1, typename T2>
void check_equal_func(const std::vector<T1>& l, const std::vector<T2>& r, const char* caller, int line)
{
    if(l.size() != r.size())
    {
        std::cerr << "check_equal called from " << caller << ", line " << line << ": Vector L size " << l.size() << " is not equal to R size " << r.size() << std::endl;
    }
    if(!std::equal(l.begin(), l.begin() + std::min(l.size(), r.size()), r.begin()))
    {
        std::cerr << "check_equal called from " << caller << ", line " << line << ": Two vectors are not equal:" << std::endl;
        for(size_t i = 0 ; i < l.size() ; ++i)
        {
            std::cerr << +l[i] << " " << +r[i];
            if(l[i] != r[i])
            {
                std::cerr << " <--";
            }
            std::cerr << std::endl;
        }
        exit(-1);
    }
}

std::string clean_string(std::string s)
{
    s.erase(std::remove_if(s.begin(), s.end(), [](unsigned char x){return std::isspace(x);}), s.end());
    return s;
}

void check_equal_func(const std::string l, const std::string r, const char* caller, int line)
{
    std::string lclean = clean_string(l);
    std::string rclean = clean_string(r);
    // convert to vector of char so we can use the vector compare function
    check_equal_func(
                std::vector<char>(lclean.begin(),lclean.end()),
                std::vector<char>(rclean.begin(),rclean.end()),
                caller,
                line);
}

template<typename T>
void check_equal_func(const BiPaGe::CollectionLittleEndian<T>& l, const std::vector<T>& r, const char* caller, int line)
{
    if(l.size() != r.size())
    {
        std::cerr << "check_equal called from " << caller << ", line " << line << ": Vector L size " << l.size() << " is not equal to R size " << r.size() << std::endl;
        exit(-1);
    }
    if(!std::equal(l.begin(), l.end(), r.begin()))
    {
        std::cerr << "check_equal called from " << caller << ", line " << line << ": Two vectors are not equal:" << std::endl;
        for(size_t i = 0 ; i < l.size() ; ++i)
        {
            std::cerr << +l[i] << " " << +r[i];
            if(l[i] != r[i])
            {
                std::cerr << " <--";
            }
            std::cerr << std::endl;
        }
        exit(-1);
    }
}

template<typename ExceptionType>
void check_exception_func(std::function<void()>f, const char* caller, int line, const char* expected)
{
    try
    {
        f();
        std::cerr << "check_exception called from " << caller << ", line " << line << ": expected \"" << expected << "\" wasn't thrown" << std::endl;
        exit(-1);
    }
    catch(const ExceptionType&)
    {
    }
}

template<typename EXPECTED, typename ACTUAL>
void check_type_func(ACTUAL val, const char* caller, int line, const char* expected)
{
    if(!std::is_same<decltype(val), EXPECTED>::value)
    {
        std::cerr << "check_type called from " << caller << ", line " << line << ": type does not match expected type " << expected << std::endl;
        exit(-1);
    }
}

template<typename T>
std::uint8_t* serialize(std::uint8_t* data, T value)
{
    *reinterpret_cast<T*>(data) = value;
    return data + sizeof(T);
}

template<typename T>
std::uint8_t* serialize(std::uint8_t* data, const std::vector<T>& values)
{
    for(const T& val : values)
    {
        data = serialize(data, val);
    }
    return data;
}

void naive_swap_impl(char* data, size_t size)
{
    for(size_t i = 0 ; i < size / 2 ; ++i)
    {
        std::swap(data[i], data[size - 1 - i]);
    }
}

template <typename T>
T naive_swap(const T& val)
{
    T copy = val;
    naive_swap_impl(reinterpret_cast<char*>(&copy), sizeof(T));
    return copy;
}
